import asyncio
import logging
from typing import Set, Literal
from playwright.async_api import async_playwright, Browser, Playwright
from .engines import YandexEngine, GoogleEngine
from .config import settings

logger = logging.getLogger(__name__)

class SearchParser:
    """Основной класс парсера"""
    
    def __init__(self, cdp_endpoint: str = None):
        self.cdp_endpoint = cdp_endpoint or settings.cdp_endpoint
        self.browser: Browser = None
        self.playwright: Playwright = None
        
    async def connect(self):
        """Подключение к существующему браузеру через CDP"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(self.cdp_endpoint)
        logger.info(f"Подключено к браузеру через {self.cdp_endpoint}")
        return self.browser
    
    async def close(self):
        """Правильное закрытие соединения"""
        try:
            if self.browser:
                # НЕ закрываем браузер, только отключаемся
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.debug(f"Ошибка при закрытии: {e}")
    
    async def parse(
        self,
        keyword: str,
        depth: int,
        mode: Literal["yandex", "google", "both"]
    ) -> Set[str]:
        """Основной метод парсинга"""
        query = f"{keyword} купить"
        collected_links: Set[str] = set()
        
        logger.info(f"Начало парсинга: query='{query}', depth={depth}, mode={mode}")
        
        if not self.browser:
            await self.connect()
        
        contexts = self.browser.contexts
        if len(contexts) == 0:
            logger.error("Нет доступных контекстов браузера!")
            raise Exception("Браузер не имеет открытых контекстов")
        
        context = contexts[0]
        logger.info(f"Используем контекст с {len(context.pages)} открытыми страницами")
        
        # HTTP заголовки
        await context.set_extra_http_headers({
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        })
        
        tasks = []
        
        if mode in ["yandex", "both"]:
            yandex_page = await context.new_page()
            yandex_engine = YandexEngine()
            tasks.append(yandex_engine.parse(yandex_page, query, depth, collected_links))
        
        if mode in ["google", "both"]:
            google_page = await context.new_page()
            google_engine = GoogleEngine()
            tasks.append(google_engine.parse(google_page, query, depth, collected_links))
        
        await asyncio.gather(*tasks)
        
        logger.info(f"Парсинг завершен. Найдено {len(collected_links)} уникальных ссылок")
        
        return collected_links
