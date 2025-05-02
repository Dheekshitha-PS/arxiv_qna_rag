import datetime

import get_arxiv_files  # Script to fetch arxiv files metadata
import download_arxiv  # Script to download PDFs
import pdfconverter  # Script for PDF to markdown parsing and chunking
import os
from tqdm import tqdm
import chromadb
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5", local_files_only=True)
model = AutoModel.from_pretrained("BAAI/bge-base-en-v1.5", local_files_only=True)
def get_embedding(text):
    # Instruction format for better retrieval performance
    instruction = "Represent this paragraph from a research paper for retrieval: "
    inputs = tokenizer(instruction + text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings[0].tolist()

# Initialize the Chroma client
client = chromadb.PersistentClient(path="/app/chroma_storage")
paper_collection = client.get_or_create_collection(name="arxiv_chunks_emb")
# paper_collection = client.get_or_create_collection(name="test")

def test_collection():
    results = paper_collection.get()
    print("Query results:", len(results['ids']))

    print(paper_collection.count(),"COllection count")
    return paper_collection.count()
# Retrieve all documents (full text) stored in ChromaDB
def get_documents_from_chromadb():
    results = paper_collection.get()
    # print("Document count in the db",paper_collection.count())
    # print("Documents retrieved from chromadb",results.keys())
    return results

import os
# print("Inside Docker, after path exists:", os.path.exists("/app/chroma_storage"))
# Process each paper and extract sections
def store_sections_chromadb(paper_id, sections, title, abstract,published_date):

    i =0
    try:
        # Now pass the full_text of the paper to extract sections and chunk them

        # Iterate over the extracted sections and store the chunks in ChromaDB
        for section, content in sections.items():
            i +=1
            chunk_title = f"{section}"  # You can modify this as needed
            chunk_id = f"{paper_id}_section_{i}"  # Ensure unique ID for each chunk
            embedding= get_embedding(content[0])
            # Store each chunk in ChromaDB
            paper_collection.add(
                documents=[content[0]],  # Chunk content
                metadatas=[{
                    "arxiv_id": paper_id,
                    "title": title,
                    "abstract": abstract,
                    "section": section,
                    "published_date":published_date
                }],
                ids=[chunk_id],embeddings=embedding
            )
            # print(f"Stored chunk: {chunk_title}")
    except Exception as e:
        print(f"Error processing paper with ID {paper_id}: {e}")


# Main loop to retrieve documents and process them
def process_all_papers(categories,MAX_RESULTS):

    all_papers = get_arxiv_files.main(categories,MAX_RESULTS)[0]  # Returns a list of papers, each containing metadata like 'url', 'title', 'abstract'


    for paper in all_papers:
        sections = download_arxiv.download_pdfs(paper)


        # Retrieve paper metadata and full text from ChromaDB
        arxiv_id = paper['arxiv_id']

        title = paper['title']
        abstract = paper['summary']
        published_date= paper['published']

        store_sections_chromadb(arxiv_id, sections, title, abstract, published_date)
    return len(all_papers)

def process_uploaded_paper(path,session_id,filename,p,date):



    # Retrieve paper metadata and full text from ChromaDB
    arxiv_id = str(session_id)+'_'+str(p)

    title = filename
    abstract = ""

    sections = download_arxiv.load_pdfs(path,arxiv_id,title)

    store_uploaded_pdf_chunks(arxiv_id, sections, title,date,session_id)


    print(f"Chunked and stored  {filename}")

# def fetch_and_process_arxiv(arxiv_id,session_id):


def store_uploaded_pdf_chunks(paper_id, sections, title, upload_date,session_id):

    i =0
    try:


        # Iterate over the extracted chunks and store them in ChromaDB
        for chunk in sections:
            i +=1
            chunk_title = f"{title}"  # You can modify this as needed
            chunk_id = f"{paper_id}_section_{i}"  # Ensure unique ID for each chunk
            embedding= get_embedding(chunk)
            # Store each chunk in ChromaDB
            paper_collection.add(
                documents=[chunk],  # Chunk content
                metadatas=[{
                    "arxiv_id": chunk_id,
                    "title": title,

                    "section": "",
                    "published_date":upload_date,
                    "session_id":session_id
                }],
                ids=[chunk_id],embeddings=embedding
            )
            # print(f"Stored chunk: {chunk_title}")
    except Exception as e:
        print(f"Error processing paper with ID {paper_id}: {e}")
