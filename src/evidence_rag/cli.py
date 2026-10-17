"""Command-line interface for Evidence-Grounded RAG System."""
import sys
import json
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from evidence_rag.config import load_config
from evidence_rag.pipeline import RAGPipeline
from evidence_rag.ingestion import IngestionEngine
from evidence_rag.schemas import ResponseStatus
from evidence_rag.logging_config import setup_logger

console = Console()
logger = setup_logger("evidence_rag.cli")


@click.group()
def main():
    """AegisCore Evidence-Grounded RAG System CLI."""
    pass


@main.command()
@click.option("--config", "-c", default=None, help="Path to custom YAML config file.")
def index(config):
    """Rebuild the vector index from data/documents/ and data/manifest.json."""
    console.print("[bold cyan]Building AegisCore Vector Index...[/bold cyan]")
    cfg = load_config(config)
    pipeline = RAGPipeline(config=cfg)
    try:
        idx = pipeline.build_index()
        console.print(
            f"[bold green]Index built successfully![/bold green] "
            f"Indexed {len(idx.chunks)} chunks with dimension {idx.vectors.shape[1]}."
        )
    except Exception as e:
        console.print(f"[bold red]Failed to build index:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.argument("user_query")
@click.option("--config", "-c", default=None, help="Path to custom YAML config file.")
@click.option("--json-out", is_flag=True, help="Output response in structured JSON format.")
def query(user_query, config, json_out):
    """Query the RAG system with a question."""
    cfg = load_config(config)
    pipeline = RAGPipeline(config=cfg)

    response = pipeline.query(user_query)

    if json_out:
        console.print(response.model_dump_json(indent=2))
        return

    # Rich formatted output
    status_color = "green" if response.status == ResponseStatus.ANSWERED else "yellow"
    if response.status in (ResponseStatus.INVALID_INPUT, ResponseStatus.GENERATION_UNAVAILABLE):
        status_color = "red"
    elif response.status == ResponseStatus.CONFLICT_DETECTED:
        status_color = "magenta"

    console.print(Panel(
        f"[bold]Status:[/bold] [{status_color}]{response.status.value}[/{status_color}]\n"
        f"[bold]Confidence:[/bold] {response.confidence:.2f}\n"
        f"[bold]Latency:[/bold] {response.latency_ms:.1f} ms\n\n"
        f"[bold]Answer:[/bold]\n{response.answer}",
        title="RAG Query Result",
        border_style=status_color
    ))

    if response.evidence:
        table = Table(title="Retrieved Evidence Passages")
        table.add_column("Rank", justify="center")
        table.add_column("Chunk ID", style="cyan")
        table.add_column("Document", style="green")
        table.add_column("Score", justify="right")
        table.add_column("Excerpt")

        for item in response.evidence:
            excerpt = item.chunk.text[:80] + ("..." if len(item.chunk.text) > 80 else "")
            table.add_row(
                str(item.rank),
                item.chunk.chunk_id,
                item.chunk.document_id,
                f"{item.score:.3f}",
                excerpt
            )
        console.print(table)

    if response.citations:
        cit_table = Table(title="Claim Citations")
        cit_table.add_column("Document ID")
        cit_table.add_column("Chunk ID")
        cit_table.add_column("Valid", justify="center")
        for cit in response.citations:
            cit_table.add_row(
                cit.document_id,
                cit.chunk_id,
                "[green]YES[/green]" if cit.is_valid else "[red]NO[/red]"
            )
        console.print(cit_table)


@main.command()
@click.option("--config", "-c", default=None, help="Path to custom YAML config file.")
def verify(config):
    """Verify corpus integrity, manifest completeness, and index state."""
    console.print("[bold cyan]Verifying AegisCore System Integrity...[/bold cyan]")
    cfg = load_config(config)

    # 1. Ingestion / Corpus validation
    try:
        engine = IngestionEngine(cfg.corpus)
        docs = engine.load_corpus()
        console.print(f"[green]Corpus Check Passed:[/green] Exactly {len(docs)} documents validated.")
    except Exception as e:
        console.print(f"[red]Corpus Check Failed:[/red] {e}")
        sys.exit(1)

    # 2. Index validation
    pipeline = RAGPipeline(config=cfg)
    try:
        idx = pipeline.ensure_index()
        console.print(f"[green]Index Check Passed:[/green] Loaded index with {len(idx.chunks)} passages.")
    except Exception as e:
        console.print(f"[red]Index Check Failed:[/red] {e}")
        sys.exit(1)

    console.print("[bold green]All system integrity checks PASSED successfully![/bold green]")


@main.command()
@click.option("--questions", "-q", default="evaluation/questions.jsonl", help="Path to evaluation questions JSONL.")
@click.option("--output", "-o", default="evaluation/results", help="Directory to save evaluation reports.")
def evaluate(questions, output):
    """Execute evaluation benchmark and compute performance metrics."""
    from evidence_rag.evaluation import EvaluationRunner
    console.print(f"[bold cyan]Running AegisCore Benchmark on {questions}...[/bold cyan]")
    runner = EvaluationRunner(questions_path=questions, output_dir=output)
    try:
        summary = runner.run_benchmark()
        metrics = summary["metrics"]

        table = Table(title="Benchmark Evaluation Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Score / Value", style="bold green", justify="right")

        table.add_row("Total Questions", str(summary["total_questions"]))
        table.add_row("Retrieval Success Rate", f"{metrics['retrieval_success_rate'] * 100:.1f}%")
        table.add_row("Status Accuracy", f"{metrics['status_accuracy'] * 100:.1f}%")
        table.add_row("Failure Detection Rate", f"{metrics['failure_detection_rate'] * 100:.1f}%")
        table.add_row("Citation Validity Rate", f"{metrics['citation_validity_rate'] * 100:.1f}%")
        table.add_row("Average Latency", f"{metrics['average_latency_ms']:.1f} ms")

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Evaluation failed:[/bold red] {e}")
        sys.exit(1)


@main.command()
def demo():
    """Run an end-to-end interactive demo demonstrating all key RAG capabilities."""
    cfg = load_config()
    pipeline = RAGPipeline(config=cfg)

    console.print(Panel(
        "[bold cyan]AegisCore Evidence-Grounded RAG System -- Live Demo[/bold cyan]\n"
        "[dim]Running 100% offline, deterministic, verified knowledge retrieval[/dim]",
        border_style="cyan"
    ))

    # Step 1: Ensure Index
    with console.status("[bold green]Verifying and loading vector index..."):
        idx = pipeline.ensure_index()
    console.print(f"[green][OK] Index Active:[/green] {len(idx.chunks)} passages ready across 20 technical documents.\n")

    demo_queries = [
        (
            "1. Factual Answerable Query",
            "What character encoding is mandatory for all incoming documents in AegisCore?",
            "Demonstrates precise factual retrieval and verified claim-level citations."
        ),
        (
            "2. Intentional Contradiction Query",
            "What is the default production top-k parameter and candidate pool size for the retrieval service?",
            "Demonstrates cross-document conflict detection (DOC-009 vs DOC-020)."
        ),
        (
            "3. Out-of-Domain Unanswerable Query",
            "What is the secret recipe for Aunt May's chocolate chip cookies?",
            "Demonstrates strict evidence sufficiency floor and canonical refusal without hallucination."
        )
    ]

    for title, q, note in demo_queries:
        console.print(f"[bold yellow][*] {title}[/bold yellow]")
        console.print(f"[dim]{note}[/dim]")
        console.print(f"[bold white]Query:[/bold white] \"{q}\"")

        resp = pipeline.query(q)

        status_style = "bold green" if resp.status == ResponseStatus.ANSWERED else "bold yellow"
        if resp.status == ResponseStatus.CONFLICT_DETECTED:
            status_style = "bold magenta"
        elif resp.status in (ResponseStatus.INVALID_INPUT, ResponseStatus.GENERATION_UNAVAILABLE):
            status_style = "bold red"

        console.print(Panel(
            f"[bold]Status:[/bold] [{status_style}]{resp.status.value}[/{status_style}] | "
            f"[bold]Confidence:[/bold] {resp.confidence:.2f} | "
            f"[bold]Latency:[/bold] {resp.latency_ms:.1f} ms\n\n"
            f"[bold]Output:[/bold]\n{resp.answer}",
            border_style=status_style.split()[-1]
        ))

        if resp.citations:
            cit_summary = ", ".join(f"[{c.document_id}:{c.chunk_id}] (valid: {c.is_valid})" for c in resp.citations)
            console.print(f"[dim]Verified Citations: {cit_summary}[/dim]")
        console.print()

    console.print("[bold green][OK] Live Demonstration Complete.[/bold green]")


if __name__ == "__main__":
    main()
