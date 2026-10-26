import asyncio
import json
from datetime import datetime as dt
from pathlib import Path

import aiohttp
from aiohttp import ClientError, ClientResponseError
from bs4 import BeautifulSoup as bs
from yarl import URL

from logger import logger as to_log


class HtmlLoader:
    def __init__(self):
        self.http_client = aiohttp.ClientSession()

    async def __call__(self, url):
        try:
            async with self.http_client.get(url) as response:
                return await response.text(encoding="utf-8")
        except ClientResponseError as e:
            to_log.info(f"HTTP Error: {e.status} - {e.message}")
            return None
        except ClientError as e:
            to_log.info(f"Network error: {str(e)}")
            return None
        except asyncio.TimeoutError:
            to_log.info(f"Request timeout error")
            return None
        except Exception as e:
            to_log.info(f"Other error: {str(e)}")
            return None
        finally:
            await self.http_client.close()


async def fetch_page(url):
    site = HtmlLoader()
    return await site(url=url)


def parse_topics(source_page: str):
    res = []
    html_parser = bs(source_page, "lxml")
    items = html_parser.select(selector=".athing.submission")

    for item in items:
        title_news = item.select(".title a")
        title = title_news[0].text if len(title_news) > 0 else None
        title_id = str(item.get("id")) if item.has_attr("id") else None
        res.append((title, title_id))
    return res


def parse_topic_links(source_page):
    link_parser = bs(source_page, "lxml")
    items = link_parser.select(selector=".commtext a ")
    links = []
    for item in items:
        if item.has_attr("href"):
            links.append(str(item.get("href")))
    return links


async def get_topic_urls(url, id_topic, title):
    url = str(URL(url).join(URL("item")).with_query(id=id_topic))

    html = await fetch_page(url=url)
    links = parse_topic_links(html)
    return title, links


async def parse_worker(url):
    topics = parse_topics(source_page=(await fetch_page(url=url)))

    async_tasks = []
    for title, id in topics:
        task = asyncio.create_task(get_topic_urls(url=url, id_topic=id, title=title))
        async_tasks.append(task)

    gathers = await asyncio.gather(return_exceptions=True, *async_tasks)
    list_res = []

    for item in gathers:
        if isinstance(item, Exception):
            to_log.error("Exception error: %s", item)
            continue
        else:
            list_res.append(item)
    return list_res


def save_to_file(data, dir):
    dir = Path(dir)
    dir.mkdir(parents=True, exist_ok=True)
    path = dir / (dt.now().strftime("%Y%m%d_%H_%M_%S") + ".json")

    try:
        with open(file=path, mode="w", encoding="utf-8") as f:
            json.dump(data, f)
            json.dump(data, ensure_ascii=False, indent=2, fp=f)
    except Exception as e:
        to_log.exception("Error! Data not saved to file! %s", e)


async def parsing_loop(args, url):
    while True:
        res = await parse_worker(url=url)
        save_to_file(data=res, dir=args.dir)
        await asyncio.sleep(args.time)
