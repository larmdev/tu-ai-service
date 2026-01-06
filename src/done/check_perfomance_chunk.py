import io
import os
import re
from pathlib import Path
from typing import List, Dict, Optional

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from fn_chunk_number import locate_chunks


# ========= GOOGLE DRIVE + SHEETS =========
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]

FOLDER_MIME = "application/vnd.google-apps.folder"
PDF_MIME = "application/pdf"

# IMPORTANT: exactly the columns you want to write (no extra columns)
COLUMNS = [
    "faculty_search", "curriculum_search", "curriculum_name", "pdf_path",
    "chunk1", "chunk2", "chunk3", "chunk4", "chunk4_2", "chunk5", "chunk6",
    "chunk7", "chunk8", "chunk9", "end_chunk","last_page"
]


# ------------------ small utils ------------------

def _extract_id_from_url(url: str) -> str:
    m = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"/folders/([a-zA-Z0-9-_]+)", url)
    if m:
        return m.group(1)
    raise ValueError(f"Cannot parse id from URL: {url}")


def _col_to_a1(col_num_1indexed: int) -> str:
    s = ""
    n = col_num_1indexed
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _debug_pdf_bytes(pdf_bytes: bytes, name: str):
    print(f"[DEBUG] PDF name: {name}")
    if not pdf_bytes.startswith(b"%PDF"):
        print("[WARN] downloaded bytes do NOT start with %PDF (might be HTML/error page)")


# ------------------ Google Drive helpers ------------------

def _drive_list_children(drive, parent_id: str) -> List[dict]:
    q = f"'{parent_id}' in parents and trashed=false"
    out = []
    page_token = None
    while True:
        resp = drive.files().list(
            q=q,
            fields="nextPageToken, files(id,name,mimeType)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            corpora="allDrives",
            pageToken=page_token,
        ).execute()
        out.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return out


def _drive_download_file_bytes(drive, file_id: str) -> bytes:
    request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return fh.getvalue()


def _drive_file_url_from_id(file_id: str) -> str:
    # your preferred "file_id only" format
    return f"https://drive.google.com/file/d/{file_id}"


# ------------------ Google Sheets helpers ------------------

def _sheets_get_header(sheets, spreadsheet_id: str, tab_name: str) -> List[str]:
    resp = sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!1:1"
    ).execute()
    return resp.get("values", [[]])[0]


def _sheets_build_pdf_index(sheets, spreadsheet_id: str, tab_name: str, pdf_col_0idx: int) -> Dict[str, int]:
    """
    Build mapping: pdf_path -> sheet row number (1-indexed)
    Reads only the pdf_path column, from row 2 downward.
    """
    col_letter = _col_to_a1(pdf_col_0idx + 1)
    resp = sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!{col_letter}2:{col_letter}"
    ).execute()
    values = resp.get("values", [])

    index: Dict[str, int] = {}
    for row_num, row in enumerate(values, start=2):
        pdf = (row[0].strip() if row and row[0] else "")
        if pdf:
            index[pdf] = row_num
    return index


def _sheets_append_row_fixed(sheets, spreadsheet_id: str, tab_name: str,
                            values: List[str], end_col_letter: str):
    """
    Append row but ONLY within A:{end_col_letter} to avoid creating extra columns (like Column 1..).
    """
    resp = sheets.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{tab_name}!A:{end_col_letter}",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [values]},
    ).execute()
    updates = resp.get("updates", {})
    return resp


def _sheets_update_row(sheets, spreadsheet_id: str, tab_name: str, row_num: int,
                       values: List[str], end_col_letter: str):
    """
    Overwrite existing row A{row_num}:{end_col_letter}{row_num}.
    """
    rng = f"{tab_name}!A{row_num}:{end_col_letter}{row_num}"
    resp = sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=rng,
        valueInputOption="USER_ENTERED",
        body={"values": [values]},
    ).execute()
    print("[DEBUG] update =", resp.get("updatedRange"))
    return resp


def _parse_rownum_from_updated_range(updated_range: Optional[str]) -> Optional[int]:
    """
    updated_range example: 'template!A137:O137'
    """
    if not updated_range:
        return None
    m = re.search(r"!A(\d+):", updated_range)
    if not m:
        return None
    return int(m.group(1))


# ------------------ Main pipeline ------------------

def process_drive_and_write_sheet(service_account_path: str, sheet_url: str, drive_url: str, tab_name: str = "template"):
    creds = service_account.Credentials.from_service_account_file(str(service_account_path), scopes=SCOPES)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)

    spreadsheet_id = _extract_id_from_url(sheet_url)
    root_folder_id = _extract_id_from_url(drive_url)
    print("[DEBUG] spreadsheet_id =", spreadsheet_id)

    # Header (row 1) must contain your COLUMNS
    header_raw = _sheets_get_header(sheets, spreadsheet_id, tab_name)
    header = [h.strip().replace("\ufeff", "").replace("\u200b", "") for h in header_raw]
    col_index = {name: i for i, name in enumerate(header)}

    missing = [c for c in COLUMNS if c not in col_index]
    if missing:
        raise RuntimeError(f"Sheet header missing columns: {missing}")

    pdf_col_0idx = col_index["pdf_path"]
    pdf_index = _sheets_build_pdf_index(sheets, spreadsheet_id, tab_name, pdf_col_0idx)

    # We will write EXACTLY len(COLUMNS) columns (A..end_col_letter)
    end_col_letter = _col_to_a1(len(COLUMNS))
    local_idx = {c: i for i, c in enumerate(COLUMNS)}

    # 1) root has faculty_search folders
    faculties = [f for f in _drive_list_children(drive, root_folder_id) if f["mimeType"] == FOLDER_MIME]

    for fac in faculties:
        faculty_name = fac["name"]
        fac_children = _drive_list_children(drive, fac["id"])

        # 2) folder name contains "ตรี"
        bachelor_folders = [x for x in fac_children if x["mimeType"] == FOLDER_MIME and ("ตรี" in x["name"])]
        for bach in bachelor_folders:
            bach_children = _drive_list_children(drive, bach["id"])

            # 3) curriculum_search folders
            curriculum_folders = [x for x in bach_children if x["mimeType"] == FOLDER_MIME]
            for cur in curriculum_folders:
                curriculum_search = cur["name"]
                cur_children = _drive_list_children(drive, cur["id"])

                # 4) pick the only PDF (or first if multiple)
                pdf_files = [x for x in cur_children if x["mimeType"] == PDF_MIME or x["name"].lower().endswith(".pdf")]
                if not pdf_files:
                    print(f"[SKIP] no PDF in: {faculty_name} / {bach['name']} / {curriculum_search}")
                    continue
                if len(pdf_files) > 1:
                    print(f"[WARN] multiple PDFs in: {faculty_name} / {curriculum_search} -> pick first")

                pdf = pdf_files[0]
                curriculum_name = pdf["name"]
                pdf_url = _drive_file_url_from_id(pdf["id"])

                # download -> bytes -> locate chunks
                try:
                    pdf_bytes = _drive_download_file_bytes(drive, pdf["id"])
                    _debug_pdf_bytes(pdf_bytes, pdf["name"])
                    chunks = locate_chunks(pdf_bytes)
                except Exception as e:
                    print(f"[SKIP] failed processing PDF: {faculty_name}/{curriculum_search}/{pdf['name']} -> {e}")
                    continue

                # Build row_values ONLY for COLUMNS (fixed width)
                row_values = [""] * len(COLUMNS)
                row_values[local_idx["faculty_search"]] = faculty_name
                row_values[local_idx["curriculum_search"]] = curriculum_search
                row_values[local_idx["curriculum_name"]] = curriculum_name
                row_values[local_idx["pdf_path"]] = pdf_url

                for k, v in chunks.items():
                    if k in local_idx:
                        row_values[local_idx[k]] = "" if v is None else str(v)

                # Upsert by pdf_path
                existing_row = pdf_index.get(pdf_url)
                if existing_row:
                    _sheets_update_row(sheets, spreadsheet_id, tab_name, existing_row, row_values, end_col_letter)
                    print(f"[OK] updated: {faculty_name} / {curriculum_search} / {curriculum_name}")
                else:
                    resp = _sheets_append_row_fixed(sheets, spreadsheet_id, tab_name, row_values, end_col_letter)
                    # try to record the new row number for this run
                    new_row = _parse_rownum_from_updated_range(resp.get("updates", {}).get("updatedRange"))
                    if new_row:
                        pdf_index[pdf_url] = new_row
                    else:
                        # fallback marker; still prevents immediate duplicates in the same run
                        pdf_index[pdf_url] = -1
                    print(f"[OK] appended: {faculty_name} / {curriculum_search} / {curriculum_name}")


if __name__ == "__main__":
    load_dotenv()

    sheet_url = os.getenv("SHEET_URL")
    drive_url = os.getenv("DRIVE_URL")
    if not sheet_url or not drive_url:
        raise RuntimeError("Missing SHEET_URL or DRIVE_URL in .env")

    sa_path = Path("service_account.json")
    if not sa_path.exists():
        raise RuntimeError(f"Missing service_account.json in current dir: {Path.cwd()}")

    process_drive_and_write_sheet(
        service_account_path=str(sa_path),
        sheet_url=sheet_url,
        drive_url=drive_url,
        tab_name="template",
    )
