import time 
import asyncio
import random
import concurrent.futures


def blocking_task(n):
    print(f"Starting blocking task {n}")
    time.sleep(n)
    return f"Blocking task {n} completed"
    
async def non_blocking_task(n):
    print(f"Starting non-blocking task {n}")
    await asyncio.sleep(n)
    return f"Non-blocking task {n} completed"
    
async def process_tasks(n):
    blocking_task(n)
    await non_blocking_task(n)
    
async def main(tasks):
    # ----------------------------------------------------------------------------------------------------------- #
        
    # process tasks individually
    # st_time = time.time()
    # # blocking task
    # for task in tasks:
    #     blocking_task(task)
    # print(f"Total time taken for blocking tasks: {time.time() - st_time}")
    
    # st_time = time.time()
    # # non-blocking task
    # for task in tasks:
    #     await non_blocking_task(task)
    # print(f"Total time taken for non-blocking tasks: {time.time() - st_time}")

    # ----------------------------------------------------------------------------------------------------------- #
    
    # st_time = time.time()
    # for task in tasks:
    #     blocking_task(task)
    #     await non_blocking_task(task)
    # print(f"Total time taken for blocking & non-blocking tasks: {time.time() - st_time}")
    
    # ----------------------------------------------------------------------------------------------------------- #
    
    # st_time = time.time()
    # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    #     futures = [executor.submit(blocking_task, task) for task in tasks]
        
    # print(f"Total time taken for blocking tasks using ThreadPoolExecutor: {time.time() - st_time}") 
    
    # st_time = time.time()
    # # non-blocking task
    # for task in tasks:
    #     await non_blocking_task(task)
    # print(f"Total time taken for non-blocking tasks: {time.time() - st_time}")
    
    # ----------------------------------------------------------------------------------------------------------- #
    
    # st_time = time.time()
    # for task in tasks:
    #     blocking_task(task)
    # print(f"Total time taken for blocking tasks: {time.time() - st_time}")
    
    # st_time = time.time()
    # tasks_to_execute = [non_blocking_task(task) for task in tasks]
    # await asyncio.gather(*tasks_to_execute)
    # print(f"Total time taken for non-blocking tasks: {time.time() - st_time}")
    
    # # ----------------------------------------------------------------------------------------------------------- #
    
    # st_time = time.time()
    # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    #     futures = [executor.submit(blocking_task, task) for task in tasks]
    # print(f"Total time taken for blocking tasks using ThreadPoolExecutor: {time.time() - st_time}")
    
    # st_time = time.time()
    # tasks_to_execute = [non_blocking_task(task) for task in tasks]
    # await asyncio.gather(*tasks_to_execute)
    # print(f"Total time taken for non-blocking tasks: {time.time() - st_time}")
    
    # ----------------------------------------------------------------------------------------------------------- #
    
    st_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        nonblocking_tasks_to_execute = [non_blocking_task(task) for task in tasks]
        blocking_task_to_execute = [
            loop.run_in_executor(executor, blocking_task, task)
            for task in tasks
        ]
        nonblocking_results = await asyncio.gather(
            asyncio.gather(*nonblocking_tasks_to_execute)
        )
        print(nonblocking_results)
        
        blocking_results = await asyncio.gather(
            asyncio.gather(*blocking_task_to_execute)
        )
        print(blocking_results)
        
    print(f"Total time taken for non-blocking tasks: {time.time() - st_time}")
    
    
if __name__ == "__main__":
    st_time = time.time()
    tasks = [3, 1, 2, 5, 4]
    asyncio.run(main(tasks))
    print(f"Total time taken: {time.time() - st_time}")