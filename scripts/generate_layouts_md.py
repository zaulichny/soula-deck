#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генерирует человекочитаемый справочник макетов LAYOUTS.md из layouts.json и шаблона.

Запускать ПОСЛЕ generate_layouts.py, когда обновили шаблон:
    python3 scripts/generate_layouts.py      # сначала карта полей
    python3 scripts/generate_layouts_md.py   # потом справочник для людей
"""
import html
import json
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LAYOUTS_JSON = os.path.join(ROOT, "layouts.json")
TEMPLATE = os.path.join(ROOT, "assets", "template.pptx")
OUT = os.path.join(ROOT, "LAYOUTS.md")

# порядок макетов в справочнике (по номеру слайда-донора)
ORDER = ["title", "section", "context", "two-columns", "agenda", "numbers",
         "before-after", "roadmap", "overview", "steps-screen",
         "features-screen", "steps-alt", "closing"]

KIND_RU = {
    "accent": "заголовок c *акцентом*",
    "plain": "строка",
    "multiline": "строки (через \\n)",
    "run": "часть строки (цифра/единица)",
}


def text_shapes(xml):
    return [m.group(0) for m in re.finditer(r"<p:sp>.*?</p:sp>", xml, re.S)
            if "<p:txBody>" in m.group(0)]


def paras(shape_xml):
    t = re.search(r"<p:txBody>(.*?)</p:txBody>", shape_xml, re.S)
    return re.findall(r"<a:p>.*?</a:p>", t.group(1), re.S) if t else []


def para_text(p):
    return html.unescape("".join(re.findall(r"<a:t>(.*?)</a:t>", p, re.S)))


def run_text(p, ri):
    rs = re.findall(r"<a:r>.*?</a:r>", p, re.S)
    if ri < len(rs):
        m = re.search(r"<a:t>(.*?)</a:t>", rs[ri], re.S)
        return html.unescape(m.group(1)) if m else ""
    return ""


def main():
    layouts = json.load(open(LAYOUTS_JSON, encoding="utf-8"))
    z = zipfile.ZipFile(TEMPLATE)

    out = [
        "# Справочник макетов SOULA Deck\n",
        "Поля каждого макета и пример «рыбы» из шаблона. В заголовке (`headline`) "
        "одно слово оборачивай в `*звёздочки*` — станет розовым акцентом.\n",
        "\n> Этот файл генерируется автоматически: "
        "`python3 scripts/generate_layouts_md.py`. Руками не правь.\n",
    ]

    names = ORDER + [n for n in layouts if n not in ORDER]
    for name in names:
        if name not in layouts:
            continue
        ld = layouts[name]
        out.append(f"\n## `{name}` — {ld['title']}\n")
        xml = z.read("ppt/slides/slide%d.xml" % ld["donor"]).decode("utf-8")
        shapes = text_shapes(xml)
        out.append("| Поле | Тип | Пример из шаблона |")
        out.append("|------|-----|-------------------|")
        items = [(f, e) for f, e in ld["fields"].items() if f != "_pagenum"]
        items.sort(key=lambda kv: (kv[1]["shape"], kv[1].get("run", 0)))
        for f, e in items:
            sidx, pidx = e["shape"], e.get("para", 0)
            ex = ""
            if sidx - 1 < len(shapes):
                ps = paras(shapes[sidx - 1])
                if pidx < len(ps):
                    ex = run_text(ps[pidx], e["run"]) if e["kind"] == "run" \
                        else para_text(ps[pidx])
            ex = ex.replace("\n", " / ")
            out.append("| `%s` | %s | %s |" % (f, KIND_RU.get(e["kind"], e["kind"]), ex))

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("OK: записано %s (%d макетов)" % (OUT, len(layouts)))


if __name__ == "__main__":
    main()
