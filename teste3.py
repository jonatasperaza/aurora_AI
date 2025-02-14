from docling.document_converter import DocumentConverter
import json
import re

editais = []

def transformar(source, titulo):
    converter = DocumentConverter()
    result = converter.convert(source)
    arquivo = result.document.export_to_markdown()
    titulo_limpo = re.sub(r'[\/:*?"<>|]', '_', titulo)

    with open("arquivos/" + titulo_limpo + ".md", "w") as f:
        f.write(arquivo)



with open("editais_pdf.json", "r", encoding="utf-8") as file:
    editais = json.load(file)

for edital in editais:
    transformar(edital["pdf"], edital["titulo"])