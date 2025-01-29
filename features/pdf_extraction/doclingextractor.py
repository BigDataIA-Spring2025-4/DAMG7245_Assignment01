from pathlib import Path
import io, os
import pandas as pd
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
)
from tempfile import NamedTemporaryFile
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.document import ConversionResult
from fastapi import UploadFile

def docling_converter(file_upload: io.BytesIO):
    """
    Converts a PDF document to markdown format with additional options for OCR, table structure, and image generation.

    Args:
        file_upload (str or Path): The path to the PDF file to be converted.

    Returns:
        Path: The path to the generated markdown file.

    The function performs the following steps:
    1. Prepares pipeline options for the PDF conversion, including OCR, table structure, and image scaling.
    2. Initializes the DocumentConverter with the specified options.
    3. Converts the PDF file using the DocumentConverter.
    4. Specifies the output directory and file name for the markdown file.
    5. Saves the converted document as a markdown file with referenced images.

    Note:
        The function assumes that the necessary libraries and classes (PdfPipelineOptions, DocumentConverter, InputFormat, PdfFormatOption, ImageRefMode) are already imported and available in the scope.
    """
    # Prepare pipeline options
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.images_scale = 2.0
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    # Initialize the DocumentConverter
    doc_converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF, InputFormat.HTML],
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                # backend=PyPdfiumDocumentBackend(),
            ),
        },
        # image_mode=ImageRefMode.REFERENCED,
        # artifacts_dir="images/"
    )
    
    file_upload.seek(0)
    with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        # Write the PDF bytes to a temporary file
        temp_file.write(file_upload.read())
        temp_file.flush()
        conv_result = doc_converter.convert(temp_file.name)
        output_dir = Path(f"{conv_result.input.file.stem}.md")
        conv_result.document.save_as_markdown(output_dir, image_mode=ImageRefMode.REFERENCED)
        print(os.path.abspath(output_dir)) 
        
        # doc_filename = output_dir / f"{conv_result.input.file.stem}.md"
        
    # temp_file_path = temp_file.name
    # Convert the file
    #conv_result = doc_converter.convert(temp_file_path)

    # Specify the output directory and file name
    # output_dir = Path(f"frontend/temp/")
    # doc_filename = output_dir / f"{conv_result.input.file.stem}.md"
    # print(output_dir)

    # Save as markdown
    # conv_result.document.save_as_markdown(doc_filename, image_mode=ImageRefMode.REFERENCED, artifacts_dir="images/")
    #conv_result.document.export_to_markdown()

    return (output_dir)


