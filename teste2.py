import requests
from bs4 import BeautifulSoup
import json
import logging
import time

# Aguarda 1 segundo


# Configuração do logging para acompanhar a execução
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Definindo headers customizados
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/115.0.0.0 Safari/537.36'
}

with open('editais_araquari.json', 'r' , encoding='utf-8') as file:
    editais = json.load(file)
print(editais[0]["link"])


def scrape_editais_pdf(base_url):
    """
    Realiza o scraping dos editais do campus Araquari.
    
    Retorna:
        Uma lista de dicionários com os dados de cada edital (título, link, data e resumo).
    """
    base_url = base_url

    
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
        edital = soup.find("div", class_="conteudo-generico")
        paragrafos = edital.find_all("p")

        
        links = edital.find_all("a") 

        # Filtra o <p> que contém um <a> com link para PDF
        pdf_link_a = None
        for a in links:
            if a and a["href"].endswith(".pdf"):
                pdf_link_a = a
                break  # Para no primeiro <p> encontrado com link de PDF

        if pdf_link_a:
            pdf_link = pdf_link_a["href"]
            titulo = pdf_link_a.text.strip()
            logging.info(f"Edital encontrado: {titulo} - {pdf_link}")
            return pdf_link
        else:
            logging.info("Nenhum link de PDF encontrado.")


        

link_editais = []

for edital in editais:
    pdf_link = scrape_editais_pdf(edital["link"])
    if pdf_link:
        link_editais.append({
            "titulo": edital["titulo"],
            "link": edital["link"],
            "pdf": pdf_link
        })

    else:
        print("Nenhum link de PDF encontrado especial.", edital["link"])
        with open("editais_error.txt", "a") as f:
            f.write(edital["link"] + "\n")
    time.sleep(0.7)


with open("editais_pdf.json", "w", encoding="utf-8") as file:
    json.dump(link_editais, file, ensure_ascii=False, indent=4)
