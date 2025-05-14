import pytest
from app import app, db, User
from bs4 import BeautifulSoup


# Настройка тестового клиента Flask
@pytest.fixture
def client():
    app.config["TESTING"] = True  # Включаем режим тестирования
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///:memory:"  # Используем временную базу данных в памяти
    )

    with app.test_client() as client:
        with app.app_context():
            # Создаем все таблицы базы данных перед тестами
            db.create_all()

        # Передаем тестового клиента для выполнения тестов
        yield client

        with app.app_context():
            # После завершения тестов удаляем все таблицы
            db.drop_all()


# Извлечение CSRF-токена из HTML-ответа
def get_csrf_token(response):
    # Используем BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.data, "html.parser")
    # Находим скрытое поле с именем csrf_token и возвращаем его значение
    return soup.find("input", {"name": "csrf_token"})["value"]


# Тест процесса регистрации
def test_register(client):
    # Проверяем, что страница регистрации доступна
    response = client.get("/register")
    assert response.status_code == 200

    # Получаем CSRF-токен со страницы
    csrf_token = get_csrf_token(response)

    # Отправляем корректные данные для регистрации
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "csrf_token": csrf_token,
        },
    )

    # Проверяем редирект после успешной регистрации
    assert response.status_code == 302
    assert response.location == "/login"

    # Проверяем, что пользователь был создан в базе данных
    user = User.query.filter_by(username="newuser").first()
    assert user is not None


# Тест регистрации с некорректным email
def test_register_invalid_email(client):
    response = client.get("/register")
    csrf_token = get_csrf_token(response)

    # Отправляем форму с некорректным email
    response = client.post(
        "/register",
        data={
            "username": "anotheruser",
            "email": "invalid_email",  # Некорректный формат email
            "password": "password123",
            "confirm_password": "password123",
            "csrf_token": csrf_token,
        },
    )

    # Проверяем, что страница осталась той же (нет редиректа)
    assert response.status_code == 200
    # Проверяем наличие сообщения об ошибке валидации email
    assert b"Invalid email address." in response.data


# Тест регистрации с несовпадающими паролями
def test_register_password_mismatch(client):
    response = client.get("/register")
    csrf_token = get_csrf_token(response)

    # Отправляем форму с разными паролями
    response = client.post(
        "/register",
        data={
            "username": "mismatchuser",
            "email": "mismatch@example.com",
            "password": "password123",
            "confirm_password": "different_password",  # Пароли не совпадают
            "csrf_token": csrf_token,
        },
    )

    # Проверяем, что страница осталась той же (нет редиректа)
    assert response.status_code == 200
    # Проверяем наличие сообщения об ошибке несоответствия паролей
    assert b"Field must be equal to password." in response.data


# Тест успешного входа в систему
def test_login_success(client):
    # Сначала регистрируем пользователя
    response = client.get("/register")
    csrf_token = get_csrf_token(response)

    client.post(
        "/register",
        data={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "csrf_token": csrf_token,
        },
    )

    # Получаем страницу входа и CSRF-токен
    response = client.get("/login")
    csrf_token = get_csrf_token(response)

    # Пытаемся войти с корректными данными
    response = client.post(
        "/login",
        data={
            "email": "login@example.com",
            "password": "password123",
            "csrf_token": csrf_token,
        },
    )

    # Проверяем редирект после успешного входа
    assert response.status_code == 302
    assert response.location == "/application"


# Тест неудачного входа в систему
def test_login_failure(client):
    # Получаем страницу входа
    response = client.get("/login")
    csrf_token = get_csrf_token(response)

    # Пытаемся войти с неверными данными
    response = client.post(
        "/login",
        data={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
            "csrf_token": csrf_token,
        },
    )

    # Проверяем, что страница осталась той же (нет редиректа)
    assert response.status_code == 200

    # Декодируем байты в строку и проверяем наличие сообщения об ошибке
    response_text = response.data.decode("utf-8")
    assert "Неверный email или пароль" in response_text
