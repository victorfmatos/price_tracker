# Sistema de Inteligência de Mercado

Este projeto é uma ferramenta de web scraping e análise de dados construída em Python. Ele foi desenvolvido para demonstrar habilidades em automação, engenharia de software e análise de dados, com o objetivo de fornecer insights valiosos sobre o comportamento do consumidor e tendências de mercado.

A ferramenta é capaz de coletar dados de múltiplos sites de e-commerce e processá-los para gerar relatórios úteis, tudo isso através de uma interface de linha de comando flexível.

### Sumário

1. [Status do Projeto](#1-status-do-projeto)
2. [Funcionalidades](#2-funcionalidades)
3. [Tecnologias Utilizadas](#3-tecnologias-utilizadas)
4. [Autor](#4-autor)

## 1. Status do Projeto

- [x] Estrutura e Configuração
  - [x] Criação do Projeto.
  - [x] Configuração do Ambiente.
  - [x] Instalação das Bibliotecas.
- [ ] Construção da lógica principal de web scraping.
  - [ ] Criação do Scraper.
  - [ ] Tratamento de Erros.
- [ ] Persistência de dados.
  - [ ] Criação da lógica de Banco de Dados.
- [ ] Desenvolver Análise e Visualização de Dados.
  - [ ] Integração com Pandas.
  - [ ] Análise de Sentimento.
  - [ ] Geração de Gráficos.
- [ ] Automação e CLI.
  - [ ] Criação da CLI.
  - [ ] Implementação da Automação.
- [ ] Relatórios e Documentação.
  - [ ] Envio de E-mail.
  - [ ] Finalização do README.md

## 2. Funcionalidades

- **Coleta de Dados Robusta:** Extração de nome, preço, avaliação e descrição de produtos.
- **Interface de Linha de Comando (CLI):** Execução de tarefas específicas (`coleta`, `análise`, `relatório`) via linha de comando.
- **Análise de Dados:**
  - **Análise de Sentimento:** Classificação das avaliações dos consumidores.
  - **Identificação de Tendências:** Monitoramento da flutuação de preços ao longo do tempo.
- **Persistência de Dados:** Armazenamento dos dados em um banco de dados.
- **Automação:** Agendamento de coletas diárias ou semanais.
- **Relatórios Automatizados:** Geração e envio de relatórios por e-mail, contendo gráficos visuais.

## 3. Tecnologias Utilizadas

- Python 3.13.7
  - `requests`: Para requisições HTTP.
  - `selenium`: Para interagir com navegador.
  - `beautifulsoup4`: Para parsing de HTML.
  - `pandas`: Para manipulação e análise de dados.
  - `argparse`: Para construção da CLI.
  - `plotly`: Para visualização de dados.
  - `schedule`: Para automação de tarefas.
  - `NLTK`: Para análise de sentimento.
  - `sqlite3`: Para utilização de banco de dados.
  - `smtplib`: Para envio por email.

## 4. Autor

### Victor Freitas Matos

- LinkedIn: [http://www.linkedin.com/in/victorfmatos](https://www.linkedin.com/in/victorfmatos)
- GitHub: [https://github.com/victorfmatos](https://github.com/victorfmatos)
