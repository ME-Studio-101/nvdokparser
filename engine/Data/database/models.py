"""
Базовый класс для моделей SQLAlchemy
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from .db import Base


class BaseModel(Base):
    """
    Базовый класс для всех моделей
    
    Автоматически добавляет:
    - id: первичный ключ
    - created_at: время создания
    - updated_at: время последнего обновления
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """
        Преобразовать модель в словарь
        
        Returns:
            dict: Словарь с данными модели
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class Site(BaseModel):
    __tablename__ = "sites"

    # Пример значения: "|ozon.ru|ozon|озон|"
    names = Column(String(1024), nullable=False)
    label = Column(String(255), nullable=False)
    erp_id = Column(Integer, nullable=False)

    @property
    def names_list(self) -> list[str]:
        return [n for n in self.names.split("|") if n]

    @names_list.setter
    def names_list(self, value: list[str]):
        # убираем пустые и пробелы
        cleaned = [v.strip() for v in value if v and v.strip()]
        self.names = "|" + "|".join(cleaned) + "|" if cleaned else ""


class Town(BaseModel):
    __tablename__ = "towns"

    erp_id = Column(Integer, nullable=False)
    label = Column(String(255), nullable=False)
    # names = Column(String(1024), nullable=False)
    group = Column(Integer, nullable=False)
    subGroup = Column(String(255), nullable=False)
    rateSource = Column(String(255), nullable=False)
    
    # @property
    # def names_list(self) -> list[str]:
    #     return [n for n in self.names.split("|") if n]

    # @names_list.setter
    # def names_list(self, value: list[str]):
    #     # убираем пустые и пробелы
    #     cleaned = [v.strip() for v in value if v and v.strip()]
    #     self.names = "|" + "|".join(cleaned) + "|" if cleaned else ""

