import asyncio
import aiohttp
import json

async def test_memory():
    async with aiohttp.ClientSession() as session:
        user = "Linda"

        print("=== Testing Memory Functionality ===\n")

        # Clear conversation history first
        print("1. Clearing conversation history...")
        async with session.post('http://localhost:8080/clear',
                              json={'user': user}) as resp:
            result = await resp.json()
            print(f"   Clear result: {result}\n")

        # First conversation
        print("2. First question (should not have context)...")
        question1 = "My name is Sarah and I'm struggling with time management"
        async with session.post('http://localhost:8080/ask',
                              json={'user': user, 'question': question1}) as resp:
            result1 = await resp.json()
            print(f"   Q: {question1}")
            print(f"   A: {result1['response']}\n")

        # Second conversation - should remember previous context
        print("3. Second question (should remember my name and topic)...")
        question2 = "What specific techniques would work for me?"
        async with session.post('http://localhost:8080/ask',
                              json={'user': user, 'question': question2}) as resp:
            result2 = await resp.json()
            print(f"   Q: {question2}")
            print(f"   A: {result2['response']}\n")

        # Third conversation - should continue remembering
        print("4. Third question (should still have full context)...")
        question3 = "Can you remind me what we discussed earlier?"
        async with session.post('http://localhost:8080/ask',
                              json={'user': user, 'question': question3}) as resp:
            result3 = await resp.json()
            print(f"   Q: {question3}")
            print(f"   A: {result3['response']}\n")

        print("=== Memory Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_memory())