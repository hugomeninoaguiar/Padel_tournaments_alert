import asyncio
import re
from datetime import date

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

URL = "https://tour.tiesports.com/fpp/calendar_(tournaments)"
TIMEOUT_MS = 30_000


_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "fev": 2, "abr": 4, "mai": 5, "ago": 8, "set": 9, "out": 10, "dez": 12,
}


def _parse_start_date(date_str: str) -> date | None:
    """Extract the start date from strings like '25 Feb - 1 Mar' or '4 - 8 Mar'."""
    today = date.today()
    # "D Mon ..." — start day has a named month
    m = re.match(r"(\d{1,2})\s+([A-Za-z]{3})", date_str)
    if m:
        day, mon = int(m.group(1)), _MONTH_MAP.get(m.group(2).lower())
        if mon:
            year = today.year + 1 if mon < today.month - 1 else today.year
            try:
                return date(year, mon, day)
            except ValueError:
                pass
    # "D - D Mon" — same month, month comes after the range
    m = re.match(r"(\d{1,2})\s*-\s*\d{1,2}\s+([A-Za-z]{3})", date_str)
    if m:
        day, mon = int(m.group(1)), _MONTH_MAP.get(m.group(2).lower())
        if mon:
            year = today.year + 1 if mon < today.month - 1 else today.year
            try:
                return date(year, mon, day)
            except ValueError:
                pass
    return None


def _months_to_check() -> list[tuple[int, int]]:
    today = date.today()
    current = (today.year, today.month)
    if today.month == 12:
        nxt = (today.year + 1, 1)
    else:
        nxt = (today.year, today.month + 1)
    return [current, nxt]


async def _select_custom_dropdown(page, select_id: str, value: str) -> None:
    """Interact with the cs-select custom dropdown widget used on this site."""
    # The native <select> is hidden; there's a custom UI wrapper around it.
    # Click the wrapper to open the dropdown, then click the matching option.
    wrapper = page.locator(f"div.cs-select:has(select#{select_id})")
    await wrapper.click()
    await page.wait_for_timeout(500)
    # Options are <li data-option data-value="..."><span>...</span></li>
    option = wrapper.locator(f"li[data-option][data-value='{value}']")
    await option.click()
    await page.wait_for_timeout(500)


async def _scrape_month(page, year: int, month: int) -> list[dict]:
    await page.goto(URL, timeout=TIMEOUT_MS)
    await page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)

    # Discover the actual select IDs from the page
    year_select_id = await page.locator("select[id*='year']").first.get_attribute("id")
    month_select_id = await page.locator("select[id*='month']").first.get_attribute("id")

    # Set year filter via custom dropdown
    await _select_custom_dropdown(page, year_select_id, str(year))

    # Set month filter via custom dropdown
    await _select_custom_dropdown(page, month_select_id, str(month))

    # Click Filtrar button
    filtrar = page.locator("button:has-text('Filtrar'), input[value='Filtrar']").first
    await filtrar.click()
    await page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)

    # Small extra wait for dynamic content
    await asyncio.sleep(2)

    # Scrape tournament rows — inspect the table/card structure
    tournaments = []
    row_locator = page.locator("table tbody tr, .tournament-row, .calendar-item")
    count = await row_locator.count()

    for i in range(count):
        row = row_locator.nth(i)
        cells = await row.locator("td").all()

        if not cells:
            # Card-style layout
            name = (await row.locator("[class*='name'], [class*='title'], h3, h4").first.inner_text()).strip()
            date_str = (await row.locator("[class*='date'], time").first.inner_text()).strip()
            location = ""
            escaloes = ""
            try:
                location = (await row.locator("[class*='local'], [class*='location'], [class*='city']").first.inner_text()).strip()
            except Exception:
                pass
            try:
                escaloes = (await row.locator("[class*='escalao'], [class*='category']").first.inner_text()).strip()
            except Exception:
                pass
        else:
            cell_texts = [((await c.inner_text()).strip()) for c in cells]
            if len(cell_texts) < 3:
                continue
            # Cell structure: [start_date, prize/category, details_blob]
            # details_blob lines: name, escalões, full_date_range, venue, counts
            category = cell_texts[1]
            if "ABS" not in category:
                continue
            details = cell_texts[2].split("\n")
            details = [d.strip() for d in details if d.strip()]
            name = details[0] if details else ""
            escaloes = details[1] if len(details) > 1 else ""
            date_str = details[2] if len(details) > 2 else cell_texts[0].replace("\n", " ")
            location = details[3] if len(details) > 3 else ""

        if not name or not date_str:
            continue

        # Try to get a detail URL
        url = ""
        try:
            link = row.locator("a").first
            href = await link.get_attribute("href")
            if href:
                url = href if href.startswith("http") else f"https://tour.tiesports.com{href}"
        except Exception:
            pass

        tournaments.append({
            "name": name,
            "date": date_str,
            "location": location,
            "escaloes": escaloes,
            "category": category,
            "url": url,
        })

    return tournaments


async def scrape_tournaments() -> list[dict]:
    months = _months_to_check()
    all_tournaments = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="pt-PT")
        page = await context.new_page()

        for year, month in months:
            try:
                results = await _scrape_month(page, year, month)
                all_tournaments.extend(results)
            except PlaywrightTimeout as e:
                await browser.close()
                raise RuntimeError(f"Timeout scraping {year}-{month:02d}: {e}") from e

        await browser.close()

    # Deduplicate by name+date and filter out past tournaments
    today = date.today()
    seen = set()
    unique = []
    for t in all_tournaments:
        key = (t["name"], t["date"])
        if key in seen:
            continue
        seen.add(key)
        start = _parse_start_date(t["date"])
        if start and start < today:
            continue
        unique.append(t)

    return unique
