import asyncio
import random
import logging
import os
from playwright.async_api import Page

logger = logging.getLogger(__name__)

async def human_pause(a: float = 1.5, b: float = 4.5):
    await asyncio.sleep(random.uniform(a, b))

async def human_scroll(page: Page):
    actions = [
        lambda: page.mouse.wheel(0, random.randint(200, 600)),
        lambda: page.mouse.wheel(0, random.randint(-300, -100)),
        lambda: page.mouse.wheel(0, random.randint(50, 150)),
    ]
    for _ in range(random.randint(1, 3)):
        await actions[random.randint(0, len(actions) - 1)]()
        await human_pause(0.4, 1.2)

async def human_mouse_movement(page: Page):
    x = random.randint(100, 900)
    y = random.randint(100, 700)
    for _ in range(random.randint(2, 6)):
        xr = x + random.randint(-30, 30)
        yr = y + random.randint(-30, 30)
        await page.mouse.move(xr, yr, steps=random.randint(6, 22))
        await human_pause(0.2, 0.6)

async def very_human_behavior(page: Page):
    await human_pause()
    await human_mouse_movement(page)
    await human_pause(0.5, 2)
    await human_scroll(page)
    await human_pause(1, 3)

async def light_human_behavior(page: Page):
    await human_pause(0.5, 1.5)
    await human_scroll(page)
    await human_pause(0.5, 1.2)

async def human_type_text(page: Page, selector: str, text: str):
    await page.click(selector)
    await human_pause(0.3, 0.8)
    for char in text:
        await page.keyboard.type(char)
        await asyncio.sleep(random.uniform(0.05, 0.12))
    await human_pause(0.3, 0.8)

async def wait_for_captcha(page: Page, engine_name: str):
    """Ожидание капчи с принудительной активацией окна"""
    captcha_detected = False
    
    while True:
        url = page.url.lower()
        if "captcha" in url or "showcaptcha" in url:
            if not captcha_detected:
                # Playwright активация
                try:
                    await page.bring_to_front()
                    await page.evaluate("() => { window.focus(); }")
                except:
                    pass
                
                # ПРИНУДИТЕЛЬНАЯ активация через PowerShell
                try:
                    ps_cmd = '''
                    $w = Get-Process chrome | Where {$_.MainWindowTitle -ne ""} | Select -First 1;
                    if ($w) {
                        $sig = '[DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr h); [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr h, int c);';
                        $t = Add-Type -MemberDefinition $sig -Name Win32 -Namespace Native -PassThru;
                        $t::ShowWindow($w.MainWindowHandle, 9);
                        $t::SetForegroundWindow($w.MainWindowHandle);
                    }
                    '''
                    os.system(f'powershell -WindowStyle Hidden -Command "{ps_cmd}"')
                except:
                    pass
                
                captcha_detected = True
                logging.warning(f"{engine_name}: Капча!")
                print(f"\n{'='*60}")
                print(f"🔔🔔🔔 {engine_name}: КАПЧА ОБНАРУЖЕНА!")
                print(f"{'='*60}\n")
                print("\a" * 3)  # 3 звуковых сигнала
            
            await asyncio.sleep(2)
        else:
            if captcha_detected:
                print(f"\n✅ {engine_name}: Капча решена! Продолжаем...\n")
            break
