"""
ОБУЧЕНИЕ: Учимся на практике
==============================

Запускайте этот файл и экспериментируйте с кодом!
Каждый пример можно запускать отдельно.
"""

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Session
from engine.Data.database import init_db, get_db, get_session, CRUDBase
from engine.Data.database.models import BaseModel


# ============================================================================
# УРОК 1: Создаем свою первую модель
# ============================================================================

class Book(BaseModel):
    """
    Модель книги.
    
    Задание: добавьте поле "author" (автор) типа String(100)
    """
    __tablename__ = "books"
    
    title = Column(String(200), nullable=False)  # Название книги
    pages = Column(Integer, nullable=True)        # Количество страниц
    # TODO: добавьте поле author здесь


def lesson_1_create_model():
    """Урок 1: Создание модели и инициализация БД"""
    print("=" * 60)
    print("УРОК 1: Создание модели")
    print("=" * 60)
    
    # Шаг 1: Инициализируем БД (создаем таблицы)
    init_db()
    print("✓ Таблица 'books' создана в БД")
    
    # Шаг 2: Проверяем, что все работает
    print("\nМодель Book содержит поля:")
    print(f"  - id (автоматически)")
    print(f"  - created_at (автоматически)")
    print(f"  - updated_at (автоматически)")
    print(f"  - title")
    print(f"  - pages")
    
    print("\n✓ Урок 1 завершен!")


# ============================================================================
# УРОК 2: Создание записей (CREATE)
# ============================================================================

def lesson_2_create():
    """Урок 2: Создание записей в БД"""
    print("\n" + "=" * 60)
    print("УРОК 2: Создание записей (CREATE)")
    print("=" * 60)
    
    # Получаем сессию БД
    db: Session = get_db()
    
    try:
        # Создаем CRUD для модели Book
        book_crud = CRUDBase(Book, db)
        
        # Создаем первую книгу
        print("\n1. Создаем книгу 'Война и мир'...")
        book1 = book_crud.create({
            "title": "Война и мир",
            "pages": 1274
        })
        print(f"   ✓ Книга создана! ID = {book1.id}")
        print(f"   ✓ Название: {book1.title}")
        print(f"   ✓ Страниц: {book1.pages}")
        print(f"   ✓ Создана: {book1.created_at}")
        
        # Создаем вторую книгу
        print("\n2. Создаем книгу 'Преступление и наказание'...")
        book2 = book_crud.create({
            "title": "Преступление и наказание",
            "pages": 671
        })
        print(f"   ✓ Книга создана! ID = {book2.id}")
        
        # Задание: создайте третью книгу самостоятельно
        print("\n3. ЗАДАНИЕ: Создайте книгу 'Мастер и Маргарита' с 384 страницами")
        # TODO: напишите код здесь
        # book3 = book_crud.create({...})
        
    finally:
        db.close()
    
    print("\n✓ Урок 2 завершен!")


# ============================================================================
# УРОК 3: Чтение записей (READ)
# ============================================================================

def lesson_3_read():
    """Урок 3: Чтение записей из БД"""
    print("\n" + "=" * 60)
    print("УРОК 3: Чтение записей (READ)")
    print("=" * 60)
    
    db: Session = get_db()
    
    try:
        book_crud = CRUDBase(Book, db)
        
        # 1. Чтение по ID
        print("\n1. Читаем книгу с ID=1...")
        book = book_crud.get(1)
        if book:
            print(f"   ✓ Найдена: {book.title}")
        else:
            print("   ✗ Книга не найдена")
        
        # 2. Чтение всех записей
        print("\n2. Читаем все книги...")
        all_books = book_crud.get_all()
        print(f"   ✓ Найдено книг: {len(all_books)}")
        for book in all_books:
            print(f"      - {book.title} (ID: {book.id}, страниц: {book.pages})")
        
        # 3. Поиск по полю
        print("\n3. Ищем книги с названием 'Война и мир'...")
        books = book_crud.get_by_field("title", "Война и мир")
        print(f"   ✓ Найдено: {len(books)}")
        
        # 4. Подсчет записей
        print("\n4. Подсчитываем количество книг...")
        count = book_crud.count()
        print(f"   ✓ Всего книг в БД: {count}")
        
        # Задание: найдите книгу с ID=2 и выведите её название
        print("\n5. ЗАДАНИЕ: Найдите книгу с ID=2 и выведите её название")
        # TODO: напишите код здесь
        
    finally:
        db.close()
    
    print("\n✓ Урок 3 завершен!")


# ============================================================================
# УРОК 4: Обновление записей (UPDATE)
# ============================================================================

def lesson_4_update():
    """Урок 4: Обновление записей"""
    print("\n" + "=" * 60)
    print("УРОК 4: Обновление записей (UPDATE)")
    print("=" * 60)
    
    db: Session = get_db()
    
    try:
        book_crud = CRUDBase(Book, db)
        
        # 1. Обновляем одну книгу
        print("\n1. Обновляем книгу с ID=1...")
        book = book_crud.update(1, {"pages": 1300})
        if book:
            print(f"   ✓ Обновлена: {book.title}")
            print(f"   ✓ Новое количество страниц: {book.pages}")
            print(f"   ✓ Обновлена: {book.updated_at}")
        
        # 2. Проверяем обновление
        print("\n2. Проверяем обновление...")
        updated_book = book_crud.get(1)
        print(f"   ✓ Страниц в БД: {updated_book.pages}")
        
        # Задание: обновите название книги с ID=2 на "Новое название"
        print("\n3. ЗАДАНИЕ: Обновите название книги с ID=2")
        # TODO: напишите код здесь
        
    finally:
        db.close()
    
    print("\n✓ Урок 4 завершен!")


# ============================================================================
# УРОК 5: Удаление записей (DELETE)
# ============================================================================

def lesson_5_delete():
    """Урок 5: Удаление записей"""
    print("\n" + "=" * 60)
    print("УРОК 5: Удаление записей (DELETE)")
    print("=" * 60)
    
    db: Session = get_db()
    
    try:
        book_crud = CRUDBase(Book, db)
        
        # 1. Проверяем количество до удаления
        count_before = book_crud.count()
        print(f"\n1. Книг до удаления: {count_before}")
        
        # 2. Удаляем книгу
        print("\n2. Удаляем книгу с ID=1...")
        deleted = book_crud.delete(1)
        if deleted:
            print("   ✓ Книга удалена")
        else:
            print("   ✗ Книга не найдена")
        
        # 3. Проверяем количество после удаления
        count_after = book_crud.count()
        print(f"\n3. Книг после удаления: {count_after}")
        print(f"   ✓ Удалено: {count_before - count_after} книг")
        
        # 4. Пытаемся прочитать удаленную книгу
        print("\n4. Пытаемся прочитать удаленную книгу...")
        book = book_crud.get(1)
        if book:
            print("   ✗ Книга все еще существует!")
        else:
            print("   ✓ Книга действительно удалена")
        
    finally:
        db.close()
    
    print("\n✓ Урок 5 завершен!")


# ============================================================================
# УРОК 6: Работа с сессиями (get_session vs get_db)
# ============================================================================

def lesson_6_sessions():
    """Урок 6: Разница между get_db() и get_session()"""
    print("\n" + "=" * 60)
    print("УРОК 6: Работа с сессиями")
    print("=" * 60)
    
    print("\n1. Способ 1: get_db() - ручное управление")
    print("   - Нужно закрывать вручную через db.close()")
    print("   - Больше контроля")
    
    db = get_db()
    try:
        book_crud = CRUDBase(Book, db)
        count = book_crud.count()
        print(f"   ✓ Книг в БД: {count}")
    finally:
        db.close()
        print("   ✓ Сессия закрыта вручную")
    
    print("\n2. Способ 2: get_session() - автоматическое управление")
    print("   - Автоматически закрывается")
    print("   - Рекомендуется для большинства случаев")
    
    db_gen = get_session()
    db = next(db_gen)
    try:
        book_crud = CRUDBase(Book, db)
        count = book_crud.count()
        print(f"   ✓ Книг в БД: {count}")
    finally:
        try:
            next(db_gen)  # Закрывает сессию автоматически
        except StopIteration:
            pass
        print("   ✓ Сессия закрыта автоматически")
    
    print("\n✓ Урок 6 завершен!")


# ============================================================================
# УРОК 7: Создание кастомного CRUD
# ============================================================================

def lesson_7_custom_crud():
    """Урок 7: Создание своего CRUD класса"""
    print("\n" + "=" * 60)
    print("УРОК 7: Кастомный CRUD класс")
    print("=" * 60)
    
    # Создаем свой CRUD класс с дополнительными методами
    class BookCRUD(CRUDBase[Book]):
        """
        Кастомный CRUD для книг.
        
        Наследуемся от CRUDBase[Book] - это означает:
        - Все базовые методы (create, get, update, delete) уже есть
        - Можем добавить свои методы
        """
        
        def get_thick_books(self, min_pages: int = 500):
            """
            Получить все толстые книги (больше min_pages страниц)
            
            Args:
                min_pages: Минимальное количество страниц
            
            Returns:
                List[Book]: Список толстых книг
            """
            return self.db.query(self.model).filter(
                self.model.pages >= min_pages
            ).all()
        
        def get_by_title(self, title: str):
            """Получить книгу по названию"""
            return self.get_first_by_field("title", title)
    
    # Используем кастомный CRUD
    db: Session = get_db()
    try:
        book_crud = BookCRUD(Book, db)
        
        # Используем кастомный метод
        print("\n1. Ищем толстые книги (>= 500 страниц)...")
        thick_books = book_crud.get_thick_books(500)
        print(f"   ✓ Найдено толстых книг: {len(thick_books)}")
        for book in thick_books:
            print(f"      - {book.title}: {book.pages} страниц")
        
        # Задание: создайте метод get_short_books() для книг < 300 страниц
        print("\n2. ЗАДАНИЕ: Создайте метод get_short_books()")
        # TODO: добавьте метод в класс BookCRUD выше
        
    finally:
        db.close()
    
    print("\n✓ Урок 7 завершен!")


# ============================================================================
# УРОК 8: Полный пример - библиотека книг
# ============================================================================

def lesson_8_full_example():
    """Урок 8: Полный пример работы с БД"""
    print("\n" + "=" * 60)
    print("УРОК 8: Полный пример - Библиотека книг")
    print("=" * 60)
    
    db: Session = get_db()
    
    try:
        book_crud = CRUDBase(Book, db)
        
        # 1. Создаем несколько книг
        print("\n1. Создаем библиотеку книг...")
        books_data = [
            {"title": "1984", "pages": 328},
            {"title": "Гарри Поттер", "pages": 320},
            {"title": "Властелин колец", "pages": 1178},
        ]
        
        created_books = []
        for book_data in books_data:
            book = book_crud.create(book_data)
            created_books.append(book)
            print(f"   ✓ Добавлена: {book.title}")
        
        # 2. Выводим все книги
        print("\n2. Список всех книг:")
        all_books = book_crud.get_all(order_by="title")
        for i, book in enumerate(all_books, 1):
            print(f"   {i}. {book.title} - {book.pages} страниц")
        
        # 3. Ищем самую толстую книгу
        print("\n3. Самая толстая книга:")
        all_books = book_crud.get_all(order_by="-pages", limit=1)
        if all_books:
            thickest = all_books[0]
            print(f"   ✓ {thickest.title} - {thickest.pages} страниц")
        
        # 4. Статистика
        print("\n4. Статистика библиотеки:")
        total_books = book_crud.count()
        total_pages = sum(book.pages for book in book_crud.get_all() if book.pages)
        print(f"   ✓ Всего книг: {total_books}")
        print(f"   ✓ Всего страниц: {total_pages}")
        
        # 5. Очистка (опционально)
        print("\n5. Очистка библиотеки...")
        for book in created_books:
            book_crud.delete(book.id)
        print(f"   ✓ Удалено книг: {len(created_books)}")
        
    finally:
        db.close()
    
    print("\n✓ Урок 8 завершен!")


# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ - ЗАПУСК ВСЕХ УРОКОВ
# ============================================================================

def run_all_lessons():
    """Запустить все уроки по порядку"""
    print("\n" + "=" * 60)
    print("ОБУЧЕНИЕ SQLAlchemy - ВСЕ УРОКИ")
    print("=" * 60)
    
    # Инициализируем БД один раз
    init_db()
    
    # Запускаем уроки
    lesson_1_create_model()
    lesson_2_create()
    lesson_3_read()
    lesson_4_update()
    lesson_5_delete()
    lesson_6_sessions()
    lesson_7_custom_crud()
    lesson_8_full_example()
    
    print("\n" + "=" * 60)
    print("ВСЕ УРОКИ ЗАВЕРШЕНЫ! 🎉")
    print("=" * 60)
    print("\nТеперь вы знаете основы работы с SQLAlchemy!")
    print("Экспериментируйте с кодом и создавайте свои модели!")


if __name__ == "__main__":
    # Запускаем все уроки
    # run_all_lessons()
    
    # Или запустите отдельный урок:
    lesson_1_create_model()
    # lesson_2_create()
    # и т.д.
