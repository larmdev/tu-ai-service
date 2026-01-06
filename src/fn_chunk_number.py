import io
import re
import unicodedata
from typing import Dict, Optional, List, Tuple
from pypdf import PdfReader


def _norm_thai(text: str) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFC", text)
    t = t.replace("ํา", "ำ").replace("าํ", "ำ")
    t = t.replace("\u200b", "").replace("\ufeff", "")
    t = t.replace(" ", "")
    t = re.sub(r"\s+", " ", t).strip()
    return t


_THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")


def _to_int_digit(s: str) -> Optional[int]:
    if not s:
        return None
    try:
        return int(s.translate(_THAI_DIGITS))
    except Exception:
        return None


def locate_chunks(pdf_bytes: bytes, debug: bool = True) -> Dict[str, Optional[int]]:
    """
    STRICT ORDER:
      chunk1 -> chunk2 -> chunk3 -> chunk4 -> chunk4_2 -> chunk5 -> chunk6 -> chunk7 -> chunk8 -> chunk9 -> end_chunk

    "Lookahead 1-step" rule:
      - while searching current target, also check ONLY the next target (one step ahead)
      - do NOT check other future targets
      - do NOT finalize appendix/end_chunk until its turn (avoid early stopping)

    TOC rule:
      - find "สารบัญ" only within pages 1..5 to decide start_page
      - any page containing "สารบัญ" is skipped for matching
    """

    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError("PDF has 0 pages or cannot be read.")

    # Patterns
    toc_re = re.compile(r"สารบัญ")
    course_desc_re = re.compile(r"(คำ)?อธิบายรายวิชา")  # tolerant
    appendix_re = re.compile(r"ภาคผนวก")
    chapter_re = re.compile(r"หมวด(?:ที่)?\s*([0-9๐-๙]+)")

    # 1) Find TOC only in pages 1..5
    toc_page: Optional[int] = None
    for i in range(1, min(5, total_pages) + 1):
        txt0 = _norm_thai(reader.pages[i - 1].extract_text() or "")
        if toc_re.search(txt0):
            toc_page = i
            if debug:
                print(f"[DEBUG] พบสารบัญที่หน้า {toc_page}")
            break
    if toc_page is None and debug:
        print("[DEBUG] ไม่พบสารบัญในหน้า 1–5 (เลิกหา)")

    start_page = (toc_page + 1) if toc_page is not None else 1

    # Ordered outputs
    order_keys = [
        "chunk1", "chunk2", "chunk3", "chunk4", "chunk4_2",
        "chunk5", "chunk6", "chunk7", "chunk8", "chunk9", "end_chunk",
    ]
    chunks: Dict[str, Optional[int]] = {k: None for k in order_keys}
    chunks["last_page"] = total_pages

    # Targets in exact order
    targets: List[Tuple[str, str, Optional[int]]] = [
        ("chunk1", "chapter", 1),
        ("chunk2", "chapter", 2),
        ("chunk3", "chapter", 3),
        ("chunk4", "chapter", 4),
        ("chunk4_2", "course_desc", None),
        ("chunk5", "chapter", 5),
        ("chunk6", "chapter", 6),
        ("chunk7", "chapter", 7),
        ("chunk8", "chapter", 8),
        ("chunk9", "chapter", 9),
        ("end_chunk", "appendix", None),
    ]

    def chapters_in_page(txt: str) -> set:
        nums = set()
        for m in chapter_re.finditer(txt):
            n = _to_int_digit(m.group(1))
            if n is not None:
                nums.add(n)
        return nums

    def match_target(kind: str, n: Optional[int], txt: str, chap_nums: set) -> bool:
        if kind == "chapter":
            assert n is not None
            return n in chap_nums
        if kind == "course_desc":
            return course_desc_re.search(txt) is not None
        if kind == "appendix":
            return appendix_re.search(txt) is not None
        return False

    t_idx = 0  # current target index

    for page in range(start_page, total_pages + 1):
        if t_idx >= len(targets):
            break

        txt = _norm_thai(reader.pages[page - 1].extract_text() or "")
        if not txt:
            continue

        # skip TOC-like pages (avoid false positives)
        if toc_re.search(txt):
            continue

        chap_nums = chapters_in_page(txt)

        # current + next only
        cur_key, cur_kind, cur_n = targets[t_idx]
        next_exists = (t_idx + 1) < len(targets)
        if next_exists:
            next_key, next_kind, next_n = targets[t_idx + 1]
        else:
            next_key, next_kind, next_n = ("", "", None)

        cur_hit = match_target(cur_kind, cur_n, txt, chap_nums)
        next_hit = match_target(next_kind, next_n, txt, chap_nums) if next_exists else False

        # ถ้าเจอ current: เติม current แล้ว "ดู next" ได้อีก 1 ตัวในหน้าเดียวกัน
        if cur_hit:
            chunks[cur_key] = page
            if debug:
                if cur_kind == "chapter":
                    print(f"[DEBUG] พบ 'หมวดที่ {cur_n}' => {cur_key} ที่หน้า {page}")
                elif cur_kind == "course_desc":
                    print(f"[DEBUG] พบ 'คำอธิบายรายวิชา' => {cur_key} ที่หน้า {page}")
                else:
                    print(f"[DEBUG] พบ 'ภาคผนวก' => {cur_key} ที่หน้า {page}")

            t_idx += 1

            # lookahead 1 step: เติม next ได้ “เฉพาะหน้าเดียวกัน” ถ้ามันอยู่หน้าเดียวกันจริง
            if next_exists and next_hit:
                chunks[next_key] = page
                if debug:
                    if next_kind == "chapter":
                        print(f"[DEBUG] (lookahead) พบ 'หมวดที่ {next_n}' => {next_key} ที่หน้า {page}")
                    elif next_kind == "course_desc":
                        print(f"[DEBUG] (lookahead) พบ 'คำอธิบายรายวิชา' => {next_key} ที่หน้า {page}")
                    else:
                        print(f"[DEBUG] (lookahead) พบ 'ภาคผนวก' => {next_key} ที่หน้า {page}")

                t_idx += 1

            continue

        # ถ้า current ยังไม่เจอ: “ดู next ได้” แต่แค่เพื่อช่วยกรณีข้าม/ดูภาพรวม
        # (เราไม่ finalize next ก่อน current) => ดังนั้นตรงนี้ไม่ทำอะไรกับ next_hit

        # หมายเหตุ: ไม่ทำอะไรเมื่อเจอ "ภาคผนวก" ระหว่างยังไม่ถึงคิว end_chunk
        # เพื่อไม่ให้ตัดเกมก่อนเวลา

    # finalize end_chunk
    if chunks["end_chunk"] is None:
        chunks["end_chunk"] = total_pages
        if debug:
            print(f"[DEBUG] ไม่พบ 'ภาคผนวก' -> end_chunk = {total_pages}")

    return chunks
