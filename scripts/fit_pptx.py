#!/usr/bin/env python3
"""Post-process a pandoc-generated .pptx so the slides fit the way we want.

pandoc gives us the right structure but leaves every text box at the reference
layout's defaults.  Two passes fix that, in place:

1. every text body gets <a:normAutofit/>, so PowerPoint shrinks a long title
   instead of letting it spill over the figure underneath;
2. a content placeholder holding plain paragraphs (no bullets) becomes a
   centred statement slide, at a size chosen from how much text there is.

Slides whose content is a figure are left alone: pandoc already scales the
image to the content area and centres it.
"""

import re
import shutil
import sys
import zipfile
from pathlib import Path

# text length (characters) -> run size, in hundredths of a point
SIZE_STEPS = [(120, 2000), (260, 1800), (420, 1600), (10**9, 1400)]

SP_RE = re.compile(r"<p:sp>.*?</p:sp>", re.S)
PARA_RE = re.compile(r"<a:p>.*?</a:p>", re.S)
TEXT_RE = re.compile(r"<a:t>(.*?)</a:t>", re.S)


def autofit(xml: str) -> str:
    """Give every body an autofit, so nothing overflows its placeholder."""
    xml = xml.replace("<a:bodyPr />", "<a:bodyPr><a:normAutofit /></a:bodyPr>")
    return re.sub(
        r"<a:bodyPr ([^/>]*)/>",
        r"<a:bodyPr \1><a:normAutofit /></a:bodyPr>",
        xml,
    )


def is_body_placeholder(sp: str) -> bool:
    ph = re.search(r"<p:ph ([^/>]*)/>", sp)
    if ph is None:
        return False
    attrs = ph.group(1)
    if 'type="' in attrs and 'type="body"' not in attrs:
        return False  # title, subtitle, date, ...
    return 'idx="' in attrs


def centre_statement(sp: str) -> str:
    """Centre a bullet-free content placeholder and size it to its text."""
    paras = PARA_RE.findall(sp)
    if not paras or not all("<a:buNone />" in p for p in paras):
        return sp  # a real list: leave pandoc's bullets alone

    n_chars = sum(len(t) for p in paras for t in TEXT_RE.findall(p))
    size = next(sz for limit, sz in SIZE_STEPS if n_chars <= limit)

    sp = sp.replace("<a:bodyPr>", '<a:bodyPr anchor="ctr">', 1)
    sp = sp.replace('<a:pPr lvl="0" indent="0" marL="0">',
                    '<a:pPr lvl="0" indent="0" marL="0" algn="ctr">')
    sp = sp.replace("<a:rPr />", f'<a:rPr sz="{size}" />')
    sp = re.sub(r"<a:rPr ((?:(?!sz=)[^/>])*)/>", rf'<a:rPr \1sz="{size}" />', sp)
    return sp


def fit_slide(xml: str) -> str:
    xml = autofit(xml)
    return SP_RE.sub(
        lambda m: centre_statement(m.group(0)) if is_body_placeholder(m.group(0)) else m.group(0),
        xml,
    )


def main(path: Path) -> None:
    tmp = path.with_suffix(".fitted.pptx")
    with zipfile.ZipFile(path) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", item.filename):
                data = fit_slide(data.decode("utf-8")).encode("utf-8")
            dst.writestr(item, data)
    shutil.move(tmp, path)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        main(Path(arg))
