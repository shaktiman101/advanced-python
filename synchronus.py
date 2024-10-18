import concurrent.futures

def task(n):
    return n**2

with concurrent.futures.ThreadPoolExecutor() as executor:
    future = executor.submit(task, 5)
    result = future.result()
    print(result)