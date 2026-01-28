# run_locate_chunks_from_url.py
#
# Usage:
#   1) Put this file next to fn_chunk_number.py (or adjust the import)
#   2) Set PDF_URL below (or export PDF_URL env var)
#   3) Run: python run_locate_chunks_from_url.py

import os
import re
import json
import requests

from function.fn_chunk_number import locate_chunks
pdf_url = "https://drive.google.com/file/d/1Xlsqq3uIACYUSGZYfpewhW33DtjgKc4U/edit"

def _drive_to_direct_download(url: str) -> str:
    """
    Convert common Google Drive share URLs to a direct download URL.
    Works only if the file is accessible (public or your environment has access via cookies, etc.).
    """
    # https://drive.google.com/file/d/<id>/view
    m = re.search(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)", url)
    if m:
        file_id = m.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    # https://drive.google.com/open?id=<id>
    m = re.search(r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)", url)
    if m:
        file_id = m.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    # already direct
    return url


def download_pdf_bytes_from_url(url: str, timeout: int = 180) -> bytes:
    direct_url = _drive_to_direct_download(url)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/pdf,*/*",
    }
    resp = requests.get(direct_url, headers=headers, timeout=timeout)
    resp.raise_for_status()

    data = resp.content

    # Quick sanity check
    if not data.startswith(b"%PDF"):
        ct = resp.headers.get("Content-Type", "")
        raise RuntimeError(
            f"Downloaded content is not a PDF. content-type={ct!r}, head={data[:32]!r}. "
            f"URL used: {direct_url}"
        )

    return data


def main():
    # You can set PDF_URL in env instead of editing code

    if pdf_url == "PUT_PDF_URL_HERE":
        raise RuntimeError("Please set PDF_URL env var or edit pdf_url in the script.")

    print("[INFO] downloading:", pdf_url)
    pdf_bytes = download_pdf_bytes_from_url(pdf_url)
    print(f"[INFO] downloaded {len(pdf_bytes):,} bytes")

    result = locate_chunks(pdf_bytes, debug=True)

    print("\n[RESULT]")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()