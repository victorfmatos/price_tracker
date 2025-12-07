# type: ignore
from logic.Scraper import Scraper
from selenium import webdriver

def main(product_url):
  options = webdriver.ChromeOptions()
  options.add_argument("--headless=new")
  
  driver = webdriver.Chrome(options=options)
  
  try:
    scraper = Scraper("src/variables.json")
    
    print(f"Buscando dados de: {product_url}")
        
    product_data = scraper.scrape_mercado_livre(product_url)
    
    if product_data:
      return product_data
    else:
      print("Não foi possível extrair os dados do produto da página.")
      return None
  finally:
    print("\nFinalizando o processo e fechando o navegador...")
    driver.quit()
    
      
if __name__ == "__main__":
  data = main("https://www.mercadolivre.com.br/samsung-galaxy-a05s-128gb-dual-sim-tela-infinita-de-67-cor-prata-6gb-ram/p/MLB37699141")
  print(data)
