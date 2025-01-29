from fastapi import FastAPI, UploadFile, Form, File
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
# import boto3
import os
from features.web_extraction.datascraper import WikiSpider, scrape_url 
from fastapi.responses import JSONResponse, FileResponse
from features.pdf_extraction.doclingextractor import pdf_docling_converter
from features.pdf_extraction.os_pdf_extraction import pdf_os_converter

from io import BytesIO

from datetime import datetime

import base64

# from services import s3
from services.s3 import S3FileManager

app = FastAPI()

AWS_BUCKET_NAME = "pdfparserdataset"
class URLInput(BaseModel):
    url: str
class PdfInput(BaseModel):
    file: str
    file_name: str

@app.post("/scrape-url")
def process_url(url_input: URLInput):
    response = requests.get(url_input.url)
    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text()
    # markdown_content = markdown.markdown(text)
    result = scrape_url(url_input.url)  # Scrape the URL
    file_name = "scraped_url.md"
    # upload_to_s3(file_name, result)

    return {
        "message": f"File {file_name} ",
        "scraped_content": result  # Include the original scraped content in the response
    }

@app.post("/open-source-scrape-url/")
def process_os_url(url_input: URLInput):
    response = requests.get(url_input.url)
    soup = BeautifulSoup(response.content, "html.parser")
    input_html_path = f"temp_{soup.title.string}.html"
    with open(input_html_path, "wb") as f:
        f.write(soup.prettify("utf-8"))
    markdown_file_path = pdf_docling_converter(input_html_path)
    return FileResponse(markdown_file_path, media_type="text/markdown", filename="data_ex.md")
    
    
@app.post("/docling-scrape-url/")
def process_docling_url(url_input: URLInput):
    markdown_file_path = pdf_docling_converter(url_input)
    return FileResponse(markdown_file_path, media_type="text/markdown", filename="data_ex.md")

@app.post("/scrape_pdf_os")
def process_pdf_os(uploaded_pdf: PdfInput):
    pdf_content = base64.b64decode(uploaded_pdf.file)
    # Convert pdf_content to a BytesIO stream for pymupdf
    pdf_stream = BytesIO(pdf_content)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    base_path = f"pdf/os/{uploaded_pdf.file_name.replace('.','').replace(' ','')}_{timestamp}/"
    s3_obj = S3FileManager(AWS_BUCKET_NAME, base_path)
    s3_obj.upload_file(AWS_BUCKET_NAME, f"{s3_obj.base_path}/{uploaded_pdf.file_name}", pdf_content)
    file_name, result = pdf_os_converter(pdf_stream, base_path, s3_obj)
    return {
        "message": f"File {file_name} ",
        "scraped_content": result  # Include the original scraped content in the response
    }

@app.post("/scrape_pdf_docling")
def process_pdf_docling(uploaded_pdf: PdfInput):
    pdf_content = base64.b64decode(uploaded_pdf.file)
    # Convert pdf_content to a BytesIO stream for pymupdf
    pdf_stream = BytesIO(pdf_content)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    base_path = f"pdf/docling/{uploaded_pdf.file_name.replace('.','').replace(' ','')}_{timestamp}/"
    s3_obj = S3FileManager(AWS_BUCKET_NAME, base_path)
    s3_obj.upload_file(AWS_BUCKET_NAME, f"{s3_obj.base_path}/{uploaded_pdf.file_name}", pdf_content)
    file_name, result = pdf_docling_converter(pdf_stream, base_path, s3_obj)
    return {
        "message": f"File {file_name} ",
        "scraped_content": result  # Include the original scraped content in the response
    }
    
    # input_pdf_path = f"temp_{file.filename}"
    # pdf_stream = await file.read()
    # # with open(input_pdf_path, "wb") as f:
    # #     f.write(await file.read())
    # markdown_file_path = docling_converter(io.BytesIO(pdf_stream))
    # print(markdown_file_path)
    # # os.remove(input_pdf_path)
    # return FileResponse(markdown_file_path, media_type="text/markdown", filename="data_ex.md")

# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

