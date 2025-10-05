from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json
import re


class Scraper:
  HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
  }
  def __init__(self, selectors_path="src/variables.json"):
    try:
      with open(selectors_path, "r", encoding="utf-8") as f:
        self.selectors = json.loads(f.read())
    except FileNotFoundError:
      print(f"Erro: O arquivo de seletores '{selectors_path}' não foi encontrado.")
      self.selectors = {}
    except json.JSONDecodeError:
      print(f"Erro: O arquivo '{selectors_path}' não é um JSON válido.")
      self.selectors = {}
  
  @staticmethod
  def extract_text(element=None):    
    if not element:
      return None
    return " ".join(element.text.split())
  
  @staticmethod
  def clean_price_string(price_string):
    if not price_string:
      return None

    match = re.search(r"[\d.,]+", price_string)
    if not match:
      return None
    
    price = match.group(0)
    cleaned_price = price.replace(".", "").replace(",", ".")
    
    try:
      return float(cleaned_price)
    except ValueError:
      return None

  def get_html(self, url, driver=None):
    try:
      if driver:
        driver.get(url)
        return BeautifulSoup(driver.page_source, "html.parser")
      response = requests.get(url, headers=self.HEADERS, timeout=10)
      response.raise_for_status()
      return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
      print(f"Erro ao buscar a URL {url}: {e}")
      return None
  
  def scrape_generic_product(self, html_content, selectors):
    try:
      if not html_content or not selectors:
        return None

      product_data = {
        "collection_date": datetime.now().isoformat(),
        "title": self.extract_text(html_content.select_one(selectors["title"])),
        "promotion_price": self.clean_price_string(self.extract_text(html_content.select_one(selectors["promotion_price"]))),
        "real_price": self.clean_price_string(self.extract_text(html_content.select_one(selectors["real_price"]))),
        "average_rating": self.extract_text(html_content.select_one(selectors["average_rating"])),
        "ratings_quantity": self.extract_text(html_content.select_one(selectors["ratings_quantity"])),
        "description": self.extract_text(html_content.select_one(selectors["description"])),
        "specifications": {}
      }
      
      if product_data["real_price"] is None:
        product_data["real_price"] = product_data["promotion_price"]
        product_data["promotion_price"] = None
      
      if product_data["ratings_quantity"]:
        match = re.search(r"\d+", product_data["ratings_quantity"])
        product_data["ratings_quantity"] = int(match.group(0)) if match else None
        
      specifications_titles = html_content.select(selectors["specifications"][0])
      specifications_values = html_content.select(selectors["specifications"][1])
      product_data["specifications"] = {
        self.extract_text(element=title): self.extract_text(element=value)
        for title, value in zip(specifications_titles, specifications_values)
      }
      
      return product_data
      
        
    except Exception as e:
      print(e)
  
  def scrape_amazon(self, html_content):
    selectors = self.selectors.get("amazon", {})
    return self.scrape_generic_product(html_content, selectors)
  
  def scrape_mercadolivre(self, html_content):
    selectors = self.selectors.get("mercado_livre", {})
    return self.scrape_generic_product(html_content, selectors)
    