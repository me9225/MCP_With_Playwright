import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

# יצירת מופע של השרת
mcp = FastMCP("WeatherIsrael")

# משתנים גלובליים לניהול הדפדפן
browser_context = {
    "browser": None,
    "page": None,
    "playwright": None
}


async def get_page():
    """
    פונקציית עזר להבטחת קיום דף פעיל בדפדפן
    """
    if browser_context["page"] is None:
        browser_context["playwright"] = await async_playwright().start()

        # headless=False מאפשר לראות את פעולת הדפדפן בלייב
        browser_context["browser"] = await browser_context["playwright"].chromium.launch(
            headless=False
        )

        browser_context["page"] = await browser_context["browser"].new_page()

    return browser_context["page"]


@mcp.tool()
async def open_weather_forecast_israel():
    """
    פתיחת אתר תחזית מזג האוויר בישראל.
    """
    page = await get_page()

    await page.goto(
        "https://www.weather2day.co.il/forecast",
        wait_until="networkidle"
    )

    return "אתר תחזית מזג האוויר נפתח בהצלחה."


@mcp.tool()
async def enter_weather_forecast_city_israel(city_name: str):
    """
    הכנסת שם עיר ישראלית בשדה החיפוש.
    """

    page = await get_page()

    search_selectors = [
        "input#search-input",
        "input[name='q']",
        "input[type='search']",
        "input[placeholder*='חיפוש']"
    ]

    for selector in search_selectors:
        try:
            await page.wait_for_selector(
                selector,
                timeout=3000
            )

            await page.fill(
                selector,
                city_name
            )

            return f"העיר {city_name} הוזנה בהצלחה."

        except Exception:
            continue

    return "לא נמצא שדה חיפוש באתר."


@mcp.tool()
async def select_weather_forecast_city_israel():
    """
    בחירת העיר מתוך רשימת ההצעות שמופיעה לאחר החיפוש.
    """

    page = await get_page()

    suggestion_selectors = [
        ".autocomplete-suggestion",
        ".search-results a",
        ".ui-menu-item",
        "ul li a"
    ]

    for selector in suggestion_selectors:
        try:
            await page.wait_for_selector(
                selector,
                timeout=5000
            )

            await page.locator(selector).first.click()

            return "העיר נבחרה בהצלחה."

        except Exception:
            continue

    try:
        await page.keyboard.press("Enter")
        return "לא נמצאה רשימת ערים, בוצע חיפוש באמצעות Enter."

    except Exception as e:
        return f"שגיאה בבחירת העיר: {str(e)}"


@mcp.tool()
async def extract_weather_data():
    """
    חילוץ נתוני מזג האוויר מהדף הנוכחי.
    """

    page = await get_page()

    await page.wait_for_load_state(
        "networkidle"
    )

    content = await page.evaluate(
        "() => document.body.innerText"
    )

    clean_content = " ".join(
        content.split()
    )

    return f"נתונים שחולצו: {clean_content[:2000]}"


if __name__ == "__main__":
    mcp.run()
