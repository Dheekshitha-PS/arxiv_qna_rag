import requests
import fitz  # PyMuPDF
import os
import chromadb
from tqdm import tqdm
import get_arxiv_files
import pdfconverter
# Setup Chroma
# client = chromadb.PersistentClient()
# # client.delete_collection("arxiv_papers")  # Delete existing collection
# collection = client.get_or_create_collection(name="arxiv_papers")





def download_pdf(url, folder="pdfs"):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    pdf_path = os.path.join(folder, url.split("/")[-1])
    with open(pdf_path, "wb") as f:
        f.write(response.content)
    return pdf_path


def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def download_pdfs(paper):
    # Main pipeline

    url =paper['pdf_url']
    title= paper["title"]
    authors= ", ".join(paper["authors"])
    published= paper["published"]
    category =paper['category']
    summary =paper['summary']

    try:
        pdf_path = download_pdf(url)

        sections = pdfconverter.extract_sections_from_markdown(pdf_path, title, summary,category,published)
        return sections

    except Exception as e:
        print(f"Failed for {url}: {e}")
