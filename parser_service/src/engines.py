import logging
from typing import Set
import time
from playwright.async_api import Page
from .human_behavior import (
    human_pause,
    very_human_behavior,
    light_human_behavior,
    wait_for_captcha,
)

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self, name: str):
        self.name = name
    
    async def parse(self, page: Page, query: str, depth: int, collected_links: Set[str]):
        raise NotImplementedError

class YandexEngine(SearchEngine):
    def __init__(self):
        super().__init__("YANDEX")
    
    async def parse(self, page: Page, query: str, depth: int, collected_links: Set[str]):
        start_time = time.time()
        logger.info(f"{self.name}: Начало парсинга '{query}'")
        print(f"\n[*] {self.name}: Старт парсинга...")
        
        initial_count = len(collected_links)
        
        # НОВОЕ: Устанавливаем дополнительные заголовки для Яндекса
        await page.set_extra_http_headers({
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        })
        
        await human_pause(2, 4)
        
        await page.goto(
            f"https://yandex.ru/search/?text={query.replace(' ', '+')}",
            wait_until="networkidle"  # Ждём полной загрузки
        )
        await wait_for_captcha(page, self.name)
        
        for n in range(1, depth + 1):
            print(f"[PAGE] {self.name}: страница {n}/{depth}")
            
            await very_human_behavior(page)
            await human_pause(2, 4)
            await wait_for_captcha(page, self.name)
            
            elems = page.locator("a.Link")
            count = await elems.count()
            
            for i in range(count):
                try:
                    href = await elems.nth(i).get_attribute("href")
                    if href and href.startswith("http") and ".ru" in href:
                        collected_links.add(href.split("?")[0])
                except:
                    pass
            
            if n < depth:
                next_btn = page.locator("a[aria-label='Следующая страница']")
                if await next_btn.count() == 0:
                    break
                
                # УВЕЛИЧЕННАЯ пауза между страницами
                await human_pause(7, 15)  # Было 5-12
                await next_btn.click()
                await human_pause(3, 5)
                await wait_for_captcha(page, self.name)
        
        elapsed = time.time() - start_time
        new_links = len(collected_links) - initial_count
        print(f"[OK] {self.name}: Собрано {new_links} ссылок за {elapsed:.1f} сек ({elapsed/60:.1f} мин)\n")
        logger.info(f"{self.name}: Завершено за {elapsed:.1f}с, собрано {new_links} ссылок")

class GoogleEngine(SearchEngine):
    def __init__(self):
        super().__init__("GOOGLE")
    
    async def parse(self, page: Page, query: str, depth: int, collected_links: Set[str]):
        start_time = time.time()
        logger.info(f"{self.name}: Начало парсинга '{query}'")
        print(f"\n[*] {self.name}: Старт парсинга...")
        
        initial_count = len(collected_links)
        
        await page.goto(
            f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=ru",
            timeout=60000,
            wait_until="domcontentloaded"
        )
        await wait_for_captcha(page, self.name)
        
        for n in range(1, depth + 1):
            print(f"[PAGE] {self.name}: страница {n}/{depth}")
            
            await light_human_behavior(page)
            await wait_for_captcha(page, self.name)
            
            elems = page.locator("a")
            count = await elems.count()
            
            for i in range(count):
                try:
                    href = await elems.nth(i).get_attribute("href")
                    if (href and href.startswith("http") and 
                        ".ru" in href and "google" not in href):
                        collected_links.add(href.split("&")[0])
                except:
                    pass
            
            if n < depth:
                next_btn = page.locator("a#pnnext")
                if await next_btn.count() == 0:
                    break
                
                await human_pause(2, 5)
                await next_btn.click()
                await wait_for_captcha(page, self.name)
        
        elapsed = time.time() - start_time
        new_links = len(collected_links) - initial_count
        print(f"[OK] {self.name}: Собрано {new_links} ссылок за {elapsed:.1f} сек ({elapsed/60:.1f} мин)\n")
        logger.info(f"{self.name}: Завершено за {elapsed:.1f}с, собрано {new_links} ссылок")
