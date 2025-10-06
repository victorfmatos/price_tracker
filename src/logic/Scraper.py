import requests
import selenium
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup, Tag
import unicodedata
import re
from typing import TypedDict, Any
from datetime import datetime
import json
import random
import time

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
    except (FileNotFoundError, json.JSONDecodeError) as e:
      print(f"Erro ao carregar o arquivo de seletores: {e}.")
      
  @staticmethod
  def _extract_text(element: Tag | None = None) -> str | None:
    """Extrai o texto de um elemento BeautifulSoup, limpando espaços extras e acentos indesejados.

    Args:
        element (Tag | None, optional): Elemento BeautifulSoup a ser extraído. Defaults to None.

    Returns:
        str | None: Texto limpo ou None se o elemento for None.
    """
    if not element:
      return None
    text = unicodedata.normalize("NFKD", element.text.strip())
    return text.encode("ascii", "ignore").decode()
  
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
    
    match = re.search(r"\$?\s?[\d.,]+", price_string)
    if not match:
      return None
    
    price = match.group(0)
    cleaned_price = re.sub(r"[^\d,]+", "", price).replace(",", ".")
    try:
      return float(cleaned_price)
    except (ValueError, TypeError):
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
    except requests.RequestException as e:
      print(f"Erro ao buscar a URL {url} (Requests): {e}")
      return None
    except WebDriverException as e:
      print(f"Erro do WebDriver para {url}: {e}")
      return None
    
  def scrape_generic_product(self, html_content: BeautifulSoup | None, selectors: dict[str, Any]) -> dict|None:
    """Extrai dados de um produto a partir do conteúdo HTML e seletores.

    Args:
        html_content (BeautifulSoup | None): Conteúdo HTML do produto.
        selectors (dict[str, Any]): Dicionário de seletores CSS.

    Returns:
        dict|None: Dicionário contendo os dados extraídos ou None em caso de falha.
    """
    data: dict[str, Any]
    try:
      if not html_content:
        return None
      
      data = {
        "collection_date": datetime.now().isoformat(),
        "title": self._extract_text(html_content.select_one(selectors["title"])),
        "real_price": self._clean_price_string(self._extract_text(html_content.select_one(selectors["real_price"]))),
        "promotion_price": self._clean_price_string(self._extract_text(html_content.select_one(selectors["promotion_price"]))),
        "average_rating": self._extract_text(html_content.select_one(selectors["average_rating"])),
        "ratings_quantity": self._extract_text(html_content.select_one(selectors["ratings_quantity"])),
        "description": self._extract_text(html_content.select_one(selectors["description"])),
        "specifications": {}
      }
      
      if data["real_price"] is None and data["promotion_price"] is not None:
        data["real_price"] = data["promotion_price"]
        data["promotion_price"] = None
        
      if data["ratings_quantity"]:
        match = re.search(r"\d+", data["ratings_quantity"])
        data["ratings_quantity"] = int(match.group(0)) if match else None
        
      specifications_titles = html_content.select(selectors["specifications"][0])
      specifications_values = html_content.select(selectors["specifications"][1])

      data["specifications"] = {
        key: val
        for title, value in zip(specifications_titles, specifications_values)
        if (key := self._extract_text(title)) and (val := self._extract_text(value))
      }
          
      return data

    except (KeyError, AttributeError, TypeError) as e:
      print(f"Erro ao extrair dados do produto: {e}")
      return None
  
  def scraper_amazon(self, url: str, driver: WebDriver | None) -> dict | None:
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

  def scraper_mercado_livre(self, url: str) -> dict | None:
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
  