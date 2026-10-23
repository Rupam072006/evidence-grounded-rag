"""Audit record store for persisting decision-support workflow transactions."""
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from evidence_rag.workflow_schemas import WorkflowRecord, ApprovalDecision, WorkflowStatus
from evidence_rag.logging_config import setup_logger

logger = setup_logger("evidence_rag.record_store")


class RecordStore:
    """Persistent local audit store for decision transactions and approval governance."""

    SECRET_PATTERNS = [
        re.compile(r"gsk_[A-Za-z0-9]{20,}"),
        re.compile(r"xai-[A-Za-z0-9]{20,}"),
        re.compile(r"AIza[A-Za-z0-9]{30,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9\-_.]{20,}", re.IGNORECASE),
    ]

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = Path(storage_dir) if storage_dir else Path("data/workflow_records")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.store_file = self.storage_dir / "records.json"
        if not self.store_file.exists():
            self._write_store({})

    def _read_store(self) -> Dict[str, Dict[str, Any]]:
        """Read all raw record dictionaries from persistent storage."""
        if not self.store_file.exists():
            return {}
        try:
            with open(self.store_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read record store from {self.store_file}: {e}")
            return {}

    def _write_store(self, data: Dict[str, Dict[str, Any]]) -> None:
        """Atomically persist record dictionary to storage file."""
        temp_file = self.store_file.with_suffix(".tmp")
        # Scrub any secrets before writing
        raw_json = json.dumps(data, indent=2, ensure_ascii=False)
        for pattern in self.SECRET_PATTERNS:
            raw_json = pattern.sub("[REDACTED_SECRET]", raw_json)

        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(raw_json)
        temp_file.replace(self.store_file)

    def save_record(self, record: WorkflowRecord) -> WorkflowRecord:
        """Persist or update a workflow record."""
        data = self._read_store()
        rec_dict = record.model_dump()
        rec_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        data[record.request_id] = rec_dict
        self._write_store(data)
        logger.info(f"Persisted workflow record {record.request_id} with status {record.status.value}")
        return WorkflowRecord(**rec_dict)

    def get_record(self, request_id: str) -> Optional[WorkflowRecord]:
        """Retrieve a specific record by request ID."""
        data = self._read_store()
        raw = data.get(request_id)
        if raw is None:
            return None
        return WorkflowRecord(**raw)

    def list_records(self) -> List[WorkflowRecord]:
        """List all stored workflow records."""
        data = self._read_store()
        records = []
        for raw in data.values():
            try:
                records.append(WorkflowRecord(**raw))
            except Exception as e:
                logger.warning(f"Failed to parse record in store: {e}")
        return sorted(records, key=lambda r: r.created_at, reverse=True)

    def record_decision(
        self,
        request_id: str,
        decision: ApprovalDecision
    ) -> Optional[WorkflowRecord]:
        """Update an existing record with a human manager approval or rejection."""
        record = self.get_record(request_id)
        if record is None:
            logger.error(f"Cannot record approval decision: Request ID {request_id} not found.")
            return None

        # Verify that record was in an approvable state
        if record.status not in (WorkflowStatus.AWAITING_APPROVAL, WorkflowStatus.RECOMMENDATION_READY):
            logger.warning(
                f"Recording decision on request {request_id} which is currently in status {record.status.value}."
            )

        new_status = (
            WorkflowStatus.APPROVED
            if decision.decision.upper() == "APPROVED"
            else WorkflowStatus.REJECTED
        )

        record.approval = decision
        record.status = new_status
        record.history.append({
            "action": f"HUMAN_{new_status.value}",
            "reviewer": decision.reviewer,
            "decision_notes": decision.decision_notes,
            "timestamp": decision.decided_at
        })
        return self.save_record(record)
