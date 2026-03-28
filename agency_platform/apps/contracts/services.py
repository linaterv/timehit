"""Business logic for contract management (S007)."""
import os

from django.db import transaction

from apps.audit.services import log_event
from apps.contracts.models import Contract


def create_contract(
    *,
    title: str,
    contract_type: str,
    document,
    signed_date,
    expiry_date=None,
    contractor=None,
    client=None,
    placement_id=None,
    status: str = "draft",
    notes: str = "",
    actor=None,
) -> Contract:
    """Create a new contract with uploaded document."""
    with transaction.atomic():
        contract = Contract(
            title=title,
            contract_type=contract_type,
            document=document,
            file_name=document.name,
            file_size=document.size,
            signed_date=signed_date,
            expiry_date=expiry_date,
            contractor=contractor,
            client=client,
            placement_id=placement_id,
            status=status,
            notes=notes,
        )
        contract.full_clean()
        contract.save()

    log_event(
        action="contract_uploaded",
        actor=actor,
        target_type="contract",
        target_id=str(contract.pk),
        detail={
            "title": title,
            "contract_type": contract_type,
            "file_name": document.name,
            "file_size": document.size,
            "contractor_id": str(contractor.pk) if contractor else None,
            "client_id": str(client.pk) if client else None,
        },
    )
    return contract


def update_contract(
    *,
    contract: Contract,
    actor,
    new_document=None,
    **fields,
) -> Contract:
    """Update contract metadata and optionally replace the document."""
    changes = {}
    old_file_name = contract.file_name

    # Track field changes
    updatable = (
        "title", "contract_type", "signed_date", "expiry_date",
        "status", "notes", "is_active",
    )
    for field in updatable:
        if field in fields:
            old_val = getattr(contract, field)
            new_val = fields[field]
            if str(old_val) != str(new_val):
                changes[field] = {"old": str(old_val), "new": str(new_val)}
                setattr(contract, field, new_val)

    # FK fields
    for fk_field in ("contractor", "client"):
        if fk_field in fields:
            old_obj = getattr(contract, fk_field)
            new_obj = fields[fk_field]
            old_id = str(old_obj.pk) if old_obj else None
            new_id = str(new_obj.pk) if new_obj else None
            if old_id != new_id:
                changes[fk_field] = {"old": old_id, "new": new_id}
                setattr(contract, fk_field, new_obj)

    if "placement_id" in fields:
        old_val = str(contract.placement_id) if contract.placement_id else None
        new_val = str(fields["placement_id"]) if fields["placement_id"] else None
        if old_val != new_val:
            changes["placement_id"] = {"old": old_val, "new": new_val}
            contract.placement_id = fields["placement_id"]

    # Handle file replacement
    file_replaced = False
    if new_document:
        file_replaced = True
        changes["document"] = {
            "old_file": old_file_name,
            "new_file": new_document.name,
        }
        # Keep old file on disk (history) — just update the record
        contract.document = new_document
        contract.file_name = new_document.name
        contract.file_size = new_document.size

    if changes:
        with transaction.atomic():
            contract.full_clean()
            contract.save()

        action = "contract_file_replaced" if file_replaced else "contract_updated"
        log_event(
            action=action,
            actor=actor,
            target_type="contract",
            target_id=str(contract.pk),
            detail={"changes": changes},
        )

    return contract


def log_contract_download(*, contract: Contract, actor) -> None:
    """Audit log entry for a document download."""
    log_event(
        action="contract_downloaded",
        actor=actor,
        target_type="contract",
        target_id=str(contract.pk),
        detail={
            "title": contract.title,
            "file_name": contract.file_name,
        },
    )
