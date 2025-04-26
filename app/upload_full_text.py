import chromadb

# Initialize Chroma client (persistent mode)
client = chromadb.PersistentClient(path="./chroma_store")

# Create or load collection
collection = client.get_or_create_collection(name="arxiv_papers")

def store_all_papers(paper_data_list):
    for paper in paper_data_list:
        try:
            collection.add(
                ids=[paper["id"]],
                metadatas=[{
                    "title": paper["title"],
                    "authors": paper["authors"],
                    "abstract": paper["abstract"]
                }],
                documents=[paper["full_text"]]
            )
            print(f"✅ Stored: {paper['id']}")
        except Exception as e:
            print(f"❌ Failed to store {paper['id']}: {str(e)}")

# Example usage:
store_all_papers(papers)
