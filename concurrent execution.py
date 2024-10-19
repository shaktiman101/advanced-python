import asyncio
import concurrent.futures
import time
from typing import List, Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CPU-bound function to run in ProcessPoolExecutor
def cpu_intensive_task(n: int) -> int:
    """Simulate CPU-intensive calculation"""
    result = 0
    for i in range(n * 1000000):
        result += i * i
    return result

# I/O-bound coroutine
async def io_task(delay: float) -> str:
    """Simulate I/O operation"""
    await asyncio.sleep(delay)
    return f"IO completed after {delay}s"

# Pattern 1: Run CPU-bound tasks in ProcessPoolExecutor from asyncio
async def run_cpu_tasks_in_process_pool(numbers: List[int]) -> List[int]:
    """Execute CPU-bound tasks in ProcessPoolExecutor while in asyncio event loop"""
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Use loop.run_in_executor to run CPU-bound tasks without blocking
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(executor, cpu_intensive_task, num)
            for num in numbers
        ]
        results = await asyncio.gather(*tasks)
        return results

# Pattern 2: Custom executor for mixing thread and async operations
async def run_mixed_tasks(
    io_delays: List[float],
    cpu_numbers: List[int]
) -> tuple[List[str], List[int]]:
    """Run both I/O and CPU-bound tasks concurrently"""
    # Create IO tasks
    io_tasks = [io_task(delay) for delay in io_delays]
    
    # Create CPU tasks using ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor() as process_executor:
        loop = asyncio.get_running_loop()
        cpu_tasks = [
            loop.run_in_executor(process_executor, cpu_intensive_task, num)
            for num in cpu_numbers
        ]
        
        # Wait for all tasks to complete
        io_results, cpu_results = await asyncio.gather(
            asyncio.gather(*io_tasks),
            asyncio.gather(*cpu_tasks)
        )
        
        return io_results, cpu_results

# Pattern 3: ThreadPoolExecutor for blocking I/O operations
async def run_blocking_io_in_threads(urls: List[str]) -> List[str]:
    """Execute blocking I/O operations in ThreadPoolExecutor"""
    def blocking_io(url: str) -> str:
        # Simulate blocking IO operation (e.g., requests.get)
        time.sleep(1)  # Simulating network delay
        return f"Data from {url}"
    
    with concurrent.futures.ThreadPoolExecutor() as thread_executor:
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(thread_executor, blocking_io, url)
            for url in urls
        ]
        results = await asyncio.gather(*tasks)
        return results

# Example usage
async def main():
    # Example 1: CPU-intensive tasks
    logger.info("Starting CPU-intensive tasks...")
    cpu_results = await run_cpu_tasks_in_process_pool([1, 2, 3])
    logger.info(f"CPU results: {cpu_results}")
    
    # Example 2: Mixed tasks
    logger.info("Starting mixed IO and CPU tasks...")
    io_results, cpu_results = await run_mixed_tasks(
        io_delays=[0.5, 1, 1.5],
        cpu_numbers=[1, 2]
    )
    logger.info(f"IO results: {io_results}")
    logger.info(f"CPU results: {cpu_results}")
    
    # Example 3: Blocking IO in threads
    logger.info("Starting blocking IO tasks in threads...")
    urls = ['http://example1.com', 'http://example2.com']
    io_results = await run_blocking_io_in_threads(urls)
    logger.info(f"Blocking IO results: {io_results}")

if __name__ == "__main__":
    asyncio.run(main())