import httpx
import asyncio

async def test():
    client = httpx.AsyncClient(timeout=10.0)
    try:
        print("Testing parser service from backend context...")
        r = await client.post(
            'http://127.0.0.1:9003/parse',
            json={'keyword': 'test', 'depth': 1, 'mode': 'yandex'}
        )
        print(f'Status: {r.status_code}')
        print(f'Response: {r.text}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await client.aclose()

asyncio.run(test())


