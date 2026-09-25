"""Toma una captura de la app en ejecución escribiendo un mensaje en el chat.
Uso: python docs/shot.py <puerto> <archivo_salida.png> "<mensaje>" """
import sys
from playwright.sync_api import sync_playwright

port, out, message = sys.argv[1], sys.argv[2], sys.argv[3]
height = int(sys.argv[4]) if len(sys.argv) > 4 else 900
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1366, "height": height}, device_scale_factor=1)
    page.goto(f"http://localhost:{port}", wait_until="networkidle")
    page.wait_for_selector("textarea", timeout=30000)
    page.fill("textarea", message)
    page.keyboard.press("Enter")
    page.wait_for_timeout(12000)
    page.screenshot(path=out, full_page=True)
    browser.close()
