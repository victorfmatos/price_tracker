import sqlite3
from dotenv import load_dotenv
import json
import os


class DatabaseManager:
  def __init__(self) -> None:
    self.connection: sqlite3.Connection
    
  def connect(self) -> sqlite3.Connection:
    load_dotenv()
    db_name = os.environ.get("DATABASE_NAME")
    if not db_name:
      raise ValueError("O nome do banco de dados não foi definido no arquivo .env.")
    self.connection = sqlite3.connect(db_name)
    
    print("Conexão com o banco de dados estabelecida.")
    return self.connection
    
    
  def create_table(self) -> None:
    if not self.connection:
      print("Erro: Nenhuma conexão com o banco de dados.")
      return
    
    cursor = self.connection.cursor()
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS product_data (
        id SERIAL PRIMARY KEY,
        collection_date TIMESTAMP NOT NULL,
        title VARCHAR(255) NOT NULL,
        real_price NUMERIC(10,2) NOT NULL,
        promotion_price NUMERIC(10,2),
        average_rating NUMERIC(3,1),
        ratings_quantity INTEGER,
        description TEXT,
        specifications JSONB,
        site VARCHAR(50) NOT NULL,
        url TEXT NOT NULL
      );
    """)
    self.connection.commit()
    print("Tabela 'product_data' criada com sucesso.")
    
    
  def get_data(self) -> list[str]:
    cursor = self.connection.cursor()
    cursor.execute("SELECT * FROM product_data")
    return cursor.fetchall()
      
  def insert_data(self, data: dict[str, str]) -> None:
    if not self.connection:
      print("Erro: Nenhuma conexão com o banco de dados.")
      return
    
    sql = """
      INSERT INTO product_data (
        collection_date, title, real_price, promotion_price, average_rating, ratings_quantity, description, specifications, site, url
      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor = self.connection.cursor()
    data["specifications"] = json.dumps(data.get("specifications"))
    cursor.execute(sql, [*data.values()])
    self.connection.commit()
    print(f"Dados do produto '{data.get("title")}' inseridos com sucesso.")


  def drop_table(self) -> None:
    if not self.connection:
      print("Erro: Nenhuma conexão com o banco de dados.")
      return
    
    cursor = self.connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS product_data")
    self.connection.commit()
    print("Tabela 'product_data' excluída com sucesso.")
      
  def close_connection(self) -> None:
    if self.connection:
      self.connection.close()
      print("Conexão com o banco de dados fechada.")