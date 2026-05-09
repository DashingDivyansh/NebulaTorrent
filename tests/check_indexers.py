import sys
import os
import asyncio
import traceback

# Add src/backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, '..', 'src', 'backend')
sys.path.append(backend_path)

# Mock logger to avoid issues if not fully configured
from logger import logger

from search.dispatcher import SearchDispatcher

async def check_indexers():
    plugins_dir = os.path.join(backend_path, 'plugins')
    dispatcher = SearchDispatcher(plugins_dir=plugins_dir)
    
    print(f"Loading plugins from {plugins_dir}...")
    dispatcher.load_plugins()
    
    if not dispatcher.plugins:
        print("No plugins found!")
        return
        
    print(f"Loaded {len(dispatcher.plugins)} plugins.\n")
    
    query = "ubuntu"
    results_report = {}
    
    # Run tests in parallel to be faster, but let's do them sequentially for clearer logging first
    # or use gather for speed.
    
    print(f"Searching for '{query}' across all indexers...\n")
    
    async def check_plugin(plugin):
        name = plugin.name
        print(f"[ ] Testing {name}...")
        try:
            # We need to peek into the response for Nyaa and others
            # But search() usually returns TorrentResult objects, not the raw response.
            # So we might need to modify the plugin or use a different approach.
            # For now, let's just catch the error and try to print more if it's Nyaa.
            
            results = await asyncio.wait_for(plugin.search(query), timeout=15.0)
            count = len(results)
            status = "WORKING" if count > 0 else "NO RESULTS"
            print(f"[+] {name}: {status} ({count} results)")
            return name, {"status": status, "count": count, "error": None}
        except asyncio.TimeoutError:
            print(f"[-] {name}: TIMEOUT (Likely ISP Block or Cloudflare)")
            return name, {"status": "TIMEOUT", "count": 0, "error": "Timeout after 15s"}
        except Exception as e:
            print(f"[-] {name}: FAILED ({str(e)})")
            return name, {"status": "FAILED", "count": 0, "error": str(e)}

    # Run all checks
    tasks = [check_plugin(p) for p in dispatcher.plugins]
    reports = await asyncio.gather(*tasks)
    
    results_report = dict(reports)

    print("\n" + "="*40)
    print(f"{'INDEXER':<20} | {'STATUS':<12} | {'RESULTS'}")
    print("-" * 40)
    
    for name, report in sorted(results_report.items()):
        status = report['status']
        count = report['count']
        print(f"{name:<20} | {status:<12} | {count}")
    
    print("="*40)

if __name__ == "__main__":
    try:
        asyncio.run(check_indexers())
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        traceback.print_exc()
