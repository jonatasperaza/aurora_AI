import requests
from bs4 import BeautifulSoup
import json
import csv
import logging

# Configuração do logging para acompanhar a execução
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Definindo headers customizados
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/115.0.0.0 Safari/537.36'
}

def scrape_editais_araquari():
    """
    Realiza o scraping dos editais do campus Araquari.
    
    Retorna:
        Uma lista de dicionários com os dados de cada edital (título, link, data e resumo).
    """
    base_url = "https://editais.ifc.edu.br/category/campus-araquari/"
    editais = []
    
    # Utiliza uma sessão para reaproveitar conexões
    session = requests.Session()
    session.headers.update(HEADERS)

    while base_url:
        try:
            response = session.get(base_url, timeout=10)
            response.raise_for_status()  # Levanta exceção para erros HTTP
        except requests.RequestException as e:
            logging.error(f"Erro ao acessar {base_url}: {e}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')

        # Busca pela seção de posts
        posts_section = soup.find('section', class_='posts')
        if not posts_section:
            logging.info("Seção de posts não encontrada nesta página.")
            break

        # Busca pelos posts dentro de <a class="noticia">
        posts = posts_section.find_all('a', class_='noticia')
        logging.info(f"Número de posts encontrados: {len(posts)}")
        if not posts:
            logging.info("Nenhum post encontrado nesta página.")
            break

        for post in posts:
            link = post.get('href', 'Sem link')
            
            # Extrai o título do elemento <div class="noticia__titulo">
            title_div = post.find('div', class_='noticia__titulo')
            title = title_div.get_text(strip=True) if title_div else 'Sem título'
            
            # Extrai a data do elemento <div class="noticia__data">
            date_div = post.find('div', class_='noticia__data')
            date = date_div.get_text(strip=True) if date_div else 'Sem data'
            
            # Extrai o resumo do elemento <div class="noticia__excerpt">
            excerpt_div = post.find('div', class_='noticia__excerpt')
            excerpt = excerpt_div.get_text(strip=True) if excerpt_div else 'Sem resumo'
            
            editais.append({
                'titulo': title,
                'link': link,
                'data': date,
                'resumo': excerpt
            })

        # Paginação: busca pelo link com classe 'next'
        next_page_tag = soup.find('a', class_='next')
        base_url = next_page_tag.get('href') if next_page_tag and next_page_tag.get('href') else None

    return editais

def save_to_json(data, filename="editais.json"):
    try:
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Dados salvos com sucesso em '{filename}'.")
    except IOError as e:
        logging.error(f"Erro ao salvar o arquivo JSON: {e}")

def save_to_csv(data, filename="editais.csv"):
    try:
        with open(filename, "w", newline='', encoding='utf-8') as csvfile:
            fieldnames = ['titulo', 'link', 'data', 'resumo']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        logging.info(f"Dados salvos com sucesso em '{filename}'.")
    except IOError as e:
        logging.error(f"Erro ao salvar o arquivo CSV: {e}")


editais_araquari = scrape_editais_araquari()
save_to_json(editais_araquari, "editais_araquari.json")
