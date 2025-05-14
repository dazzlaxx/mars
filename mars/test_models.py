import pytest
from app import app, db, User


# Фикстура для настройки тестового клиента
@pytest.fixture
def client():
    app.config["TESTING"] = True  # Включение режима тестирования
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///:memory:"  # Использование временной базы данных в памяти
    )

    with app.app_context():
        db.create_all()  # Создание всех таблиц в памяти
        yield app.test_client()  # Возврат клиента для тестирования


# Тест для проверки создания пользователя
def test_user_creation(client):
    with app.app_context():  # Установка контекста приложения
        # Проверка, существует ли уже пользователь с заданным email
        existing_user = User.query.filter_by(email="test@example.com").first()
        if existing_user:
            db.session.delete(existing_user)  # Удаление существующего пользователя
            db.session.commit()  # Подтверждение изменений в базе данных

        # Создание нового пользователя
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")  # Установка пароля для пользователя
        db.session.add(user)  # Добавление пользователя в сессию базы данных
        db.session.commit()  # Подтверждение изменений в базе данных

        # Проверка, что пользователь был создан правильно
        assert user.username == "testuser"  # Проверка имени пользователя
        assert (
            user.check_password("password123") is True
        )  # Проверка, что пароль правильный
