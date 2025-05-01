import json

from fastapi import FastAPI, Query
from prompt_template import answer_query
from create_chunks import process_all_papers

app = FastAPI()

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
