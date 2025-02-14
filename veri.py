
import json


with open('editais_pdf.json', 'r' , encoding='utf-8') as file:
    editais = json.load(file)
print(len(editais))