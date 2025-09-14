import os
import asyncio
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()
async def call_llm(prompt: str) -> str:
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = await client.messages.create(
        max_tokens=256,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful University counselor that give advices. Please keep your response short (less than 100 words), concise, straight to the point.",
                "role": "user",
                "content": f"Respond in 10 words: {prompt}",
            }
        ],
        model="claude-sonnet-4-20250514",
    )
    # print(message.content)
    return (message.content[0].text)

if __name__ == "__main__":
    result = asyncio.run(call_llm('Can you tell me why I suck'))

    print('Call Result:', result)