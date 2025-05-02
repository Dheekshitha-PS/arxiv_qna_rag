from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

# Wrap your embedder
# embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")


CACHE_DIR = "/app/.cache/huggingface"




# Wrap your ChromaDB (already created)
import chromadb

_vector_store = None
_index = None
client = chromadb.PersistentClient(path="/app/chroma_storage")
chroma_collection = client.get_or_create_collection(name="arxiv_chunks_emb")

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    return _vector_store

def get_index():

    global _index
    if _index is None:

        embed_model    = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5",   cache_folder=CACHE_DIR)
        Settings.embed_model =embed_model
        _index = VectorStoreIndex.from_vector_store(get_vector_store(),embed_model=embed_model)
    return _index

def delete_session(session_id):

    chroma_collection.delete(where = {"session_id": session_id})

