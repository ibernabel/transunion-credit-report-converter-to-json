"""
TransUnion PDF to JSON API - Interactive CLI for Credit Report Parsing.
"""

from src.utils.logging_config import api_logger
from src.scrubber.service import PIIScrubber
from src.parser.engine import ParserEngine
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
import uvicorn
import typer
from typing import Optional
import sys
from pathlib import Path

# Add project root to sys.path to allow running as a script
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


app = typer.Typer(
    help="TransUnion PDF to JSON API - Interactive CLI for TransUnion Credit Report Parsing",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    if value:
        from src.main import app as fastapi_app
        console.print(
            f"TransUnion PDF to JSON API CLI [bold]v{fastapi_app.version}[/bold]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show application version and exit."
    ),
):
    """
    TransUnion PDF to JSON API - Interactive CLI
    """
    pass


@app.command()
def parse(
    input_file: Path = typer.Option(
        ..., "--input", "-i", help="Path to the TransUnion PDF credit report", exists=True, dir_okay=False
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Path to save the JSON result (pii-scrubbed)"
    ),
    pretty: bool = typer.Option(
        True, "--pretty/--no-pretty", help="Format JSON output with indentation"),
):
    """
    Parse a TransUnion PDF credit report into structured JSON.
    """
    if not input_file.suffix.lower() == ".pdf":
        console.print("[red]Error:[/red] Only PDF files are supported.")
        raise typer.Exit(code=1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Reading PDF...", total=None)
            with open(input_file, "rb") as f:
                content = f.read()

            progress.add_task(
                description="Parsing credit report structure...", total=None)
            # Use sync wrapper or run in loop if needed, but Engine might be async
            # Given src/api/routes.py: parser = await ParserEngine.from_pdf_bytes(content)
            import asyncio

            async def run_parse():
                parser = await ParserEngine.from_pdf_bytes(content)
                report = await parser.get_report()
                return report

            report = asyncio.run(run_parse())

            progress.add_task(description="Scrubbing PII data...", total=None)
            scrubbed_report = PIIScrubber.scrub_report(report)

        # Output results
        json_data = scrubbed_report.model_dump_json(
            indent=4 if pretty else None)

        if output_file:
            with open(output_file, "w") as f:
                f.write(json_data)
            console.print(
                f"[green]Successfully parsed![/green] Result saved to: [bold]{output_file}[/bold]")
        else:
            console.print(
                Panel(json_data, title="Scrubbed Credit Report JSON", expand=False))

    except Exception as e:
        console.print(f"[red]Error processing PDF:[/red] {str(e)}")
        api_logger.error(f"CLI Parse error: {str(e)}", exc_info=True)
        raise typer.Exit(code=1)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind the server to"),
    port: int = typer.Option(8000, help="Port to bind the server to"),
    reload: bool = typer.Option(
        False, "--reload", help="Enable auto-reload for development"),
):
    """
    Start the FastAPI server.
    """
    console.print(
        f"[bold blue]Starting TransUnion PDF to JSON API API server on {host}:{port}...[/bold blue]")
    uvicorn.run("src.main:app", host=host, port=port, reload=reload)


@app.command()
def version():
    """
    Show application version.
    """
    from src.main import app as fastapi_app
    console.print(f"TransUnion PDF to JSON API CLI [bold]v{fastapi_app.version}[/bold]")


if __name__ == "__main__":
    app()
