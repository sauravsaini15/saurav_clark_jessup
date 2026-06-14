import json
import os
import glob
import re
import zipfile
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

GOOGLE_DRIVE_API_URL = os.environ.get("GOOGLE_DRIVE_API_URL", "http://localhost:8018")
GOOGLE_CALENDAR_API_URL = os.environ.get("GOOGLE_CALENDAR_API_URL", "http://localhost:8016")
AIRTABLE_API_URL = os.environ.get("AIRTABLE_API_URL", "http://localhost:8032")
DROPBOX_API_URL = os.environ.get("DROPBOX_API_URL", "http://localhost:8082")
NOTION_API_URL = os.environ.get("NOTION_API_URL", "http://localhost:8010")

SIGNAL_FILE_IDS = [
    "1DriveFile02JPG_segA",
    "1DriveFile03HEIC_segB",
    "1DriveFile04PDF_stdcurrent",
    "1DriveFile07JPG_segC",
]
CONDITION_LOG_FILE_ID = "1DriveFile01XLSX_form"


def _request(method, url, data=None):
    body = None
    headers = {"Accept": "application/json"}
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=body, method=method, headers=headers)
    with urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_get(base_url, endpoint):
    return _request("GET", f"{base_url}{endpoint}")


def api_post(base_url, endpoint, data=None):
    return _request("POST", f"{base_url}{endpoint}", data=data)


def _get(url):
    return _request("GET", url)


def _post(url, data=None):
    return _request("POST", url, data=data)


def read_file(path):
    with open(path) as f:
        return f.read()


def file_exists(path):
    return os.path.exists(path)


def audit_summary(base_url):
    try:
        data = api_get(base_url, "/audit/summary")
    except (URLError, HTTPError, ValueError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data.get("endpoints", {})


def audit_requests(base_url):
    try:
        data = api_get(base_url, "/audit/requests")
    except (URLError, HTTPError, ValueError, OSError):
        return []
    if not isinstance(data, dict):
        return []
    return data.get("requests", [])


def endpoint_called(summary, method_path_prefix):
    return any(key.startswith(method_path_prefix) for key in summary.keys())


def drive_condition_log_name():
    try:
        data = api_get(GOOGLE_DRIVE_API_URL, f"/drive/v3/files/{CONDITION_LOG_FILE_ID}")
    except (URLError, HTTPError, ValueError, OSError):
        return "file_01.xlsx"
    if isinstance(data, dict) and data.get("name"):
        return data["name"]
    return "file_01.xlsx"


def _strip_ns(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


def _xlsx_shared_strings(zf):
    strings = []
    try:
        raw = zf.read("xl/sharedStrings.xml")
    except KeyError:
        return strings
    root = ET.fromstring(raw)
    for si in root:
        if _strip_ns(si.tag) != "si":
            continue
        text = "".join((n.text or "") for n in si.iter() if _strip_ns(n.tag) == "t")
        strings.append(text)
    return strings


def _col_letter(cell_ref):
    return "".join(ch for ch in cell_ref if ch.isalpha())


def _row_number(cell_ref):
    digits = "".join(ch for ch in cell_ref if ch.isdigit())
    return int(digits) if digits else 0


def xlsx_rows(path):
    rows = {}
    if not path or not os.path.exists(path):
        return rows
    try:
        with zipfile.ZipFile(path) as zf:
            shared = _xlsx_shared_strings(zf)
            sheets = [n for n in zf.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n)]
            if not sheets:
                return rows
            sheets.sort()
            root = ET.fromstring(zf.read(sheets[0]))
            for cell in root.iter():
                if _strip_ns(cell.tag) != "c":
                    continue
                ref = cell.attrib.get("r", "")
                if not ref:
                    continue
                ctype = cell.attrib.get("t", "")
                value = ""
                if ctype == "inlineStr":
                    value = "".join((n.text or "") for n in cell.iter() if _strip_ns(n.tag) == "t")
                else:
                    vnode = None
                    for n in cell:
                        if _strip_ns(n.tag) == "v":
                            vnode = n
                            break
                    if vnode is not None and vnode.text is not None:
                        if ctype == "s":
                            try:
                                value = shared[int(vnode.text)]
                            except (ValueError, IndexError):
                                value = ""
                        else:
                            value = vnode.text
                rows.setdefault(_row_number(ref), {})[_col_letter(ref)] = value
    except (zipfile.BadZipFile, ET.ParseError, OSError):
        return {}
    return rows


def xlsx_all_text(path):
    rows = xlsx_rows(path)
    parts = []
    for cells in rows.values():
        parts.extend(str(v) for v in cells.values())
    return " ".join(parts).lower()


def find_condition_log(name):
    cands = set()
    if name:
        cands.update(glob.glob(f"**/{name}", recursive=True))
    cands.update(glob.glob("**/*.xlsx", recursive=True))
    headered = []
    for path in cands:
        text = xlsx_all_text(path)
        if "condition code" in text:
            headered.append((path, text))
    for path, text in headered:
        if re.search(r"code\s*[1-5]", text):
            return path
    if headered:
        return headered[0][0]
    for path in cands:
        if os.path.basename(path) == name:
            return path
    return None


def segment_row_values(rows, letter):
    target = letter.lower()
    for _rnum, cells in sorted(rows.items()):
        for v in cells.values():
            norm = str(v).strip().lower()
            if norm == target or norm == f"segment {target}" or norm.endswith(f" {target}"):
                return [str(x).strip().lower() for x in cells.values()]
    return []


def test_google_drive_files_listed():
    summary = audit_summary(GOOGLE_DRIVE_API_URL)
    assert endpoint_called(summary, "GET /drive/v3/files")


def test_google_drive_signal_files_downloaded():
    requests = audit_requests(GOOGLE_DRIVE_API_URL)
    seen = {fid for entry in requests for fid in SIGNAL_FILE_IDS if fid in (entry.get("path") or "")}
    assert len(seen) >= 2


def test_google_drive_log_headers_present():
    text = xlsx_all_text(find_condition_log(drive_condition_log_name()))
    assert all(h in text for h in ["segment id", "condition code", "recommended action", "survey date", "standards version", "escalation"])


def test_google_drive_log_segment_a_code_2():
    rows = xlsx_rows(find_condition_log(drive_condition_log_name()))
    assert any("code 2" in v for v in segment_row_values(rows, "A"))


def test_google_drive_log_segment_b_code_4():
    rows = xlsx_rows(find_condition_log(drive_condition_log_name()))
    assert any("code 4" in v for v in segment_row_values(rows, "B"))


def test_google_drive_log_segment_c_code_3():
    rows = xlsx_rows(find_condition_log(drive_condition_log_name()))
    assert any("code 3" in v for v in segment_row_values(rows, "C"))


def test_google_drive_log_standards_version_v23():
    text = xlsx_all_text(find_condition_log(drive_condition_log_name()))
    assert "v2.3" in text


def test_google_drive_log_segment_b_escalation_yes():
    rows = xlsx_rows(find_condition_log(drive_condition_log_name()))
    assert any(v == "yes" for v in segment_row_values(rows, "B"))


def test_google_drive_log_survey_date_recorded():
    text = xlsx_all_text(find_condition_log(drive_condition_log_name()))
    assert ("2026-10-05" in text) or ("10/05/2026" in text) or ("october 5, 2026" in text)


def test_google_drive_log_segment_b_foot_traffic_action():
    text = xlsx_all_text(find_condition_log(drive_condition_log_name()))
    assert "foot traffic" in text


def test_google_calendar_events_listed():
    summary = audit_summary(GOOGLE_CALENDAR_API_URL)
    assert endpoint_called(summary, "GET /calendar/v3/calendars")


def test_google_drive_log_stale_code_2_segment_b():
    rows = xlsx_rows(find_condition_log(drive_condition_log_name()))
    assert any("code 2" in v for v in segment_row_values(rows, "B"))


def test_google_drive_log_old_version_v19():
    text = xlsx_all_text(find_condition_log(drive_condition_log_name()))
    assert "v1.9" in text


def test_google_drive_log_segment_c_low_severity():
    rows = xlsx_rows(find_condition_log(drive_condition_log_name()))
    assert any(("code 1" in v) or ("code 2" in v) for v in segment_row_values(rows, "C"))


def test_airtable_distractor():
    summary = audit_summary(AIRTABLE_API_URL)
    assert len(summary) > 0


def test_dropbox_distractor():
    summary = audit_summary(DROPBOX_API_URL)
    assert len(summary) > 0


def test_notion_distractor():
    summary = audit_summary(NOTION_API_URL)
    assert len(summary) > 0
