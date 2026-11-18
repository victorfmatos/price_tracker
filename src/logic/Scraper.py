from bs4 import BeautifulSoup, Tag
from pathlib import Path
from playwright.sync_api import Page
from json import JSONDecodeError
from typing import TypedDict
from datetime import datetime
import random
import json
import re


class ProductData(TypedDict):
  collection_date: str
  title: str
  real_price: float
  promotion_price: float
  average_rating: float
  ratings_quantity: int
  description: str
  specifications: dict[str, str]

class Scraper:
  """Realiza a extração de dados de produtos de páginas web."""
  def __init__(self, selectors_path: Path) -> None:
    """Inicializa o Scraper carregando os seletores CSS de um arquivo JSON.

    Args:
        selectors_path (str): Caminho para o arquivo JSON de seletores.
    """
    
    self.selectors = {}
    try:
      with open(selectors_path, "r", encoding="utf-8") as f:
        self.selectors = json.load(f)
    except (FileNotFoundError, JSONDecodeError) as e:
      raise RuntimeError(f"Erro ao carregar os seletores do arquivo '{selectors_path}': {e}")
      
  @staticmethod
  def _extract_text(element: Tag | None) -> str:
    """Extrai o texto de um elemento BeautifulSoup, limpando espaços extras.

    Args:
        element (Tag | None): Elemento BeautifulSoup a ser extraído.

    Returns:
        str: Texto limpo ou vazio se o elemento for None.
    """
    if not element:
      return ""
    return " ".join(element.text.strip().split())
  
  @staticmethod
  def _clean_price_string(price_string: str) -> float:
    """Limpa uma string de preços para extrair o valor numérico.

    Args:
        price_string (str): Preço a ser limpo.

    Returns:
        float: Número limpo ou 0.0 se a string for inválida.
    """
    
    match = re.search(r"[\d]+(?:[.,]\d+)*", price_string)
    if not match:
      return 0.0
    
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
      if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
          clean_str = clean_str.replace('.', '')    
    try:
      return float(clean_str)
    except ValueError:
      raise ValueError(f"Não foi possível converter a string de preço '{price_string}' para float.")

  @staticmethod
  def _extract_first_match(soup: BeautifulSoup, selector_list: list[str]) -> str:
    for selector in selector_list:
      element = soup.select_one(selector)
      if element and (text := Scraper._extract_text(element)):
        return text
    return ""
      
  @staticmethod
  def _get_html_content(url: str, page: Page) -> BeautifulSoup:
    page.wait_for_timeout(random.uniform(4000, 9000))
    
    page.goto(url, wait_until="load", timeout=30000)
    
    page.mouse.wheel(0, random.randint(300, 700))
    page.wait_for_timeout(random.uniform(800, 1800))
    
    page.wait_for_load_state("load")
    
    return BeautifulSoup(page.content(), "html.parser")
    
  def scrape_generic_product(self, page_url: str, page: Page) -> ProductData:
    
    html_content = self._get_html_content(page_url, page)
    
    selectors = self.selectors["mercado_livre"]["selectors"]
    
    collection_date = datetime.now().isoformat()
    title = self._extract_first_match(html_content, selectors["title"])
    raw_real_price = self._clean_price_string(self._extract_first_match(html_content, selectors["real_price"]))
    raw_promotion_price = self._clean_price_string(self._extract_first_match(html_content, selectors["promotion_price"]))
    raw_average_rating = self._extract_first_match(html_content, selectors["average_rating"])
    raw_ratings_quantity = self._extract_first_match(html_content, selectors["ratings_quantity"])
    description = self._extract_first_match(html_content, selectors["description"])
        
    if raw_real_price == 0.0 and raw_promotion_price > 0.0:
      real_price = raw_promotion_price
      promotion_price = 0.0
    else: 
      real_price = raw_real_price
      promotion_price = raw_promotion_price
      
    average_rating = 0.0
    if raw_average_rating:
      rating_match = re.search(r"\d+(?:[.,]\d+)?", raw_average_rating)
      if rating_match:
        average_rating = float(rating_match.group(0).replace(",", "."))

    ratings_quantity = 0
    if raw_ratings_quantity:
      match = re.search(r"\d+", raw_ratings_quantity)
      if match:
        ratings_quantity = int(match.group(0))
      
    specifications_titles: list[Tag] = html_content.select(selectors["specifications"][0]) or []
    specifications_values: list[Tag] = html_content.select(selectors["specifications"][1]) or []

    specifications: dict[str, str] = {
      key: val
      for spec_title, spec_value in zip(specifications_titles, specifications_values)
      if (key := self._extract_text(spec_title)) and (val := self._extract_text(spec_value))
    }
    
    data: ProductData = {
      "collection_date": collection_date,
      "title": title,
      "real_price": real_price,
      "promotion_price": promotion_price,
      "average_rating": average_rating,
      "ratings_quantity": ratings_quantity,
      "description": description,
      "specifications": specifications
    }
    
    return data
  