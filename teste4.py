from pathlib import Path
import json
from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, PdfFormatOption

editais = []
with open("editais_pdf.json", "r", encoding="utf-8") as file:
    editais = json.load(file)

def main(source, titulo):
    try:
        input_doc = source

        # Explicitly set the accelerator
        # accelerator_options = AcceleratorOptions(
        #     num_threads=8, device=AcceleratorDevice.AUTO
        # )
        accelerator_options = AcceleratorOptions(
            num_threads=8, device=AcceleratorDevice.AUTO
        )
        # accelerator_options = AcceleratorOptions(
        #     num_threads=8, device=AcceleratorDevice.MPS
        # )
        # accelerator_options = AcceleratorOptions(
        #     num_threads=8, device=AcceleratorDevice.CUDA
        # )

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

        # Convert the document
        conversion_result = converter.convert(input_doc)
        doc = conversion_result.document

        # List with total time per document
        doc_conversion_secs = conversion_result.timings["pipeline_total"].times

        md = doc.export_to_markdown()
        
        # Salvar o resultado em um arquivo
        output_file = f"resultado_{titulo.replace(' ', '_')}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md)
            
        print(f"Arquivo salvo como: {output_file}")
        print(f"Conversion secs: {doc_conversion_secs}")
    except Exception as e:
        print(f"Erro ao processar {titulo}: {str(e)}")

if __name__ == "__main__":
    try:
        for edital in editais:
            main(edital.get("url"), edital.get("titulo"))
    except Exception as e:
        print(f"Erro ao processar editais: {str(e)}")