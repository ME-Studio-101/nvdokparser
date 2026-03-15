from sqlalchemy.orm import Session
from sqlalchemy import select

from engine.Data.database.models import Site

def find_site_by_alias(session: Session, alias: str) -> Site | None:
    pattern = f"%|{alias}|%"   # чтобы не ловить подстроки
    stmt = select(Site).where(Site.names.like(pattern))
    return session.execute(stmt).scalars().first()