import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from app.prompts import build_prompt


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found in .env"
    )


client = OpenAI(api_key=api_key)


def generate_answer(question, context):

    prompt = build_prompt(
        question=question,
        context=context
    )

    try:
        start_time = time.perf_counter()

        stream = client.responses.create(
            model="gpt-5-mini",
            input=prompt,
            stream=True
        )

        answer_parts = []
        ttft_seconds = None
        final_response = None

        for event in stream:

            # First actual piece of generated text
            if event.type == "response.output_text.delta":

                if ttft_seconds is None:
                    ttft_seconds = (
                        time.perf_counter() - start_time
                    )

                answer_parts.append(event.delta)

            # Final response contains usage information
            elif event.type == "response.completed":
                final_response = event.response

        total_response_time = (
            time.perf_counter() - start_time
        )

        answer = "".join(answer_parts)

        if final_response is not None:
            input_tokens = final_response.usage.input_tokens
            output_tokens = final_response.usage.output_tokens
            total_tokens = final_response.usage.total_tokens
        else:
            input_tokens = None
            output_tokens = None
            total_tokens = None

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

    except Exception as error:
        return {
            "answer": f"OpenAI Error: {error}",
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "ttft_seconds": None,
            "total_response_time_seconds": None
        }
# 20261001 change return value end