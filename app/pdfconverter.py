import pymupdf4llm
from markdown_it import MarkdownIt
import tiktoken
from sentence_splitter import SentenceSplitter
import re

def count_tokens(text, model_name="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model_name)
    return len(enc.encode(text))


def semantic_chunking(text, max_tokens=1000, model_name="gpt-3.5-turbo"):
    splitter = SentenceSplitter(language='en')
    sentences = splitter.split(text)
    enc = tiktoken.encoding_for_model(model_name)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        token_count = len(enc.encode(sentence))
        if current_tokens + token_count > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_tokens = token_count
        else:
            current_chunk.append(sentence)
            current_tokens += token_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def format_chunk(title, abstract, section_name, content,category,published_date):
    return f"Title: {title}\npublished_date:{published_date}\n,category: \n{category}, Abstract: {abstract}\nSection: {section_name}\n\n{content}"


def extract_sections_from_markdown(pdf_path, title, abstract,category,published_date):

    markdown_text = pymupdf4llm.to_markdown(pdf_path)

    md = MarkdownIt()
    tokens = md.parse(markdown_text)
    # print(tokens,"TOKENS")
    sections = {}
    current_section = None

    reference_headers = {"references", "reference", "bibliography"}

    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            inline_token = tokens[i + 1]

            # Inside your loop, before checking for reference
            heading_text_raw = inline_token.content.strip()

            # Remove markdown formatting (bold, italic, etc.)
            heading_text_clean = re.sub(r"[*_`]", "", heading_text_raw)

            # Remove section numbering like '1.', '1.1', '2.3.4'
            heading_text_clean = re.sub(r"^\d+(\.\d+)*\s*", "", heading_text_clean)

            # Convert to lowercase
            heading_text_lower = heading_text_clean.lower()
            if heading_text_lower in reference_headers:
                break  # Stop processing at references

            current_section = inline_token.content.strip()

            current_section = re.sub(r"[*_`]", "", current_section)

            # Remove section numbering like '1.', '1.1', '2.3.4'
            current_section = re.sub(r"^\d+(\.\d+)*\s*", "", current_section)

            # Convert to lowercase
            current_section = current_section.lower()
            if current_section not in sections:
                sections[current_section] = []

        elif token.type == "inline" and current_section is not None:
            content = token.content.strip()
            if content:
                sections[current_section].append(content)

    # Final formatted output with optional semantic chunking
    processed_sections = {}
    for section, texts in sections.items():
        full_text = " ".join(texts)
        tokens = count_tokens(full_text)

        if tokens > 1000:
            chunks = semantic_chunking(full_text)
            for i, chunk in enumerate(chunks):
                section_key = f"{section}_part_{i + 1}"
                processed_sections[section_key] = [
                    format_chunk(title, abstract, section_key, chunk,category,published_date)
                ]
        else:
            processed_sections[section] = [
                format_chunk(title, abstract, section, full_text,category,published_date)
            ]
    # print("Processed sections keys are:::",processed_sections.keys())

    return processed_sections


