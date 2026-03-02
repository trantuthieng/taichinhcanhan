"""Audit log repository."""

import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.audit import AuditLog
from repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session: Session):
        super().__init__(AuditLog, session)

    def log_action(
        self,
        user_id: int,
        action: str,
        entity_type: str = None,
        entity_id: int = None,
        old_value: dict = None,
        new_value: dict = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=json.dumps(old_value, ensure_ascii=False, default=str) if old_value else None,
            new_value=json.dumps(new_value, ensure_ascii=False, default=str) if new_value else None,
        )
        self.session.add(entry)
        self.session.flush()
        return entry

    def get_recent(self, user_id: int, limit: int = 50) -> List[AuditLog]:
        return (
            self.session.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
