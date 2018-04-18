import asyncio
import re
from datetime import datetime

import aiohttp


from .log import logger

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


async def fetch(url, spider, session, semaphore):
    with (await semaphore):
        try:
            if callable(spider.headers):
                headers = spider.headers()
            else:
                headers = spider.headers
            async with session.get(url, headers=headers, proxy=spider.proxy) as response:
                if response.status in [200, 201]:
                    data = await response.text()
                    return data
                logger.error('Error: {} {}'.format(url, response.status))
                return None
        except:
            return None


class Spider:
    url_list = []
    parsers = []
    error_urls = []
    urls_count = 0
    concurrency = 10
    interval = None #Todo: Limit the interval between two requests
    headers = {}
    proxy = None
    cookie_jar = None

    @classmethod
    def is_running(cls):
        is_running = False
        for parser in cls.parsers:
            if not parser.pre_parse_urls.empty() or len(parser.parsing_urls) > 0:
                is_running = True
        return is_running

    @classmethod
    def parse(cls, html):
        # print(html)
        pass

    @classmethod
    def run(cls):
        logger.info('Spider started!')
        start_time = datetime.now()
        loop = asyncio.get_event_loop()

        try:
            cls.semaphore = asyncio.Semaphore(cls.concurrency)
            tasks = asyncio.wait([cls.init_parse(url) for url in cls.url_list])
            loop.run_until_complete(tasks)
        except KeyboardInterrupt:
            for task in asyncio.Task.all_tasks():
                task.cancel()
            loop.run_forever()
        finally:
            end_time = datetime.now()
            for parser in cls.parsers:
                if parser.item is not None:
                    logger.info('Item "{}": {}'.format(parser.item.name, parser.item.count))
            logger.info('Requests count: {}'.format(cls.urls_count))
            logger.info('Error count: {}'.format(len(cls.error_urls)))
            logger.info('Time usage: {}'.format(end_time - start_time))
            logger.info('Spider finished!')
            loop.close()

    @classmethod
    async def init_parse(cls, url):
        async with aiohttp.ClientSession(cookie_jar=cls.cookie_jar) as session:
            logger.info('session in')
            logger.info('spider url: {}'.format(url))
            html = await fetch(url, cls, session, cls.semaphore)
            cls.parse(html)