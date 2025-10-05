from logic.Scraper import Scraper
from selenium import webdriver
import json

def main(product_url):
  options = webdriver.ChromeOptions()
  options.add_argument("--headless=new")
  
  driver = webdriver.Chrome(options=options)
  
  try:
    scraper = Scraper("src/variables.json")
    
    print(f"Buscando dados de: {product_url}")
    
    html_content = scraper.get_html(product_url, driver)
    
    if html_content:
      product_data = scraper.scrape_amazon(html_content)
      
      if product_data:
        print(json.dumps(product_data, indent=2, ensure_ascii=False))
      else:
        print("Não foi possível extrair os dados do produto da página.")
    else:
      print("Falha ao obter o conteúdo HTML da página.")
  finally:
    print("\nFinalizando o processo e fechando o navegador...")
    driver.quit()
    
      
if __name__ == "__main__":
  main("https://www.amazon.com.br/Samsung-Imersiva-Traseira-Frontal-Android/dp/B0F3M62DY3")
  