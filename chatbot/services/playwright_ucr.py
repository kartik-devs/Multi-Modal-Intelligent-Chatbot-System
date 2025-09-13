from typing import Tuple, Optional, Dict, Any
import asyncio

from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re


def fetch_ucr_fee(
    acct_key: str,
    service_date: str,
    procedure_code: str,
    zip_code: str,
    percentile: str = "50",
    timeout_ms: int = 15000,
) -> Tuple[Optional[str], Optional[str]]:
    """Use Playwright to submit the UCR Fee Viewer form and return the page HTML.

    Returns (html, error).
    """
    url = f"https://www.feeinfo.com/DecisionPointUCR/?acctkey={acct_key}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(url, wait_until="domcontentloaded")

            # Attempt to find the actual content frame robustly
            def find_middle_frame():
                # Prefer frame by URL pattern first
                for f in page.frames:
                    u = (getattr(f, "url", "") or "").lower()
                    n = (getattr(f, "name", "") or "").lower()
                    if "/welcome.html/getbody" in u:
                        return f
                    if n == "middle" or "body" in n:
                        return f
                return None

            middle = None
            for _ in range(20):  # wait up to ~5s
                middle = find_middle_frame()
                if middle:
                    break
                page.wait_for_timeout(250)

            # Last-resort: try to switch via frame_locator (some pages delay names)
            if middle is None:
                try:
                    page.frame_locator("iframe[name=middle]")
                    for f in page.frames:
                        if (f.name or "").lower() == "middle":
                            middle = f
                            break
                except Exception:
                    pass

            if middle is None:
                html = page.content()
                browser.close()
                return None, "Unable to locate middle frame on UCR page"

            # Helpers to robustly target varying selector names
            def fill_first(value: str, selectors: list[str], wait_ms: int = 8000) -> None:
                last_err = None
                for sel in selectors:
                    try:
                        middle.wait_for_selector(sel, timeout=wait_ms)
                        middle.fill(sel, value)
                        return
                    except Exception as e:
                        last_err = e
                if last_err:
                    raise last_err

            def select_first(value: str, selectors: list[str], wait_ms: int = 8000) -> None:
                last_err = None
                for sel in selectors:
                    try:
                        middle.wait_for_selector(sel, timeout=wait_ms)
                        try:
                            middle.select_option(sel, value=value)
                            return
                        except Exception:
                            middle.select_option(sel, label=f"{value}th Percentile")
                            return
                    except Exception as e:
                        last_err = e
                if last_err:
                    raise last_err

            # Fill out the form fields with resilient selectors
            fill_first(service_date, [
                'input[name="serviceDate"]',
                'input[name="Sdate"]',
                '#serviceDate',
                'input[placeholder*="Service"]',
            ])

            fill_first(procedure_code, [
                'input[name="procedureCode"]',
                'input[name="cpt"]',
                '#procedureCode',
            ])

            fill_first(zip_code, [
                'input[name="zipCode"]',
                'input[name="zip"]',
                '#zipCode',
            ])

            # Percentile handling: site returns 50-95 automatically; dropdown is only 25-45
            if str(percentile) in {"25", "30", "35", "40", "45"}:
                # Only attempt selection when in the supported dropdown range
                try:
                    # Ensure element is interactable
                    middle.click('select[name="percentile"], #percentile, select', timeout=5000)
                except Exception:
                    pass
                select_first(str(percentile), [
                    'select[name="percentile"]',
                    '#percentile',
                    'select',
                ])
            # else: skip selecting; server will return 50-95 by default

            # Submit
            try:
                middle.click('input[type="submit"], input[value="Submit"], button:has-text("Submit")')
            except Exception:
                # try pressing Enter in last field
                middle.press('input[name="zipCode"], input[name="zip"]', 'Enter')

            # Wait until the loading message is gone or a likely result appears
            try:
                middle.wait_for_timeout(800)  # brief settle
                # Prefer a table-like element, else disappearance of loading text
                middle.wait_for_selector("table, #resultsDiv, .table", timeout=max(timeout_ms, 20000))
            except Exception:
                try:
                    middle.wait_for_selector(
                        'text=/^(?:(?!Loading your estimated charge).)*$/',
                        timeout=timeout_ms,
                    )
                except Exception:
                    pass

            html = middle.content()
            browser.close()
            return html, None
    except Exception as e:
        return None, str(e)


# ---- Async Playwright version that fills by IDs and submits form reliably ----
async def fetch_ucr_fee_async(
    acct_key: str,
    service_date: str,
    procedure_code: str,
    zip_code: str,
    percentile: str = "50",
    timeout_ms: int = 30000,
) -> Tuple[Optional[str], Optional[str]]:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Go directly to the middle frame content instead of the frameset
            url = f"https://www.feeinfo.com/DecisionPointUCR/welcome.html/getBody/?acctkey={acct_key}"
            await page.goto(url, timeout=timeout_ms)
            await page.wait_for_load_state("domcontentloaded")

            # Fill fields directly by IDs present on the frame page
            # These exist on the middle frame content page too when navigated directly
            try:
                await page.fill("#servicedate", service_date)
                await page.fill("#procCode", procedure_code)
                await page.fill("#zip", zip_code)
                if percentile in {"25", "30", "35", "40", "45"}:
                    await page.select_option("#percentile", percentile)
                else:
                    # Default to All so 50–95 are returned
                    await page.select_option("#percentile", "All")
            except Exception:
                pass

            # Submit via button then wait for results containers
            try:
                await page.click("#submitBtn")
            except Exception:
                # JS fallback
                await page.evaluate(
                    "() => { const f=document.forms['search']; if(f){ if(f.requestSubmit) f.requestSubmit(); else f.submit(); }}"
                )

            try:
                await page.wait_for_selector("#fulltablediv, #filtertablediv", timeout=timeout_ms)
            except Exception:
                # Fallback: spinner hidden or any table appears
                try:
                    await page.wait_for_selector("table", timeout=timeout_ms)
                except Exception:
                    pass

            await asyncio.sleep(1.5)
            html = await page.content()
            await browser.close()
            return html, None
    except Exception as e:
        return None, f"Playwright async error: {str(e)}"


def fetch_ucr_fee_sync(
    acct_key: str,
    service_date: str,
    procedure_code: str,
    zip_code: str,
    percentile: str = "50",
    timeout_ms: int = 30000,
) -> Tuple[Optional[str], Optional[str]]:
    """Synchronous wrapper around the async implementation."""
    return asyncio.run(
        fetch_ucr_fee_async(
            acct_key=acct_key,
            service_date=service_date,
            procedure_code=procedure_code,
            zip_code=zip_code,
            percentile=percentile,
            timeout_ms=timeout_ms,
        )
    )


def parse_ucr_html(html: str) -> Dict[str, Any]:
    """Parse UCR HTML and extract a single row of results if present.

    Returns a dict with normalized keys or an error key.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        percentiles: Dict[str, Any] = {}
        description = None
        code = None

        print(f"HTML content length: {len(html)}")
        print(f"Text content preview: {text[:500]}...")

        # Method 1: Look for specific percentile table rows (percentiles1-5 classes)
        percentile_rows = soup.find_all("tr", class_=re.compile(r"percentiles[1-5]"))
        if percentile_rows:
            print(f"Found {len(percentile_rows)} percentile rows")
            for row in percentile_rows:
                cells = row.find_all("td")
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    # Look for pattern like "50th : $ 67.21" in both HTML and text
                    match = re.search(r'(\d{2})<sup>th</sup>\s*:\s*\$\s*([0-9,.]+)', str(cell))
                    if not match:
                        # Fallback for plain text
                        match = re.search(r'(\d{2})th\s*:\s*\$\s*([0-9,.]+)', cell_text)
                    if match:
                        pct_num = match.group(1)
                        value = float(match.group(2).replace(",", ""))
                        percentiles[pct_num] = value
                        print(f"Found {pct_num}th percentile: {value}")

        # Method 2: Fallback to regex over whole page
        if not percentiles:
            print("Trying regex fallback...")
            for m in re.finditer(r"(\d{2})th\s*:\s*\$\s*([0-9,.]+)", text):
                pct_num = m.group(1)
                value = float(m.group(2).replace(",", ""))
                percentiles[pct_num] = value
                print(f"Regex found {pct_num}th percentile: {value}")

        # Extract code and description
        m_code = re.search(r"Code\s*:\s*([A-Za-z0-9]+)", text)
        if m_code:
            code = m_code.group(1)
        m_desc = re.search(r"Desc\s*:\s*(.+?)\s*Percentiles", text)
        if m_desc:
            description = m_desc.group(1).strip()

        result: Dict[str, Any] = {
            "procedureCode": code,
            "description": description,
            "percentiles": percentiles,
            "currency": "USD",
        }
        if not percentiles:
            result["error"] = "Percentiles not found"
            result["debug_html_preview"] = text[:1000]
        
        print(f"Final result: {result}")
        return result
    except Exception as e:
        print(f"Parse error: {str(e)}")
        return {"error": str(e)}


