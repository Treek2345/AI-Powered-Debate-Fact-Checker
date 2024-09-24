import aiohttp
import asyncio
from bs4 import BeautifulSoup
from cachetools import TTLCache
from aiolimiter import AsyncLimiter
import logging

class EfficientWebSearch:
    def __init__(self, cache_size=100, cache_ttl=3600, rate_limit=10):
        self.cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        self.limiter = AsyncLimiter(rate_limit, 1)  # 10 requests per second
        self.session = None
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def search(self, query, num_results=3, timeout=5):
        await self.initialize()  # Ensure session is initialized

        if query in self.cache:
            self.logger.info(f"Cache hit for query: {query}")
            return self.cache[query]

        async with self.limiter:
            try:
                url = f"https://duckduckgo.com/html/?q={query}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }

                async with self.session.get(url, headers=headers, timeout=timeout) as response:
                    if response.status != 200:
                        self.logger.error(f"HTTP error {response.status} for query: {query}")
                        return []
                    html = await response.text()

                soup = BeautifulSoup(html, 'html.parser')
                results = []
                for result in soup.find_all('div', class_='result__body')[:num_results]:
                    title_elem = result.find('h2', class_='result__title')
                    snippet_elem = result.find('a', class_='result__snippet')
                    link_elem = result.find('a', class_='result__url')

                    if title_elem and snippet_elem and link_elem:
                        title = title_elem.text.strip()
                        snippet = snippet_elem.text.strip()
                        link = link_elem.get('href', '')
                        # Extract the actual URL from the DuckDuckGo redirect
                        if link.startswith('/l/?kh=-1&uddg='):
                            link = link[15:]  # Remove the prefix

                        results.append({'title': title, 'snippet': snippet, 'link': link})

                if not results:
                    self.logger.warning(f"No results found for query: {query}")

                self.cache[query] = results
                return results

            except asyncio.TimeoutError:
                self.logger.error(f"Search timed out for query: {query}")
                return []

            except aiohttp.ClientError as e:
                self.logger.error(f"Network error during web search: {e}")
                return []

            except Exception as e:
                self.logger.error(f"Unexpected error during web search: {e}")
                return []

    async def batch_search(self, queries):
        await self.initialize()
        tasks = [self.search(query) for query in queries]
        return await asyncio.gather(*tasks)

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# Example usage (you can remove this if you don't need it)
async def main():
    async with EfficientWebSearch() as searcher:
        results = await searcher.search("Python programming")
        print(results)

if __name__ == "__main__":
    asyncio.run(main()) 