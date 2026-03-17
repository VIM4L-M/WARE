from litellm import completion
import os

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Set GROQ_API_KEY in your environment before running this script.")

response = completion(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hello in one sentence!"}],
    api_key=groq_api_key,
)

print("Groq connection successful!")
print(response.choices[0].message.content)