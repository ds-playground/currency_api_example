import httpx

class HTTPClient:
    @staticmethod
    async def get(url):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
