from __future__ import annotations

import io
from pathlib import Path
from typing import Union

import pdfplumber


# ---------------------------
# Public functions (NO page selection)
# ---------------------------
def text_with_tables(pdf_bytes: bytes) -> str:
    """
    Convert PDF bytes -> text (with tables in markdown) for ALL pages.

    Output format per page:
      ------------------------------------------------------------
      PAGE X
      ------------------------------------------------------------
      [TEXT]
      ...
      [TABLE 1]
      | ... |
      ...
    """
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        outputs = []
        for idx, page in enumerate(pdf.pages):
            page_no = idx + 1
            page_text = _extract_page_text_and_tables(page)

            outputs.append("-" * 60)
            outputs.append(f"PAGE {page_no}")
            outputs.append("-" * 60)
            outputs.append(page_text if page_text else "[EMPTY] No text/tables extracted.")
            outputs.append("")  # blank line between pages

        return "\n".join(outputs).rstrip()


# ---------------------------
# Internal helpers
# ---------------------------
def _normalize_ws(s: str) -> str:
    return " ".join((s or "").replace("\t", " ").split()).strip()


def _table_to_markdown(table) -> str:
    """Convert list-of-rows to a simple markdown table."""
    if not table:
        return ""

    rows = [[_normalize_ws(c) for c in row] for row in table]
    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []

    def md_row(r):
        return "| " + " | ".join(r) + " |"

    out = []
    out.append(md_row(header))
    out.append("| " + " | ".join(["---"] * len(header)) + " |")

    for r in body:
        if len(r) < len(header):
            r = r + [""] * (len(header) - len(r))
        out.append(md_row(r[: len(header)]))

    return "\n".join(out)


def _word_center(word):
    return ((word["x0"] + word["x1"]) / 2.0, (word["top"] + word["bottom"]) / 2.0)


def _in_bbox(x, y, bbox, pad=1.0):
    x0, y0, x1, y1 = bbox
    return (x0 - pad) <= x <= (x1 + pad) and (y0 - pad) <= y <= (y1 + pad)


def _build_line(line_words, char_tol=1.5):
    line_words = sorted(line_words, key=lambda w: w["x0"])
    parts = []
    last_x1 = None

    x0 = min(w["x0"] for w in line_words)
    x1 = max(w["x1"] for w in line_words)
    top = min(w["top"] for w in line_words)
    bottom = max(w["bottom"] for w in line_words)

    for w in line_words:
        if last_x1 is not None and (w["x0"] - last_x1) > char_tol:
            parts.append(" ")
        parts.append(w["text"])
        last_x1 = w["x1"]

    text = "".join(parts).strip()
    return {"top": top, "bottom": bottom, "x0": x0, "x1": x1, "text": text}


def _group_words_to_lines(words, line_tol=3.0, char_tol=1.5):
    if not words:
        return []

    words = sorted(words, key=lambda w: (w["top"], w["x0"]))

    lines = []
    cur_words = []
    cur_top = words[0]["top"]

    for w in words:
        if abs(w["top"] - cur_top) > line_tol:
            if cur_words:
                lines.append(_build_line(cur_words, char_tol=char_tol))
            cur_words = [w]
            cur_top = w["top"]
        else:
            cur_words.append(w)

    if cur_words:
        lines.append(_build_line(cur_words, char_tol=char_tol))

    return lines


def _lines_to_paragraph_text(lines, para_gap=6.0, indent_gap=14.0):
    if not lines:
        return ""

    out_lines = []
    prev = None

    for ln in lines:
        if not ln.get("text"):
            continue

        if prev is None:
            out_lines.append(ln["text"])
            prev = ln
            continue

        vertical_gap = ln["top"] - prev["bottom"]
        indent_delta = ln["x0"] - prev["x0"]

        new_para = (vertical_gap > para_gap) or (indent_delta > indent_gap)

        if new_para:
            out_lines.append("")  # blank line = new paragraph
            out_lines.append(ln["text"])
        else:
            out_lines.append(ln["text"])

        prev = ln

    return "\n".join(out_lines).strip()


def _extract_page_text_and_tables(page) -> str:
    parts = []

    tables = page.find_tables()
    table_bboxes = [t.bbox for t in tables]

    words = page.extract_words(
        keep_blank_chars=False,
        use_text_flow=True,
        extra_attrs=["fontname", "size"],
    ) or []

    outside_words = []
    for w in words:
        cx, cy = _word_center(w)
        inside_any = any(_in_bbox(cx, cy, bbox, pad=1.0) for bbox in table_bboxes)
        if not inside_any:
            outside_words.append(w)

    text_lines = _group_words_to_lines(outside_words, line_tol=3.0, char_tol=1.5)

    blocks = []
    for ln in text_lines:
        blocks.append({"kind": "line", "top": ln["top"], "x0": ln["x0"], "payload": ln})

    for idx, t in enumerate(tables, start=1):
        x0, y0, x1, y1 = t.bbox
        blocks.append({"kind": "table", "top": y0, "x0": x0, "payload": {"index": idx, "table": t}})

    blocks.sort(key=lambda b: (b["top"], b["x0"]))

    pending_lines = []

    def flush_text():
        nonlocal pending_lines
        if pending_lines:
            text = _lines_to_paragraph_text(pending_lines, para_gap=6.0, indent_gap=14.0)
            if text.strip():
                parts.append("[TEXT]")
                parts.append(text)
            pending_lines = []

    for b in blocks:
        if b["kind"] == "line":
            pending_lines.append(b["payload"])
        else:
            flush_text()
            idx = b["payload"]["index"]
            t = b["payload"]["table"]
            md = _table_to_markdown(t.extract())
            if md.strip():
                parts.append(f"[TABLE {idx}]")
                parts.append(md)

    flush_text()

    return "\n\n".join([p for p in parts if p and p.strip()]).strip()
