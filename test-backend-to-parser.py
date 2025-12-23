"""Test Backend -> Parser Service connection"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_connection():
    print("=" * 50)
    print("Testing Backend -> Parser Service connection")
    print("=" * 50)
    print()
    
    # Test 1: Direct httpx call
    print("[1/3] Testing direct httpx call...")
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "http://127.0.0.1:9003/parse",
                json={"keyword": "test", "depth": 1, "mode": "yandex"}
            )
            print(f"  [OK] Direct call: {response.status_code}")
            print(f"    Response: {response.text[:100]}")
    except Exception as e:
        print(f"  [FAIL] Direct call failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 2: Using ParserServiceClient
    print("[2/3] Testing ParserServiceClient...")
    try:
        from app.adapters.parser_client import ParserServiceClient
        client = ParserServiceClient()
        print(f"  Client base_url: {client.base_url}")
        
        result = await client.start_parse(
            keyword="test",
            depth=1,
            mode="yandex"
        )
        print(f"  [OK] ParserServiceClient works!")
        print(f"    Task ID: {result.get('task_id')}")
    except Exception as e:
        print(f"  [FAIL] ParserServiceClient failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 3: Check settings
    print("[3/3] Checking settings...")
    try:
        from app.config import settings
        print(f"  PARSER_SERVICE_URL: {settings.PARSER_SERVICE_URL}")
    except Exception as e:
        print(f"  [FAIL] Settings check failed: {e}")
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_connection())

