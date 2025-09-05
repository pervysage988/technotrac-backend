# app/api/routes/admin.py
from uuid import UUID
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.db.models.equipment import Equipment, EquipmentStatus
from app.db.models.user import OwnerProfile, KycStatus
from app.db.models.audit_log import AuditLog
from app.schemas.equipment import EquipmentOut
from app.schemas.user import OwnerProfileRead
from app.schemas.audit_log import AuditLogRead
from app.core.authz import require_admin  # ✅ centralized

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------- enums ----------
class AuditAction(str, Enum):
    APPROVE_EQUIPMENT = "APPROVE_EQUIPMENT"
    REJECT_EQUIPMENT = "REJECT_EQUIPMENT"
    VERIFY_KYC = "VERIFY_KYC"
    MARK_KYC_PENDING = "MARK_KYC_PENDING"


# ---------- helper ----------
async def record_admin_action(
    session: AsyncSession,
    admin_id: str | UUID,
    action: AuditAction,
    entity: str,
    entity_id: UUID,
    payload: dict | None = None,
):
    log = AuditLog(
        actor_user_id=UUID(str(admin_id)),  # ensure UUID
        action=action.value,
        entity=entity,
        entity_id=entity_id,
        payload=payload or {},
    )
    session.add(log)
    # ⚠️ no commit — caller should commit after updating state + log


# -------- Equipment approvals --------
@router.get("/listings/pending", response_model=list[EquipmentOut])
async def list_pending_equipment(
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    q = select(Equipment).where(Equipment.status == EquipmentStatus.PENDING_REVIEW)
    res = await session.execute(q)
    return list(res.scalars())


@router.post("/listings/{equipment_id}/approve", response_model=EquipmentOut)
async def approve_equipment(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    eq = await session.get(Equipment, equipment_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if eq.status == EquipmentStatus.APPROVED:
        raise HTTPException(status_code=409, detail="Already approved")

    eq.status = EquipmentStatus.APPROVED
    await record_admin_action(session, admin.id, AuditAction.APPROVE_EQUIPMENT, "Equipment", equipment_id)

    await session.commit()
    await session.refresh(eq)
    return eq


@router.post("/listings/{equipment_id}/reject", response_model=EquipmentOut)
async def reject_equipment(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    eq = await session.get(Equipment, equipment_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if eq.status == EquipmentStatus.REJECTED:
        raise HTTPException(status_code=409, detail="Already rejected")

    eq.status = EquipmentStatus.REJECTED
    await record_admin_action(session, admin.id, AuditAction.REJECT_EQUIPMENT, "Equipment", equipment_id)

    await session.commit()
    await session.refresh(eq)
    return eq


# -------- User (Owner) KYC approvals --------
@router.get("/users/kyc/pending", response_model=list[OwnerProfileRead])
async def list_pending_kyc(
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    q = select(OwnerProfile).where(
        OwnerProfile.kyc_status.in_([KycStatus.UNVERIFIED, KycStatus.PENDING])
    )
    res = await session.execute(q)
    return list(res.scalars())


@router.post("/users/{user_id}/kyc/verify", response_model=OwnerProfileRead)
async def verify_user_kyc(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    q = select(OwnerProfile).where(OwnerProfile.user_id == user_id)
    res = await session.execute(q)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Owner profile not found")

    profile.kyc_status = KycStatus.VERIFIED
    await record_admin_action(session, admin.id, AuditAction.VERIFY_KYC, "OwnerProfile", user_id)

    await session.commit()
    await session.refresh(profile)
    return profile


@router.post("/users/{user_id}/kyc/mark-pending", response_model=OwnerProfileRead)
async def mark_user_kyc_pending(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    q = select(OwnerProfile).where(OwnerProfile.user_id == user_id)
    res = await session.execute(q)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Owner profile not found")

    profile.kyc_status = KycStatus.PENDING
    await record_admin_action(session, admin.id, AuditAction.MARK_KYC_PENDING, "OwnerProfile", user_id)

    await session.commit()
    await session.refresh(profile)
    return profile


# -------- Audit logs --------
@router.get("/audit-logs", response_model=list[AuditLogRead])
async def list_audit_logs(
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
    admin=Depends(require_admin),
):
    q = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    res = await session.execute(q)
    return list(res.scalars())
