import os
import aiofiles
import asyncio
from pocketflow import AsyncFlow, AsyncParallelBatchNode
import asyncio
from dataclasses import dataclass
from typing import Dict, Any

from call_llm import call_llm

@dataclass
class UserRequest:
    user: str
    question: str
    response_queue: asyncio.Queue  # To send response back to client

UserDataBase = {'Linda': 'Student',
                'Miguel': 'Counselor',
                'Mike': 'Athlete'}

class RequestHandler:
    def __init__(self):
        self.request_queue = asyncio.Queue()
        self.batch_size = 3  # Process requests in batches
        self.processing = False

    async def add_request(self, user: str, question: str) -> Dict[str, Any]:
        # Create response queue for this specific request
        response_queue = asyncio.Queue()
        await self.request_queue.put(UserRequest(user, question, response_queue))
        
        # Wait for response
        response = await response_queue.get()
        return response

    async def process_requests(self):
        self.processing = True
        while self.processing:
            batch = []
            try:
                # Collect batch_size requests or wait for 2 seconds
                while len(batch) < self.batch_size:
                    try:
                        request = await asyncio.wait_for(self.request_queue.get(), timeout=2.0)
                        batch.append(request)
                    except asyncio.TimeoutError:
                        break

                if batch:
                    # Process batch with ParallelNode
                    node = ParallelNode()
                    shared = {
                        "requests": batch
                    }
                    results = await node.process(shared)
                    
                    # Send responses back to clients
                    for request, result in zip(batch, results):
                        await request.response_queue.put(result)
                        
            except Exception as e:
                print(f"Error processing batch: {e}")

class ParallelNode(AsyncParallelBatchNode):
    '''Takes multiple user calls and return llm response in parallel
        Workflow: prep, exec, clean up.    
    '''
    async def prep_async(self, shared):
        requests = shared.get("requests", [])
        return [(req.question, req.user) for req in requests]
    
    async def exec_async(self, one_job_tuple):
        '''Handle request for ONE user only. Runs concurrently for all users'''
        user_prompt, user = one_job_tuple
        print(f'     Handling prompt with length {len(user_prompt)} for {user}')
        prompt = f'User {user} is a university {UserDataBase[user]}. Please assist this user with following question: \n{user_prompt}'
        response = await call_llm(prompt)

        return {'user': user, 'response': response}
    
    async def post_async(self, shared, prep_res, list_of_all_results):
        return list_of_all_results

