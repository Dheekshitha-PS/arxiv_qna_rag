from langchain_community.chat_models import ChatOpenAI
import chroma_wrap
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# from langchain_ollama import OllamaLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings


from dotenv import load_dotenv
import os
import openai
from pathlib import Path

# Load environment variables from the .env file
# Load env manually
env_path = Path(__file__).parent.parent / '.env'  # One level up from app/
load_dotenv(dotenv_path=env_path)



# Get OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# llm = OllamaLLM(model="mistral", base_url="http://host.docker.internal:11434")
# print("Imported Chroma wrap")
# Prompt for Chain-of-Thought RAG
prompt_template = PromptTemplate.from_template("""
You are a scientific reasoning assistant.
Your task is to answer the given question strictly using only the context provided below.
Follow the reasoning steps outlined below and make sure to cite your sources clearly.

##Important Rules:

Do not use any prior knowledge or information outside the context given to you.

If the answer is not found in the context, respond:
"I don't know based on the given papers."

## Step-by-Step Instructions:

Read the question and understand what it's asking.

Scan the context given to you to identify relevant sections that may contain the answer.

Extract evidence supporting the answer from those sections only.

Formulate a concise and accurate response, clearly stating your reasoning.

Include citations only for the source materials used based on the chunks provided to you. Do not use your knoweldege to 
answer the question. Provide the answer in a valid JSON format.


~Question:~

{question}

~Context:~
{context}

## Output format
Give me a valid JSON format with the following information.

~Answer:~

Your answer to the user's question. Give a detailed response

~Source used:~

What are the chunks used from the source chunks provided to you

~Confirmation~

Did you really use the chunks provided to you to generate the response. Yes or No


""")

# Wrap OpenAI LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.2,openai_api_key=openai.api_key)


Settings.llm = llm

# Wrap in a LangChain
# llm_chain = LLMChain(llm=llm, prompt=prompt_template)
llm_chain = prompt_template | llm

def answer_query(question: str):
    # Retrieve the index and prepare the query engine


    index = chroma_wrap.get_index()

    # query_engine = index.as_query_engine(similarity_top_k=5)
    # llama_response = query_engine.query(question)
    # print("QUERY ENGINE RESPONSE")
    #
    # print(llama_response)
    # # Extract relevant source nodes
    # nodes = llama_response.source_nodes
    retriever = index.as_retriever(similarity_top_k=5)
    nodes = retriever.retrieve(question)
    # for i, node in enumerate(nodes):
    #     print(f"\n--- Chunk {i + 1} ---\n{node.text}")
    # This is where you print the citation details
    print("Citations of retrieved papers:")
    for node in nodes:
        meta = node.node.metadata  # access metadata dictionary
        print(f"- {meta.get('arxiv_id')} | {meta.get('title')} | {meta.get('published_date')}")

    # Extract content from nodes to form the context for the model
    context = "\n\n".join([n.node.get_content() for n in nodes])
    # print(context)
    # Prepare the final answer with LangChain
    final_answer = llm_chain.invoke({
        "question": question,
        "context": context
    })

    # You can also append citations to the final answer if desired
    # citations = "\n".join([f"- {node.node.metadata.get('arxiv_id')} | {node.node.metadata.get('title')} | {node.node.metadata.get('published_date')}" for node in nodes])
    # final_answer += "\n\nCitations:\n" + citations

    print("And the final answer from LLM is: ")
    print(final_answer)
    return final_answer
