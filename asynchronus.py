import asyncio

async def task(n):
    await asyncio.sleep(1)
    return n**2

async def main():
    # result = await task(5)
    # print(result)
    print(await task(5))
    
asyncio.run(main())