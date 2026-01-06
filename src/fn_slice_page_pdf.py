import io
from pypdf import PdfReader, PdfWriter

def slice_pdf_pages(pdf_bytes: bytes, start_page: int, end_page: int) -> bytes:
    """
    start_page/end_page เป็นเลขหน้าที่คนใช้ (1-indexed)
    เช่น 2-4 = หน้า 2,3,4
    """
    if start_page < 1 or end_page < start_page:
        raise ValueError("Invalid page range")

    reader = PdfReader(io.BytesIO(pdf_bytes))
    total = len(reader.pages)
    if total == 0:
        raise ValueError("PDF has 0 pages")

    # clamp ให้อยู่ในช่วงจริงของไฟล์
    start_i = max(0, start_page - 1)
    end_i = min(total - 1, end_page - 1)

    writer = PdfWriter()
    for i in range(start_i, end_i + 1):
        writer.add_page(reader.pages[i])

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()
