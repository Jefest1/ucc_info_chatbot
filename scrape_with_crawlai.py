from langchain.document_loaders.base import BaseLoader
from langchain.docstore.document import Document
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.deep_crawling import DFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
    ContentTypeFilter
)

import asyncio
from pprint import pprint


class Crawl4AILoader(BaseLoader):
    def __init__(self, start_url: str, browser_config: BrowserConfig = None, run_config: CrawlerRunConfig = None):
        """
        Initialize the Crawl4AI document loader with pre-defined configuration values.

        Args:
            start_url (str): The URL to start crawling from.
            browser_config (BrowserConfig, optional): Browser configuration for crawl4ai.
              Defaults to a configuration with max_depth=5, following internal and external links,
              a maximum of 5 concurrent requests, and a custom user agent.
            run_config (CrawlerRunConfig, optional): Crawl run configuration controlling crawl behavior.
              Defaults to a configuration with word_count_threshold=200 and screenshot capture enabled.
        """
        self.start_url = start_url
        self.browser_config = browser_config
        self.run_config = run_config
        self._crawler = AsyncWebCrawler(config=self.browser_config)

    async def _crawl(self) -> list[Document]:
        """
        Private method to initiate crawling from the start_url and return a list of Document objects.
        """
        # Start the asynchronous crawler.
        await self._crawler.start()
        # filter chains

        # Run the crawler using the provided run_config.
        results_list = await self._crawler.arun(self.start_url, crawler_config=self.run_config)

        documents = []
        for result in results_list:
            # Each result should have properties such as URL and markdown content.
            metadata = {
                "url": getattr(result, "url", self.start_url)
            }
            content = getattr(result, "markdown", "")
            if content:
                documents.append(
                    Document(page_content=content, metadata=metadata))

        # Clean up crawler resources.
        await self._crawler.close()
        return documents

    async def aload(self) -> list[Document]:
        """
        Asynchronously load and return the list of Document objects representing crawled content.
        """
        return await self._crawl()

# Asynchronous main function to test the loader


async def return_docs():

    filter_chain = FilterChain([
        # Only follow URLs with specific patterns
        URLPatternFilter(patterns=["*admission-notices*", "*news*",
                         "*vcs-desk*", "*announcements*", "*press-releases"]),

        # Only crawl specific domains
        DomainFilter(allowed_domains=["cans.ucc.edu.gh", "ces.ucc.edu.gh"]),

        # Only include specific content types
        ContentTypeFilter(allowed_types=["text/html"])
    ])
    # crawler configurations
    run_config = CrawlerRunConfig(
        deep_crawl_strategy=DFSDeepCrawlStrategy(
            max_depth=1000,
            filter_chain=filter_chain,
            include_external=True
        ),
        excluded_tags=["form", "header", "footer"],
        keep_data_attributes=False,
        verbose=True
    )

    browser_config = BrowserConfig()
    loader = Crawl4AILoader("https://ucc.edu.gh/",
                            run_config=run_config, browser_config=browser_config)
    docs = await loader.aload()

    for doc in docs:
        print(f"URL: {doc.metadata.get('url')}")
        snippet = doc.page_content[:]
        pprint(f"Content snippet: {snippet}...")
        print("------------")

if __name__ == "__main__":
    asyncio.run(return_docs())
