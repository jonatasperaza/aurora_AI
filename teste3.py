from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)

from docling.datamodel.settings import settings
import json
import re

editais = []

accelerator_options = AcceleratorOptions(
    num_threads=8, device=AcceleratorDevice.AUTO
)

pipeline_options = PdfPipelineOptions()
pipeline_options.accelerator_options = accelerator_options
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.do_cell_matching = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)

    # Enable the profiling to measure the time spent
settings.debug.profile_pipeline_timings = True

def transformar(source, titulo):
        print(source)
        print(titulo)
        converter = DocumentConverter()
        result = converter.convert(source)
        arquivo = result.document.export_to_markdown()
        titulo_limpo = re.sub(r'[\/:*?"<>|]', '_', titulo)

        with open("arquivos/" + titulo_limpo + ".md", "w", encoding="utf-8") as f:
            f.write(arquivo)



with open("editais_pdf.json", "r", encoding="utf-8") as file:
    editais = json.load(file)
    
print(len(editais))

for edital in editais:
    transformar(edital["pdf"], edital["titulo"])