import csv
from collections import defaultdict
from pathlib import Path


INPUT_FILE = Path("manual_evaluation.csv")


def calculate_summary():
    if not INPUT_FILE.exists():
        print(f"\nFile not found: {INPUT_FILE}")
        print(
            "This file will be created after the final benchmark "
            "and manual scoring."
        )
        return

    provider_stats = defaultdict(
        lambda: {
            "accuracy_scores": [],
            "hallucinations": [],
            "successful": 0,
            "failed": 0,
        }
    )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            provider = row["provider"]
            status = row["status"]

            stats = provider_stats[provider]

            if status != "success":
                stats["failed"] += 1
                continue

            stats["successful"] += 1

            accuracy = row[
                "answer_accuracy_score"
            ].strip()

            hallucination = row[
                "hallucination"
            ].strip()

            if accuracy:
                score = float(accuracy)

                if score not in {0, 1, 2}:
                    raise ValueError(
                        f"Invalid accuracy score "
                        f"for {provider}: {score}"
                    )

                stats["accuracy_scores"].append(
                    score / 2
                )

            if hallucination:
                value = int(hallucination)

                if value not in {0, 1}:
                    raise ValueError(
                        f"Invalid hallucination value "
                        f"for {provider}: {value}"
                    )

                stats["hallucinations"].append(
                    value
                )

    print("\n=== Evaluation Summary ===\n")

    for provider, stats in provider_stats.items():

        accuracy_scores = stats[
            "accuracy_scores"
        ]

        hallucinations = stats[
            "hallucinations"
        ]

        if accuracy_scores:
            answer_accuracy = (
                sum(accuracy_scores)
                / len(accuracy_scores)
            )
        else:
            answer_accuracy = None

        if hallucinations:
            hallucination_rate = (
                sum(hallucinations)
                / len(hallucinations)
            )
        else:
            hallucination_rate = None

        total_requests = (
            stats["successful"]
            + stats["failed"]
        )

        if total_requests:
            failure_rate = (
                stats["failed"]
                / total_requests
            )
        else:
            failure_rate = None

        print(f"Provider: {provider}")

        print(
            "  Answer Accuracy: "
            + (
                f"{answer_accuracy:.2%}"
                if answer_accuracy is not None
                else "N/A"
            )
        )

        print(
            "  Hallucination Rate: "
            + (
                f"{hallucination_rate:.2%}"
                if hallucination_rate is not None
                else "N/A"
            )
        )

        print(
            "  Failure Rate: "
            + (
                f"{failure_rate:.2%}"
                if failure_rate is not None
                else "N/A"
            )
        )

        print(
            f"  Successful Requests: "
            f"{stats['successful']}"
        )

        print(
            f"  Failed Requests: "
            f"{stats['failed']}"
        )

        print(
            f"  Manually Scored Answers: "
            f"{len(accuracy_scores)}"
        )

        print()


if __name__ == "__main__":
    calculate_summary()