import sys
import os
import json
from typing import Dict
from datetime import datetime
import re
from openpyxl import load_workbook

from .playwright_ucr import fetch_ucr_fee_sync, parse_ucr_html


def fill_sheet(input_path: str, acctkey: str) -> str:
    wb = load_workbook(input_path)
    ws = wb.active

    # Ensure headers for percentile columns exist
    headers: Dict[str, str] = {
        "50": "D",
        "55": "E",
        "60": "F",
        "65": "G",
        "70": "H",
        "75": "I",
        "80": "J",
        "85": "K",
        "90": "L",
        "95": "M",
    }
    for pct, col in headers.items():
        if not ws[f"{col}1"].value:
            ws[f"{col}1"] = pct

    # Iterate rows starting from 2 (assuming row 1 is header)
    row = 2
    while True:
        date_v = ws[f"A{row}"].value
        cpt_v = ws[f"B{row}"].value
        zip_v = ws[f"C{row}"].value
        if not date_v and not cpt_v and not zip_v:
            break

        if date_v and cpt_v and zip_v:
            # Normalize date to strict MM/DD/YYYY (10 chars with slashes)
            def coerce_date(val) -> str:
                if isinstance(val, datetime):
                    return val.strftime("%m/%d/%Y")
                s = str(val).strip()
                for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%Y/%m/%d"):
                    try:
                        return datetime.strptime(s, fmt).strftime("%m/%d/%Y")
                    except Exception:
                        continue
                # last resort: try M/D/YYYY and pad
                m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
                if m:
                    mm = m.group(1).zfill(2)
                    dd = m.group(2).zfill(2)
                    yy = m.group(3)
                    return f"{mm}/{dd}/{yy}"
                return s

            service_date = coerce_date(date_v)
            procedure_code = re.sub(r"\D", "", str(cpt_v)).strip()  # digits only
            zip_code = re.sub(r"\D", "", str(zip_v)).strip().zfill(5)  # exactly 5 digits

            # Basic validations per site requirements
            if len(service_date) != 10 or service_date.count('/') != 2:
                print(f"Row {row}: error invalid date '{service_date}'", flush=True)
                row += 1
                continue
            if not procedure_code:
                print(f"Row {row}: error missing CPT", flush=True)
                row += 1
                continue
            if not re.match(r"^\d{5}$", zip_code):
                print(f"Row {row}: error invalid ZIP '{zip_code}'", flush=True)
                row += 1
                continue

            print(f"Row {row}: date={service_date} cpt={procedure_code} zip={zip_code} ...", flush=True)
            html, err = fetch_ucr_fee_sync(
                acct_key=acctkey,
                service_date=service_date,
                procedure_code=procedure_code,
                zip_code=zip_code,
                percentile="50",
                timeout_ms=20000,
            )
            if not err and html:
                parsed = parse_ucr_html(html)
                # Save snapshot for auditing
                try:
                    snap_dir = os.path.dirname(input_path)
                    snap_name = f"row_{row}_{procedure_code}_{zip_code}.html"
                    with open(os.path.join(snap_dir, snap_name), "w", encoding="utf-8") as f:
                        f.write(html)
                except Exception:
                    pass
                per = parsed.get("percentiles", {}) if isinstance(parsed.get("percentiles"), dict) else {}
                for pct, col in headers.items():
                    if pct in per:
                        ws[f"{col}{row}"] = per[pct]
                print(f"Row {row}: percentiles={json.dumps(per)}", flush=True)
            else:
                ws[f"{headers['50']}{row}"] = f"ERR: {err}" if err else "ERR"
                print(f"Row {row}: error {err}", flush=True)

        row += 1

    out_path = os.path.splitext(input_path)[0] + "_filled.xlsx"
    wb.save(out_path)
    print(f"Wrote: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m chatbot.services.ucr_batch_runner <input_excel_path> <acctkey>")
        sys.exit(1)
    input_excel = sys.argv[1]
    acct = sys.argv[2]
    result = fill_sheet(input_excel, acct)
    print(f"Wrote: {result}")


