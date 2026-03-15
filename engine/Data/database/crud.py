"""
Модуль с базовыми CRUD операциями через SQLAlchemy ORM
"""
from typing import Optional, List, Type, TypeVar, Generic, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .db import get_session
from .models import BaseModel


# Тип для Generic CRUD
ModelType = TypeVar("ModelType", bound=BaseModel)


class CRUDBase(Generic[ModelType]):
    """
    Базовый класс для CRUD операций
    
    Использование:
        class UserCRUD(CRUDBase[User]):
            pass
        
        user_crud = UserCRUD(User, db)
        user = user_crud.create({"name": "Иван"})
    """
    
    def __init__(self, model: Type[ModelType], db: Optional[Session] = None):
        """
        Инициализация CRUD операций
        
        Args:
            model: Класс модели SQLAlchemy
            db: Сессия БД. Если не указана, будет создана новая
        """
        self.model = model
        self._db = db
    
    @property
    def db(self) -> Session:
        """Получить сессию БД"""
        if self._db is None:
            # Создаем новую сессию, если не передана
            self._db = next(get_session())
        return self._db
    
    def create(self, data: Dict[str, Any], commit: bool = True) -> ModelType:
        """
        Создать новую запись
        
        Args:
            data: Словарь с данными {column: value}
            commit: Автоматически закоммитить транзакцию
            
        Returns:
            ModelType: Созданная модель
        """
        db_obj = self.model(**data)
        self.db.add(db_obj)
        if commit:
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def get(self, record_id: int) -> Optional[ModelType]:
        """
        Получить запись по ID
        
        Args:
            record_id: ID записи
            
        Returns:
            ModelType: Модель или None
        """
        return self.db.query(self.model).filter(self.model.id == record_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Получить все записи
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            order_by: Поле для сортировки (например, "id" или "-created_at" для DESC)
            
        Returns:
            List[ModelType]: Список моделей
        """
        query = self.db.query(self.model)
        
        # Сортировка
        if order_by:
            if order_by.startswith("-"):
                # DESC сортировка
                field = getattr(self.model, order_by[1:])
                query = query.order_by(field.desc())
            else:
                # ASC сортировка
                field = getattr(self.model, order_by)
                query = query.order_by(field)
        
        # Пагинация
        query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_by_field(self, field: str, value: Any) -> List[ModelType]:
        """
        Получить записи по полю
        
        Args:
            field: Имя поля
            value: Значение поля
            
        Returns:
            List[ModelType]: Список моделей
        """
        return self.db.query(self.model).filter(getattr(self.model, field) == value).all()
    
    def get_by_fields(self, **filters) -> List[ModelType]:
        """
        Получить записи по нескольким полям
        
        Args:
            **filters: Поля и их значения для фильтрации
            
        Returns:
            List[ModelType]: Список моделей
            
        Example:
            users = crud.get_by_fields(name="Иван", age=25)
        """
        conditions = [getattr(self.model, key) == value for key, value in filters.items()]
        return self.db.query(self.model).filter(and_(*conditions)).all()
    
    def get_first_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """
        Получить первую запись по полю
        
        Args:
            field: Имя поля
            value: Значение поля
            
        Returns:
            ModelType: Модель или None
        """
        return self.db.query(self.model).filter(getattr(self.model, field) == value).first()
    
    def update(
        self,
        record_id: int,
        data: Dict[str, Any],
        commit: bool = True
    ) -> Optional[ModelType]:
        """
        Обновить запись
        
        Args:
            record_id: ID записи
            data: Словарь с данными для обновления {column: value}
            commit: Автоматически закоммитить транзакцию
            
        Returns:
            ModelType: Обновленная модель или None, если запись не найдена
        """
        db_obj = self.get(record_id)
        if not db_obj:
            return None
        
        for key, value in data.items():
            setattr(db_obj, key, value)
        
        if commit:
            self.db.commit()
            self.db.refresh(db_obj)
        
        return db_obj
    
    def delete(self, record_id: int, commit: bool = True) -> bool:
        """
        Удалить запись
        
        Args:
            record_id: ID записи
            commit: Автоматически закоммитить транзакцию
            
        Returns:
            bool: True если запись удалена, False если не найдена
        """
        db_obj = self.get(record_id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        if commit:
            self.db.commit()
        
        return True
    
    def count(self) -> int:
        """
        Получить количество записей в таблице
        
        Returns:
            int: Количество записей
        """
        return self.db.query(self.model).count()
    
    def exists(self, record_id: int) -> bool:
        """
        Проверить существование записи
        
        Args:
            record_id: ID записи
            
        Returns:
            bool: True если запись существует
        """
        return self.db.query(self.model).filter(self.model.id == record_id).first() is not None
    
    def commit(self):
        """Закоммитить текущую транзакцию"""
        self.db.commit()
    
    def rollback(self):
        """Откатить текущую транзакцию"""
        self.db.rollback()
