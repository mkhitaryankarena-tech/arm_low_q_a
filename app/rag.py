import re
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer, util

LAW_PATH = Path("data/electronic_communications_law.txt")


# Multilingual embedding model
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

def load_law():
    with open(LAW_PATH, "r", encoding="utf-8") as file:
        return file.read()


def split_into_articles(text):
    pattern = r"(?=Հոդված\s+\d+)"

    parts = re.split(pattern, text)

    articles = []

    for part in parts:
        part = part.strip()

        if part.startswith("Հոդված"):
            articles.append(part)

    return articles


# Load law only once
law_text = load_law()

articles = split_into_articles(law_text)


# Create embeddings for all articles
print("Creating article embeddings...")

article_embeddings = model.encode(
    articles,
    convert_to_tensor=True
)

print(f"Loaded {len(articles)} articles.")

def extract_article_info(article_text):
    first_line = article_text.split("\n")[0].strip()

    match = re.search(
        r"Հոդված\s+(\d+(?:\.\d+)?)",
        first_line
    )

    if match:
        article_number = match.group(1)
    else:
        article_number = "Unknown"

    return {
        "article_number": article_number,
        "title": first_line
    }
def keyword_boost(question, article_text):
    question_lower = question.lower()
    article_lower = article_text.lower()
    boost = 0.0
    title_lower = article_text.split("\n")[0].lower()
    keyword_groups = {
    "license": [
        "license", "licensing", "licence", "licensee", "licensees",
        "լիցենզիա", "լիցենզիայի", "լիցենզավորման", "լիցենզավորվող"
    ],

    "purpose": [
        "purpose", "purposes",
        "նպատակ", "նպատակները"
    ],

    "operator": [
        "operator", "operators",
        "օպերատոր", "օպերատորի"
    ],

    "frequency": [
        "frequency", "frequencies", "spectrum",
        "հաճախականություն", "հաճախականությունների",
        "ռադիոհաճախականություն", "ռադիոհաճախականությունների"
    ],

    "rights": [
        "right", "rights",
        "իրավունք", "իրավունքներ", "իրավունքների"
    ],

    "obligations": [
        "obligation", "obligations", "duties",
        "պարտավորություն", "պարտավորություններ", "պարտավորությունների"
    ],

    "regulator": [
        "regulator", "regulator's",
        "կարգավորող", "կարգավորողի"
    ],

    "powers": [
        "power", "powers", "authority",
        "իրավասություն", "իրավասությունները", "իրավասությունների"
    ],

    "functions": [
        "function", "functions",
        "գործառույթ", "գործառույթները", "գործառույթների"
    ],

    "interconnection": [
        "interconnection", "interconnect",
        "փոխկապակցում", "փոխկապակցման"
    ],

    "user": [
        "user", "users", "subscriber", "subscribers",
        "օգտագործող", "օգտագործողների",
        "բաժանորդ", "բաժանորդների"
    ],

    "dominance": [
        "dominance", "dominant",
        "գերիշխող", "գերիշխող դիրք"
    ],

    "tariff": [
        "tariff", "tariffs", "rate", "rates",
        "սակագին", "սակագներ", "սակագների",
        "դրույքաչափ", "դրույքաչափեր"
    ]
}

    for keywords in keyword_groups.values():

        question_matches = any(
            keyword in question_lower
            for keyword in keywords
        )

        article_matches = any(
            keyword in article_lower
            for keyword in keywords
        )

        if question_matches and article_matches:
            boost += 0.15
        # Small extra boost for title matches
    question_words = re.findall(r"\w+", question_lower)
    for word in question_words:
     if len(word) >= 5 and word in title_lower:
        boost += 0.05
    return boost

#top_k=3 mins we will return 3 articles with the highest similarity scores to the question
def search_articles(question, top_k=7, min_score=0.25):  

    question_embedding = model.encode(
        question,
        convert_to_tensor=True
    )

    scores = util.cos_sim(
        question_embedding,
        article_embeddings
    )[0]
  
    combined_scores = []

    for index, semantic_score in enumerate(scores):

        boost = keyword_boost(
            question,
            articles[index]
        )

        final_score = (
            float(semantic_score) + boost
        )

        combined_scores.append(final_score)

    top_indices = np.argsort(
        combined_scores
    )[-top_k:][::-1]

    results = []

    for index in top_indices:

        score = combined_scores[index]

        if score < min_score:
            continue

        article_text = articles[index]

        article_info = extract_article_info(
            article_text
        )

        results.append({
            "article": article_text,
            "article_number":
                article_info["article_number"],
            "title":
                article_info["title"],
            "score":
                float(score)
        })

    return results


if __name__ == "__main__":

    question = input("\nAsk a question: ")  
   
    results = search_articles(question)

    print("\nTop matching articles:\n")

    for result in results:

        print("=" * 70)

        print(
            "Score:",
            round(result["score"], 4)
        )

        print(result["article"][:1500])

        print()