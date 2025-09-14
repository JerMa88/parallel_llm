import os
import asyncio
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()
async def call_llm(system_message: str, messages: list) -> str:
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = await client.messages.create(
        max_tokens=256,
        system=system_message,
        messages=messages,
        model="claude-sonnet-4-20250514",
    )
    return message.content[0].text

async def call_llm_simple(prompt: str) -> str:
    system_message = "You are a helpful University counselor that give advices. Please keep your response short (less than 100 words), concise, straight to the point."
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    return await call_llm(system_message, messages)

if __name__ == "__main__":
    result = asyncio.run(call_llm_simple('Can you tell me why I suck'))

    print('Call Result:', result)