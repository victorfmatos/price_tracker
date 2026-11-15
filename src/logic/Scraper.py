from json import JSONDecodeError
from bs4 import BeautifulSoup
from typing import TypedDict
from datetime import datetime
import random
import json
import re
import time

class ProductData(TypedDict, total=False):
  collection_date: str
  title: str | None
  real_price: float | None
  promotion_price: float | None
  average_rating: float | None
  ratings_quantity: int | None
  description: str | None
  specifications: dict[str, str]
  site: str
  url: str

class Scraper:
  """Realiza a extração de dados de produtos de páginas web."""
  def __init__(self, selectors_path = "src/variables.json"):
    """Inicializa o Scraper carregando os seletores CSS de um arquivo JSON.

    Args:
        selectors_path (str, optional): Caminho para o arquivo JSON de seletores. Defaults to "src/variables.json".
    """
    
    self.selectors = {}
    try:
      with open(selectors_path, "r", encoding="utf-8") as f:
        self.selectors = json.loads(f.read())
    except (FileNotFoundError, JSONDecodeError) as e:
      print(f"Erro ao carregar o arquivo de seletores: {e}.")
      
  @staticmethod
  def _extract_text(element):
    """Extrai o texto de um elemento BeautifulSoup, limpando espaços extras.

    Args:
        element (Tag | None, optional): Elemento BeautifulSoup a ser extraído. Defaults to None.

    Returns:
        str | None: Texto limpo ou None se o elemento for None.
    """
    if not element:
      return None
    return " ".join(element.text.split())
  
  @staticmethod
  def _clean_price_string(price_string):
    """Limpa uma string de preços para extrair o valor numérico.

    Args:
        price_string (str | None): Preço a ser limpo.

    Returns:
        float | None: Número limpo ou None se a string for None.
    """
    if not price_string:
      return None
    
    match = re.search(r"[\d]+(?:[.,]\d+)*", price_string)
    if not match:
      return None
    
    clean_str = match.group(0)
    
    if ',' in clean_str and '.' in clean_str:
      if clean_str.find(',') > clean_str.find('.'):
        clean_str = clean_str.replace('.', '').replace(',', '.')
      else:
        clean_str = clean_str.replace(',', '')
    
    elif ',' in clean_str:
      clean_str = clean_str.replace(',', '.')
      
    elif '.' in clean_str:
      parts = clean_str.split('.')
      if len(parts) > 1 and len(parts[-1]) == 3 and len(parts) == 2:
        clean_str = clean_str.replace('.', '')
    
    try:
      return float(clean_str)
    except ValueError:
      return None
      
  def _get_json_ld_data_and_html_content(self, url, driver):
    time.sleep(random.uniform(4.0, 9.0))
    
    driver.goto(url, wait_until="domcontentloaded", timeout=30000)
    
    driver.mouse.wheel(0, random.randint(300, 700))
    time.sleep(random.uniform(0.8, 1.8))
    
    html_content = BeautifulSoup(driver.content(), "html.parser")
    
    
    return html_content
    
  def scrape_generic_product(self, page_url, driver):
    
    html_content = self._get_json_ld_data_and_html_content(page_url, driver)
    
    selectors = self.selectors["mercado_livre"]
    
    collection_date = datetime.now().isoformat()
    title = self._extract_text(html_content.select_one(selectors["title"]))
    raw_real_price = self._clean_price_string(self._extract_text(html_content.select_one(selectors["real_price"])))
    raw_promotion_price = self._clean_price_string(self._extract_text(html_content.select_one(selectors["promotion_price"])))
    raw_average_rating = self._extract_text(html_content.select_one(selectors["average_rating"]))
    raw_ratings_quantity = self._extract_text(html_content.select_one(selectors["ratings_quantity"]))
    description = self._extract_text(html_content.select_one(selectors["description"]))
    
    print(raw_real_price, raw_promotion_price)
    
    if raw_real_price is None and raw_promotion_price is not None:
      real_price = raw_promotion_price
      promotion_price = None
    else: 
      real_price = raw_real_price
      promotion_price = raw_promotion_price
      
    average_rating = float(raw_average_rating.replace(',', '.')) if raw_average_rating else None

    ratings_quantity = None
    if raw_ratings_quantity:
      match = re.search(r"\d+", raw_ratings_quantity)
      if match:
        ratings_quantity = int(match.group(0))

    data = {
      "collection_date": collection_date,
      "title": title,
      "real_price": real_price,
      "promotion_price": promotion_price,
      "average_rating": average_rating,
      "ratings_quantity": ratings_quantity,
      "description": description,
    }
      
    specifications_titles = html_content.select(selectors["specifications"][0])
    specifications_titles = specifications_titles if specifications_titles else []
    specifications_values = html_content.select(selectors["specifications"][1])
    specifications_values = specifications_values if specifications_values else []

    data["specifications"] = {
      key: val
      for title, value in zip(specifications_titles, specifications_values)
      if (key := self._extract_text(title)) and (val := self._extract_text(value))
    }
    
    return data
  