import json
import csv
from pathlib import Path

from app.benchmark_questions import BENCHMARK_QUESTIONS


INPUT_FILE = Path("benchmark_results.json")
OUTPUT_FILE = Path("manual_evaluation.csv")


def build_question_map():
    return {
        question["id"]: question
        for question in BENCHMARK_QUESTIONS
    }


def create_manual_evaluation_file():

    if not INPUT_FILE.exists():
        print(f"\nFile not found: {INPUT_FILE}")
        print(
            "This is expected before the final benchmark run.\n"
            "After Run All, download benchmark_results.json "
            "and place it in the project root."
        )
        return

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        benchmark_data = json.load(file)

    results = benchmark_data.get(
        "benchmark_results",
        []
    )

    question_map = build_question_map()

    rows = []

    for benchmark_item in results:

        question_id = benchmark_item.get(
            "question_id"
        )

        if question_id is not None:
            question_id = int(question_id)

        question_info = question_map.get(
            question_id,
            {}
        )

        providers = benchmark_item.get(
            "results",
            []
        )

        for provider_result in providers:

            status = provider_result.get(
                "status",
                "unknown"
            )

            # Manual fields intentionally start empty.
            # Failed provider requests remain unscored.
            answer_accuracy_score = ""
            answer_accuracy_normalized = ""
            hallucination = ""

            rows.append({
                "question_id": question_id,

                "language": question_info.get(
                    "language",
                    ""
                ),

                "type": question_info.get(
                    "type",
                    ""
                ),

                "question": question_info.get(
                    "question",
                    benchmark_item.get(
                        "question",
                        ""
                    )
                ),

                "expected_articles": " | ".join(
                    str(article)
                    for article in question_info.get(
                        "expected_articles",
                        []
                    )
                ),

                "expected_points": " | ".join(
                    question_info.get(
                        "expected_points",
                        []
                    )
                ),

                "provider": provider_result.get(
                    "provider",
                    ""
                ),

                "status": status,

                "answer": provider_result.get(
                    "answer",
                    ""
                ),

                "answer_accuracy_score":
                    answer_accuracy_score,

                "answer_accuracy_normalized":
                    answer_accuracy_normalized,

                "hallucination":
                    hallucination,

                "evaluator_notes": "",
            })

    fieldnames = [
        "question_id",
        "language",
        "type",
        "question",
        "expected_articles",
        "expected_points",
        "provider",
        "status",
        "answer",
        "answer_accuracy_score",
        "answer_accuracy_normalized",
        "hallucination",
        "evaluator_notes",
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n=== Manual Evaluation File ===\n")

    print(
        f"Benchmark questions read: "
        f"{len(results)}"
    )

    print(
        f"Evaluation rows created: "
        f"{len(rows)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        "\nManual evaluation file "
        "created successfully."
    )


if __name__ == "__main__":
    create_manual_evaluation_file()