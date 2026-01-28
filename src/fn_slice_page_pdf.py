def ensure_pdf_bytes(b: bytes, label: str = "pdf") -> None:
    if not b:
        raise ValueError(f"{label}: empty bytes")
    if not b.startswith(b"%PDF-"):
        head_txt = b[:200].decode("utf-8", errors="ignore")
        raise ValueError(
            f"{label}: not a PDF (missing %PDF-). First 200 chars:\n{head_txt}"
        )

import io
from pypdf import PdfReader, PdfWriter

def slice_pdf_pages(pdf_bytes: bytes, start_page: int, end_page: int) -> bytes:
    """
    start_page/end_page เป็นเลขหน้าที่คนใช้ (1-indexed) เช่น 2-4 = หน้า 2,3,4
    """
    if start_page < 1 or end_page < start_page:
        raise ValueError(f"Invalid page range: {start_page}-{end_page}")

    # ต้องเป็น pdf เต็มไฟล์ก่อน
    ensure_pdf_bytes(pdf_bytes, "source_pdf")

    reader = PdfReader(io.BytesIO(pdf_bytes))

    # ถ้าเจอไฟล์เข้ารหัส ให้ลอง decrypt ก่อน (บางไฟล์ต้องทำ)
    if getattr(reader, "is_encrypted", False):
        try:
            reader.decrypt("")  # ลองรหัสว่าง
        except Exception:
            pass

    total = len(reader.pages)
    if total == 0:
        raise ValueError("PDF has 0 pages")

    # clamp ให้อยู่ในช่วงจริงของไฟล์
    start_i = max(0, start_page - 1)
    end_i = min(total - 1, end_page - 1)

    # ✅ สำคัญ: clamp แล้วต้องยัง valid
    if start_i > end_i:
        raise ValueError(
            f"Page range out of bounds after clamp: "
            f"requested {start_page}-{end_page}, total={total}"
        )

    writer = PdfWriter()
    for i in range(start_i, end_i + 1):
        writer.add_page(reader.pages[i])

    # ✅ อีกชั้น: ต้องมีหน้า
    if len(writer.pages) == 0:
        raise ValueError(
            f"Slice produced 0 pages: requested {start_page}-{end_page}, "
            f"clamped idx {start_i}-{end_i}, total={total}"
        )

    out = io.BytesIO()
    writer.write(out)
    chunk = out.getvalue()

    # ✅ เช็คว่า chunk เป็น PDF จริง
    ensure_pdf_bytes(chunk, "chunk_pdf")
    return chunk