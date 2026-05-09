import asyncio
import time

TEST_QUERY = "ubuntu"

class DummyPlugin:
async def search(self, query):
return [
{
"title": "Ubuntu ISO",
"seeders": 120,
"size": "4.5 GB"
}
]

plugins = [DummyPlugin()]

async def test_plugin(plugin):
name = plugin.**class**.**name**

```
print(f"\nTesting {name}...")
start = time.time()

try:
    results = await plugin.search(TEST_QUERY)

    elapsed = round(time.time() - start, 2)

    if results and len(results) > 0:
        print(f"[WORKING] {name}")
        print(f"Results: {len(results)}")
        print(f"Time: {elapsed}s")

        first = results[0]

        print("Sample Result:")
        print(f"  Title: {first.get('title')}")
        print(f"  Seeders: {first.get('seeders')}")
        print(f"  Size: {first.get('size')}")

    else:
        print(f"[NO RESULTS] {name}")

except Exception as e:
    print(f"[FAILED] {name}")
    print(f"Error: {str(e)}")
```

async def main():
print("=" * 50)
print("Plugin Health Check")
print("=" * 50)

```
tasks = [test_plugin(plugin) for plugin in plugins]

await asyncio.gather(*tasks)
```

if **name** == "**main**":
asyncio.run(main())
