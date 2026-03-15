"""
ОБУЧЕНИЕ: Разбор кода базы данных SQLAlchemy
============================================

Этот файл содержит подробные объяснения каждого компонента системы БД.
Читайте по порядку, выполняйте примеры и экспериментируйте!
"""

# ============================================================================
# ЧАСТЬ 1: ЧТО ТАКОЕ SQLAlchemy И ЗАЧЕМ ОН НУЖЕН?
# ============================================================================

"""
SQLAlchemy - это библиотека для работы с базами данных в Python.

БЕЗ SQLAlchemy (чистый SQL):
    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Иван",))
    # Проблемы:
    # - Нужно писать SQL вручную
    # - Легко сделать ошибку
    # - Нет проверки типов
    # - Сложно поддерживать

С SQLAlchemy (ORM):
    user = User(name="Иван")
    db.add(user)
    db.commit()
    # Преимущества:
    # - Код на Python, не SQL
    # - Автоматическая проверка
    # - Легко читать и понимать
"""


# ============================================================================
# ЧАСТЬ 2: БАЗОВЫЕ КОНЦЕПЦИИ SQLAlchemy
# ============================================================================

"""
1. ENGINE (движок)
   - Это "мост" между Python и базой данных
   - Знает, КАК подключиться к БД (SQLite, PostgreSQL, MySQL и т.д.)
   - Создается один раз на все приложение

2. SESSION (сессия)
   - Это "рабочее пространство" для работы с БД
   - Через сессию мы добавляем, изменяем, удаляем данные
   - Сессию нужно закрывать после работы

3. MODEL (модель)
   - Это Python класс, который представляет таблицу в БД
   - Каждый объект модели = одна строка в таблице
   - Поля класса = колонки в таблице

4. BASE (базовый класс)
   - Это "родитель" для всех моделей
   - SQLAlchemy использует его, чтобы понять структуру таблиц
"""


# ============================================================================
# ЧАСТЬ 3: РАЗБОР db.py - ПОДКЛЮЧЕНИЕ К БД
# ============================================================================

"""
Файл db.py отвечает за подключение к базе данных.

Давайте разберем его по частям:
"""

# Импорты
from pathlib import Path
from typing import Optional, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool

"""
Что здесь происходит:
- pathlib.Path - для работы с путями к файлам
- typing - для указания типов (помогает IDE понимать код)
- create_engine - создает "движок" для подключения к БД
- sessionmaker - создает "фабрику" для создания сессий
- Session - класс сессии SQLAlchemy
- declarative_base - создает базовый класс для моделей
"""

# Базовый класс для моделей
Base = declarative_base()

"""
Base - это "родитель" для всех наших моделей.
Когда мы создаем модель (например, User), мы наследуемся от Base.
SQLAlchemy смотрит на Base и знает, какие таблицы нужно создать.

Пример:
    class User(Base):  # <- наследуемся от Base
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
"""

# Глобальные переменные
_engine: Optional[create_engine] = None
_SessionLocal: Optional[sessionmaker] = None

"""
Эти переменные хранят:
- _engine - движок БД (создается один раз)
- _SessionLocal - фабрика сессий (создается один раз)

Почему глобальные?
- Чтобы не создавать их заново каждый раз
- Это паттерн "Singleton" (один экземпляр на все приложение)
"""


def get_db_path() -> Path:
    """
    Эта функция определяет, ГДЕ будет храниться файл базы данных.
    
    Returns:
        Path: Путь к файлу БД (Data/app.db)
    
    Как работает:
    1. Находит папку, где находится этот файл (db.py)
    2. Поднимается на уровень вверх (parent) - попадаем в Data/
    3. Создает путь к файлу app.db
    4. Создает папку Data/, если её нет
    """
    current_dir = Path(__file__).parent.parent  # Папка Data/
    db_path = current_dir / "app.db"  # Файл app.db в папке Data/
    db_path.parent.mkdir(parents=True, exist_ok=True)  # Создаем папку, если нет
    return db_path


def get_engine(db_path: Optional[str] = None):
    """
    Создает или возвращает "движок" для подключения к БД.
    
    Движок (engine) - это объект, который знает:
    - К какой БД подключаться (SQLite в нашем случае)
    - Где находится файл БД
    - Как с ней работать
    
    Args:
        db_path: Путь к файлу БД (если не указан, используется Data/app.db)
    
    Returns:
        Engine: SQLAlchemy engine
    
    Как работает:
    1. Проверяет, создан ли уже движок (_engine)
    2. Если нет - создает новый
    3. Если да - возвращает существующий (Singleton паттерн)
    """
    global _engine
    
    if _engine is None:  # Если движок еще не создан
        if db_path is None:
            db_path = get_db_path()  # Получаем путь по умолчанию
        else:
            db_path = Path(db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Создаем движок для SQLite
        database_url = f"sqlite:///{db_path}"
        # sqlite:/// - это формат URL для SQLite
        # Например: sqlite:///C:/dev/nvparser/engine/Data/app.db
        
        _engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},  # Разрешаем работу из разных потоков
            poolclass=StaticPool,  # Тип пула соединений
            echo=False  # True = показывать все SQL запросы (для отладки)
        )
    
    return _engine


def get_session_factory():
    """
    Создает "фабрику" для создания сессий.
    
    Фабрика (factory) - это функция/класс, который создает объекты.
    В нашем случае - создает сессии для работы с БД.
    
    Returns:
        sessionmaker: Фабрика для создания сессий
    
    Как работает:
    1. Получает движок (engine)
    2. Создает sessionmaker - это "завод" по производству сессий
    3. Возвращает этот "завод"
    
    Зачем нужна фабрика?
    - Чтобы создавать новые сессии, когда нужно
    - Каждая сессия - это отдельное "рабочее пространство"
    """
    global _SessionLocal
    
    if _SessionLocal is None:  # Если фабрика еще не создана
        engine = get_engine()  # Получаем движок
        _SessionLocal = sessionmaker(
            autocommit=False,  # Не коммитить автоматически (мы делаем это вручную)
            autoflush=False,   # Не отправлять изменения автоматически
            bind=engine        # Привязываем к нашему движку
        )
    
    return _SessionLocal


def get_session() -> Generator[Session, None, None]:
    """
    Создает сессию БД и автоматически закрывает её после использования.
    
    Это ГЕНЕРАТОР - специальная функция, которая работает с yield.
    
    Yields:
        Session: SQLAlchemy сессия
    
    Как работает:
    1. Создает новую сессию
    2. Отдает её (yield) - код может использовать
    3. После использования автоматически закрывает (finally)
    
    Пример использования:
        for db in get_session():  # <- цикл создает сессию
            user = db.query(User).first()  # <- работаем с БД
        # <- здесь сессия автоматически закроется
    
    Или с next():
        db_gen = get_session()
        db = next(db_gen)  # Получаем сессию
        # ... работаем ...
        next(db_gen)  # Закрываем сессию
    """
    SessionLocal = get_session_factory()  # Получаем фабрику
    db = SessionLocal()  # Создаем новую сессию
    try:
        yield db  # Отдаем сессию (код может использовать)
    finally:
        db.close()  # Всегда закрываем сессию, даже если была ошибка


def get_db(db_path: Optional[str] = None) -> Session:
    """
    Получить сессию БД напрямую (без генератора).
    
    Args:
        db_path: Путь к файлу БД (если нужна другая БД)
    
    Returns:
        Session: SQLAlchemy сессия
    
    ВАЖНО: Сессию нужно закрывать вручную через db.close()!
    
    Пример:
        db = get_db()
        try:
            # работаем с БД
        finally:
            db.close()
    
    Когда использовать get_db() vs get_session()?
    - get_db() - когда нужен прямой контроль
    - get_session() - когда нужна автоматическая очистка (рекомендуется)
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
    
    return SessionLocal()  # Создаем и возвращаем сессию


def init_db():
    """
    Инициализирует базу данных - создает все таблицы.
    
    Как работает:
    1. Получает движок
    2. Base.metadata содержит информацию о всех моделях
    3. create_all() создает все таблицы, которые еще не существуют
    
    Когда вызывать?
    - Один раз при первом запуске приложения
    - Или когда добавили новую модель
    
    Пример:
        init_db()  # Создаст все таблицы из всех моделей
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    # Base.metadata - это "каталог" всех моделей
    # create_all() - создает таблицы для всех моделей, которые наследуются от Base


# ============================================================================
# ЧАСТЬ 4: РАЗБОР models.py - БАЗОВАЯ МОДЕЛЬ
# ============================================================================

"""
Файл models.py содержит базовый класс для всех моделей.

Модель - это Python класс, который представляет таблицу в БД.
Каждый объект модели = одна строка в таблице.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from .db import Base


class BaseModel(Base):
    """
    Базовый класс для всех моделей.
    
    Все модели должны наследоваться от BaseModel, а не от Base напрямую.
    Почему? Потому что BaseModel добавляет полезные поля автоматически.
    
    __abstract__ = True означает:
    - Это НЕ таблица сама по себе
    - Это "шаблон" для других моделей
    - SQLAlchemy не будет создавать таблицу для BaseModel
    
    Автоматически добавляет каждому наследнику:
    - id: первичный ключ (уникальный номер записи)
    - created_at: когда создана запись
    - updated_at: когда последний раз обновлена
    """
    __abstract__ = True  # Это абстрактный класс (не создает таблицу)
    
    # Поля, которые будут в КАЖДОЙ модели
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # primary_key=True - это главный ключ (уникальный идентификатор)
    # index=True - создает индекс для быстрого поиска
    # autoincrement=True - автоматически увеличивается (1, 2, 3, ...)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # default=datetime.utcnow - автоматически ставит текущее время при создании
    # nullable=False - поле обязательно (не может быть пустым)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    # onupdate=datetime.utcnow - автоматически обновляется при изменении записи
    
    def to_dict(self):
        """
        Преобразует модель в обычный словарь Python.
        
        Зачем это нужно?
        - Иногда нужно отправить данные в JSON
        - Или просто получить словарь вместо объекта
        
        Returns:
            dict: Словарь с данными модели
        
        Пример:
            user = User(username="Иван")
            user_dict = user.to_dict()
            # {'id': 1, 'username': 'Иван', 'created_at': ...}
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        # self.__table__.columns - все колонки таблицы
        # getattr(self, column.name) - получаем значение поля
        # Создаем словарь: имя_колонки -> значение


# ============================================================================
# ЧАСТЬ 5: ПРИМЕР СОЗДАНИЯ МОДЕЛИ
# ============================================================================

"""
Теперь давайте создадим свою модель, чтобы понять, как это работает.
"""

from sqlalchemy import Column, String, Integer

class User(BaseModel):
    """
    Пример модели пользователя.
    
    Это НАСТОЯЩАЯ таблица (не абстрактная).
    SQLAlchemy создаст таблицу "users" в БД.
    """
    __tablename__ = "users"  # Имя таблицы в БД
    
    # Поля таблицы
    username = Column(String(50), unique=True, nullable=False, index=True)
    # String(50) - текстовая колонка, максимум 50 символов
    # unique=True - значение должно быть уникальным
    # nullable=False - поле обязательно
    # index=True - создает индекс для быстрого поиска
    
    email = Column(String(100), unique=True, nullable=True)
    # nullable=True - поле может быть пустым (NULL)
    
    age = Column(Integer, nullable=True)
    # Integer - целое число


"""
Что происходит, когда мы создаем модель?

1. SQLAlchemy видит, что User наследуется от BaseModel
2. BaseModel наследуется от Base
3. SQLAlchemy смотрит на все Column в классе User
4. Создает SQL запрос для создания таблицы:

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INTEGER
);

5. Когда мы вызываем init_db(), все таблицы создаются автоматически!
"""


# ============================================================================
# ЧАСТЬ 6: РАЗБОР crud.py - ОПЕРАЦИИ С ДАННЫМИ
# ============================================================================

"""
CRUD = Create, Read, Update, Delete
Это основные операции с данными.

Файл crud.py содержит универсальный класс для работы с любой моделью.
"""

from typing import Optional, List, Type, TypeVar, Generic, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .db import get_session
from .models import BaseModel

# TypeVar - это "переменная типа" для Generic
ModelType = TypeVar("ModelType", bound=BaseModel)
# bound=BaseModel означает: ModelType может быть только классом, который наследуется от BaseModel


class CRUDBase(Generic[ModelType]):
    """
    Базовый класс для CRUD операций.
    
    Generic[ModelType] означает:
    - Это "универсальный" класс
    - ModelType - это тип модели (User, Product, Order и т.д.)
    - Когда мы создаем CRUDBase[User], ModelType становится User
    
    Зачем Generic?
    - Чтобы IDE и Python понимали типы
    - user_crud.get(1) вернет User, а не просто "что-то"
    - Безопасность типов
    
    Пример использования:
        user_crud = CRUDBase(User, db)
        user = user_crud.create({"username": "Иван"})
        # user имеет тип User, а не просто "объект"
    """
    
    def __init__(self, model: Type[ModelType], db: Optional[Session] = None):
        """
        Инициализация CRUD.
        
        Args:
            model: Класс модели (например, User)
            db: Сессия БД (если не указана, создастся новая)
        
        Как работает:
        - Сохраняем класс модели (User)
        - Сохраняем сессию БД
        - Теперь можем работать с этой моделью через эту сессию
        """
        self.model = model  # Класс модели (User)
        self._db = db       # Сессия БД
    
    @property
    def db(self) -> Session:
        """
        Свойство (property) для получения сессии.
        
        Если сессия не была передана при создании, создает новую.
        
        Returns:
            Session: Сессия БД
        """
        if self._db is None:
            self._db = next(get_session())
        return self._db
    
    def create(self, data: Dict[str, Any], commit: bool = True) -> ModelType:
        """
        Создать новую запись в БД.
        
        Args:
            data: Словарь с данными {"поле": "значение"}
            commit: Автоматически сохранить изменения
        
        Returns:
            ModelType: Созданная модель
        
        Как работает:
        1. Создаем объект модели: User(**data)
           Например: User(username="Иван", email="ivan@test.com")
        2. Добавляем в сессию: db.add(user)
           (пока только в памяти, не в БД!)
        3. Сохраняем: db.commit()
           (теперь реально в БД)
        4. Обновляем объект: db.refresh(user)
           (получаем id и другие поля из БД)
        
        Пример:
            user = user_crud.create({"username": "Иван", "age": 25})
            print(user.id)  # 1 (автоматически присвоен БД)
        """
        db_obj = self.model(**data)  # Создаем объект модели
        # **data распаковывает словарь: {"username": "Иван"} -> username="Иван"
        
        self.db.add(db_obj)  # Добавляем в сессию (пока в памяти)
        
        if commit:
            self.db.commit()      # Сохраняем в БД
            self.db.refresh(db_obj)  # Обновляем объект (получаем id)
        
        return db_obj
    
    def get(self, record_id: int) -> Optional[ModelType]:
        """
        Получить запись по ID.
        
        Args:
            record_id: ID записи
        
        Returns:
            ModelType или None, если не найдено
        
        Как работает:
        1. db.query(User) - начинаем запрос к таблице users
        2. .filter(User.id == record_id) - фильтруем по ID
        3. .first() - берем первую запись (или None)
        
        Пример:
            user = user_crud.get(1)
            if user:
                print(user.username)
        """
        return self.db.query(self.model).filter(self.model.id == record_id).first()
        # self.model - это класс модели (User)
        # self.model.id - это поле id из модели
        # filter() - условие WHERE в SQL
        # first() - получить первую запись или None
    
    def get_all(
        self,
        skip: int = 0,
        limit: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Получить все записи с пагинацией и сортировкой.
        
        Args:
            skip: Сколько записей пропустить (для пагинации)
            limit: Максимум записей
            order_by: Поле для сортировки ("id" или "-created_at" для DESC)
        
        Returns:
            List[ModelType]: Список моделей
        
        Пример:
            # Первые 10 записей
            users = user_crud.get_all(skip=0, limit=10)
            
            # Следующие 10 записей
            users = user_crud.get_all(skip=10, limit=10)
            
            # Сортировка по дате создания (новые первые)
            users = user_crud.get_all(order_by="-created_at")
        """
        query = self.db.query(self.model)  # Начинаем запрос
        
        # Сортировка
        if order_by:
            if order_by.startswith("-"):
                # DESC сортировка (убывание)
                field = getattr(self.model, order_by[1:])  # Убираем "-"
                query = query.order_by(field.desc())
            else:
                # ASC сортировка (возрастание)
                field = getattr(self.model, order_by)
                query = query.order_by(field)
        
        # Пагинация
        query = query.offset(skip)  # Пропускаем skip записей
        if limit:
            query = query.limit(limit)  # Берем максимум limit записей
        
        return query.all()  # Выполняем запрос и получаем все результаты
    
    def update(
        self,
        record_id: int,
        data: Dict[str, Any],
        commit: bool = True
    ) -> Optional[ModelType]:
        """
        Обновить запись.
        
        Args:
            record_id: ID записи
            data: Словарь с полями для обновления
            commit: Автоматически сохранить
        
        Returns:
            ModelType или None, если запись не найдена
        
        Как работает:
        1. Находим запись по ID
        2. Обновляем поля через setattr()
        3. Сохраняем изменения
        
        Пример:
            user = user_crud.update(1, {"age": 26, "email": "new@test.com"})
        """
        db_obj = self.get(record_id)  # Находим запись
        if not db_obj:
            return None
        
        # Обновляем каждое поле
        for key, value in data.items():
            setattr(db_obj, key, value)
            # setattr(obj, "age", 26) эквивалентно obj.age = 26
        
        if commit:
            self.db.commit()      # Сохраняем
            self.db.refresh(db_obj)  # Обновляем объект
        
        return db_obj
    
    def delete(self, record_id: int, commit: bool = True) -> bool:
        """
        Удалить запись.
        
        Args:
            record_id: ID записи
            commit: Автоматически сохранить
        
        Returns:
            bool: True если удалено, False если не найдено
        
        Пример:
            deleted = user_crud.delete(1)
            if deleted:
                print("Пользователь удален")
        """
        db_obj = self.get(record_id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)  # Помечаем для удаления
        if commit:
            self.db.commit()  # Реально удаляем из БД
        
        return True


# ============================================================================
# ЧАСТЬ 7: ПРАКТИЧЕСКИЙ ПРИМЕР - ПОЛНЫЙ ЦИКЛ РАБОТЫ
# ============================================================================

"""
Теперь давайте посмотрим, как все это работает вместе.
"""

def example_full_cycle():
    """
    Полный пример работы с БД от начала до конца.
    """
    # ШАГ 1: Импортируем все необходимое
    from engine.Data.database import init_db, get_db, CRUDBase
    from sqlalchemy import Column, String, Integer
    from engine.Data.database.models import BaseModel
    
    # ШАГ 2: Создаем модель (если еще не создана)
    class Product(BaseModel):
        __tablename__ = "products"
        name = Column(String(100), nullable=False)
        price = Column(Integer, nullable=False)
    
    # ШАГ 3: Инициализируем БД (создаем таблицы)
    init_db()
    print("✓ База данных инициализирована")
    
    # ШАГ 4: Получаем сессию БД
    db = get_db()
    
    try:
        # ШАГ 5: Создаем CRUD для нашей модели
        product_crud = CRUDBase(Product, db)
        
        # ШАГ 6: CREATE - создаем запись
        product = product_crud.create({
            "name": "Ноутбук",
            "price": 50000
        })
        print(f"✓ Создан продукт: {product.name}, ID={product.id}")
        
        # ШАГ 7: READ - читаем запись
        found_product = product_crud.get(product.id)
        print(f"✓ Найден продукт: {found_product.name}, цена={found_product.price}")
        
        # ШАГ 8: UPDATE - обновляем запись
        updated_product = product_crud.update(product.id, {"price": 45000})
        print(f"✓ Обновлена цена: {updated_product.price}")
        
        # ШАГ 9: READ ALL - читаем все записи
        all_products = product_crud.get_all()
        print(f"✓ Всего продуктов: {len(all_products)}")
        
        # ШАГ 10: DELETE - удаляем запись
        product_crud.delete(product.id)
        print(f"✓ Продукт удален")
        
    finally:
        # ШАГ 11: Закрываем сессию
        db.close()
        print("✓ Сессия закрыта")


# ============================================================================
# ЧАСТЬ 8: ЧАСТЫЕ ВОПРОСЫ И ОТВЕТЫ
# ============================================================================

"""
Q: Когда использовать get_db() vs get_session()?
A: 
   - get_db() - когда нужен прямой контроль, не забыть закрыть через db.close()
   - get_session() - когда нужна автоматическая очистка (рекомендуется)

Q: Что такое commit()?
A: 
   - commit() сохраняет изменения в БД
   - До commit() все изменения только в памяти
   - После commit() изменения реально записываются в файл БД

Q: Зачем нужен refresh()?
A: 
   - После создания записи БД присваивает ID
   - refresh() обновляет объект, чтобы получить этот ID
   - Без refresh() у объекта может не быть id

Q: Что такое Generic[ModelType]?
A: 
   - Это способ сделать класс "универсальным"
   - CRUDBase[User] работает с User
   - CRUDBase[Product] работает с Product
   - Python и IDE понимают типы

Q: Можно ли создать кастомный CRUD?
A: 
   Да! Наследуйтесь от CRUDBase и добавляйте свои методы:
   
   class UserCRUD(CRUDBase[User]):
       def get_by_email(self, email: str):
           return self.get_first_by_field("email", email)
"""


if __name__ == "__main__":
    print("Это обучающий файл!")
    print("Читайте комментарии в коде для понимания.")
    print("\nДля запуска примеров используйте example.py")
