import asyncio
from aiohttp import web
from local_llm import LlamaLocalLLM
from memory import LocalConversationMemory
from datetime import datetime

# Same user database as Anthropic version
UserDataBase = {'Linda': 'Student',
                'Miguel': 'Counselor',
                'Mike': 'Athlete'}

# Initialize global memory and model instances
memory = LocalConversationMemory()
llm_model = None

async def initialize_model():
    """Initialize the local LLM model"""
    global llm_model
    llm_model = LlamaLocalLLM()
    await llm_model.initialize()
    print("Local LLM model initialized successfully!")

async def handle_request(request):
    global llm_model

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

        # Get response from local LLM using conversation history
        response = await llm_model.generate_response(system_message, messages)

        # Add LLM's response to memory
        memory.add_assistant_message(user, response)

        # Log response
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Responded to {user} with status code: 200")

        return web.json_response({'user': user, 'response': response})
    except Exception as e:
        # Log error
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Error occurred with status code: 400 - {str(e)}")
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

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        'status': 'healthy',
        'model_loaded': llm_model is not None,
        'timestamp': datetime.now().isoformat()
    })

async def init_app():
    """Initialize the web application"""
    # Initialize the model first
    await initialize_model()

    app = web.Application()
    app.router.add_post('/ask', handle_request)
    app.router.add_post('/clear', clear_conversation)
    app.router.add_get('/health', health_check)

    return app

if __name__ == '__main__':
    print("Starting Local LLM Server...")
    print("This may take a few minutes to download and load the model...")

    # Create and run the app
    app = init_app()
    web.run_app(app, port=8081)  # Different port from Anthropic server