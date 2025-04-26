import chromadb
print(chromadb.__version__)
# Force duckdb storage (avoid FAISS)
# client = chromadb.PersistentClient(path="F:/NLP/arxivQnA/chroma_storage")
client = chromadb.PersistentClient(path="/app/chroma_storage")
# Now interact with the collection
# collection = client.get_collection(name="arxiv_papers")
# print(collection.count())
collection = client.get_collection(name="arxiv_chunks_emb")
results = collection.get()
titleslist= []
titles =results['metadatas']
# print(titles)
for m in titles:
    titleslist.append(m['title'])
print(len(set(titleslist)))

print(collection.count())

# pip install --force-reinstall duckdb
print(client.list_collections())  # This helps verify if 'arxiv_papers' or 'arxiv_papers_chunks' is present
#
# paper_collection = client.get_or_create_collection(name="test")
# print(paper_collection.count())

