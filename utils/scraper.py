import asyncio
import logging
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.deep_crawling import DFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import FilterChain, DomainFilter, ContentTypeFilter
from langchain.docstore.document import Document
from dedup import is_duplicate

logger = logging.getLogger(__name__)


class Crawl4AILoader:
    def __init__(self, run_config: CrawlerRunConfig = None, browser_config: BrowserConfig = None):
        """Initialize the Crawl4AI document loader with improved configuration.

        Args:
            run_config (CrawlerRunConfig, optional): Custom run configuration. Defaults to None.
            browser_config (BrowserConfig, optional): Custom browser configuration. Defaults to None.
        """
        # Set up improved browser configuration
        if browser_config is None:
            browser_config = BrowserConfig()
        self.browser = AsyncWebCrawler(config=browser_config)

        # Set up improved run configuration
        if run_config is None:
            filter_chain = FilterChain([
                DomainFilter(allowed_domains=["ucc.edu.gh", "*.ucc.edu.gh"]),
                ContentTypeFilter(allowed_types=["text/html"])
            ])
            
            run_config = CrawlerRunConfig(
                deep_crawl_strategy=DFSDeepCrawlStrategy(
                    max_depth=1000,  
                    filter_chain=filter_chain,
                    include_external=True 
                ),  
                keep_data_attributes=False,
                verbose=True
            )
        self.run_config = run_config

    async def crawl_urls(self, urls: list[str]) -> list[Document]:
        """Crawl multiple URLs and extract content.

        Args:
            urls (list[str]): List of URLs to crawl.

        Returns:
            list[Document]: List of documents with extracted content.
        """
        await self.browser.start()

        docs: list[Document] = []

        for url in urls:
            try:
                logger.info("Crawling %s", url)
                results = await self.browser.arun(url, crawler_config=self.run_config)
                for res in results:
                    content = getattr(res, "markdown")
                    if content:
                        metadata = {"url": getattr(res, "url", url)}
                        docs.append(Document(
                            page_content=content,
                            metadata=metadata
                        ))
                
            except Exception as e:
                logger.error("Error crawling %s: %s", url, str(e))
        
        await self.browser.close()
        logger.info("Crawling completed. Found %d unique documents from %d URLs", 
                   len(docs), len(urls))
        return docs


def run_crawl(urls: list[str]) -> list[Document]:
    """Synchronous wrapper for crawling URLs.

    Args:
        urls (list[str]): List of URLs to crawl.

    Returns:
        list[Document]: List of documents with extracted content.
    """
    return asyncio.run(Crawl4AILoader().crawl_urls(urls))
