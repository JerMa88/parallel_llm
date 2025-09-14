import asyncio
import aiohttp
import random

# Available users (matching server's UserDatabase)
USERS = ['Linda', 'Miguel', 'Mike']

# Sample questions for random selection
SAMPLE_QUESTIONS = [
    "What are effective study techniques for finals?",
    "How can I manage my time better?",
    "What's the best way to prepare for exams?",
    "How do I deal with academic stress?",
    "Can you suggest some productivity tips?",
    "What's a good workout routine?",
    "How to balance sports and studies?",
    "What are good mental health practices?",
]

async def ask_question(session, user, question):
    async with session.post('http://localhost:8080/ask', 
                          json={'user': user, 'question': question}) as resp:
        return await resp.json()

async def main():
    async with aiohttp.ClientSession() as session:
        print("Enter the amount of concurrent user calls (Ctrl+C to exit)")
        while True:
            try:
                # Get number of concurrent calls from user
                n_calls = int(input("Enter number of concurrent calls (1-10): "))
                if not 1 <= n_calls <= 10:
                    print("Please enter a number between 1 and 10")
                    continue
                
                # Create list of concurrent tasks
                tasks = []
                for _ in range(n_calls):
                    user = random.choice(USERS)
                    question = random.choice(SAMPLE_QUESTIONS)
                    print(f"Queuing request as {user}: {question}")
                    tasks.append(ask_question(session, user, question))
                
                # Execute all tasks concurrently and wait for results
                # Create a list to collect responses
                responses = []
                # Wait for responses and print them as they arrive
                i = 1
                for task in asyncio.as_completed(tasks):
                    response = await task
                    responses.append(response)
                    print(f"{i}. LLM Response to {response['user']}: {response['response']}\n")
                    i += 1

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except ValueError:
                print("Please enter a valid number")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
