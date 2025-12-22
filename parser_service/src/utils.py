from typing import Set
import logging

logger = logging.getLogger(__name__)

def save_links(links: Set[str], filename: str = "results.txt"):
    """Сохранение ссылок в файл"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for link in sorted(links):
                f.write(link + "\n")
        logger.info(f"Сохранено {len(links)} ссылок в {filename}")
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

def setup_logging(log_file: str = "parser.log"):
    """Настройка логирования"""
    logging.basicConfig(
        filename=log_file,
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    logging.getLogger("").addHandler(console)
