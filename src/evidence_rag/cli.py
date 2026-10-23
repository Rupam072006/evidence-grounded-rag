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


def safe_text(text: str) -> str:
    """Sanitize unicode characters for Windows terminals."""
    if not text:
        return text
    replacements = {
        "\u2011": "-",  # non-breaking hyphen
        "\u2013": "-",  # en dash
        "\u2014": "--", # em dash
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
        "\u2026": "...", # ellipsis
        "\u00a0": " ",  # non-breaking space
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    encoding = sys.stdout.encoding or "utf-8"
    try:
        text.encode(encoding)
        return text
    except UnicodeEncodeError:
        return text.encode(encoding, errors="replace").decode(encoding)


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
@click.option("--mode", "-m", default=None, type=click.Choice(["mock", "groq", "grok", "gemini"], case_sensitive=False), help="Generation mode: mock, groq, grok, or gemini.")
@click.option("--json-out", is_flag=True, help="Output response in structured JSON format.")
def query(user_query, config, mode, json_out):
    """Query the RAG system with a question."""
    cfg = load_config(config)
    if mode:
        cfg.generation.mode = mode.lower()
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
        f"[bold]Answer:[/bold]\n{safe_text(response.answer)}",
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
            f"[bold]Output:[/bold]\n{safe_text(resp.answer)}",
            border_style=status_style.split()[-1]
        ))

        if resp.citations:
            cit_summary = ", ".join(f"[{c.document_id}:{c.chunk_id}] (valid: {c.is_valid})" for c in resp.citations)
            console.print(f"[dim]Verified Citations: {cit_summary}[/dim]")
        console.print()

    console.print("[bold green][OK] Live Demonstration Complete.[/bold green]")


# ==============================================================================
# Decision-Support Workflow Subcommands
# ==============================================================================

@main.group()
def workflow():
    """Decision-Support Workflow and Human Approval Gate commands."""
    pass


@workflow.command("evaluate")
@click.option("--request-id", "-i", default=None, help="Custom request ID (e.g. REQ-001). Auto-generated if omitted.")
@click.option("--title", "-t", required=True, help="Short title of the proposal.")
@click.option("--proposal", "-p", required=True, help="Detailed proposal text or business problem description.")
@click.option("--department", "-d", default="Marketing", help="Department submitting the proposal.")
@click.option("--budget", "-b", default=None, type=float, help="Requested budget amount in USD.")
@click.option("--submitted-by", "-s", default="analyst", help="Username or ID of the submitter.")
@click.option("--config", "-c", default="configs/marketing_workflow.yaml", help="Path to workflow config YAML.")
@click.option("--json-out", is_flag=True, help="Output full record as JSON.")
def workflow_evaluate(request_id, title, proposal, department, budget, submitted_by, config, json_out):
    """Evaluate a business proposal against organizational policies and stop at human approval gate."""
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowRequest, WorkflowStatus

    if not request_id:
        import uuid
        request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"

    req = WorkflowRequest(
        request_id=request_id,
        title=title,
        proposal_text=proposal,
        department=department,
        requested_budget=budget,
        submitted_by=submitted_by
    )

    wf = DecisionWorkflow(config_path=config)
    record = wf.evaluate_proposal(req)

    if json_out:
        console.print(record.model_dump_json(indent=2))
        return

    # Rich formatted output
    status_color = "yellow" if record.status == WorkflowStatus.AWAITING_APPROVAL else "green"
    if record.status in (WorkflowStatus.INVALID_REQUEST, WorkflowStatus.GENERATION_FAILED, WorkflowStatus.INDEX_UNAVAILABLE):
        status_color = "red"
    elif record.status == WorkflowStatus.CONFLICT_DETECTED:
        status_color = "magenta"

    console.print(Panel(
        f"[bold]Request ID:[/bold] {record.request_id}\n"
        f"[bold]Title:[/bold] {record.request.title}\n"
        f"[bold]Department:[/bold] {record.request.department} | [bold]Requested Budget:[/bold] ${record.request.requested_budget or 0:,.2f}\n"
        f"[bold]Status:[/bold] [{status_color}]{record.status.value}[/{status_color}]\n"
        f"[bold]Human Approval Boundary:[/bold] [bold yellow]PAUSED AT APPROVAL GATE[/bold yellow] (No external action taken)",
        title="[bold cyan]Workflow Proposal Evaluation[/bold cyan]",
        border_style=status_color
    ))

    if record.recommendation:
        rep = record.recommendation
        console.print(Panel(
            f"[bold]Action Recommendation:[/bold] {rep.recommended_action}\n\n"
            f"[bold]Executive Summary:[/bold]\n{safe_text(rep.summary)}\n\n"
            f"[bold]Risk Assessment:[/bold]\n{safe_text(rep.risk_assessment)}",
            title="Recommendation Summary",
            border_style="cyan"
        ))

        # Verified facts table
        if rep.verified_facts:
            fact_table = Table(title="Verified Facts (Machine-Audited Grounding)")
            fact_table.add_column("Claim / Fact")
            fact_table.add_column("Source", style="cyan")
            fact_table.add_column("Chunk ID", style="green")
            for f in rep.verified_facts:
                fact_table.add_row(safe_text(f.statement), f.source_document_id, f.source_chunk_id)
            console.print(fact_table)

        # Inferences, Assumptions, Unknowns
        if rep.inferences:
            console.print("[bold cyan]Inferences (Deductions from Evidence):[/bold cyan]")
            for inf in rep.inferences:
                console.print(f"  • {safe_text(inf)}")
        if rep.assumptions:
            console.print("[bold yellow]Assumptions (Working Premises):[/bold yellow]")
            for a in rep.assumptions:
                console.print(f"  • {safe_text(a)}")
        if rep.unknowns:
            console.print("[bold red]Unknowns & Missing Info:[/bold red]")
            for u in rep.unknowns:
                console.print(f"  • {safe_text(u)}")

    console.print(
        f"\n[dim]To approve or reject this proposal, run:\n"
        f"python -m evidence_rag.cli workflow approve {record.request_id} --decision APPROVED --reviewer \"<Name>\" --notes \"<Reason>\"[/dim]\n"
    )


@workflow.command("approve")
@click.argument("request_id")
@click.option("--decision", "-d", type=click.Choice(["APPROVED", "REJECTED"], case_sensitive=False), required=True, help="Human approval decision.")
@click.option("--reviewer", "-r", required=True, help="Name of the human reviewer.")
@click.option("--notes", "-n", default="", help="Auditable justification notes for the decision.")
@click.option("--config", "-c", default="configs/marketing_workflow.yaml", help="Path to workflow config YAML.")
@click.option("--json-out", is_flag=True, help="Output full updated record as JSON.")
def workflow_approve(request_id, decision, reviewer, notes, config, json_out):
    """Submit a binding human approval or rejection decision for a pending workflow proposal."""
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowStatus

    wf = DecisionWorkflow(config_path=config)
    try:
        record = wf.submit_approval(
            request_id=request_id,
            decision=decision.upper(),
            reviewer=reviewer,
            notes=notes
        )
    except KeyError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    if json_out:
        console.print(record.model_dump_json(indent=2))
        return

    color = "green" if record.status == WorkflowStatus.APPROVED else "red"
    console.print(Panel(
        f"[bold]Request ID:[/bold] {record.request_id}\n"
        f"[bold]Final Status:[/bold] [{color}]{record.status.value}[/{color}]\n"
        f"[bold]Reviewer:[/bold] {record.approval.reviewer}\n"
        f"[bold]Timestamp:[/bold] {record.approval.decided_at}\n"
        f"[bold]Reviewer Notes:[/bold] {safe_text(record.approval.decision_notes)}",
        title=f"[bold {color}]Human Approval Decision Recorded[/bold {color}]",
        border_style=color
    ))


@workflow.command("show")
@click.argument("request_id")
@click.option("--config", "-c", default="configs/marketing_workflow.yaml", help="Path to workflow config YAML.")
@click.option("--json-out", is_flag=True, help="Output record as raw JSON.")
def workflow_show(request_id, config, json_out):
    """Display the full audit trail and recommendation for a specific workflow proposal."""
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowStatus

    wf = DecisionWorkflow(config_path=config)
    record = wf.get_record(request_id)
    if not record:
        console.print(f"[bold red]Record not found:[/bold red] No proposal with ID {request_id}")
        sys.exit(1)

    if json_out:
        console.print(record.model_dump_json(indent=2))
        return

    status_color = "yellow" if record.status == WorkflowStatus.AWAITING_APPROVAL else ("green" if record.status == WorkflowStatus.APPROVED else "red")
    console.print(Panel(
        f"[bold]Request ID:[/bold] {record.request_id}\n"
        f"[bold]Title:[/bold] {record.request.title}\n"
        f"[bold]Department:[/bold] {record.request.department} | [bold]Budget:[/bold] ${record.request.requested_budget or 0:,.2f}\n"
        f"[bold]Status:[/bold] [{status_color}]{record.status.value}[/{status_color}]\n"
        f"[bold]Submitted By:[/bold] {record.request.submitted_by} on {record.created_at}",
        title=f"Workflow Record: {record.request_id}",
        border_style=status_color
    ))

    if record.recommendation:
        rep = record.recommendation
        console.print(Panel(
            f"[bold]Action Recommendation:[/bold] {rep.recommended_action}\n\n"
            f"[bold]Executive Summary:[/bold]\n{safe_text(rep.summary)}\n\n"
            f"[bold]Risk Assessment:[/bold]\n{safe_text(rep.risk_assessment)}",
            title="Recommendation",
            border_style="cyan"
        ))

    if record.approval:
        app = record.approval
        dec_color = "green" if app.decision == "APPROVED" else "red"
        console.print(Panel(
            f"[bold]Decision:[/bold] [{dec_color}]{app.decision}[/{dec_color}]\n"
            f"[bold]Reviewer:[/bold] {app.reviewer}\n"
            f"[bold]Timestamp:[/bold] {app.decided_at}\n"
            f"[bold]Notes:[/bold] {safe_text(app.decision_notes)}",
            title="Human Approval Sign-off",
            border_style=dec_color
        ))


@workflow.command("list")
@click.option("--config", "-c", default="configs/marketing_workflow.yaml", help="Path to workflow config YAML.")
def workflow_list(config):
    """List all stored workflow proposal records and their current approval status."""
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowStatus

    wf = DecisionWorkflow(config_path=config)
    records = wf.list_records()

    if not records:
        console.print("[yellow]No workflow records found in record store.[/yellow]")
        return

    table = Table(title=f"Stored Workflow Records ({len(records)} total)")
    table.add_column("Request ID", style="cyan")
    table.add_column("Title")
    table.add_column("Budget", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Submitted By")
    table.add_column("Reviewer")

    for r in records:
        st_color = "yellow" if r.status == WorkflowStatus.AWAITING_APPROVAL else ("green" if r.status == WorkflowStatus.APPROVED else "red")
        reviewer = r.approval.reviewer if r.approval else "[dim]--[/dim]"
        budget_str = f"${r.request.requested_budget:,.0f}" if r.request.requested_budget is not None else "--"
        table.add_row(
            r.request_id,
            r.request.title[:40] + ("..." if len(r.request.title) > 40 else ""),
            budget_str,
            f"[{st_color}]{r.status.value}[/{st_color}]",
            r.request.submitted_by,
            reviewer
        )
    console.print(table)


if __name__ == "__main__":
    main()

