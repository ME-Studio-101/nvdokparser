"""
Пример использования базы данных с SQLAlchemy ORM
"""
from typing import Optional
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Session
from .db import Base, get_db, get_session, init_db
from .models import BaseModel
from .crud import CRUDBase


# Пример модели
class User(BaseModel):
    """Пример модели пользователя"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    age = Column(Integer, nullable=True)


def example_basic_usage():
    """Базовый пример использования"""
    print("=" * 60)
    print("Пример 1: Базовое использование")
    print("=" * 60)
    
    # Инициализируем БД (создаем таблицы)
    init_db()
    print("✓ База данных инициализирована")
    
    # Получаем сессию
    db: Session = get_db()
    
    # Создаем CRUD для модели User
    user_crud = CRUDBase(User, db)
    
    # CREATE - создание записи
    print("\n1. CREATE - создание пользователя...")
    user = user_crud.create({
        "username": "test_user",
        "email": "test@example.com",
        "age": 25
    })
    print(f"   ✓ Создан пользователь: ID={user.id}, username={user.username}")
    
    # READ - чтение записи
    print("\n2. READ - чтение пользователя...")
    found_user = user_crud.get(user.id)
    print(f"   ✓ Найден пользователь: {found_user.username}, email={found_user.email}")
    
    # UPDATE - обновление записи
    print("\n3. UPDATE - обновление пользователя...")
    updated_user = user_crud.update(user.id, {"age": 26, "email": "newemail@example.com"})
    print(f"   ✓ Обновлен пользователь: age={updated_user.age}, email={updated_user.email}")
    
    # READ ALL - чтение всех записей
    print("\n4. READ ALL - чтение всех пользователей...")
    all_users = user_crud.get_all()
    print(f"   ✓ Всего пользователей: {len(all_users)}")
    
    # GET BY FIELD - поиск по полю
    print("\n5. GET BY FIELD - поиск по username...")
    users_by_name = user_crud.get_by_field("username", "test_user")
    print(f"   ✓ Найдено пользователей: {len(users_by_name)}")
    
    # COUNT - подсчет записей
    print("\n6. COUNT - подсчет записей...")
    count = user_crud.count()
    print(f"   ✓ Всего записей в таблице: {count}")
    
    # DELETE - удаление записи
    print("\n7. DELETE - удаление пользователя...")
    deleted = user_crud.delete(user.id)
    print(f"   ✓ Пользователь удален: {deleted}")
    
    # Проверка удаления
    found_after_delete = user_crud.get(user.id)
    print(f"   ✓ Проверка: пользователь найден = {found_after_delete is not None}")
    
    db.close()
    print("\n" + "=" * 60)


def example_with_context():
    """Пример использования с контекстным менеджером"""
    print("\n" + "=" * 60)
    print("Пример 2: Использование с контекстным менеджером")
    print("=" * 60)
    
    # Использование get_session() как генератора
    db_gen = get_session()
    db: Session = next(db_gen)
    
    try:
        user_crud = CRUDBase(User, db)
        
        # Создаем несколько пользователей
        user1 = user_crud.create({"username": "user1", "email": "user1@test.com"})
        user2 = user_crud.create({"username": "user2", "email": "user2@test.com"})
        
        print(f"✓ Создано пользователей: {user_crud.count()}")
        
        # Получаем всех с сортировкой
        users = user_crud.get_all(order_by="-created_at", limit=10)
        print(f"✓ Получено пользователей: {len(users)}")
        
    finally:
        try:
            next(db_gen)  # Завершаем генератор (он сам закроет сессию)
        except StopIteration:
            pass
    
    print("=" * 60)


def example_custom_crud():
    """Пример создания кастомного CRUD класса"""
    print("\n" + "=" * 60)
    print("Пример 3: Кастомный CRUD класс")
    print("=" * 60)
    
    class UserCRUD(CRUDBase[User]):
        """Кастомный CRUD для пользователей с дополнительными методами"""
        
        def get_by_email(self, email: str) -> Optional[User]:
            """Получить пользователя по email"""
            return self.get_first_by_field("email", email)
        
        def get_adults(self) -> list[User]:
            """Получить всех взрослых пользователей (age >= 18)"""
            return self.db.query(self.model).filter(self.model.age >= 18).all()
    
    db: Session = get_db()
    try:
        user_crud = UserCRUD(User, db)
        
        # Используем кастомные методы
        user = user_crud.get_by_email("test@example.com")
        if user:
            print(f"✓ Найден пользователь по email: {user.username}")
        
        adults = user_crud.get_adults()
        print(f"✓ Взрослых пользователей: {len(adults)}")
    finally:
        db.close()
    print("=" * 60)


if __name__ == "__main__":
    example_basic_usage()
    example_with_context()
    example_custom_crud()
