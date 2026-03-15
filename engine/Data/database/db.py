"""
Модуль для подключения к базе данных через SQLAlchemy
"""
from pathlib import Path
from typing import Optional, Generator, Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool

from engine.Settings.settings import PATHS


# Базовый класс для моделей
Base = declarative_base()


# Глобальные переменные
_engine: Optional[create_engine] = None
_SessionFactory: Optional[sessionmaker] = None


def get_engine():
    """
    Получить/создать engine
    """
    global _engine
    
    if _engine is None:
        _engine = create_engine(
            f"sqlite:///{PATHS['DB']}",
            connect_args={"check_same_thread": False}, # Разрешаем работу из разных потоков
            poolclass=StaticPool, # Тип пула соединений
            echo=False  # Вывод SQL запросов в консоль
        )
    
    return _engine


def get_session_factory():
    """
    Получить/создать фабрику сессий
    """
    global _SessionFactory
    
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(
            autocommit=False, # Не коммитить автоматически
            autoflush=False, # Не отправлять изменения автоматически
            bind=engine
        )
    
    return _SessionFactory


def get_session() -> Iterator[Session]:
    """
    Получить сессию БД (генератор)
    """
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = get_session_factory()
    session = _SessionFactory()
    try:
        yield session
    finally:
        session.close()


def get_db(db_path: Optional[str] = None) -> Session:
    """
    Получить сессию БД (для прямого использования)
    """
    if db_path:
        # Если указан другой путь, создаем новый engine
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        SessionLocal = sessionmaker(bind=engine)
    else:
        SessionLocal = get_session_factory()
    
    return SessionLocal()


def init_db():
    """
    Инициализировать базу данных (создать все таблицы)
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


# Получаем engine для экспорта
engine = get_engine()
