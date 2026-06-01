#!/usr/bin/env python3
"""
Одноразовый генератор карты макетов (layouts.json) из шаблона SOULA.

Проходит по слайдам-донорам шаблона, перечисляет текстовые формы в порядке
документа (ровно так же, как это потом делает build_deck.py) и присваивает
каждой форме понятное имя поля. Заодно проверяет, что структура шаблона
совпала с ожидаемой — если форм стало больше/меньше, упадёт с ошибкой.

Запускать НЕ нужно при обычной работе скилла — он уже сгенерировал layouts.json.
Запускать только если поменялся сам шаблон (assets/template.pptx).

    python3 scripts/generate_layouts.py
"""
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(ROOT, "assets", "template.pptx")
OUT = os.path.join(ROOT, "layouts.json")

# Имя поля для каждой текстовой формы донора, в порядке документа.
# None  -> форма остаётся как в шаблоне (например, нижний колонтитул "SOULA").
# "@n"  -> номер страницы, проставляется автоматически.
# Поля с суффиксом ":runK" редактируют конкретный run внутри одного абзаца
# (используется для цифр вида "68" + "%").
LAYOUTS = {
    "title": {
        "donor": 2,
        "title": "Титульный слайд",
        "fields": [
            "eyebrow", "headline", "subtitle",
            "presenter_label", "presenter",
            "team_label", "team",
            "date_label", "date",
            None, "@n",
        ],
    },
    "section": {
        "donor": 3,
        "title": "Разделитель раздела",
        "fields": ["number", "eyebrow", "headline", "subtitle", None, "@n"],
    },
    "context": {
        "donor": 4,
        "title": "Контекст: тезис + поддержка",
        "fields": ["eyebrow", "headline", "lead", "supporting", "note", None, "@n"],
    },
    "two-columns": {
        "donor": 5,
        "title": "Две колонки",
        "fields": [
            "eyebrow", "headline",
            "colA_tag", "colA_heading", "colA_body",
            "colB_tag", "colB_heading", "colB_body",
            None, "@n",
        ],
    },
    "agenda": {
        "donor": 6,
        "title": "Повестка / список (до 4 пунктов)",
        "fields": [
            "eyebrow", "headline",
            "item1_num", "item1_heading", "item1_body",
            "item2_num", "item2_heading", "item2_body",
            "item3_num", "item3_heading", "item3_body",
            "item4_num", "item4_heading", "item4_body",
            None, "@n",
        ],
    },
    "numbers": {
        "donor": 7,
        "title": "Цифры / метрики (3 показателя)",
        "fields": [
            "eyebrow", "headline", "intro",
            "stat1_value:run0", "stat1_label",
            "stat2_value:run0", "stat2_label",
            "stat3_value:run0", "stat3_label",
            None, "@n",
        ],
        # отдельные поля для второго run (единица измерения)
        "extra": {
            "stat1_unit": {"shape": 4, "para": 0, "run": 1, "kind": "run"},
            "stat2_unit": {"shape": 6, "para": 0, "run": 1, "kind": "run"},
            "stat3_unit": {"shape": 8, "para": 0, "run": 1, "kind": "run"},
        },
    },
    "before-after": {
        "donor": 8,
        "title": "Было / Стало",
        "fields": [
            "eyebrow", "headline",
            "before_tag", "before_heading", "before_lines",
            "after_tag", "after_heading", "after_lines",
            None, "@n",
        ],
    },
    "roadmap": {
        "donor": 9,
        "title": "Дорожная карта (4 фазы)",
        "fields": [
            "eyebrow", "headline",
            "phase1_tag", "phase1_heading", "phase1_body",
            "phase2_tag", "phase2_heading", "phase2_body",
            "phase3_tag", "phase3_heading", "phase3_body",
            "phase4_tag", "phase4_heading", "phase4_body",
            None, "@n",
        ],
    },
    "overview": {
        "donor": 10,
        "title": "Обзор: тезис слева + пункты справа (до 4)",
        "fields": [
            "eyebrow", "headline", "intro",
            "bullet1_heading", "bullet1_body",
            "bullet2_heading", "bullet2_body",
            "bullet3_heading", "bullet3_body",
            "bullet4_heading", "bullet4_body",
            None, "@n",
        ],
    },
    "steps-screen": {
        "donor": 11,
        "title": "Как это работает + скриншот (3 шага)",
        "fields": [
            "screen_label", "eyebrow", "headline",
            "step1_num", "step1_heading", "step1_body",
            "step2_num", "step2_heading", "step2_body",
            "step3_num", "step3_heading", "step3_body",
            None, "@n",
        ],
    },
    "features-screen": {
        "donor": 12,
        "title": "Что получаешь + скриншот (3 пункта)",
        "fields": [
            "screen_label", "eyebrow", "headline",
            "feature1_heading", "feature1_body",
            "feature2_heading", "feature2_body",
            "feature3_heading", "feature3_body",
            None, "@n",
        ],
    },
    "steps-alt": {
        "donor": 13,
        "title": "Как это работает (компактно) + скриншот",
        "fields": [
            "eyebrow", "headline", "screen_label",
            "step1_tag", "step1_heading", "step1_body",
            "step2_tag", "step2_heading", "step2_body",
            "step3_tag", "step3_heading", "step3_body",
            None, "@n",
        ],
    },
    "closing": {
        "donor": 14,
        "title": "Спасибо / контакты",
        "fields": [
            "eyebrow", "headline", "subtitle",
            "contact1_label", "contact1_value",
            "contact2_label", "contact2_value",
            "contact3_label", "contact3_value",
            None, "@n",
        ],
    },
}

# поля, которые по смыслу являются заголовком с акцентом (*слово*)
ACCENT_FIELDS = {"headline"}
# поля-метки/цифры: один run, акцентный, заменяем как обычный текст
# (остальное определяется по структуре шаблона ниже)
MULTILINE_FIELDS = {"before_lines", "after_lines"}


def shapes_with_text(slide_xml):
    """Формы с текстом в порядке документа — та же логика, что в build_deck.py."""
    out = []
    for sp in re.finditer(r"<p:sp>.*?</p:sp>", slide_xml, re.S):
        body = sp.group(0)
        if "<p:txBody>" in body:
            out.append(body)
    return out


def paragraphs(shape_xml):
    txb = re.search(r"<p:txBody>(.*?)</p:txBody>", shape_xml, re.S)
    return re.findall(r"<a:p>.*?</a:p>", txb.group(1), re.S) if txb else []


def runs(para_xml):
    return re.findall(r"<a:r>.*?</a:r>", para_xml, re.S)


def run_is_accent(run_xml):
    return ('val="FF2E6E"' in run_xml) or ('b="1"' in run_xml)


def main():
    with zipfile.ZipFile(TEMPLATE) as z:
        slide_xmls = {
            int(re.search(r"slide(\d+)\.xml", n).group(1)): z.read(n).decode("utf-8")
            for n in z.namelist()
            if re.match(r"ppt/slides/slide\d+\.xml$", n)
        }

    result = {}
    problems = []
    for name, spec in LAYOUTS.items():
        donor = spec["donor"]
        xml = slide_xmls[donor]
        shapes = shapes_with_text(xml)
        fields_def = spec["fields"]
        if len(shapes) != len(fields_def):
            problems.append(
                f"{name}: форм в шаблоне {len(shapes)}, в карте {len(fields_def)}"
            )
            continue

        fields = {}
        for idx, fname in enumerate(fields_def, start=1):
            shape_xml = shapes[idx - 1]
            paras = paragraphs(shape_xml)
            if fname is None:
                continue
            if fname == "@n":
                fields["_pagenum"] = {"shape": idx, "para": 0, "kind": "pagenum"}
                continue

            # поле с указанием конкретного run: "name:runK"
            run_idx = None
            if ":run" in fname:
                fname, rk = fname.split(":run")
                run_idx = int(rk)

            # определить вид поля
            if fname in MULTILINE_FIELDS:
                kind = "multiline"
            elif run_idx is not None:
                kind = "run"
            elif fname in ACCENT_FIELDS:
                kind = "accent"
            else:
                # если у первого абзаца есть акцентный run и поле — это метка,
                # всё равно достаточно простой замены текста (один run)
                kind = "plain"

            entry = {"shape": idx, "para": 0, "kind": kind}
            if run_idx is not None:
                entry["run"] = run_idx
            fields[fname] = entry

        # дополнительные поля (например, единицы измерения у цифр)
        for fname, entry in spec.get("extra", {}).items():
            fields[fname] = entry

        result[name] = {
            "donor": donor,
            "title": spec["title"],
            "fields": fields,
        }

    if problems:
        print("ОШИБКИ СТРУКТУРЫ (шаблон не совпал с картой):", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        sys.exit(1)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK: записано {OUT} ({len(result)} макетов)")


if __name__ == "__main__":
    main()
