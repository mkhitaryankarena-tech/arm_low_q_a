from app.providers.gemini_provider import generate_answer


question = "What are the purposes of the law?"

context = """
Հոդված 1. Օրենքի նպատակները

Սույն օրենքի հիմնական նպատակներն են՝
ապահովել Հայաստանի Հանրապետությունում
էլեկտրոնային հաղորդակցության զարգացումը։
"""


result = generate_answer(
    question=question,
    context=context
)


print("\nGemini result:\n")

print("Answer:")
print(result["answer"])

print("\nInput tokens:")
print(result["input_tokens"])

print("\nOutput tokens:")
print(result["output_tokens"])

print("\nTotal tokens:")
print(result["total_tokens"])

print("\nTTFT:")
print(result["ttft_seconds"])

print("\nTotal response time:")
print(result["total_response_time_seconds"])