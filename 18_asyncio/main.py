import asyncio
import os
from datetime import datetime
from uuid import uuid4

import aiofiles
import aiohttp
import aiohttp.web_exceptions
import bs4
from loguru import logger

parced = set()
headers = {
    "accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53",
    "Accept-Language": "en-US,en;q=0.9,it;q=0.8,es;q=0.7",
    "referer": "https://www.google.com/",
    "cookie": "DSID=AAO-7r4OSkS76zbHUkiOpnI0kk-X19BLDFF53G8gbnd21VZV2iehu-w_2v14cxvRvrkd_NjIdBWX7wUiQ66f-D8kOkTKD1BhLVlqrFAaqDP3LodRK2I0NfrObmhV9HsedGE7-mQeJpwJifSxdchqf524IMh9piBflGqP0Lg0_xjGmLKEQ0F4Na6THgC06VhtUG5infEdqMQ9otlJENe3PmOQTC_UeTH5DnENYwWC8KXs-M4fWmDADmG414V0_X0TfjrYu01nDH2Dcf3TIOFbRDb993g8nOCswLMi92LwjoqhYnFdf1jzgK0",
}


async def save_page(page: str, filename: str, path: str | None = ""):
    if path and not os.path.exists(path):
        os.makedirs(path)
    filename = filename.replace(" ", "_")
    if len(filename) > 15:
        filename = filename[:15] + "<cut>"
    async with aiofiles.open(f"{path}{filename}.html", mode="w") as f:
        await f.writelines(page)


async def download_page(url):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url, headers=headers)
        if resp.status != 200:
            logger.error(
                f"\nURL: {url}\n Code: {resp.status} | Body:\n {(await resp.text())[:500]}..."
            )
            return
        try:
            page = await resp.text()
        except UnicodeDecodeError as e:
            logger.error(f"\nURL: {url}\nUnicodeDecodeError: {e}")
            return
        except aiohttp.ClientConnectorError as e:
            logger.error(f"\nURL: {url}\nClientConnectorError: {e}")
            return
    return page


async def download_and_save(url: str, comment_page_id: str):
    page = await download_page(url)
    if not page:
        return
    soap = bs4.BeautifulSoup(page, "html.parser")
    title = soap.find("title")

    await save_page(
        page,
        title.get_text() if title else str(uuid4()),
        f"./files/{comment_page_id}/comments_pages/",
    )


async def parse_news_item_comments(page_id: str):
    comments_page = await download_page(
        f"https://news.ycombinator.com/item?id={page_id}"
    )
    if not comments_page:
        return

    soap = bs4.BeautifulSoup(comments_page, "html.parser")
    tasks = []
    for link in soap.find_all("a", attrs={"rel": "nofollow"}):
        if link.get("href") and link.get("href").startswith("http"):
            tasks.append(
                asyncio.create_task(download_and_save(link.get("href"), page_id))
            )
    await asyncio.gather(*tasks)


async def parse_news_item(page_id: str, url: str):
    news_item_page = await download_page(url)
    if not news_item_page:
        return
    soap = bs4.BeautifulSoup(news_item_page, "html.parser")

    title = soap.find("title")
    await save_page(
        news_item_page, title.get_text() if title else page_id, f"./files/{page_id}/"
    )
    await parse_news_item_comments(page_id)
    parced.add(page_id)


def parse_main_page(soap: bs4.BeautifulSoup):
    news = {}
    for item in soap.find_all("tr", class_="athing"):
        page_id = item.get("id")
        link = item.find("span", class_="titleline").find("a").get("href")
        news[page_id] = link
    return news


async def main():
    while True:
        l1 = len(parced)
        main_page = await download_page("https://news.ycombinator.com/")
        if not main_page:
            raise RuntimeError("No main page recieved")
        news = parse_main_page(bs4.BeautifulSoup(main_page, "html.parser"))
        tasks = []
        for page_id, url in news.items():
            if page_id not in parced:
                tasks.append(asyncio.create_task(parse_news_item(page_id, url)))
        await asyncio.gather(*tasks)
        logger.info(
            f"Crawling ended on {datetime.now().isoformat()}\nCollected: {len(parced) - l1}"
        )
        await asyncio.sleep(30)
        return


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped by Ctrl+C")
