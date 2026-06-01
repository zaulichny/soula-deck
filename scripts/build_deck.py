#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Собирает презентацию .pptx в фирменном стиле SOULA из спецификации слайдов.

Идея (ровно как написано на 1-м слайде шаблона): не перерисовываем дизайн, а
берём слайд-донор нужного макета и подставляем в него текст. Поэтому шрифты,
цвета, отступы, орб и градиенты сохраняются автоматически.

Зависимостей нет — только стандартная библиотека Python 3.

Использование:
    python3 build_deck.py --spec spec.json --out deck.pptx
    # необязательно: --template assets/template.pptx --layouts layouts.json

Формат spec.json:
{
  "slides": [
    {"layout": "title", "fields": {"headline": "Заголовок, *акцент* и ясность", ...}},
    {"layout": "two-columns", "fields": {...}},
    ...
  ]
}

Имена макетов и их поля смотри в layouts.json (или в LAYOUTS.md).
В заголовках одно слово/фразу можно выделить звёздочками: *вот так* —
оно станет жирным розовым (фирменный акцент). Ровно один акцент на заголовок.
В многострочных полях (before_lines / after_lines) разделяй строки переводом строки.
"""
import argparse
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

ACCENT_COLOR = "FF2E6E"  # фирменный розовый


# ---------- экранирование текста для XML ----------
def esc(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ---------- работа с run / paragraph / shape (строковая хирургия) ----------
def find_blocks(xml, tag):
    """Вернуть список (start, end, text) для всех <tag>...</tag> на верхнем уровне поиска."""
    return [(m.start(), m.end(), m.group(0))
            for m in re.finditer(r"<%s>.*?</%s>" % (tag, tag), xml, re.S)]


def text_shapes(slide_xml):
    """Спаны форм <p:sp>...</p:sp>, содержащих текст — в порядке документа.

    Та же логика, что в generate_layouts.py, поэтому индексы полей совпадают.
    """
    out = []
    for m in re.finditer(r"<p:sp>.*?</p:sp>", slide_xml, re.S):
        if "<p:txBody>" in m.group(0):
            out.append((m.start(), m.end(), m.group(0)))
    return out


def grab_tag(tag, xml):
    """Вернуть первый элемент <tag.../> ИЛИ <tag ...>...</tag> (с вложениями).

    Важно: элемент может быть самозакрывающимся ИЛИ иметь дочерние теги
    (например, <a:rPr><a:solidFill><a:srgbClr/></a:solidFill></a:rPr>).
    Простая регулярка ".*?/>" ошибочно обрывалась бы на первом вложенном
    самозакрывающемся теге, поэтому различаем два случая явно.
    """
    m = re.search(
        r"<%s\b(?:[^>]*?/>|[^>]*?>.*?</%s>)" % (tag, tag), xml, re.S)
    return m.group(0) if m else ""


def run_rpr(run_xml):
    """Достать <a:rPr.../> (или <a:rPr>...</a:rPr>) из run; '' если нет."""
    return grab_tag("a:rPr", run_xml)


def run_is_accent(run_xml):
    return ('val="%s"' % ACCENT_COLOR in run_xml) or ('b="1"' in run_xml)


def set_run_text(run_xml, new_text):
    """Заменить содержимое <a:t> в одном run."""
    if re.search(r"<a:t[^>]*>.*?</a:t>", run_xml, re.S):
        return re.sub(r"(<a:t[^>]*>).*?(</a:t>)",
                      lambda m: m.group(1) + esc(new_text) + m.group(2),
                      run_xml, count=1, flags=re.S)
    # run без <a:t> — добавить перед концом
    return run_xml.replace("</a:r>", "<a:t>%s</a:t></a:r>" % esc(new_text), 1)


def para_set_plain(para_xml, new_text):
    """Положить весь текст в первый run абзаца, остальные runs обнулить."""
    runs = find_blocks(para_xml, "a:r")
    if not runs:
        return para_xml
    out = para_xml
    # с конца, чтобы офсеты не съезжали
    for i in range(len(runs) - 1, -1, -1):
        s, e, rxml = runs[i]
        txt = new_text if i == 0 else ""
        out = out[:s] + set_run_text(rxml, txt) + out[e:]
    return out


def para_set_run(para_xml, run_idx, new_text):
    runs = find_blocks(para_xml, "a:r")
    if run_idx >= len(runs):
        return para_xml
    s, e, rxml = runs[run_idx]
    return para_xml[:s] + set_run_text(rxml, new_text) + para_xml[e:]


def para_set_accent(para_xml, new_text):
    """Перестроить runs абзаца из текста с *акцентом*.

    Формат rPr берём из шаблона: обычный — из первого неакцентного run,
    акцентный — из первого акцентного run (если есть).
    """
    runs = find_blocks(para_xml, "a:r")
    normal_rpr, accent_rpr = "", ""
    for _, _, rxml in runs:
        if run_is_accent(rxml):
            if not accent_rpr:
                accent_rpr = run_rpr(rxml)
        else:
            if not normal_rpr:
                normal_rpr = run_rpr(rxml)
    if not normal_rpr and runs:
        normal_rpr = run_rpr(runs[0][2])
    if not accent_rpr:
        accent_rpr = normal_rpr  # запасной вариант: без выделения

    # разбить по *...*  (нечётные сегменты = акцент)
    parts = new_text.split("*")
    new_runs = []
    for i, seg in enumerate(parts):
        if seg == "":
            continue
        rpr = accent_rpr if (i % 2 == 1) else normal_rpr
        new_runs.append("<a:r>%s<a:t>%s</a:t></a:r>" % (rpr, esc(seg)))
    runs_xml = "".join(new_runs)

    # сохранить pPr (если есть) и endParaRPr (если есть)
    ppr = grab_tag("a:pPr", para_xml)
    endpr = grab_tag("a:endParaRPr", para_xml)
    inner = ppr + runs_xml + endpr
    return "<a:p>%s</a:p>" % inner


def shape_set_multiline(shape_xml, value):
    """Заменить абзацы формы строками из value (по одному абзацу на строку)."""
    lines = value.split("\n")
    txb = re.search(r"(<p:txBody>)(.*?)(</p:txBody>)", shape_xml, re.S)
    if not txb:
        return shape_xml
    body = txb.group(2)
    paras = find_blocks(body, "a:p")
    if not paras:
        return shape_xml
    # часть тела до первого абзаца (bodyPr, lstStyle) и после последнего
    head = body[:paras[0][0]]
    tail = body[paras[-1][1]:]
    templates = [p[2] for p in paras]
    new_paras = []
    for i, line in enumerate(lines):
        tmpl = templates[i] if i < len(templates) else templates[-1]
        new_paras.append(para_set_plain(tmpl, line))
    new_body = head + "".join(new_paras) + tail
    return shape_xml[:txb.start(2)] + new_body + shape_xml[txb.end(2):]


def apply_field(shape_xml, entry, value):
    """Применить одно поле к XML формы и вернуть новый XML формы."""
    kind = entry["kind"]
    if kind == "multiline":
        return shape_set_multiline(shape_xml, value)

    para_idx = entry.get("para", 0)
    txb = re.search(r"(<p:txBody>)(.*?)(</p:txBody>)", shape_xml, re.S)
    if not txb:
        return shape_xml
    body = txb.group(2)
    paras = find_blocks(body, "a:p")
    if para_idx >= len(paras):
        return shape_xml
    ps, pe, pxml = paras[para_idx]

    if kind == "accent":
        new_p = para_set_accent(pxml, value)
    elif kind == "run":
        new_p = para_set_run(pxml, entry.get("run", 0), value)
    else:  # plain, pagenum
        new_p = para_set_plain(pxml, value)

    new_body = body[:ps] + new_p + body[pe:]
    return shape_xml[:txb.start(2)] + new_body + shape_xml[txb.end(2):]


def build_slide(donor_xml, layout_def, fields, page_number):
    """Вернуть XML слайда-донора с подставленными значениями."""
    # сгруппировать операции по индексу формы
    ops_by_shape = {}
    fdef = layout_def["fields"]

    # автонумерация страницы
    if "_pagenum" in fdef:
        e = dict(fdef["_pagenum"])
        ops_by_shape.setdefault(e["shape"], []).append((e, "%02d" % page_number))

    unknown = []
    for fname, value in fields.items():
        if fname not in fdef:
            unknown.append(fname)
            continue
        e = fdef[fname]
        ops_by_shape.setdefault(e["shape"], []).append((e, str(value)))

    if unknown:
        sys.stderr.write(
            "  ! неизвестные поля для макета '%s': %s\n"
            % (layout_def.get("_name", "?"), ", ".join(unknown))
        )

    shapes = text_shapes(donor_xml)
    out = donor_xml
    # применяем с конца, чтобы офсеты форм не съезжали
    for sidx in sorted(ops_by_shape.keys(), reverse=True):
        if sidx < 1 or sidx > len(shapes):
            sys.stderr.write("  ! форма #%d вне диапазона\n" % sidx)
            continue
        s, e, sxml = shapes[sidx - 1]
        new_sxml = sxml
        for entry, value in ops_by_shape[sidx]:
            new_sxml = apply_field(new_sxml, entry, value)
        out = out[:s] + new_sxml + out[e:]
    return out


# ---------- сборка пакета .pptx ----------
SLIDE_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
NOTES_SLIDE_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
SLIDE_CT = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
NOTES_SLIDE_CT = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"


def rebuild_presentation_rels(rels_xml, n_slides):
    """Сохранить все связи кроме слайдов; добавить n_slides новых связей.

    Возвращает (новый_xml, [rId слайдов в порядке]).
    """
    kept = re.findall(r"<Relationship\b[^>]*?/>", rels_xml)
    kept = [r for r in kept if ('Type="%s"' % SLIDE_TYPE) not in r]
    max_id = 0
    for r in kept:
        m = re.search(r'Id="rId(\d+)"', r)
        if m:
            max_id = max(max_id, int(m.group(1)))
    slide_ids = []
    new_rels = []
    for i in range(1, n_slides + 1):
        rid = "rId%d" % (max_id + i)
        slide_ids.append(rid)
        new_rels.append(
            '<Relationship Id="%s" Type="%s" Target="slides/slide%d.xml"/>'
            % (rid, SLIDE_TYPE, i)
        )
    inner = "".join(kept) + "".join(new_rels)
    new_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + inner + "</Relationships>"
    )
    return new_xml, slide_ids


def rebuild_presentation_xml(pres_xml, slide_ids):
    """Переписать <p:sldIdLst> на новый набор слайдов."""
    ids = []
    for i, rid in enumerate(slide_ids):
        ids.append('<p:sldId id="%d" r:id="%s"/>' % (256 + i, rid))
    new_lst = "<p:sldIdLst>" + "".join(ids) + "</p:sldIdLst>"
    return re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", new_lst, pres_xml, flags=re.S)


def rebuild_content_types(ct_xml, n_slides):
    """Убрать Override для слайдов и заметок; добавить Override для новых слайдов."""
    # удалить старые слайд- и notesSlide-оверрайды
    ct_xml = re.sub(
        r'<Override PartName="/ppt/slides/slide\d+\.xml"[^>]*/>', "", ct_xml)
    ct_xml = re.sub(
        r'<Override PartName="/ppt/notesSlides/notesSlide\d+\.xml"[^>]*/>', "", ct_xml)
    adds = "".join(
        '<Override PartName="/ppt/slides/slide%d.xml" ContentType="%s"/>'
        % (i, SLIDE_CT)
        for i in range(1, n_slides + 1)
    )
    return ct_xml.replace("</Types>", adds + "</Types>")


def strip_notes_rel(slide_rels_xml):
    """Убрать связь со слайдом-заметкой (заметки в итоговый файл не кладём)."""
    return re.sub(
        r"<Relationship\b[^>]*Type=\"%s\"[^>]*/>" % re.escape(NOTES_SLIDE_TYPE),
        "", slide_rels_xml)


def main():
    ap = argparse.ArgumentParser(description="Сборка .pptx в стиле SOULA из spec.json")
    ap.add_argument("--spec", required=True, help="JSON со слайдами")
    ap.add_argument("--out", required=True, help="куда сохранить .pptx")
    ap.add_argument("--template", default=os.path.join(ROOT, "assets", "template.pptx"))
    ap.add_argument("--layouts", default=os.path.join(ROOT, "layouts.json"))
    args = ap.parse_args()

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    with open(args.layouts, encoding="utf-8") as f:
        layouts = json.load(f)
    for name, ld in layouts.items():
        ld["_name"] = name

    slides = spec.get("slides", [])
    if not slides:
        sys.exit("В spec.json нет слайдов (ключ 'slides').")

    # прочитать все части шаблона
    with zipfile.ZipFile(args.template) as z:
        parts = {n: z.read(n) for n in z.namelist()}

    donor_cache = {}  # номер донора -> (xml, rels_xml)

    def donor(num):
        if num not in donor_cache:
            sx = parts["ppt/slides/slide%d.xml" % num].decode("utf-8")
            rels = parts["ppt/slides/_rels/slide%d.xml.rels" % num].decode("utf-8")
            donor_cache[num] = (sx, rels)
        return donor_cache[num]

    # построить новые слайды
    new_slides = {}   # имя_части -> bytes
    new_rels = {}
    for i, sl in enumerate(slides, start=1):
        layout_name = sl.get("layout")
        if layout_name not in layouts:
            sys.exit("Слайд %d: неизвестный макет '%s'. Доступные: %s"
                     % (i, layout_name, ", ".join(layouts)))
        ld = layouts[layout_name]
        dxml, drels = donor(ld["donor"])
        slide_xml = build_slide(dxml, ld, sl.get("fields", {}), i)
        new_slides["ppt/slides/slide%d.xml" % i] = slide_xml.encode("utf-8")
        new_rels["ppt/slides/_rels/slide%d.xml.rels" % i] = \
            strip_notes_rel(drels).encode("utf-8")

    n = len(slides)

    # переписать служебные части
    pres_rels = parts["ppt/_rels/presentation.xml.rels"].decode("utf-8")
    pres_rels, slide_ids = rebuild_presentation_rels(pres_rels, n)
    pres_xml = parts["ppt/presentation.xml"].decode("utf-8")
    pres_xml = rebuild_presentation_xml(pres_xml, slide_ids)
    ct_xml = parts["[Content_Types].xml"].decode("utf-8")
    ct_xml = rebuild_content_types(ct_xml, n)

    # какие части НЕ копируем из шаблона (старые слайды, заметки)
    def skip(name):
        if re.match(r"ppt/slides/slide\d+\.xml$", name):
            return True
        if re.match(r"ppt/slides/_rels/slide\d+\.xml\.rels$", name):
            return True
        if name.startswith("ppt/notesSlides/"):
            return True
        return False

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            if skip(name):
                continue
            if name == "[Content_Types].xml":
                data = ct_xml.encode("utf-8")
            elif name == "ppt/presentation.xml":
                data = pres_xml.encode("utf-8")
            elif name == "ppt/_rels/presentation.xml.rels":
                data = pres_rels.encode("utf-8")
            z.writestr(name, data)
        for name, data in new_slides.items():
            z.writestr(name, data)
        for name, data in new_rels.items():
            z.writestr(name, data)

    print("OK: %s — %d слайд(ов)" % (args.out, n))


if __name__ == "__main__":
    main()
