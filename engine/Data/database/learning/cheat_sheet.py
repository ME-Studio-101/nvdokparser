"""
ШПАРГАЛКА: Быстрый справочник по работе с БД
==============================================

Используйте этот файл как справочник при работе с БД.
"""

# ============================================================================
# 1. ИМПОРТЫ
# ============================================================================

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.orm import Session
from engine.Data.database import init_db, get_db, get_session, CRUDBase
from engine.Data.database.models import BaseModel


# ============================================================================
# 2. СОЗДАНИЕ МОДЕЛИ
# ============================================================================

class MyModel(BaseModel):
    """Пример модели"""
    __tablename__ = "my_table"  # Имя таблицы в БД
    
    # Типы полей:
    name = Column(String(100), nullable=False)           # Текст (до 100 символов)
    description = Column(Text, nullable=True)            # Длинный текст
    age = Column(Integer, nullable=True)                 # Целое число
    price = Column(Float, nullable=True)                 # Дробное число
    is_active = Column(Boolean, default=True)            # Логическое значение
    created = Column(DateTime, default=datetime.utcnow)  # Дата и время
    
    # Опции:
    # nullable=False  - поле обязательно
    # nullable=True   - поле может быть пустым
    # unique=True     - значение должно быть уникальным
    # index=True      - создает индекс для быстрого поиска
    # default=value    - значение по умолчанию


# ============================================================================
# 3. ИНИЦИАЛИЗАЦИЯ БД
# ============================================================================

# Создать все таблицы (вызвать один раз при первом запуске)
init_db()


# ============================================================================
# 4. РАБОТА С СЕССИЕЙ
# ============================================================================

# Способ 1: get_db() - ручное управление
db = get_db()
try:
    # работа с БД
    pass
finally:
    db.close()

# Способ 2: get_session() - автоматическое управление (рекомендуется)
db_gen = get_session()
db = next(db_gen)
try:
    # работа с БД
    pass
finally:
    try:
        next(db_gen)  # Автоматически закроет
    except StopIteration:
        pass


# ============================================================================
# 5. CRUD ОПЕРАЦИИ
# ============================================================================

# Получаем сессию
db = get_db()

# Создаем CRUD для модели
crud = CRUDBase(MyModel, db)

# CREATE - Создание
obj = crud.create({
    "name": "Название",
    "age": 25
})

# READ - Чтение по ID
obj = crud.get(1)  # Получить запись с ID=1

# READ ALL - Чтение всех
all_objects = crud.get_all()                          # Все записи
objects = crud.get_all(skip=0, limit=10)              # С пагинацией
objects = crud.get_all(order_by="name")                # С сортировкой
objects = crud.get_all(order_by="-created_at")        # Сортировка DESC

# READ BY FIELD - Поиск по полю
objects = crud.get_by_field("name", "Значение")       # Все записи с name="Значение"
obj = crud.get_first_by_field("name", "Значение")     # Первая запись

# READ BY FIELDS - Поиск по нескольким полям
objects = crud.get_by_fields(name="Иван", age=25)

# UPDATE - Обновление
updated = crud.update(1, {"name": "Новое имя"})

# DELETE - Удаление
deleted = crud.delete(1)

# COUNT - Подсчет
count = crud.count()

# EXISTS - Проверка существования
exists = crud.exists(1)

# Закрываем сессию
db.close()


# ============================================================================
# 6. КАСТОМНЫЙ CRUD
# ============================================================================

class MyModelCRUD(CRUDBase[MyModel]):
    """Кастомный CRUD с дополнительными методами"""
    
    def get_active(self):
        """Получить все активные записи"""
        return self.db.query(self.model).filter(
            self.model.is_active == True
        ).all()
    
    def get_by_name(self, name: str):
        """Получить по имени"""
        return self.get_first_by_field("name", name)


# Использование
db = get_db()
my_crud = MyModelCRUD(MyModel, db)
active_items = my_crud.get_active()
db.close()


# ============================================================================
# 7. РАБОТА С ТРАНЗАКЦИЯМИ
# ============================================================================

db = get_db()
crud = CRUDBase(MyModel, db)

try:
    # Создаем несколько записей БЕЗ автоматического commit
    obj1 = crud.create({"name": "Первый"}, commit=False)
    obj2 = crud.create({"name": "Второй"}, commit=False)
    
    # Сохраняем все сразу
    crud.commit()
    
except Exception as e:
    # Откатываем изменения при ошибке
    crud.rollback()
    print(f"Ошибка: {e}")

finally:
    db.close()


# ============================================================================
# 8. ПРЕОБРАЗОВАНИЕ В СЛОВАРЬ
# ============================================================================

obj = crud.get(1)
obj_dict = obj.to_dict()
# {'id': 1, 'name': '...', 'created_at': ..., ...}


# ============================================================================
# 9. ТИПИЧНЫЕ ЗАДАЧИ
# ============================================================================

# Задача 1: Создать запись, если её нет
def create_if_not_exists(crud, data, field_name, field_value):
    """Создать запись, если её еще нет"""
    existing = crud.get_first_by_field(field_name, field_value)
    if not existing:
        return crud.create(data)
    return existing

# Задача 2: Обновить или создать (upsert)
def upsert(crud, data, field_name, field_value):
    """Обновить, если есть, иначе создать"""
    existing = crud.get_first_by_field(field_name, field_value)
    if existing:
        return crud.update(existing.id, data)
    else:
        return crud.create(data)

# Задача 3: Получить последние N записей
def get_latest(crud, n=10):
    """Получить последние N записей"""
    return crud.get_all(order_by="-created_at", limit=n)


# ============================================================================
# 10. ОБРАБОТКА ОШИБОК
# ============================================================================

from sqlalchemy.exc import IntegrityError

db = get_db()
crud = CRUDBase(MyModel, db)

try:
    obj = crud.create({"name": "Дубликат"})
    crud.commit()
except IntegrityError as e:
    # Ошибка уникальности (например, дубликат)
    print(f"Запись уже существует: {e}")
    crud.rollback()
except Exception as e:
    # Другая ошибка
    print(f"Ошибка: {e}")
    crud.rollback()
finally:
    db.close()


# ============================================================================
# 11. ПОЛЕЗНЫЕ СОВЕТЫ
# ============================================================================

"""
1. Всегда закрывайте сессию через db.close() или используйте get_session()

2. Используйте commit=False для создания нескольких записей за раз,
   затем вызовите commit() один раз

3. Используйте try/except/finally для обработки ошибок

4. Для уникальных полей используйте unique=True

5. Для часто используемых полей в поиске добавляйте index=True

6. Используйте order_by для сортировки результатов

7. Используйте limit и skip для пагинации больших списков

8. Создавайте кастомные CRUD классы для сложной логики

9. Используйте to_dict() для преобразования в JSON

10. Инициализируйте БД (init_db()) один раз при первом запуске
"""
