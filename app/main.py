import json

from fastapi import FastAPI, Query,UploadFile, File, Form
from prompt_template import answer_query
from create_chunks import process_all_papers, process_uploaded_paper
from typing import List
import shutil, os
from uuid import uuid4
import uuid
from datetime import date
import chroma_wrap
app = FastAPI()
session_store = {}
active_sessions = set()

@app.get("/")
def read_root():
    return {"message": "Welcome to the arXiv Q&A system!"}

@app.get("/ask")
def ask(question: str = Query(description="Question to ask the system")):
    try:
        answer = answer_query(question)
        print("And the final answer from LLM is: ")

        print(answer.keys())


        final_dict= {"question": question,"answer":answer}



        return final_dict
    except Exception as e:
        return {"error": str(e)}

@app.get("/getpapers")
def  downloadpapers(categories, MAX_RESULTS):


    try:
        paper_count= process_all_papers(json.loads(categories), MAX_RESULTS)
        return {paper_count, ' papers are chunked and stored in chromadb'}
    except Exception as e:
        return {"error": str(e)}

# from utils import process_pdf, fetch_and_process_arxiv  # You'll create these

UPLOAD_ROOT = "uploaded_pdfs/"

@app.post("/upload/")
async def upload_pdfs(files: List[UploadFile] = File(...)):


    session_id = str(uuid.uuid4())
    global session_store
    session_store['session_id'] = session_id
    active_sessions.add(session_id)

    session_dir = os.path.join(UPLOAD_ROOT, session_id)
    os.makedirs(session_dir, exist_ok=True)
    upload_date = date.today()
    format_string = '%Y-%m-%d'
    upload_date=  upload_date.strftime(format_string)
    saved_paths = []
    filenames=[]
    for file in files:
        file_path = os.path.join(session_dir, file.filename)
        filename= file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(file_path)
        filenames.append(filename)
    session_store['filenames'] =filenames
    for p in range(len(saved_paths)):
        process_uploaded_paper(saved_paths[p], session_id=session_id,filename= filenames[p],p=p,date=upload_date)

    return {"message": f"Processed {len(saved_paths)} file(s)", "session_id": session_id,"filenames uploaded":filenames}



@app.post("/askPDF/")
async def ask_pdf(

    question: str = Form(...)
):
    global session_store
    meta_filter=   {"session_id": session_store['session_id'], "title": session_store['filenames']}


    answer = answer_query(question,meta_filter)
    print("And the final answer from LLM is: ")

    print(answer)

    final_dict = {"question": question, "answer": answer}

    return final_dict

@app.post("/close_session")
def close_session(session_id: str):
    try:
        chroma_wrap.delete_session(session_id)
        return {"message": f"Session {session_id} closed and data deleted."}
    except Exception as e:
        print(f"Error deleting papers in  {session_id}: {e}")

@app.on_event("shutdown")
def shutdown_event():
    chroma_wrap.delete_session(active_sessions['session_id)'])
