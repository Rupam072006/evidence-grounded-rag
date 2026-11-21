"""MASTERDB Persistence and Capability Client Adapter.

Connects the CMO Agent to the local MASTERDB platform (cap-cmo-marketing-intelligence)
while maintaining complete failover resilience to the local RecordStore when disconnected.
"""
from typing import Optional, List, Dict, Any
from pathlib import Path
import httpx

from evidence_rag.record_store import RecordStore
from evidence_rag.workflow_schemas import WorkflowRecord, ApprovalDecision
from evidence_rag.logging_config import setup_logger
from evidence_rag.api.config import api_settings

logger = setup_logger("evidence_rag.api.masterdb_client")


class MasterDBPersistenceAdapter:
    """Hybrid persistence adapter targeting local MASTERDB capability with RecordStore fallback."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        capability_id: Optional[str] = None,
        application_id: Optional[str] = None,
        record_store: Optional[RecordStore] = None
    ):
        self.base_url = (base_url or api_settings.masterdb_url).rstrip("/")
        self.capability_id = capability_id or api_settings.masterdb_capability_id
        self.application_id = application_id or api_settings.masterdb_app_id
        self.record_store = record_store or RecordStore()

    def check_connection(self) -> Dict[str, Any]:
        """Probe MASTERDB health and capability registration."""
        try:
            with httpx.Client(timeout=1.5) as client:
                resp = client.get(f"{self.base_url}/health")
                if resp.status_code == 200:
                    return {
                        "connected": True,
                        "status": "MASTERDB_CONNECTED",
                        "base_url": self.base_url,
                        "capability_id": self.capability_id,
                        "details": resp.json()
                    }
                return {
                    "connected": False,
                    "status": "MASTERDB_UNAVAILABLE",
                    "base_url": self.base_url,
                    "status_code": resp.status_code
                }
        except Exception as e:
            logger.debug(f"MASTERDB not reachable at {self.base_url}: {e}. Falling back to local store.")
            return {
                "connected": False,
                "status": "LOCAL_STORE_FALLBACK",
                "base_url": self.base_url,
                "reason": str(e)
            }

    def fetch_marketing_intelligence(
        self,
        query_params: Optional[Dict[str, Any]] = None,
        bearer_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute governed retrieval against cap-cmo-marketing-intelligence.

        Follows canonical flow:
        1. Request Access Grant (POST /access/request)
        2. Retrieve Governed Records (POST /capabilities/{capability_id}/retrieve)
        """
        token = bearer_token or "mock-rs256-test-token"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=3.0) as client:
                # Step 1: Access grant request
                access_payload = {
                    "application_id": self.application_id,
                    "capability_id": self.capability_id,
                    "purpose": "marketing_intelligence"
                }
                grant_resp = client.post(
                    f"{self.base_url}/access/request",
                    json=access_payload,
                    headers=headers
                )
                if grant_resp.status_code != 200:
                    logger.warning(f"MASTERDB access grant request failed: {grant_resp.text}")
                    return {"status": "ACCESS_DENIED", "details": grant_resp.text}

                grant_data = grant_resp.json()
                grant_token = grant_data.get("access_token")
                request_id = grant_data.get("request_id")

                # Step 2: Governed retrieve
                retrieve_payload = {
                    "application_id": self.application_id,
                    "access_token": grant_token,
                    "request_id": request_id,
                    "query_params": query_params or {}
                }
                retrieve_resp = client.post(
                    f"{self.base_url}/capabilities/{self.capability_id}/retrieve",
                    json=retrieve_payload,
                    headers=headers
                )
                if retrieve_resp.status_code == 200:
                    return retrieve_resp.json()
                return {"status": "RETRIEVAL_ERROR", "details": retrieve_resp.text}

        except Exception as e:
            logger.info(f"MASTERDB governed retrieval skipped/failed ({e}); returning fallback intelligence.")
            return {
                "status": "OFFLINE_FALLBACK",
                "capability_id": self.capability_id,
                "data": {"dataset_id": "ds-cmo-marketing-001", "records": []}
            }

    def save_record(self, record: WorkflowRecord) -> WorkflowRecord:
        """Persist workflow record to local store and sync audit event if MASTERDB is online."""
        saved = self.record_store.save_record(record)
        # Attempt non-blocking audit sync to Pravah if configured
        try:
            self._sync_audit_event(record)
        except Exception as e:
            logger.debug(f"Optional MASTERDB audit sync omitted: {e}")
        return saved

    def _sync_audit_event(self, record: WorkflowRecord) -> None:
        """Synchronize high-watermark governance events to MASTERDB Pravah event bus."""
        event_payload = {
            "event_type": "CMO_PROPOSAL_RECORDED",
            "request_id": record.request_id,
            "trace_id": record.trace_id,
            "status": record.status.value,
            "department": record.request.department
        }
        with httpx.Client(timeout=0.5) as client:
            client.post(f"{self.base_url}/pravah/events", json=event_payload)

    def get_record(self, request_id: str) -> Optional[WorkflowRecord]:
        """Fetch audit record by request ID."""
        return self.record_store.get_record(request_id)

    def list_records(self) -> List[WorkflowRecord]:
        """List all stored workflow records."""
        return self.record_store.list_records()

    def record_decision(
        self,
        request_id: str,
        decision: ApprovalDecision
    ) -> Optional[WorkflowRecord]:
        """Record human manager approval or rejection."""
        return self.record_store.record_decision(request_id, decision)
