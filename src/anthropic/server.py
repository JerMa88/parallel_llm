import asyncio
from aiohttp import web
from call_llm import call_llm
from datetime import datetime

UserDataBase = {'Linda': 'Student',
                'Miguel': 'Counselor',
                'Mike': 'Athlete'}

async def handle_request(request):
    try:
        data = await request.json()
        user = data['user']
        question = data['question']
        
        if user not in UserDataBase:
            return web.json_response({'error': 'Unknown user'}, status=400)
            
        prompt = f'User {user} is a university {UserDataBase[user]}. Please assist this user with following question: \n{question}'
        
        # Log received prompt
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Received prompt: {prompt}")
        
        response = await call_llm(prompt)
        
        # Log response
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Responded with status code: 200")
        
        return web.json_response({'user': user, 'response': response})
    except Exception as e:
        # Log error
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Error occurred with status code: 400")
        return web.json_response({'error': str(e)}, status=400)

app = web.Application()
app.router.add_post('/ask', handle_request)

if __name__ == '__main__':
    web.run_app(app, port=8080)