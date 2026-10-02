import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found in .env"
    )


client = Groq(
    api_key=api_key
)


response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "You can understand Armenian and English."
            )
        },
        {
            "role": "user",
            "content": "Պատասխանիր հայերեն. Ի՞նչ է էլեկտրոնային հաղորդակցությունը։"
        }
    ],
    temperature=0.2
)


print("\nGROQ RESPONSE:\n")
print(
    response.choices[0].message.content
)