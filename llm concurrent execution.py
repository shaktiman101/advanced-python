import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Agent:
    id: str
    name: str
    status: str
    last_active: datetime

class AsyncAgentManager:
    def __init__(self, 
                 max_concurrent_calls: int = 5,
                 rate_limit_calls: int = 20,
                 rate_limit_period: int = 60):
        """
        Initialize the async agent manager with rate limiting and concurrency control
        
        Args:
            max_concurrent_calls: Maximum number of concurrent LLM API calls
            rate_limit_calls: Maximum number of calls allowed in the rate limit period
            rate_limit_period: Rate limit period in seconds
        """
        self.semaphore = asyncio.Semaphore(max_concurrent_calls)
        self.rate_limit_calls = rate_limit_calls
        self.rate_limit_period = rate_limit_period
        self.call_timestamps: List[float] = []
        self.agents: Dict[str, Agent] = {}
        
        # For any blocking operations
        self.thread_pool = ThreadPoolExecutor()
        
        # Shared session for all HTTP requests
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.thread_pool.shutdown()

    async def _enforce_rate_limit(self):
        """Enforce rate limiting for API calls"""
        current_time = time.time()
        
        # Remove timestamps older than the rate limit period
        self.call_timestamps = [
            ts for ts in self.call_timestamps 
            if current_time - ts < self.rate_limit_period
        ]
        
        if len(self.call_timestamps) >= self.rate_limit_calls:
            # Calculate sleep time needed to satisfy rate limit
            sleep_time = self.call_timestamps[0] + self.rate_limit_period - current_time
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, waiting {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
        
        self.call_timestamps.append(current_time)

    async def _make_llm_call(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Make an async LLM API call with rate limiting and retries"""
        async with self.semaphore:  # Limit concurrent calls
            await self._enforce_rate_limit()
            
            for attempt in range(3):  # Retry logic
                try:
                    # Simulated LLM API call - replace with your actual LLM API
                    async with self.session.post(
                        "https://your-llm-api-endpoint/v1/completions",
                        json={"prompt": prompt, **kwargs},
                        timeout=30
                    ) as response:
                        if response.status == 429:  # Rate limit exceeded
                            retry_after = int(response.headers.get('Retry-After', 60))
                            await asyncio.sleep(retry_after)
                            continue
                            
                        response.raise_for_status()
                        return await response.json()
                        
                except aiohttp.ClientError as e:
                    if attempt == 2:  # Last attempt
                        raise
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
    async def process_agent_task(self, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single agent task"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
            
        agent.status = "processing"
        agent.last_active = datetime.now()
        
        try:
            # Make the LLM call
            result = await self._make_llm_call(
                prompt=task['prompt'],
                temperature=task.get('temperature', 0.7),
                max_tokens=task.get('max_tokens', 150)
            )
            
            # Process the result
            processed_result = await self._process_llm_result(result)
            
            agent.status = "idle"
            return processed_result
            
        except Exception as e:
            agent.status = "error"
            logger.error(f"Error processing task for agent {agent_id}: {str(e)}")
            raise

    async def _process_llm_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process the LLM result, potentially using ThreadPoolExecutor for CPU-intensive operations"""
        if self._is_cpu_intensive_processing_needed(result):
            loop = asyncio.get_running_loop()
            # Run CPU-intensive processing in thread pool
            return await loop.run_in_executor(
                self.thread_pool,
                self._cpu_intensive_processing,
                result
            )
        return result

    def _is_cpu_intensive_processing_needed(self, result: Dict[str, Any]) -> bool:
        """Determine if CPU-intensive processing is needed"""
        # Add your logic here
        return False

    def _cpu_intensive_processing(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle any CPU-intensive processing in a thread pool"""
        # Add your CPU-intensive processing here
        return result

    async def process_multiple_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple agent tasks concurrently"""
        coroutines = [
            self.process_agent_task(task['agent_id'], task)
            for task in tasks
        ]
        return await asyncio.gather(*coroutines, return_exceptions=True)

# Example usage
async def main():
    async with AsyncAgentManager(
        max_concurrent_calls=5,
        rate_limit_calls=20,
        rate_limit_period=60
    ) as manager:
        # Register some agents
        manager.agents = {
            "agent1": Agent("agent1", "Assistant 1", "idle", datetime.now()),
            "agent2": Agent("agent2", "Assistant 2", "idle", datetime.now())
        }
        
        # Example tasks
        tasks = [
            {
                "agent_id": "agent1",
                "prompt": "Analyze this data...",
                "temperature": 0.7
            },
            {
                "agent_id": "agent2",
                "prompt": "Summarize this text...",
                "temperature": 0.5
            }
        ]
        
        # Process tasks
        results = await manager.process_multiple_tasks(tasks)
        logger.info(f"Processed {len(results)} tasks")

if __name__ == "__main__":
    asyncio.run(main())