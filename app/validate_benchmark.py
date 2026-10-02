from app.benchmark_questions import BENCHMARK_QUESTIONS


def validate_benchmark():
    errors = []

    expected_ids = set(range(1, 20))
    actual_ids = {q.get("id") for q in BENCHMARK_QUESTIONS}

    # Check question count
    if len(BENCHMARK_QUESTIONS) != 19:
        errors.append(
            f"Expected 19 questions, found {len(BENCHMARK_QUESTIONS)}."
        )

    # Check IDs
    missing_ids = expected_ids - actual_ids
    extra_ids = actual_ids - expected_ids

    if missing_ids:
        errors.append(
            f"Missing question IDs: {sorted(missing_ids)}"
        )

    if extra_ids:
        errors.append(
            f"Unexpected question IDs: {sorted(extra_ids)}"
        )

    # Check every question
    for q in BENCHMARK_QUESTIONS:
        question_id = q.get("id", "UNKNOWN")

        required_fields = [
            "id",
            "language",
            "type",
            "question",
            "expected_articles",
            "expected_points",
        ]

        for field in required_fields:
            if field not in q:
                errors.append(
                    f"Q{question_id}: missing '{field}'"
                )

        if not q.get("question"):
            errors.append(
                f"Q{question_id}: question is empty"
            )

        expected_articles = q.get("expected_articles")

        if not isinstance(expected_articles, list):
            errors.append(
                f"Q{question_id}: expected_articles must be a list"
            )

        expected_points = q.get("expected_points")

        if not isinstance(expected_points, list):
            errors.append(
                f"Q{question_id}: expected_points must be a list"
            )
        elif len(expected_points) == 0:
            errors.append(
                f"Q{question_id}: expected_points is empty"
            )

        language = q.get("language")

        if language not in {"hy", "en"}:
            errors.append(
                f"Q{question_id}: invalid language '{language}'"
            )

        question_type = q.get("type")

        if question_type not in {
            "answerable",
            "adversarial",
            "synthesis",
        }:
            errors.append(
                f"Q{question_id}: invalid type '{question_type}'"
            )

    # Dataset composition
    armenian_answerable = [
        q for q in BENCHMARK_QUESTIONS
        if q.get("language") == "hy"
        and q.get("type") == "answerable"
    ]

    english_answerable = [
        q for q in BENCHMARK_QUESTIONS
        if q.get("language") == "en"
        and q.get("type") == "answerable"
    ]

    adversarial_or_synthesis = [
        q for q in BENCHMARK_QUESTIONS
        if q.get("type") in {"adversarial", "synthesis"}
    ]

    if len(armenian_answerable) < 5:
        errors.append(
            "Dataset must contain at least 5 Armenian answerable questions."
        )

    if len(english_answerable) < 5:
        errors.append(
            "Dataset must contain at least 5 English answerable questions."
        )

    if len(adversarial_or_synthesis) < 3:
        errors.append(
            "Dataset must contain at least 3 adversarial/synthesis questions."
        )

    # Result
    print("\n=== Benchmark Dataset Validation ===\n")

    print(f"Total questions: {len(BENCHMARK_QUESTIONS)}")
    print(f"Armenian answerable: {len(armenian_answerable)}")
    print(f"English answerable: {len(english_answerable)}")
    print(
        "Adversarial / synthesis: "
        f"{len(adversarial_or_synthesis)}"
    )

    if errors:
        print("\nVALIDATION FAILED\n")

        for error in errors:
            print(f"- {error}")

        return False

    print("\nVALIDATION PASSED")
    print("All benchmark questions contain the required ground-truth fields.")

    return True


if __name__ == "__main__":
    validate_benchmark()