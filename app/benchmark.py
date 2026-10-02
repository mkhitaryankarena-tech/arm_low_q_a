import time
import re

from app.rag import search_articles
from app.benchmark_questions import BENCHMARK_QUESTIONS

from app.providers.gemini_provider import (
    generate_answer as gemini_generate
)

from app.providers.groq_provider import (
    generate_answer as groq_generate
)

from app.providers.openai_provider import (
    generate_answer as openai_generate
)


PROVIDERS = {
    "gemini": gemini_generate,
    "groq": groq_generate,
    "openai": openai_generate
}
MODEL_PRICING = {
    "gemini": {
        "input": 0.75,
        "output": 3.75
    },
    "groq": {
        "input": 0.15,
        "output": 0.60
    },
    "openai": {
        "input": 0.25,
        "output": 2.00
    }
}
def calculate_cost(provider_name, input_tokens, output_tokens):

    if input_tokens is None or output_tokens is None:
        return None

    pricing = MODEL_PRICING[provider_name]

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing["input"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output"]

    return input_cost + output_cost
def get_expected_articles(question):
    """
    Find the ground-truth expected articles
    for a benchmark question.
    """

    for item in BENCHMARK_QUESTIONS:
        if item["question"] == question:
            return [
                str(article)
                for article in item.get("expected_articles", [])
            ]

    return []
def get_question_id(question):
    for item in BENCHMARK_QUESTIONS:
        if item["question"] == question:
            return item["id"]

    return None

def extract_cited_articles(answer):
    """
    Extract article numbers cited in an LLM answer.

    Supports examples such as:
    - Հոդված 10
    - հոդված 15
    - Article 10
    - Հ.10
    - հ.42
    - Հոդվածներ 43 և 45
    - Հոդվածներ 10, 15 և 16
    - Articles 33 and 34
    """

    if not answer:
        return []

    cited_articles = []

    # 1. Singular article references
    singular_patterns = [
        r"(?:Հոդված|Article)\s*(\d+)",
        r"(?:Հ\.|հ\.)\s*(\d+)",
    ]

    for pattern in singular_patterns:
        matches = re.findall(
            pattern,
            answer,
            flags=re.IGNORECASE
        )
        cited_articles.extend(matches)

    # 2. Multiple article references
    plural_pattern = (
        r"(?:Հոդվածներ|Articles)\s+"
        r"((?:\d+\s*(?:,|և|and)?\s*)+)"
    )

    plural_matches = re.findall(
        plural_pattern,
        answer,
        flags=re.IGNORECASE
    )

    for group in plural_matches:
        numbers = re.findall(r"\d+", group)
        cited_articles.extend(numbers)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(cited_articles))


def run_benchmark(question):

    # Retrieve once so every provider gets the same context.
    results = search_articles(
        question,
        top_k=7
    )

    expected_articles = get_expected_articles(question)
    question_id = get_question_id(question)
    retrieved_articles = [
        str(result["article_number"])
        for result in results
    ]

    matched_articles = [
        article
        for article in expected_articles
        if article in retrieved_articles
    ]

    retrieval_accuracy = (
        len(matched_articles) / len(expected_articles)
        if expected_articles
        else None
    )

    if not results:
        return {
            "question_id": question_id,
            "question": question,
            "expected_articles": expected_articles,
            "retrieved_articles": [],
            "matched_articles": [],
            "retrieval_accuracy": None,
            "sources": [],
            "results": []
        }

    context = "\n\n".join(
        result["article"]
        for result in results
    )

    benchmark_results = []

    for provider_name, generate_function in PROVIDERS.items():

        start_time = time.perf_counter()

        try:
            provider_response = generate_function(
            question=question,
            context=context
            )

            elapsed = time.perf_counter() - start_time
#20260930 change return all provider response to dict with answer and token usage
            answer = provider_response["answer"]
            input_tokens = provider_response["input_tokens"]
            output_tokens = provider_response["output_tokens"]
            total_tokens = provider_response["total_tokens"]
            # TTFT and provider-measured total response time.
# Gemini and Groq do not have these fields yet,
# so .get() safely returns None for them.
            ttft_seconds = provider_response.get("ttft_seconds")
            provider_total_response_time = provider_response.get(
            "total_response_time_seconds"
            )
            estimated_cost_usd = calculate_cost(
            provider_name,
            input_tokens,
            output_tokens
            )
            # Detect provider errors returned as strings.
            answer_text = str(answer).strip()

            is_error = (
                 answer_text.startswith("Error:")
                or answer_text.startswith("OpenAI Error:")
            )

            # Do not calculate citation metrics for failed requests.
            if not is_error:

                cited_articles = extract_cited_articles(answer)

                correct_citations = [
                    article
                    for article in cited_articles
                    if article in expected_articles
                ]

                unsupported_citations = [
                    article
                    for article in cited_articles
                    if article not in retrieved_articles
                ]

                citation_accuracy = (
                    len(correct_citations) / len(cited_articles)
                    if cited_articles
                    else 0.0
                )

                citation_completeness = (
                    len(correct_citations) / len(expected_articles)
                    if expected_articles
                    else None
                )

                unsupported_citation_rate = (
                    len(unsupported_citations) / len(cited_articles)
                    if cited_articles
                    else 0.0
                )

            else:

                cited_articles = []
                correct_citations = []
                unsupported_citations = []

                citation_accuracy = None
                citation_completeness = None
                unsupported_citation_rate = None

            benchmark_results.append({
                "provider": provider_name,
                "status": "error" if is_error else "success",
                "answer": answer,

# Total benchmark call time.
                "latency_seconds": round(elapsed, 3),

# True TTFT from streaming provider.
                "ttft_seconds": ttft_seconds,

# Provider-measured generation time.
                "total_response_time_seconds": provider_total_response_time,

                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "estimated_cost_usd": (        #calculating costs
                round(estimated_cost_usd, 6)
                if estimated_cost_usd is not None
                 else None
                ),
                "cited_articles": cited_articles,
                "correct_citations": correct_citations,
                "citation_accuracy": (
                    round(citation_accuracy, 3)
                    if citation_accuracy is not None
                    else None
                ),

                "citation_completeness": (
                    round(citation_completeness, 3)
                    if citation_completeness is not None
                    else None
                ),

                "unsupported_citations": unsupported_citations,

                "unsupported_citation_rate": (
                    round(unsupported_citation_rate, 3)
                    if unsupported_citation_rate is not None
                    else None
                )
            })

        except Exception as error:

            elapsed = time.perf_counter() - start_time

            benchmark_results.append({
                "provider": provider_name,
                "status": "error",
                "answer": str(error),
                "latency_seconds": round(elapsed, 3),
                "ttft_seconds": None,
                "total_response_time_seconds": None,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "estimated_cost_usd": None,   #error  costs
                "cited_articles": [],
                "correct_citations": [],
                "citation_accuracy": None,
                "citation_completeness": None,
                "unsupported_citations": [],
                "unsupported_citation_rate": None
            })

    sources = []

    for result in results:
        sources.append({
            "article_number": result["article_number"],
            "title": result["title"],
            "score": result["score"]
        })

    return {
        "question": question,
        "expected_articles": expected_articles,
        "retrieved_articles": retrieved_articles,
        "matched_articles": matched_articles,

        "retrieval_accuracy": (
            round(retrieval_accuracy, 3)
            if retrieval_accuracy is not None
            else None
        ),

        "sources": sources,
        "results": benchmark_results
    }