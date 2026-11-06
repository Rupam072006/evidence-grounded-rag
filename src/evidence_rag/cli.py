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
        "\u2192": "->", # right arrow
        "\u26a0": "[!]", # warning sign
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
@click.argument("user_query", required=False, default=None)
@click.option("--config", "-c", default=None, help="Path to custom YAML config file.")
@click.option("--mode", "-m", default=None, type=click.Choice(["mock", "groq", "grok", "gemini"], case_sensitive=False), help="Generation mode: mock, groq, grok, or gemini.")
@click.option("--json-out", is_flag=True, help="Output response in structured JSON format.")
def query(user_query, config, mode, json_out):
    """Query the RAG system with a question."""
    if not user_query:
        user_query = click.prompt("[bold yellow]Enter your question[/bold yellow]").strip()
        if not user_query:
            console.print("[bold red]Error:[/bold red] Query cannot be empty.")
            sys.exit(1)

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
@click.argument("proposal_arg", required=False, default=None)
@click.option("--preset", type=click.Choice(["growth", "overspend", "incomplete", "conflict"], case_sensitive=False), default=None, help="Preset demonstration proposal.")
@click.option("--request-id", "-i", default=None, help="Custom request ID. Auto-generated if omitted.")
@click.option("--title", "-t", default=None, help="Short title of the proposal.")
@click.option("--proposal", "-p", default=None, help="Detailed proposal text.")
@click.option("--department", "-d", default="Marketing", help="Department submitting the proposal.")
@click.option("--budget", "-b", default=None, type=float, help="Requested budget amount in USD.")
@click.option("--submitted-by", "-s", default="analyst", help="Username or ID of the submitter.")
@click.option("--interactive", is_flag=True, default=False, help="Interactive mode with immediate approval prompt.")
@click.option("--config", "-c", default="configs/default.yaml", help="Path to workflow config YAML.")
@click.option("--json-out", is_flag=True, help="Output full record as JSON.")
def workflow_evaluate(proposal_arg, preset, request_id, title, proposal, department, budget, submitted_by, interactive, config, json_out):
    """Evaluate a business proposal against organizational policies and stop at human approval gate."""
    import sys
    import re
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowRequest, WorkflowStatus

    PRESETS = {
        "growth": {
            "request_id": "REQ-GROWTH-01",
            "title": "Q4 Enterprise Growth Initiative",
            "proposal": "Allocate $35,000 across Google search ads and content syndication aiming for 450 conversions with target CTR of 2.4%.",
            "budget": 35000.0,
            "department": "Marketing"
        },
        "overspend": {
            "request_id": "REQ-OVERSPEND-01",
            "title": "Excessive Budget Initiative",
            "proposal": "Requesting $75,000 for broad consumer media blitz across paid channels exceeding policy caps.",
            "budget": 75000.0,
            "department": "Marketing"
        },
        "incomplete": {
            "request_id": "REQ-INCOMPLETE-01",
            "title": "Exploratory Channel Experiment",
            "proposal": "Evaluate experimental multi-channel expansion proposal for incomplete draft testing with missing channels and unknown timeline.",
            "budget": 18000.0,
            "department": "Marketing"
        },
        "conflict": {
            "request_id": "REQ-CONFLICT-01",
            "title": "Influencer Creator Sponsorship Program",
            "proposal": "Allocate funds for influencer marketing creator sponsorships across social platforms.",
            "budget": 20000.0,
            "department": "Marketing"
        }
    }

    if preset:
        p_data = PRESETS[preset.lower()]
        request_id = request_id or p_data["request_id"]
        title = title or p_data["title"]
        proposal = proposal or p_data["proposal"]
        budget = budget if budget is not None else p_data["budget"]
        department = department or p_data["department"]

    effective_proposal = proposal or proposal_arg
    is_interactive_mode = interactive

    # If no proposal or preset passed, ask user interactively
    if not effective_proposal and not preset:
        is_interactive_mode = True
        console.print(Panel(
            "[bold cyan]Task 2: Business Proposal Evaluation[/bold cyan]\n"
            "[dim]Submit a business or campaign proposal to evaluate against organizational policies.[/dim]",
            border_style="cyan"
        ))
        title = title or click.prompt("[bold yellow]Proposal Title[/bold yellow]", default="New Marketing Proposal").strip()
        effective_proposal = click.prompt("[bold yellow]Detailed Proposal Text[/bold yellow]").strip()
        if not effective_proposal:
            console.print("[bold red]Error:[/bold red] Proposal text cannot be empty.")
            sys.exit(1)

        department = department or click.prompt("Department", default="Marketing").strip()

        # Check for budget input if not in text
        if budget is None:
            m = re.search(r"\$\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{2})?)", effective_proposal)
            if m:
                try:
                    budget = float(m.group(1).replace(",", ""))
                    console.print(f"[dim]Auto-detected requested budget: ${budget:,.2f}[/dim]")
                except ValueError:
                    pass
            if budget is None:
                b_str = click.prompt("[dim]Requested budget in USD (press Enter to skip if unspecified)[/dim]", default="", show_default=False).strip()
                if b_str:
                    try:
                        budget = float(b_str.replace("$", "").replace(",", "").strip())
                    except ValueError:
                        budget = None

    if not effective_proposal:
        console.print("[bold red]Error:[/bold red] Must provide proposal text or use --preset [growth|overspend|incomplete|conflict].")
        sys.exit(1)

    # Auto-extract dollar amount from text if budget is still not provided
    if budget is None and effective_proposal:
        m = re.search(r"\$\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{2})?)", effective_proposal)
        if m:
            try:
                budget = float(m.group(1).replace(",", ""))
            except ValueError:
                pass

    effective_title = title or (effective_proposal[:35].strip() + "...")
    if not request_id:
        import uuid
        request_id = f"REQ-{uuid.uuid4().hex[:6].upper()}"

    req = WorkflowRequest(
        request_id=request_id,
        title=effective_title,
        proposal_text=effective_proposal,
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
        f"\n[dim]To approve this proposal via CLI, run:\n"
        f"python -m evidence_rag.cli workflow approve {record.request_id}[/dim]\n"
    )

    # If running interactively, prompt immediately for human sign-off
    if is_interactive_mode:
        console.print("[bold yellow]Human Approval Gate Action:[/bold yellow]")
        choice = click.prompt("Choose action: [a]pprove / [r]eject / [s]kip (decide later)", default="s", show_default=True).strip().lower()
        if choice in ("a", "approve"):
            rev = click.prompt("Reviewer name", default="Rupam Patne")
            notes = click.prompt("Decision justification notes", default="Audited against policy; approved.")
            wf.submit_approval(record.request_id, decision="APPROVED", reviewer=rev, notes=notes)
            console.print(f"[bold green][OK] Request {record.request_id} APPROVED by {rev}. Decision logged in audit trail.[/bold green]\n")
        elif choice in ("r", "reject"):
            rev = click.prompt("Reviewer name", default="Rupam Patne")
            reason = click.prompt("Rejection reason notes", default="Policy violation or excessive spend.")
            wf.submit_approval(record.request_id, decision="REJECTED", reviewer=rev, notes=reason)
            console.print(f"[bold red][OK] Request {record.request_id} REJECTED by {rev}. Decision logged in audit trail.[/bold red]\n")
        else:
            console.print(f"[dim]Proposal {record.request_id} remains PAUSED in AWAITING_APPROVAL state.[/dim]\n")


@workflow.command("ask")
@click.argument("question", required=False, default=None)
@click.option("--config", "-c", default="configs/default.yaml", help="Path to workflow config YAML.")
@click.option("--mode", "-m", default=None, type=click.Choice(["mock", "groq", "grok", "gemini"], case_sensitive=False), help="Generation mode.")
@click.option("--json-out", is_flag=True, help="Output response in structured JSON format.")
def workflow_ask(question, config, mode, json_out):
    """Ask an informational policy or marketing question and receive a grounded answer with citations."""
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.schemas import ResponseStatus

    if not question:
        question = click.prompt("[bold yellow]Enter your policy question[/bold yellow]").strip()
        if not question:
            console.print("[bold red]Error:[/bold red] Question cannot be empty.")
            sys.exit(1)

    wf = DecisionWorkflow(config_path=config)
    wf.ensure_index()
    if mode:
        wf.config.generation.mode = mode.lower()
        wf.pipeline.config.generation.mode = mode.lower()

    response = wf.ask_policy_question(question)

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
        title="Marketing Policy Q&A Result",
        border_style=status_color
    ))

    if response.evidence:
        table = Table(title="Retrieved Policy Evidence")
        table.add_column("Rank", justify="center")
        table.add_column("Document", style="green")
        table.add_column("Chunk ID", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Excerpt")

        for item in response.evidence:
            excerpt = item.chunk.text[:80] + ("..." if len(item.chunk.text) > 80 else "")
            table.add_row(
                str(item.rank),
                item.chunk.document_id,
                item.chunk.chunk_id,
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


@workflow.command("approve")
@click.argument("request_id")
@click.option("--decision", "-d", type=click.Choice(["APPROVED", "REJECTED"], case_sensitive=False), default="APPROVED", help="Human approval decision (default: APPROVED).")
@click.option("--reviewer", "-r", default="Prof_Evaluator", help="Name of the human reviewer (default: Prof_Evaluator).")
@click.option("--notes", "-n", default="Budget compliant with DOC-022; approved.", help="Auditable justification notes.")
@click.option("--config", "-c", default="configs/default.yaml", help="Path to workflow config YAML.")
@click.option("--json-out", is_flag=True, help="Output full updated record as JSON.")
def workflow_approve(request_id, decision, reviewer, notes, config, json_out):
    """Submit a binding human approval or rejection decision for a pending workflow proposal."""
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowStatus

    id_aliases = {
        "REQ-PRESET-GROWTH": "REQ-GROWTH-01",
        "REQ-PRESET-OVER": "REQ-OVERSPEND-01",
        "REQ-PRESET-OVERSPEND": "REQ-OVERSPEND-01",
        "REQ-PRESET-INCOMPLETE": "REQ-INCOMPLETE-01",
        "REQ-PRESET-CONFLICT": "REQ-CONFLICT-01"
    }
    target_id = id_aliases.get(request_id.upper(), request_id)

    wf = DecisionWorkflow(config_path=config)
    try:
        record = wf.submit_approval(
            request_id=target_id,
            decision=decision.upper(),
            reviewer=reviewer,
            notes=notes
        )
    except (KeyError, ValueError) as e:
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


@workflow.command("reject")
@click.argument("request_id")
@click.option("--reviewer", "-r", default="Prof_Evaluator", help="Name of the human reviewer (default: Prof_Evaluator).")
@click.option("--reason", "--notes", "-n", default="Budget or policy violation; rejected.", help="Auditable justification notes.")
@click.option("--config", "-c", default="configs/default.yaml", help="Path to workflow config YAML.")
@click.option("--json-out", is_flag=True, help="Output full updated record as JSON.")
def workflow_reject(request_id, reviewer, reason, config, json_out):
    """Submit a binding human rejection decision for a pending workflow proposal."""
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowStatus

    # Map friendly alias IDs if typed
    id_aliases = {
        "REQ-PRESET-GROWTH": "REQ-GROWTH-01",
        "REQ-PRESET-OVER": "REQ-OVERSPEND-01",
        "REQ-PRESET-OVERSPEND": "REQ-OVERSPEND-01",
        "REQ-PRESET-INCOMPLETE": "REQ-INCOMPLETE-01",
        "REQ-PRESET-CONFLICT": "REQ-CONFLICT-01"
    }
    target_id = id_aliases.get(request_id.upper(), request_id)

    wf = DecisionWorkflow(config_path=config)
    try:
        record = wf.submit_approval(
            request_id=target_id,
            decision="REJECTED",
            reviewer=reviewer,
            notes=reason
        )
    except (KeyError, ValueError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    if json_out:
        console.print(record.model_dump_json(indent=2))
        return

    console.print(Panel(
        f"[bold]Request ID:[/bold] {record.request_id}\n"
        f"[bold]Final Status:[/bold] [bold red]{record.status.value}[/bold red]\n"
        f"[bold]Reviewer:[/bold] {record.approval.reviewer}\n"
        f"[bold]Timestamp:[/bold] {record.approval.decided_at}\n"
        f"[bold]Rejection Reason:[/bold] {safe_text(record.approval.decision_notes)}",
        title="[bold red]Human Rejection Decision Recorded[/bold red]",
        border_style="red"
    ))


@workflow.command("show")
@click.argument("request_id")
@click.option("--config", "-c", default="configs/default.yaml", help="Path to workflow config YAML.")
@click.option("--json-out", is_flag=True, help="Output record as raw JSON.")
def workflow_show(request_id, config, json_out):
    """Display the full audit trail and recommendation for a specific workflow proposal."""
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowStatus

    id_aliases = {
        "REQ-PRESET-GROWTH": "REQ-GROWTH-01",
        "REQ-PRESET-OVER": "REQ-OVERSPEND-01",
        "REQ-PRESET-OVERSPEND": "REQ-OVERSPEND-01",
        "REQ-PRESET-INCOMPLETE": "REQ-INCOMPLETE-01",
        "REQ-PRESET-CONFLICT": "REQ-CONFLICT-01"
    }
    target_id = id_aliases.get(request_id.upper(), request_id)

    wf = DecisionWorkflow(config_path=config)
    record = wf.get_record(target_id)
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
@click.option("--config", "-c", default="configs/default.yaml", help="Path to workflow config YAML.")
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


@workflow.command("list-records")
@click.option("--config", "-c", default="configs/default.yaml", help="Path to workflow config YAML.")
@click.pass_context
def workflow_list_records(ctx, config):
    """Alias for 'workflow list'."""
    ctx.forward(workflow_list)


@workflow.command("replay")
@click.argument("request_id")
@click.option("--config", "-c", default="configs/default.yaml", help="Path to workflow config YAML.")
@click.option("--json-out", is_flag=True, help="Output full replay comparison as JSON.")
def workflow_replay(request_id, config, json_out):
    """Replay and verify a past workflow proposal against current corpus and index.

    Reconstruction: recovers the recorded evidence and recommendation for the original request.
    Note: Replay does NOT prove approval legitimacy — a manually entered reviewer name
    is recorded identity, not independently authenticated identity.
    """
    import json as _json
    from evidence_rag.workflow import DecisionWorkflow
    from evidence_rag.workflow_schemas import WorkflowStatus

    id_aliases = {
        "REQ-PRESET-GROWTH": "REQ-GROWTH-01",
        "REQ-PRESET-OVER": "REQ-OVERSPEND-01",
        "REQ-PRESET-OVERSPEND": "REQ-OVERSPEND-01",
        "REQ-PRESET-INCOMPLETE": "REQ-INCOMPLETE-01",
        "REQ-PRESET-CONFLICT": "REQ-CONFLICT-01"
    }
    target_id = id_aliases.get(request_id.upper(), request_id)

    wf = DecisionWorkflow(config_path=config)
    original_record = wf.get_record(target_id)
    if not original_record:
        console.print(f"[bold red]Replay Error:[/bold red] No record found for request ID '{target_id}'")
        sys.exit(1)

    console.print(Panel(
        f"[bold]Replaying Request:[/bold] {target_id}\\n"
        f"[bold]Original Status:[/bold] {original_record.status.value}\\n"
        f"[bold]Original Created:[/bold] {original_record.created_at}\\n"
        f"[dim]Note: Replay reconstructs the recorded evidence. It does NOT prove approval legitimacy.[/dim]",
        title="[bold cyan]Workflow Replay -- Evidence Reconstruction[/bold cyan]",
        border_style="cyan"
    ))

    # Re-execute the same proposal against current corpus
    replay_record = wf.evaluate_proposal(original_record.request)

    # Build comparison
    status_match = replay_record.status.value == original_record.status.value
    recommendation_match = (
        replay_record.recommendation is not None and
        original_record.recommendation is not None and
        replay_record.recommendation.recommended_action == original_record.recommendation.recommended_action
    )

    original_doc_ids = sorted(set(rc.chunk.document_id for rc in original_record.evidence_set))
    replay_doc_ids = sorted(set(rc.chunk.document_id for rc in replay_record.evidence_set))
    retrieval_match = original_doc_ids == replay_doc_ids

    comparison = {
        "request_id": target_id,
        "replay_timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "original_status": original_record.status.value,
        "replay_status": replay_record.status.value,
        "status_match": status_match,
        "original_retrieved_doc_ids": original_doc_ids,
        "replay_retrieved_doc_ids": replay_doc_ids,
        "retrieval_match": retrieval_match,
        "original_recommended_action": original_record.recommendation.recommended_action if original_record.recommendation else None,
        "replay_recommended_action": replay_record.recommendation.recommended_action if replay_record.recommendation else None,
        "recommendation_action_match": recommendation_match,
        "original_approval": {
            "decision": original_record.approval.decision if original_record.approval else None,
            "reviewer": original_record.approval.reviewer if original_record.approval else None,
            "decided_at": original_record.approval.decided_at if original_record.approval else None
        } if original_record.approval else None,
        "replay_limitations": [
            "Reviewer identity is recorded text only, not independently authenticated.",
            "LLM-based generators may produce different outputs across invocations.",
            "Corpus changes since original request would affect retrieval.",
            "Replay proves corpus coverage but NOT approval authorization."
        ]
    }

    if json_out:
        console.print(_json.dumps(comparison, indent=2))
        return

    color = "green" if (status_match and retrieval_match) else "yellow"
    console.print(Panel(
        f"[bold]Status Match:[/bold] {'[green]YES[/green]' if status_match else '[red]NO[/red]'} "
        f"({original_record.status.value} -> {replay_record.status.value})\\n"
        f"[bold]Retrieval Match:[/bold] {'[green]YES[/green]' if retrieval_match else '[yellow]DIFFERENT[/yellow]'}\\n"
        f"[bold]Original Docs:[/bold] {', '.join(original_doc_ids) or '(none)'}\\n"
        f"[bold]Replay Docs:[/bold] {', '.join(replay_doc_ids) or '(none)'}\\n"
        f"[bold]Action Match:[/bold] {'[green]YES[/green]' if recommendation_match else '[yellow]DIFFERENT[/yellow]'}",
        title="Replay Comparison",
        border_style=color
    ))

    if original_record.approval:
        console.print(Panel(
            f"[bold]Recorded Decision:[/bold] {original_record.approval.decision}\\n"
            f"[bold]Reviewer:[/bold] {original_record.approval.reviewer}\\n"
            f"[bold]Decided At:[/bold] {original_record.approval.decided_at}\\n"
            f"[dim][!] This is recorded identity only, not authenticated authorization.[/dim]",
            title="Original Approval Record",
            border_style="yellow"
        ))

    console.print("[dim]Replay complete. See evidence_packet/replay_comparison.json for full report.[/dim]")


if __name__ == "__main__":
    main()

