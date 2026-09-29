import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://localhost:8000/api/nonexistent")
        print(resp.status_code, resp.text)
        
asyncio.run(main())
