import asyncio
import aiohttp
import sys

USERS = ['Linda', 'Miguel', 'Mike']

async def check_health(session):
    """Check if the local server is healthy"""
    try:
        async with session.get('http://localhost:8081/health') as resp:
            return await resp.json()
    except Exception as e:
        return {'error': str(e)}

async def chat_session(session, selected_user):
    print(f"\nStarting chat as {selected_user}. Type 'quit' to exit.")
    print("Ask your question:")

    while True:
        try:
            question = input("> ")
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not question.strip():
                continue

            async with session.post('http://localhost:8081/ask',
                                  json={'user': selected_user, 'question': question}) as resp:
                response = await resp.json()
                if 'error' in response:
                    print(f"Error: {response['error']}")
                else:
                    print(f"\nResponse: {response['response']}\n")

        except Exception as e:
            print(f"Error: {e}")

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

    # User selection
    print("\nWelcome to the Local AI Assistant! Please select your user:")
    for idx, user in enumerate(USERS, 1):
        print(f"{idx}. {user}")

    while True:
        try:
            choice = int(input("Enter your choice (1-3): "))
            if 1 <= choice <= len(USERS):
                selected_user = USERS[choice-1]
                break
            print("Please enter a valid number between 1 and 3")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)

    # Start chat session
    async with aiohttp.ClientSession() as session:
        await chat_session(session, selected_user)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")