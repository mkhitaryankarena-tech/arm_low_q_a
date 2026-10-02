import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from app.prompts import build_prompt


# Load variables from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in the .env file."
    )


# Create Gemini client
client = genai.Client(api_key=api_key)


def generate_answer(question, context):
    """
    Generate an Armenian answer using only
    the retrieved legal context.

    Also measure:
    - TTFT
    - total response time
    - token usage
    """

    prompt = build_prompt(
        question=question,
        context=context
    )

    # Try up to 3 times if Gemini is temporarily unavailable
    for attempt in range(3):

        try:
            start_time = time.perf_counter()

            stream = client.models.generate_content_stream(
                model="gemini-3.8-flash",
                contents=prompt
            )

            answer_parts = []
            ttft_seconds = None

            input_tokens = None
            output_tokens = None
            total_tokens = None

            for chunk in stream:

                # Measure TTFT when first actual text arrives
                if chunk.text:

                    if ttft_seconds is None:
                        ttft_seconds = (
                            time.perf_counter() - start_time
                        )

                    answer_parts.append(chunk.text)

                # Gemini may provide usage metadata
                # on the final streaming chunk.
                usage = chunk.usage_metadata

                if usage is not None:

                    input_tokens = usage.prompt_token_count
                    output_tokens = usage.candidates_token_count
                    total_tokens = usage.total_token_count

            total_response_time = (
                time.perf_counter() - start_time
            )

            answer = "".join(answer_parts)

            return {
                "answer": answer,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "ttft_seconds": (
                    round(ttft_seconds, 3)
                    if ttft_seconds is not None
                    else None
                ),
                "total_response_time_seconds": round(
                    total_response_time,
                    3
                )
            }

        except errors.ServerError as error:

            error_text = str(error)

            # Do NOT retry quota/rate-limit errors.
            # They should count as provider failures immediately.
            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "quota" in error_text.lower()
            ):
                return {
                    "answer": f"Error: {error}",
                    "input_tokens": None,
                    "output_tokens": None,
                    "total_tokens": None,
                    "ttft_seconds": None,
                    "total_response_time_seconds": None
                }

            # Retry genuine temporary server errors.
            if attempt < 2:

                print(
                    f"\nGemini is temporarily unavailable. "
                    f"Retrying... ({attempt + 1}/3)"
                )

                time.sleep(3)

            else:

                print(
                    "\nGemini is still unavailable "
                    "after 3 attempts."
                )

                return {
                    "answer": f"Error: {error}",
                    "input_tokens": None,
                    "output_tokens": None,
                    "total_tokens": None,
                    "ttft_seconds": None,
                    "total_response_time_seconds": None
                }

        except Exception as error:

            return {
                "answer": f"Error: {error}",
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "ttft_seconds": None,
                "total_response_time_seconds": None
            }