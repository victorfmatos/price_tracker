from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from pathlib import Path
from logic.Scraper import Scraper, ProductData
import os

PROFILE_DIR = os.path.expanduser("~/.price_tracker_profile")
DEFAULT_SELECTORS_PATH = Path(__file__).resolve().parent / "variables.json"

def main(product_url: str) -> ProductData:  
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
    
    try:
      page = context.pages[0] if context.pages else context.new_page()
      scraper = Scraper(DEFAULT_SELECTORS_PATH)
      print(f"Buscando dados de: {product_url}")
      return scraper.scrape_generic_product(product_url, page)
    finally:
      context.close()

if __name__ == "__main__":
  data = main("https://www.mercadolivre.com.br/kit-ventoinhas-aigo-darkflash-ar12-pro-argb-5x120mm-preto/up/MLBU2344679274")
  print(data)
