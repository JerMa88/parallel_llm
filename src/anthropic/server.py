import asyncio
from aiohttp import web
from call_llm import call_llm
from memory import ConversationMemory
from datetime import datetime

UserDataBase = {'Linda': 'Student',
                'Miguel': 'Counselor',
                'Mike': 'Athlete'}

# Initialize global memory instance
memory = ConversationMemory()

async def handle_request(request):
    try:
        data = await request.json()
        user = data['user']
        question = data['question']

        if user not in UserDataBase:
            return web.json_response({'error': 'Unknown user'}, status=400)

        # Add user's question to memory
        memory.add_user_message(user, question)

        # Get messages for API call (includes conversation history)
        system_message, messages = memory.get_messages_for_api(user, UserDataBase[user])

        # Log received question
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] User {user} asked: {question}")

        # Get response from LLM using conversation history
        response = await call_llm(system_message, messages)

        # Add LLM's response to memory
        memory.add_assistant_message(user, response)

        # Log response
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Responded to {user} with status code: 200")

        return web.json_response({'user': user, 'response': response})
    except Exception as e:
        # Log error
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Error occurred with status code: 400")
        return web.json_response({'error': str(e)}, status=400)

async def clear_conversation(request):
    try:
        data = await request.json()
        user = data['user']

        if user not in UserDataBase:
            return web.json_response({'error': 'Unknown user'}, status=400)

        memory.clear_conversation(user)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Cleared conversation history for {user}")

        return web.json_response({'message': f'Conversation history cleared for {user}'})
    except Exception as e:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Error clearing conversation: {e}")
        return web.json_response({'error': str(e)}, status=400)

app = web.Application()
app.router.add_post('/ask', handle_request)
app.router.add_post('/clear', clear_conversation)

if __name__ == '__main__':
    web.run_app(app, port=8080)