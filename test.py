import asyncio
from elasticsearch import AsyncElasticsearch

async def test():
    client = AsyncElasticsearch(hosts=["http://localhost:9200"])
    print(await client.ping())
    await client.close()

asyncio.run(test())

