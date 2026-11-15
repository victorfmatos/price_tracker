import browser_cookie3
from playwright.sync_api import sync_playwright, Cookie
from playwright_stealth import Stealth
from logic.Scraper import Scraper
import os

PROFILE_DIR = os.path.expanduser(".price_tracker_profile")

def get_cookies():
  cj = browser_cookie3.chrome(domain_name="mercadolivre.com.br")
  playwright_cookies = []
  
  for c in cj:
    cookie = {
      "name": c.name,
      "value": c.value or "",
      "domain": c.domain,
      "path": c.path,
      "secure": bool(c.secure),
      "sameSite": "Lax"
    }
    
    if c.expires:
      cookie["expires"] = float(c.expires)
    playwright_cookies.append(cookie)
  
  return playwright_cookies

def main(product_url):
  cookies = get_cookies()
  
  with Stealth().use_sync(sync_playwright()) as p:
    context = p.chromium.launch_persistent_context(
      user_data_dir=PROFILE_DIR,
      channel="chrome",
      headless=False,
      chromium_sandbox=True,
      locale="pt-BR",
      viewport={"width": 1366, "height": 768},
      args=[
        "--disable-blink-features=AutomationControlled",
        "--test-type"
      ]
    )
    
    if cookies:
      context.add_cookies(cookies)
    
    page = context.pages[0] if context.pages else context.new_page()
      
    scraper = Scraper("src/variables.json")
    print(f"Buscando dados de: {product_url}")
    product_data = scraper.scrape_generic_product(product_url, page)
    
    return product_data    
      
if __name__ == "__main__":
  data = main("https://www.mercadolivre.com.br/kit-ventoinhas-aigo-darkflash-ar12-pro-argb-5x120mm-preto/up/MLBU2344679274")
  print(data)
