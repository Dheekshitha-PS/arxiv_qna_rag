from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")
model = AutoModel.from_pretrained("BAAI/bge-base-en-v1.5")

def get_embedding(text):
    # Instruction format for better retrieval performance
    instruction = "Represent this paragraph from a research paper for retrieval: "
    inputs = tokenizer(instruction + text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings[0].tolist()
