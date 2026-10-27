# Cascading Deletion Orchestration Engine

```python
"""
Privacy deletion API with cascading delete orchestration.
Handles deletion requests across multiple backend services
with verification and audit logging.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class DeletionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PARTIALLY_COMPLETED = "partially_completed"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


class ServiceDeletionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"  # For legally exempt data


@dataclass
class DeletionTarget:
    service_name: str
    data_categories: list[str]
    priority: int  # Lower number = delete first
    legal_hold_check: bool = True
    retention_exempt: bool = False  # True if data must be retained (e.g., tax records)


@dataclass
class ServiceDeletionResult:
    service_name: str
    status: ServiceDeletionStatus
    records_deleted: int
    records_retained: int
    retention_reason: Optional[str]
    completed_at: Optional[datetime]
    error_message: Optional[str]


@dataclass
class DeletionRequest:
    request_id: str
    subject_id: str
    status: DeletionStatus
    created_at: datetime
    scope: list[str]  # Data categories to delete
    exclude: list[str]  # Data categories exempt from deletion
    service_results: list[ServiceDeletionResult] = field(default_factory=list)
    verified_at: Optional[datetime] = None
    verification_method: Optional[str] = None


class CascadingDeletionOrchestrator:
    """
    Orchestrate data deletion across multiple backend services
    in the correct order, handling dependencies, legal holds,
    and retention requirements.
    """

    def __init__(self, service_registry: list[DeletionTarget], audit_logger):
        self.targets = sorted(service_registry, key=lambda t: t.priority)
        self.audit = audit_logger

    def execute_deletion(
        self,
        subject_id: str,
        scope: list[str],
        exclude: list[str] = None
    ) -> DeletionRequest:
        """
        Execute cascading deletion across all registered services.

        Args:
            subject_id: The data subject whose data should be deleted
            scope: Data categories to delete (or ["all"])
            exclude: Data categories to exclude from deletion

        Returns:
            DeletionRequest with results from each service
        """
        exclude = exclude or []

        request = DeletionRequest(
            request_id=str(uuid.uuid4()),
            subject_id=subject_id,
            status=DeletionStatus.IN_PROGRESS,
            created_at=datetime.now(timezone.utc),
            scope=scope,
            exclude=exclude
        )

        self.audit.log_deletion_start(request)

        for target in self.targets:
            # Skip if data category not in scope
            if "all" not in scope:
                relevant_categories = set(target.data_categories) & set(scope)
                if not relevant_categories:
                    continue

            # Skip if explicitly excluded
            if set(target.data_categories) & set(exclude):
                result = ServiceDeletionResult(
                    service_name=target.service_name,
                    status=ServiceDeletionStatus.SKIPPED,
                    records_deleted=0,
                    records_retained=0,
                    retention_reason="Excluded by request",
                    completed_at=datetime.now(timezone.utc),
                    error_message=None
                )
                request.service_results.append(result)
                continue

            # Check retention exemptions
            if target.retention_exempt:
                result = ServiceDeletionResult(
                    service_name=target.service_name,
                    status=ServiceDeletionStatus.SKIPPED,
                    records_deleted=0,
                    records_retained=0,
                    retention_reason="Legal retention requirement",
                    completed_at=datetime.now(timezone.utc),
                    error_message=None
                )
                request.service_results.append(result)
                continue

            # Check legal holds
            if target.legal_hold_check:
                hold = self._check_legal_hold(subject_id, target.service_name)
                if hold:
                    result = ServiceDeletionResult(
                        service_name=target.service_name,
                        status=ServiceDeletionStatus.SKIPPED,
                        records_deleted=0,
                        records_retained=0,
                        retention_reason=f"Legal hold: {hold}",
                        completed_at=datetime.now(timezone.utc),
                        error_message=None
                    )
                    request.service_results.append(result)
                    continue

            # Execute deletion for this service
            result = self._delete_from_service(subject_id, target)
            request.service_results.append(result)

        # Determine overall status
        statuses = [r.status for r in request.service_results]
        if all(s in (ServiceDeletionStatus.COMPLETED, ServiceDeletionStatus.SKIPPED) for s in statuses):
            request.status = DeletionStatus.COMPLETED
        elif any(s == ServiceDeletionStatus.FAILED for s in statuses):
            request.status = DeletionStatus.PARTIALLY_COMPLETED
        else:
            request.status = DeletionStatus.COMPLETED

        self.audit.log_deletion_complete(request)
        return request

    def verify_deletion(self, request: DeletionRequest) -> DeletionRequest:
        """
        Verify that data was actually deleted from all services.
        Run after deletion to confirm no data remnants exist.
        """
        for result in request.service_results:
            if result.status == ServiceDeletionStatus.COMPLETED:
                # Attempt to query for the subject's data
                remaining = self._check_data_exists(
                    request.subject_id, result.service_name
                )
                if remaining > 0:
                    result.status = ServiceDeletionStatus.FAILED
                    result.error_message = f"Verification failed: {remaining} records still exist"

        request.verified_at = datetime.now(timezone.utc)
        request.verification_method = "post_deletion_query"

        all_verified = all(
            r.status in (ServiceDeletionStatus.COMPLETED, ServiceDeletionStatus.SKIPPED)
            for r in request.service_results
        )
        request.status = DeletionStatus.VERIFIED if all_verified else DeletionStatus.PARTIALLY_COMPLETED

        self.audit.log_deletion_verification(request)
        return request

    def _check_legal_hold(self, subject_id: str, service: str) -> Optional[str]:
        """Check if any legal hold applies to this subject's data."""
        # Integration point with legal hold management system
        return None  # Override in production with actual legal hold check

    def _delete_from_service(
        self, subject_id: str, target: DeletionTarget
    ) -> ServiceDeletionResult:
        """Execute deletion against a specific backend service."""
        # Integration point with actual backend service deletion API
        return ServiceDeletionResult(
            service_name=target.service_name,
            status=ServiceDeletionStatus.COMPLETED,
            records_deleted=0,
            records_retained=0,
            retention_reason=None,
            completed_at=datetime.now(timezone.utc),
            error_message=None
        )

    def _check_data_exists(self, subject_id: str, service: str) -> int:
        """Check if data still exists for a subject in a service."""
        # Integration point with service data existence check
        return 0
```
