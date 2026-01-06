from datetime import date, datetime
import os
import json
import numpy as np
import pandas as pd
import streamlit as st
from google.cloud import firestore
from streamlit_extras.stylable_container import stylable_container
from assets.assets import logging_setup
from typing import Any, Dict, List, Optional, Tuple

logger = logging_setup("contacts")

if "export_csv" not in st.session_state:
    st.session_state["export_csv"] = ""
if "edit_uids" not in st.session_state:
    st.session_state["edit_uids"] = ""
if "came_from" not in st.session_state:
    st.session_state["came_from"] = ""

project_id = "iee-dscc"
CONTACTS_COLLECTION = "contacts"
STAFF_COLLECTION = "staff"
STATUS_COLLECTION = "status"
NORMALIZED_COLLECTION = "normalized"

NORM_DOCS = {
    "contact_status": "contact_status",
    "season": "season",
    "solo_group": "solo_group",
    "year_level": "year_level",
    "follow_next_year": "follow_next_year",
    "university": "university", 
    "full_info": "full_info",
}

# ---------- URL router helpers (no experimental APIs) ----------
ROUTES = ("contacts", "edit", "overview", "alerts")

def set_qp(**kwargs):
    # Replace the whole query (also clears keys not provided)
    st.query_params = {k: ("" if v is None else str(v)) for k, v in kwargs.items()}

# def get_view() -> str:
#     v = st.query_params.get("view", "contacts")
#     # Some Streamlit versions might still yield list-like; guard it:
#     if isinstance(v, list):
#         v = v[0] if v else "contacts"
#     v = (v or "contacts").lower()
#     return v if v in ROUTES else "contacts"

# def get_uid() -> str | None:
#     uid = st.query_params.get("uid")
#     if isinstance(uid, list):
#         uid = uid[0] if uid else None
#     return str(uid) if uid not in (None, "") else None

def goto_contacts():
    set_qp(view="contacts")

# def goto_edit(uid: str):
#     set_qp(view="edit", uid=str(uid))

# ---------- Load Config ----------
def load_config():
    """Load configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "edit", "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "staff_list": ["GG", "RF", "MK", "JJ"],
        "status_config": {},
        "available_colors": {}
    }

# =============================================================================
# Schema & constants
# =============================================================================
DATA_ORDER = [
    "uid","nickname","line_name","university","year_level","solo_group","season",
    "phone","email","staff_owner","created_at","last_contact_at","day_last_contact",
    "contact_status","status","follow_next_year","comment","call_note" 
]
VISIBLE_ORDER = [
    "nickname","line_name","university","year_level","solo_group","season",
    "phone","email","staff_owner","created_at","last_contact_at","day_last_contact",
    "contact_status","status","follow_next_year","comment","call_note"
]
ALL_OPTIONS = ["ALL"] + VISIBLE_ORDER

# Keys for filter widgets / model state
K = {
    "date": "f_date",
    "last_contact_date": "f_last_contact_date",
    "search": "f_search",
    "uni": "f_uni",
    "yl": "f_yl",
    "season": "f_season",
    "group": "f_group",
    "staff": "f_staff",
    "cstatus": "f_cstatus",
    "status": "f_status",
    "follow_next_year": "f_follow_next_year",
    "cols_widget": "col_select_widget",
    "cols_model":  "col_select_model",
    "reset_btn": "btn_reset_filters"
}
DEFAULT_SELECTED_COLS = ["ALL"]

# Force-reset nonce for filter widgets
FLT_NONCE_KEY = "flt_nonce"

CREATED_RANGE_VAL_KEY = "v_created_range"
LAST_RANGE_VAL_KEY = "v_last_contact_range"

def wkey(base: str) -> str:
    # Initialize if not exists
    if FLT_NONCE_KEY not in st.session_state:
        st.session_state[FLT_NONCE_KEY] = 0
    return f"{base}__{st.session_state[FLT_NONCE_KEY]}"

STATUS_BADGE_MAP = {
    "สมัครแล้ว": "badge--blue",
    "หายไป": "badge--red",
    "ไปกับเอเจนซี่อื่น": "badge--darkred",
    "อยู่ระหว่างตัดสินใจ": "badge--yellow",
    "เดินทางปีถัดไป": "badge--purple",
}
CONTACT_STATUS_BADGE_MAP = {"ติดต่อได้": "badge--ok", "ติดต่อไม่ได้": "badge--fail"}

# YEAR_LEVEL_OPTS = ["ปี 1","ปี 2","ปี 3","ปี 4","ปี 5","ปี 6","ป.โท"]
# SOLO_GROUP_OPTS = ["solo","group"]
# SEASON_OPTS = ["Summer","Spring"]
# STAFF_OPTS = ["GG","RF","MK","JJ"]
# CONTACT_STATUS_OPTS = ["ติดต่อได้","ติดต่อไม่ได้"]
# STATUS_OPTS = ["สมัครแล้ว","หายไป","ไปกับเอเจนซี่อื่น","อยู่ระหว่างตัดสินใจ","เดินทางปีถัดไป"]

def parse_date(s):
    if pd.isna(s) or s == "": return None
    if isinstance(s, (pd.Timestamp, datetime)): return s.date()
    try: return pd.to_datetime(s).date()
    except Exception: return None

def ensure_schema(df: pd.DataFrame) -> pd.DataFrame:
    # Silent check: Ensure uid column exists
    if "uid" not in df.columns:
        logger.error("CRITICAL: uid column missing from database query result in ensure_schema()")
        logger.error(f"Available columns: {df.columns.tolist()}")
        logger.error("Adding empty uid column as fallback to prevent crash")
        # Add empty uid column as fallback instead of stopping
        df["uid"] = pd.NA

    for c in DATA_ORDER:
        if c not in df.columns:
            df[c] = pd.NA
    df["created_at"] = df["created_at"].apply(parse_date)
    df["last_contact_at"] = df["last_contact_at"].apply(parse_date)
    df["day_last_contact"] = pd.to_numeric(df["day_last_contact"], errors="coerce")

    # Convert uid to string and handle NULL values
    df["uid"] = df["uid"].astype("string").replace({"None": pd.NA, "nan": pd.NA, "<NA>": pd.NA})

    # Silent check for invalid uid values
    if df["uid"].isna().any():
        invalid_count = df["uid"].isna().sum()
        logger.warning(f"Found {invalid_count} records with NULL/invalid uid in database")
        # Keep all records - don't filter (user requested not to lose data)

    return df
def _firestore_client() -> firestore.Client:
    return firestore.Client(project=project_id)

def _load_collection_map(collection_name: str, field_name: str) -> dict:
    """Map: doc_id -> doc[field_name]"""
    db = _firestore_client()
    out = {}
    for d in db.collection(collection_name).stream():
        data = d.to_dict() or {}
        out[str(d.id)] = (data.get(field_name) or "").strip()
    return out

def _load_status_map() -> dict:
    """Map: status_id -> {status, bg_color, text_color}"""
    db = _firestore_client()
    out = {}
    for d in db.collection(STATUS_COLLECTION).stream():
        data = d.to_dict() or {}
        out[str(d.id)] = {
            "status": (data.get("status") or "").strip(),
            "bg_color": data.get("bg_color") or "#FFE5E5",
            "text_color": data.get("text_color") or "#000000ff",
        }
    return out

def _load_normalized_doc(doc_name: str) -> dict:
    """Map: code(str) -> label(str) from normalized/<doc_name>"""
    db = _firestore_client()
    snap = db.collection(NORMALIZED_COLLECTION).document(doc_name).get()
    if not snap.exists:
        return {}
    data = snap.to_dict() or {}
    return {str(k): str(v) for k, v in data.items() if v is not None}

# ---------- Load Data from Database ----------
@st.cache_data(show_spinner=False, ttl=600)
def load_contacts_from_db() -> pd.DataFrame:
    """
    Firestore version: Load contacts and map normalized/staff/status -> labels.
    Return DataFrame compatible with existing ensure_schema + UI.
    """
    db = _firestore_client()

    # mapping tables (cache)
    staff_map = _load_collection_map(STAFF_COLLECTION, "staff_owner")  # staff_id -> staff_owner
    status_map = _load_status_map()                                    # status_id -> status + colors
    norm_contact_status = _load_normalized_doc(NORM_DOCS["contact_status"])
    norm_season = _load_normalized_doc(NORM_DOCS["season"])
    norm_solo_group = _load_normalized_doc(NORM_DOCS["solo_group"])
    norm_year_level = _load_normalized_doc(NORM_DOCS["year_level"])
    norm_follow_next_year = _load_normalized_doc(NORM_DOCS["follow_next_year"])
    norm_university = _load_normalized_doc(NORM_DOCS["university"])   

    results: List[Dict[str, Any]] = []

    for doc in db.collection(CONTACTS_COLLECTION).stream():
        data = doc.to_dict() or {}

        uid = str(doc.id)
        nickname = (data.get("nickname") or "").strip()
        line_name = (data.get("line_name") or "").strip()

        staff_id = str((data.get("staff_id") or "")).strip()
        status_id = str((data.get("status_id") or "")).strip()

        # normalized codes
        cs_code = str((data.get("contact_status") or "")).strip()
        season_code = str((data.get("season") or "")).strip()
        solo_code = str((data.get("solo_group") or "")).strip()
        yl_code = str((data.get("year_level") or "")).strip()
        fny_code = str((data.get("follow_next_year_id") or data.get("follow_next_year") or "")).strip()
        u_code = str((data.get("university") or "")).strip()
        s = status_map.get(status_id, {})

        row = {
            "uid": uid,
            "nickname": nickname ,  # fallback
            "line_name": line_name ,
            "university": norm_university.get(u_code, u_code),  
            "year_level": norm_year_level.get(yl_code, yl_code),
            "solo_group": norm_solo_group.get(solo_code, solo_code),
            "season": norm_season.get(season_code, season_code),
            "phone": (data.get("phone") or "").strip(),
            "email": (data.get("email") or "").strip(),

            "staff_owner": staff_map.get(staff_id) or "ยังไม่ได้กำหนด",

            "created_at": data.get("created_at"),
            "last_contact_at": data.get("last_contact_at"),
            "day_last_contact": data.get("day_last_contact"),

            "contact_status": norm_contact_status.get(cs_code, cs_code),
            "status": (s.get("status") or "").strip(),
            "status_bg_color": s.get("bg_color") or "#FFE5E5",
            "status_text_color": s.get("text_color") or "#000000ff",

            "follow_next_year": norm_follow_next_year.get(fny_code, fny_code),

            "comment": (data.get("comment") or "").strip(),
            "call_note": (data.get("call_note") or "").strip(),
        }

        results.append(row)

    df = pd.DataFrame(results)
    return ensure_schema(df)

# ===== Stable No. mapping: start 1 from oldest created_at =====
def build_no_map(df_all: pd.DataFrame) -> dict:
    rank_df = (
        df_all.sort_values(by=["created_at","uid"], ascending=[True, True])
              .loc[:, ["uid","created_at"]]
              .reset_index(drop=True)
    )
    rank_df["No."] = range(1, len(rank_df) + 1)
    return dict(zip(rank_df["uid"], rank_df["No."]))

def initialize_contacts_data():
    """Initialize contacts data and NO_MAP in session state"""
    if "contacts_df" not in st.session_state:
        st.session_state["contacts_df"] = (
            load_contacts_from_db()  # เปลี่ยนจาก load_csv_df(CSV_PATH)
            .sort_values(by=["created_at","uid"], ascending=[False, True])  # newest first
            .reset_index(drop=True)
        )

    if "NO_MAP" not in st.session_state:
        st.session_state["NO_MAP"] = build_no_map(st.session_state["contacts_df"])

    return st.session_state["contacts_df"], st.session_state["NO_MAP"]

# ----------------------------------------------------------------------------- #
#                                  CONTACTS PAGE ONLY                           #
# ----------------------------------------------------------------------------- #
# Edit page has been moved to edit/edit.py

# ----------------------------------------------------------------------------- #
#                              CONTACTS (TABLE)                                  #
# ----------------------------------------------------------------------------- #
def get_date_bounds(df_base: pd.DataFrame, col: str) -> tuple[date, date]:
    series = df_base[col].dropna()
    today = date.today()
    if series.empty:
        return today, today
    return series.min(), series.max()

def reset_all_filters():
    # 1. รีเซ็ตโมเดลรายการคอลัมน์ที่เลือกให้เป็นค่าว่าง (เพื่อเข้าสู่โหมด Default)
    st.session_state[K["cols_model"]] = []

    # 2. [เพิ่มส่วนนี้] ลบสถานะของ Checkbox ในปุ่มเลือกคอลัมน์ เพื่อให้ UI รีเฟรชใหม่
    # ต้องลูปดูคอลัมน์ทั้งหมดที่มีโอกาสถูกสร้างเป็น checkbox
    all_possible_cols = [c for c in ALL_OPTIONS if c != "ALL"] 
    for col in all_possible_cols:
        widget_key = f"col_{col}" # คีย์ที่ตั้งไว้ใน select_columns_ui
        if widget_key in st.session_state:
            del st.session_state[widget_key]

    if CREATED_RANGE_VAL_KEY in st.session_state:
        del st.session_state[CREATED_RANGE_VAL_KEY]
    if LAST_RANGE_VAL_KEY in st.session_state:
        del st.session_state[LAST_RANGE_VAL_KEY]

    # 3. รีเซ็ตตัวกรองอื่นๆ (Dropdown/Search) ผ่าน Nonce
    st.session_state[FLT_NONCE_KEY] += 1


def select_columns_ui():
    model_key = K["cols_model"]
    all_cols = [c for c in ALL_OPTIONS if c != "ALL"]

    # --- DEFAULT ---
    # model ว่าง = ALL mode
    if model_key not in st.session_state:
        st.session_state[model_key] = []

    selected = set(st.session_state[model_key])

    popover = st.popover("Columns", width="stretch")

    # --- individual columns ---
    for col in all_cols:
        # when ALL mode → show unchecked but visible
        checked = col in selected

        new_checked = popover.checkbox(
            col,
            value=checked,
            key=f"col_{col}"
        )

        if new_checked != checked:
            if new_checked:
                # selecting any column exits ALL mode
                selected.add(col)
            else:
                selected.discard(col)

    st.session_state[model_key] = list(selected)

    # --- RETURN LOGIC ---
    # ALL mode → show all fields
    if not selected:
        return VISIBLE_ORDER

    return [c for c in VISIBLE_ORDER if c in selected]


def popover_filter_checkbox(name: str, df_base, column: str, key: str, df: bool = True):
    # 1. เตรียม Options (รองรับทั้ง DataFrame และ List)
    if df and hasattr(df_base, 'columns'): # เช็คว่าเป็น DataFrame ไหม
        options = sorted(df_base[column].dropna().unique())
    else:
        options = sorted(df_base) # กรณีส่ง List เข้ามา (เช่น Alert Color)

    # --- จุดที่แก้ไข (วิธีที่ 2) ---
    # ใช้ K.get(key, key) แทน K[key]
    # ความหมาย: ลองหา key ใน K ก่อน ถ้าไม่เจอ ให้ใช้คำว่า key นั้นตรงๆ เลย
    # (เช่นถ้าหา "last_contact" ใน K ไม่เจอ ก็จะใช้คำว่า "last_contact" เป็น ID แทน)
    base_key = K.get(key, key) 
    state_key = wkey(base_key)
    # ---------------------------

    # init state
    if state_key not in st.session_state:
        st.session_state[state_key] = []

    selected = set(st.session_state[state_key])

    with st.popover(name, width="stretch"):
        for opt in options:
            checked = opt in selected
            # แปลง opt เป็น string เสมอเพื่อความปลอดภัยในการตั้ง key
            new_checked = st.checkbox(
                str(opt),
                value=checked,
                key=f"{state_key}_{opt}"
            )

            if new_checked:
                selected.add(opt)
            else:
                selected.discard(opt)

    st.session_state[state_key] = list(selected)
    return st.session_state[state_key]

def date_range_box(
    label: str,
    min_d: date,
    max_d: date,
    value_key: str,
    widget_key_base: str,
) -> tuple[date, date]:
    # default range (ถ้าไม่เคยเลือก)
    if value_key not in st.session_state:
        st.session_state[value_key] = (min_d, max_d)

    cur_start, cur_end = st.session_state[value_key]

    # กันหลุด bounds (เช่น data เปลี่ยน)
    cur_start = max(min_d, cur_start)
    cur_end = min(max_d, cur_end)
    if cur_start > cur_end:
        cur_start, cur_end = min_d, max_d

    # กล่องที่ user เห็น
    box_label = f"{label} {cur_start:%Y/%m/%d} – {cur_end:%Y/%m/%d}"

    with st.popover(box_label, width="stretch"):
        sel = st.date_input(
            label,
            value=(cur_start, cur_end),
            min_value=min_d,
            max_value=max_d,
            key=wkey(widget_key_base),
            label_visibility="collapsed",
        )

        if isinstance(sel, (list, tuple)) and len(sel) == 2:
            st.session_state[value_key] = (sel[0], sel[1])
        else:
            st.session_state[value_key] = (sel, sel)

    return st.session_state[value_key]

    
def filters_ui(df_base: pd.DataFrame):
    # หาขอบเขตวันที่ต่ำสุด-สูงสุดจากข้อมูล
        # bounds สำหรับ Created
    min_c, max_c = get_date_bounds(df_base, "created_at")
    # bounds สำหรับ Last Contact
    min_l, max_l = get_date_bounds(df_base, "last_contact_at")
    
    toolbar_container = st.container(border=True)
    with toolbar_container:
        # =================================================================
        # ROW 1: c1 ถึง c7 (7 ช่อง) - เพิ่ม Last Contact มาที่ c7
        # สัดส่วน: [0.13, 0.22, 0.13, 0.13, 0.13, 0.13, 0.13]
        # (ช่อง c2 Date กว้าง 22%, ที่เหลือช่องละ 13%)
        # =================================================================
        c1, c2, c3, c4, c5, c6, c7 = st.columns([0.13, 0.22, 0.13, 0.13, 0.13, 0.13, 0.13])

        with c1:
            # 1. ปุ่มเลือก Columns
            visible_cols = select_columns_ui()
            
        with c2:
            with stylable_container(
                key="created_date_inline",
                css_styles=["""
                div[data-testid="stDateInput"] div[data-baseweb="input"]:first-of-type::before {
                    content: "Created Date";
                    position: absolute;
                    left: 14px;
                    top: 50%;
                    transform: translateY(-50%);
                    width: 92px;               
                    text-align: left;          
                    color: #6B7280;
                    font-weight: 500;
                    font-size: 14px;
                    pointer-events: none;
                    z-index: 2;
                }
                div[data-testid="stDateInput"] div[data-baseweb="input"]:first-of-type input {
                    padding-left: 122px !important;  /* 14 + 92 + 16(gap) */
                }
                """]
            ):
                sel = st.date_input(
                    "Created Date",
                    value=(min_c, max_c),
                    min_value=min_c,
                    max_value=max_c,
                    key=wkey(K["date"]),
                    label_visibility="collapsed",
                )

            if isinstance(sel, (list, tuple)) and len(sel) == 2:
                created_start, created_end = sel
            else:
                created_start = created_end = sel

        with c3:
            # 3. University
            uni = popover_filter_checkbox("University", df_base, "university", "uni")
            
        with c4:
            # 4. Year Level
            yl = popover_filter_checkbox("Year", df_base, "year_level", "yl")
            
        with c5:
            # 5. Season
            season = popover_filter_checkbox("Season", df_base, "season", "season")
            
        with c6:
            # 6. Type (Solo/Group)
            solo_group = popover_filter_checkbox("Type", df_base, "solo_group", "group")

        with c7:
            staff = popover_filter_checkbox("Staff", df_base, "staff_owner", "staff")


        # =================================================================
        # ROW 2: c8 ถึง c13 (6 ช่อง)
        # สัดส่วน: [0.115, 0.115, 0.125, 0.125, 0.37, 0.15]
        # (Search กว้าง 37%, Reset 15%)
        # =================================================================
        c8, c9, c10, c11, c12, c13 = st.columns([0.13, 0.13, 0.22, 0.13, 0.24, 0.15])

        with c8:
            # 9. Status
            status = popover_filter_checkbox("Status", df_base, "status", "status")
            
        with c9:
            # 10. Contact Status
            cstatus = popover_filter_checkbox("Contact Status", df_base, "contact_status", "cstatus")

        with c10:
            with stylable_container(
                key="last_contact_date_inline",
                css_styles=["""
                div[data-testid="stDateInput"] div[data-baseweb="input"]:first-of-type::before {
                    content: "Last Contact";
                    position: absolute;
                    left: 14px;
                    top: 50%;
                    transform: translateY(-50%);
                    width: 92px;
                    text-align: left;
                    color: #6B7280;
                    font-weight: 500;
                    font-size: 14px;
                    pointer-events: none;
                    z-index: 2;
                }
                div[data-testid="stDateInput"] div[data-baseweb="input"]:first-of-type input {
                    padding-left: 122px !important;  /* 14 + 92 + 16(gap) */
                }
                """]
            ):
                sel_l = st.date_input(
                    "Last Contact Date",
                    value=(min_l, max_l),
                    min_value=min_l,
                    max_value=max_l,
                    key=wkey(K["last_contact_date"]),
                    label_visibility="collapsed",
                )

            if isinstance(sel_l, (list, tuple)) and len(sel_l) == 2:
                lc_start, lc_end = sel_l
            else:
                lc_start = lc_end = sel_l
            
        with c11:
            # 11. Follow Next Year
            follow_next_year = popover_filter_checkbox("Follow Next Year", df_base, "follow_next_year", "follow_next_year")

        with c12:
            # 12. Search Input
            with stylable_container(
                key="css_text_input",
                css_styles=["""input { background-color: rgb(244 244 244); }"""]
            ):
                q = st.text_input(
                    "Search",
                    value="", 
                    key=wkey(K["search"]), 
                    label_visibility="collapsed",
                    placeholder="Search all fields..."
                )

        with c13:
            # 13. Reset Button
            st.button(
                "Reset", 
                key=K["reset_btn"], 
                use_container_width=True,
                on_click=reset_all_filters
            )
    dstart, dend = created_start, created_end

    return dict(
        visible_cols=visible_cols,
        dstart=created_start, dend=created_end,   # created_at filter
        lc_start=lc_start, lc_end=lc_end,         # last_contact_at filter

        staff=staff, uni=uni, yl=yl, season=season, solo_group=solo_group,
        status=status, cstatus=cstatus, follow_next_year=follow_next_year,
        q=q,
    )

def _to_ts_scalar(x):
    if isinstance(x, (list, tuple, np.ndarray, pd.Series, pd.Index)):
        x = x[0] if len(x) else None
    if x is None:
        return None
    return pd.Timestamp(x).normalize()

def render_contacts():
    # Initialize data
    df_base_all, NO_MAP = initialize_contacts_data()

    filters = filters_ui(df_base_all)
    visible_cols = filters["visible_cols"]
    # export_btn_slot = filters["export_btn_slot"]

    df = df_base_all.copy()

    # created range
    ds_ts = _to_ts_scalar(filters["dstart"])
    de_ts = _to_ts_scalar(filters["dend"])
    created_dt = pd.to_datetime(df["created_at"], errors="coerce").dt.normalize()
    if (ds_ts is not None) and (de_ts is not None):
        df = df[created_dt.between(ds_ts, de_ts, inclusive="both")].copy()

    # last contact range
    ls_ts = _to_ts_scalar(filters["lc_start"])
    le_ts = _to_ts_scalar(filters["lc_end"])
    last_dt = pd.to_datetime(df["last_contact_at"], errors="coerce").dt.normalize()
    if (ls_ts is not None) and (le_ts is not None):
        df = df[last_dt.between(ls_ts, le_ts, inclusive="both")].copy()


    def _multi(df_, col, vals): return df_ if not vals else df_[df_[col].isin(vals)]
    df = _multi(df, "university", filters["uni"])
    df = _multi(df, "year_level", filters["yl"])
    df = _multi(df, "season", filters["season"])
    df = _multi(df, "solo_group", filters["solo_group"])
    df = _multi(df, "staff_owner", filters["staff"])
    df = _multi(df, "contact_status", filters["cstatus"])
    df = _multi(df, "status", filters["status"])
    df = _multi(df, "follow_next_year", filters["follow_next_year"])

    def _filter_text(df_in: pd.DataFrame, query: str) -> pd.DataFrame:
        if not query or query.strip() == "": return df_in
        tokens = [t.strip().lower() for t in query.split() if t.strip()]
        if not tokens: return df_in
        def row_text(r):
            # Search across all columns
            parts = [str(val) for val in r.values if pd.notna(val)]
            return " ".join(parts).lower()
        mask = df_in.apply(lambda r: all(tok in row_text(r) for tok in tokens), axis=1)
        return df_in[mask]

    df = _filter_text(df, filters["q"]).reset_index(drop=True)

    # No. mapping + sort by created_at descending (newest first), then by last_contact_at descending
    df_view = df.copy()

    # Defensive check: Ensure uid column exists (silent - only log errors)
    if "uid" not in df_view.columns:
        logger.error("CRITICAL: uid column missing from df_view at render_contacts line 395")
        logger.error(f"Available columns in df_view: {df_view.columns.tolist()}")
        logger.error(f"DataFrame shape: {df_view.shape}")
        # Skip adding No. column instead of crashing - continue silently
    else:
        # Only add No. column if uid exists
        df_view.insert(0, "No.", df_view["uid"].map(NO_MAP))

    df_view = df_view.sort_values(by=["created_at", "last_contact_at"], ascending=[False, False]).reset_index(drop=True)

    # Load config for status colors
    config = load_config()

    # Build status → (bg_color, text_color) mapping from database (status table)
    status_color_map: dict[str, tuple[str, str]] = {}
    if {"status", "status_bg_color", "status_text_color"}.issubset(df_view.columns):
        try:
            tmp = df_view[["status", "status_bg_color", "status_text_color"]].dropna(subset=["status"])
            tmp["status"] = tmp["status"].astype(str).str.strip()
            for _, row in tmp.iterrows():
                key = row["status"]
                if not key or key in status_color_map:
                    continue
                bg = row["status_bg_color"]
                fg = row["status_text_color"]
                if pd.notna(bg) and pd.notna(fg) and str(bg).strip() and str(fg).strip():
                    status_color_map[key] = (str(bg), str(fg))
        except Exception:
            status_color_map = {}

    def get_status_colors(key: str) -> tuple[str | None, str | None]:
        """Resolve status name to (bg_color, text_color).

        Priority:
        1) Colors from status table (status_color_map)
        2) Colors from edit/config.json (status_config)
        3) Default palette aligned with CSS
        """
        key = (key or "").strip()
        if not key:
            return None, None

        # 1) Colors from database (status table)
        if key in status_color_map:
            return status_color_map[key]

        # 2) Colors from config.json (legacy)
        cfg = (config.get("status_config") or {}).get(key)
        if cfg:
            bg = cfg.get("bg_color")
            fg = cfg.get("text_color")
            if bg and fg:
                return bg, fg

        # 3) Default palette aligned with components/iee.css
        default_map = {
            "สมัครแล้ว": ("#e8f0ff", "#1e40af"),       # badge--blue
            "หายไป": ("#fee2e2", "#991b1b"),          # badge--red
            "ไปกับเอเจนซี่อื่น": ("#f6dada", "#7f1d1d"), # badge--darkred
            "อยู่ระหว่างตัดสินใจ": ("#fef9c3", "#92400e"), # badge--yellow
            "เดินทางปีถัดไป": ("#f3e8ff", "#6d28d9"),    # badge--purple
        }
        if key in default_map:
            return default_map[key]

        return None, None

    def badge_with_color(text: str, bg_color: str, text_color: str) -> str:
        return f"<span style='background: {bg_color}; color: {text_color}; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-size: 12px; display: inline-block;'>{text}</span>"

    def badge(text: str, cls: str) -> str:
        return f"<span class='badge {cls}'>{text}</span>"

    def render_badges(df_in: pd.DataFrame) -> pd.DataFrame:
        df_out = df_in.copy()
        for col in ("Created", "Last Contact"):
            if col in df_display_visible.columns:
                df_display_visible[col] = df_display_visible[col].apply(
                    lambda d: d.isoformat()
                    if isinstance(d, date)
                    else (pd.to_datetime(d).date().isoformat() if pd.notna(d) and str(d)!="" else "")
                )
        if "contact_status" in df_out.columns:
            df_out["contact_status"] = df_out["contact_status"].apply(
                lambda x: badge(x, CONTACT_STATUS_BADGE_MAP.get(str(x), "")) if pd.notna(x) else x
            )
        if "status" in df_out.columns:
            def _render_status_badge(x):
                if pd.isna(x) or str(x).strip() == "":
                    return x
                key = str(x).strip()

                # Prefer DB/config colors when available
                bg, fg = get_status_colors(key)
                if bg and fg:
                    return badge_with_color(key, bg, fg)

                # Fallback to CSS class mapping
                return badge(key, STATUS_BADGE_MAP.get(key, "badge--blue"))

            df_out["status"] = df_out["status"].apply(_render_status_badge)
        return df_out

    show_cols = [c for c in VISIBLE_ORDER if c in visible_cols]
    # Keep uid for later use but don't display it
    df_show  = df_view[["uid"] + show_cols].copy()

    rename_map = {
        "uid":"UID","nickname":"Nickname","line_name":"LINE Name","university":"University",
        "year_level":"Year","solo_group":"Type","season":"Season","phone":"Phone",
        "email":"Email","staff_owner":"Staff","created_at":"Created",
        "last_contact_at":"Last Contact","day_last_contact":"หายไปกี่วัน",
        "contact_status":"Contact Status","status":"Status","follow_next_year":"Follow Next Year","comment":"Comment","call_note":"Call Note"
    }
    df_display = df_show.rename(columns=rename_map)

    # Keep UID for selection logic but don't display it
    df_display_visible = df_display.drop(columns=["UID"])
    
    # Format dates
    for col in ("created_at","last_contact_at"):
        if col in df_display_visible.columns:
            df_display_visible[col] = df_display_visible[col].apply(
                lambda d: d.isoformat()
                if isinstance(d, date)
                else (pd.to_datetime(d).date().isoformat() if pd.notna(d) and str(d)!="" else "")
            )

    # Edit button - show only when rows are selected
    # First render dataframe to get selection, then show button
    # We'll need to do this after dataframe render, so move button logic below

    # Table title with improved styling
    st.markdown(f"""
    <style>
    .table-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: #1f2a44;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }}
    </style>
    <div class="table-title" style="display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0 0.25rem 0;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-weight: 700; font-size: 1.2rem; color: #202224;">All Contacts</span>
            <span style="background: #E8F0FF; color: #1E40AF; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: 700; font-size: 0.9rem;">
                {len(df_display_visible)}
            </span>
        </div>
        <span style="font-size: 0.875rem; color: #6B7280; display: flex; align-items: center; gap: 0.35rem;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            Select rows and click Edit button
        </span>
    </div>
    """, unsafe_allow_html=True)


    # Add CSS to center align all table content and reduce top margin
    st.markdown("""
    <style>
    [data-testid="stDataFrame"] {
        margin-top: -1.5rem !important;
    }
    [data-testid="stDataFrame"] table thead tr th {
        text-align: center !important;
    }
    [data-testid="stDataFrame"] table tbody tr td {
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Styling functions for status columns
    # Use configured colors first; fall back to default palette aligned with CSS classes
    def color_contact_status(val):
        """Apply background color to contact_status column"""
        if pd.isna(val) or val == "":
            return ""
        if val == "ติดต่อไม่ได้":
            return "background-color: #FFE5E5; color: #EF3826; font-weight: 700; border-radius: 4.5px; padding: 4px 12px; text-align: center;"
        else:
            return "background-color: #E5F9F5; color: #00D9A5; font-weight: 700; border-radius: 4.5px; padding: 4px 12px; text-align: center;"

    def color_status(val):
        """Apply background color to status column"""
        if pd.isna(val) or val == "":
            return ""
        key = str(val).strip()

        # Resolve colors using DB → config → default palette
        bg, fg = get_status_colors(key)
        if bg and fg:
            return f"background-color: {bg}; color: {fg}; font-weight: 700; border-radius: 4.5px; padding: 4px 12px; text-align: center;"

        # Generic fallback when no color is known
        return "background-color: #F5F5F5; color: #666666; font-weight: 700; border-radius: 4.5px; padding: 4px 12px; text-align: center;"

    # Check if filtered data is empty
    if len(df_display_visible) == 0:
        st.info("No records found")
    else:
        # Apply styling with proper method
        styled_df = df_display_visible.style

        if "Contact Status" in df_display_visible.columns:
            styled_df = styled_df.map(color_contact_status, subset=["Contact Status"])

        if "Status" in df_display_visible.columns:
            styled_df = styled_df.map(color_status, subset=["Status"])

        # Display with event for row selection (multi-row mode)
        event = st.dataframe(
            styled_df,
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
            key="contacts_table"
        )

        # Show Edit button when rows are selected
        if event.selection and len(event.selection.rows) > 0:
            selected_indices = event.selection.rows
            num_selected = len(selected_indices)

            # Get UIDs of selected rows (use original df_display with UID column)
            selected_uids = [str(df_display.iloc[idx]["UID"]) for idx in selected_indices]

            # Show Edit button above the table
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # st.markdown('<div style="margin-top: -3rem; margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
                edit_label = f"✏️ Edit {num_selected} contact{'s' if num_selected > 1 else ''}"
                if st.button(edit_label, width="stretch", type="primary", key="edit_selected_btn"):
                    query_params = {
                        "edit_uids_len": str(len(selected_uids)),
                    }
                    for i, uid in enumerate(selected_uids):
                        query_params[f"edit_uids{i}"] = str(uid)
                        
                    # st.session_state["edit_uids"] = selected_uids
                    st.session_state["came_from"] = "contacts"

                    # Navigate to edit page
                    st.switch_page(page="views/edits.py", query_params=query_params)

    # st.markdown('</div>', unsafe_allow_html=True)

    # Export (filtered view)
    export_df = df_view[show_cols].rename(columns=rename_map)

    # Create export button with SVG icon to match overview style
    csv_data = export_df.to_csv(index=False).encode("utf-8-sig")
    
    st.session_state["export_csv"] = csv_data
    # # Use st.download_button with custom label containing SVG
    # import base64
    # b64 = base64.b64encode(csv_data).decode()

    # with export_btn_slot:
    #     st.markdown(f"""
    #     <div style="margin-bottom: 1rem;">
    #         <a href="data:text/csv;base64,{b64}" download="contacts_filtered.csv" style="text-decoration: none;">
    #             <button class="export-button">
    #                 <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px;">
    #                     <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    #                     <polyline points="7 10 12 15 17 10"></polyline>
    #                     <line x1="12" y1="15" x2="12" y2="3"></line>
    #                 </svg>
    #                 Export
    #             </button>
    #         </a>
    #     </div>
    #     """, unsafe_allow_html=True)

def title_contacts():
    with stylable_container(
        key="css_align_popover",
        css_styles=["""
        div:nth-child(2) > div[data-testid="stVerticalBlock"] {
            align-items: flex-end !important;
            padding: 1.25rem 0px 1rem !important;
        }
        """]
    ):
        col_title, col_export = st.columns([8, 2])

        with col_title:
            st.markdown(f"## Contacts")

        with col_export:
            with st.popover(label="Download CSV"):
                file_name = st.text_input("File name", value="customer_contacts", placeholder="File name")
                pop_col1, pop_col2 = st.columns(2)
                with pop_col1:
                    download_confirm = st.button("Confirm", width="stretch")
                with pop_col2:
                    if download_confirm:
                        st.download_button(
                            "Download",
                            st.session_state['export_csv'],
                            f"{file_name}.csv",
                            "text/csv",
                            key='download-csv',
                            width="stretch"
                        )
                    else:
                        st.download_button(
                            "Download",
                            "",
                            f"{file_name}.csv",
                            "text/csv",
                            key='download-csv',
                            disabled=True,
                            width="stretch"
                        ) 
