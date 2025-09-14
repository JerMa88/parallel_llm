import asyncio
import aiohttp
import random

# Same users and questions as Anthropic client
USERS = ['Linda', 'Miguel', 'Mike']

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
    """Send a question to the local LLM server"""
    async with session.post('http://localhost:8081/ask',
                          json={'user': user, 'question': question}) as resp:
        return await resp.json()

async def check_health(session):
    """Check if the local server is healthy"""
    try:
        async with session.get('http://localhost:8081/health') as resp:
            return await resp.json()
    except Exception as e:
        return {'error': str(e)}

async def main():
    async with aiohttp.ClientSession() as session:
        # First check if server is running
        print("Checking local LLM server health...")
        health = await check_health(session)
        if 'error' in health:
            print(f"Error connecting to server: {health['error']}")
            print("Make sure to start the local server first: python local_server.py")
            return

        print(f"Server status: {health}")
        if not health.get('model_loaded', False):
            print("Model is still loading, please wait...")
            return

        print("\nEnter the amount of concurrent user calls (Ctrl+C to exit)")
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
                responses = []
                i = 1
                print(f"\nExecuting {n_calls} concurrent requests...")
                for task in asyncio.as_completed(tasks):
                    response = await task
                    responses.append(response)
                    if 'error' in response:
                        print(f"{i}. Error for request: {response['error']}")
                    else:
                        print(f"{i}. Local LLM Response to {response['user']}: {response['response']}\n")
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