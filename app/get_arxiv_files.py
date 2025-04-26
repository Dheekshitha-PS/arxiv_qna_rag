import requests
import feedparser
from datetime import datetime, timedelta

# Define the arXiv categories
categories = {
    "NLP": "cs.CL",
    "Computer Vision": "cs.CV",
    "Soft Matter": "cond-mat.soft",
    "Quantum Physics": "quant-ph"
}

# Get date from 1 year ago
one_year_ago = datetime.now() - timedelta(days=365)
date_filter = one_year_ago.strftime('%Y%m%d%H%M%S')

# Base arXiv API URL
BASE_URL = "http://export.arxiv.org/api/query"




def fetch_arxiv_data(category_code, max_results=50):
    query = f"cat:{category_code}"
    url = f"{BASE_URL}?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"

    print(f"Fetching {category_code} from arXiv...")
    response = requests.get(url)
    feed = feedparser.parse(response.content)

    papers = []
    for entry in feed.entries:
        published_date = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
        if published_date < one_year_ago:
            continue  # skip papers older than 1 year
        pdf_url = next((link.href for link in entry.links if link.type == 'application/pdf'), None)
        arxiv_id = pdf_url.split("/")[-1].replace(".pdf", "")
        paper = {
            "title": entry.title,
            "authors": [author.name for author in entry.authors],
            "published": entry.published,
            "summary": entry.summary,
            "pdf_url":pdf_url,
            "category": category_code,
            "arxiv_id": arxiv_id
        }
        papers.append(paper)
    return papers

def main(categories,MAX_RESULTS):
    all_papers = []
    for domain, cat_code in categories.items():
        papers = fetch_arxiv_data(cat_code, MAX_RESULTS)
        all_papers.extend(papers)
        print(f"{len(papers)} papers fetched for {domain}")

    print(f"\nTotal papers fetched: {len(all_papers)}")

    # Optional: print sample
    for paper in all_papers[:3]:
        print("\n---")
        print("Title:", paper["title"])
        print("Authors:", ", ".join(paper["authors"]))
        print("Published:", paper["published"])
        print("PDF URL:", paper["pdf_url"])
    return [all_papers,len(all_papers)]


