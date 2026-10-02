import re
from pathlib import Path


LAW_PATH = Path("data/electronic_communications_law.txt")

def load_law():
    with open(LAW_PATH, "r", encoding="utf-8") as file:
        return file.read()

def split_into_articles(text):
    pattern = r"(?=Հոդված\s+\d+)"

    articles = re.split(pattern, text)

    return [
        article.strip()
        for article in articles
        if article.strip().startswith("Հոդված")
    ]

law_text = load_law()
articles = split_into_articles(law_text)
print("Total articles:", len(articles))

for article in articles[:3]:
    print("\n------------------------------")
    print(article[:500])