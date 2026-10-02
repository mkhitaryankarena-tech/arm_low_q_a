import os
import time

from dotenv import load_dotenv
from groq import Groq
from app.prompts import build_prompt


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found in .env"
    )


client = Groq(api_key=api_key)


def generate_answer(question, context):

    # Use the common prompt from app/prompts.py
    prompt = build_prompt(
        question=question,
        context=context
    )

    try:
        start_time = time.perf_counter()

        stream = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a legal Q&A assistant. "
                        "Follow the instructions in the user prompt."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
           temperature=0.1,
            stream=True
        )

        answer_parts = []
        ttft_seconds = None

        input_tokens = None
        output_tokens = None
        total_tokens = None

        for chunk in stream:

            # Measure TTFT when the first actual text arrives
            if chunk.choices:
                content = chunk.choices[0].delta.content

                if content:

                    if ttft_seconds is None:
                        ttft_seconds = (
                            time.perf_counter() - start_time
                        )

                    answer_parts.append(content)

            # Usage normally arrives with the final streaming chunk
            if chunk.usage is not None:
                input_tokens = chunk.usage.prompt_tokens
                output_tokens = chunk.usage.completion_tokens
                total_tokens = chunk.usage.total_tokens

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

    except Exception as error:
        return {
            "answer": f"Error: {error}",
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "ttft_seconds": None,
            "total_response_time_seconds": None
        }
    # 20261001 change return value end