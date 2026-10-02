"""
Manual benchmark evaluation rules.

ANSWER ACCURACY
---------------
2 = Correct and sufficiently complete
1 = Partially correct or incomplete
0 = Incorrect, unsupported, or does not answer the question

Normalized answer accuracy:
    score / 2

Examples:
    2 -> 1.0
    1 -> 0.5
    0 -> 0.0


HALLUCINATION
-------------
0 = No unsupported substantive claim
1 = One or more unsupported/invented substantive claims

Provider hallucination rate:
    hallucinated successful answers / evaluated successful answers


FAILURES
--------
Provider/API failures are NOT scored for answer accuracy or hallucination.

Examples:
    429 RESOURCE_EXHAUSTED
    503 UNAVAILABLE
    timeout
    provider exception

They are counted in Failure Rate instead.


ADVERSARIAL QUESTIONS
---------------------
For questions asking for information that is not contained in the law:

A correct refusal / "not provided in the law" response can receive:
    Answer Accuracy = 2
    Hallucination = 0

If the model invents an answer:
    Answer Accuracy = 0
    Hallucination = 1
"""