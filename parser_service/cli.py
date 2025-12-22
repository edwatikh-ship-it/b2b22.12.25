import asyncio
import typer
from typing_extensions import Annotated
from src.parser import SearchParser
from src.utils import save_links, setup_logging
from src.config import settings

app = typer.Typer(help="Search Parser - Парсер поисковиков Яндекс и Google")

@app.command()
def parse(
    keyword: Annotated[str, typer.Argument(help="Ключевое слово для поиска")],
    depth: Annotated[int, typer.Argument(help="Количество страниц")] = 1,
    mode: Annotated[str, typer.Argument(help="Режим: yandex, google, both")] = "yandex",
    output: Annotated[str, typer.Option("--output", "-o", help="Файл результатов")] = "results.txt"
):
    setup_logging(settings.log_file)
    
    if mode not in ["yandex", "google", "both"]:
        typer.echo("❌ Режим должен быть: yandex, google или both")
        raise typer.Exit(code=1)
    
    typer.echo(f"🔍 Запуск парсера...")
    typer.echo(f"📌 Ключевое слово: {keyword}")
    typer.echo(f"📊 Глубина: {depth} страниц")
    typer.echo(f"🌐 Режим: {mode}")
    
    async def run():
        parser = SearchParser()
        try:
            links = await parser.parse(keyword, depth, mode)
            save_links(links, output)
            return links
        finally:
            # Правильное завершение соединения
            await parser.close()
    
    links = asyncio.run(run())
    
    typer.echo(f"\n✅ Найдено {len(links)} уникальных ссылок")
    typer.echo(f"💾 Результаты сохранены в {output}")

if __name__ == "__main__":
    app()
