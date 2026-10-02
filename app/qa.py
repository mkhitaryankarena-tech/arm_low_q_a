from app.rag import search_articles

from app.providers.gemini_provider import (
    generate_answer as gemini_generate
)

from app.providers.groq_provider import (
    generate_answer as groq_generate
)

from app.providers.openai_provider import (
    generate_answer as openai_generate
)


NOT_FOUND_TEXT = "Պատասխանը չի գտնվել"


def generate_with_provider(provider, question, context):

    if provider == "gemini":
        return gemini_generate(question, context)

    elif provider == "groq":
        return groq_generate(question, context)

    elif provider == "openai":
        return openai_generate(question, context)

    else:
        raise ValueError(
            f"Unknown provider: {provider}"
        )


def ask_question(question, provider="groq"):

    # Retrieve the same legal context regardless of LLM provider
    results = search_articles(
        question,
        top_k=5
    )

    if not results:
        return {
            "question": question,
            "provider": provider,
            "answer": (
                "Պատասխանը չի գտնվել "
                "տրամադրված օրենքում։"
            ),
            "sources": []
        }

    context_parts = []

    for result in results:
        context_parts.append(
            result["article"]
        )

    context = "\n\n".join(context_parts)

    # Generate answer with selected provider
    provider_response = generate_with_provider(
    provider=provider,
    question=question,
    context=context
    )

# Providers now return a dictionary because
# benchmark also collects token usage.
    if isinstance(provider_response, dict):
     answer = provider_response["answer"]
    else:
    # Backward compatibility
        answer = provider_response

# Do not show candidate sources when provider failed
    if (
    answer.startswith("Error:")
    or answer.startswith("OpenAI Error:")
    ):
        sources = []

    elif NOT_FOUND_TEXT in answer:
        sources = []

    else:
        sources = results

    return {
        "question": question,
        "provider": provider,
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    question = input("\nAsk a question: ")

    result = ask_question(
        question,
        provider="groq"
    )

    print("\nPROVIDER:")
    print(result["provider"])

    print("\nANSWER:\n")
    print(result["answer"])

    print("\nSOURCES:\n")

    if not result["sources"]:
        print("No supporting sources.")

    for source in result["sources"]:

        first_line = source["article"].split("\n")[0]

        print(
            first_line,
            "- score:",
            round(source["score"], 4)
        )