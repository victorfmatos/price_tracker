from json import JSONDecodeError
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Any
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
from datetime import datetime
import requests
import json
import re
import random
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
  HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
  }
  def __init__(self, selectors_path: str = "src/variables.json") -> None:
    """Inicializa o Scraper carregando os seletores CSS de um arquivo JSON.

    Args:
        selectors_path (str, optional): Caminho para o arquivo JSON de seletores. Defaults to "src/variables.json".
    """
    self.selectors: dict[str, Any] = {}
    try:
      with open(selectors_path, "r", encoding="utf-8") as f:
        self.selectors = json.loads(f.read())
    except (FileNotFoundError, JSONDecodeError) as e:
      print(f"Erro ao carregar o arquivo de seletores: {e}.")
      
  @staticmethod
  def _extract_text(element: Tag | None = None) -> str | None:
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
  def _clean_price_string(price_string: str | None) -> float | None:
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
      
  def _get_html_content(self, url: str, driver: WebDriver | None = None) -> BeautifulSoup | None:
    """Busca o conteúdo HTML de uma URL usando Requests ou Selenium.

    Args:
        url (str): A URL da página a ser buscada.
        driver (WebDriver | None, optional): Instância opcional do WebDriver do Selenium. Defaults to None.

    Returns:
        BeautifulSoup | None: Um objeto BeautifulSoup ou None em caso de falha.
    """
    try:
      delay = random.uniform(2, 5)
      time.sleep(delay)
      if driver:
        driver.get(url)
        return BeautifulSoup(driver.page_source, "html.parser")
      response = requests.get(url, headers=self.HEADERS, timeout=10)
      response.raise_for_status()
      return BeautifulSoup(response.text, "html.parser")
    except RequestException as e:
      print(f"Erro ao buscar a URL {url} (Requests): {e}")
      return None
    except WebDriverException as e:
      print(f"Erro ao buscar a URL {url} (WebDriver): {e}")
      return None
    
  def scrape_generic_product(self, html_content: BeautifulSoup | None, selectors: dict[str, Any]) -> ProductData | None:
    """Extrai dados de um produto a partir do conteúdo HTML e seletores.

    Args:
        html_content (BeautifulSoup | None): Conteúdo HTML do produto.
        selectors (dict[str, Any]): Dicionário de seletores CSS.

    Returns:
        dict|None: Dicionário contendo os dados extraídos ou None em caso de falha.
    """
    try:
      if not html_content:
        return None
      
      collection_date = datetime.now().isoformat()
      title = self._extract_text(html_content.select_one(selectors["title"]))
      raw_real_price = self._clean_price_string(self._extract_text(html_content.select_one(selectors["real_price"])))
      raw_promotion_price = self._clean_price_string(self._extract_text(html_content.select_one(selectors["promotion_price"])))
      raw_average_rating = self._extract_text(html_content.select_one(selectors["average_rating"]))
      raw_ratings_quantity = self._extract_text(html_content.select_one(selectors["ratings_quantity"]))
      description = self._extract_text(html_content.select_one(selectors["description"]))

      
      # data: ProductData = {
      #   "collection_date": datetime.now().isoformat(),
      #   "title": self._extract_text(html_content.select_one(selectors["title"])),
      #   "real_price": self._clean_price_string(self._extract_text(html_content.select_one(selectors["real_price"]))),
      #   "promotion_price": self._clean_price_string(self._extract_text(html_content.select_one(selectors["promotion_price"]))),
      #   "average_rating": self._extract_text(html_content.select_one(selectors["average_rating"])),
      #   "ratings_quantity": self._extract_text(html_content.select_one(selectors["ratings_quantity"])),
      #   "description": self._extract_text(html_content.select_one(selectors["description"])),
      #   "specifications": {}
      # }
      
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

      data: ProductData = {
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

    except (KeyError, AttributeError) as e:
      print(f"Erro ao extrair dados do produto: {e}")
      return None
  
  def scrape_amazon(self, url: str, driver: WebDriver | None) -> ProductData | None:
    """Extrai dados de um produto da Amazon usando Selenium.

    Args:
        url (str): URL da página da Amazon.
        driver (WebDriver | None): Instância do WebDriver do Selenium.

    Returns:
        dict | None: Dicionário contendo os dados extraídos ou None em caso de falha.
    """
    html_content = self._get_html_content(url, driver)
    selectors = self.selectors.get("amazon", {})
    if not selectors:
      return None
    
    data = self.scrape_generic_product(html_content, selectors)
    
    if data is None:
      return None
    
    data["site"] = "Amazon"
    data["url"] = url
    return data

  def scrape_mercado_livre(self, url: str) -> ProductData | None:
    """Extrai dados de um produto do Mercado Livre usando Requests.

    Args:
        url (str): URL da página do Mercado Livre.

    Returns:
        dict | None: Dicionário contendo os dados extraídos ou None em caso de falha.
    """
    html_content = self._get_html_content(url)
    selectors = self.selectors.get("mercado_livre", {})
    if not selectors:
      return None
    
    data = self.scrape_generic_product(html_content, selectors)
    
    if data is None:
      return None
    
    data["site"] = "Mercado Livre"
    data["url"] = url
    return data
  