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
        self._playwright_started = False
        
    async def connect(self):
        """Подключение к существующему браузеру через CDP"""
        try:
            # Check if CDP endpoint is available before connecting
            import httpx
            try:
                # Chrome CDP blocks Python HTTP libraries, so use subprocess to call curl
                import subprocess
                import json
                result = subprocess.run(
                    ["curl", "-s", "-m", "5", f"{self.cdp_endpoint}/json/version"],
                    capture_output=True,
                    text=True,
                    timeout=6
                )
                if result.returncode == 0 and result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        if "Browser" not in data:
                            raise Exception("CDP response missing Browser field")
                        logger.info(f"CDP endpoint is available: {self.cdp_endpoint}")
                    except json.JSONDecodeError:
                        raise Exception("CDP response is not valid JSON")
                else:
                    raise Exception(f"curl returned code {result.returncode}: {result.stderr}")
            except Exception as cdp_check_err:
                error_msg = f"Chrome CDP is not available at {self.cdp_endpoint}. Please start Chrome with --remote-debugging-port=9222. Error: {cdp_check_err}"
                logger.error(error_msg)
                raise Exception(error_msg) from cdp_check_err
            
            # Start playwright only if not already started
            if not self._playwright_started:
                self.playwright = await async_playwright().start()
                self._playwright_started = True
            
            # Connect to existing Chrome via CDP
            self.browser = await self.playwright.chromium.connect_over_cdp(self.cdp_endpoint)
            logger.info(f"Подключено к браузеру через {self.cdp_endpoint}")
            return self.browser
        except Exception as e:
            logger.error(f"Ошибка подключения к CDP: {e}")
            raise
    
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
            logger.warning("Нет доступных контекстов браузера, создаем новый контекст")
            # Create a new browser context with small window size (not fullscreen)
            # Window will be maximized only when captcha is detected
            context = await self.browser.new_context(
                viewport={"width": 800, "height": 600},
                no_viewport=False
            )
            logger.info("Создан новый контекст браузера (размер окна: 800x600)")
        else:
            context = contexts[0]
            logger.info(f"Используем существующий контекст с {len(context.pages)} открытыми страницами")
            
            # Ensure existing pages have small viewport if not set
            for page in context.pages:
                try:
                    current_viewport = await page.viewport_size()
                    if current_viewport is None or current_viewport.get("width", 0) > 1200:
                        await page.set_viewport_size({"width": 800, "height": 600})
                except:
                    pass
        
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
