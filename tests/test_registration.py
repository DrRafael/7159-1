import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()

@pytest.fixture
def test_user():
    user = ("testuser", "testuser@example.com", "password")
    add_user(*user) 
    yield user
    
def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, test_user, connection):
    """Тест добавления нового пользователя."""
    username, _, _ = test_user
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."
    assert user == test_user, "Данные пользователя должны совпадать."    

def test_add_existing_user(setup_database, test_user):
    assert not add_user(*test_user), "Повторное добавление существующего пользователя должно провалиться."

def test_authenticate_user(setup_database, test_user):
    username, _, password = test_user
    assert authenticate_user(username, password), "Аутентификация должна была пройти успешно (правильный пароль)."
    assert not authenticate_user(username, password + "randomgibberish"), "Аутентификация должна была провалиться (неверный пароль)."
    assert not authenticate_user("nota" + username, password), "Аутентификация должна была провалиться (несуществующий пользователь)."    

def test_display_users(setup_database, test_user, capsys):
    display_users()
    captured = capsys.readouterr()
    assert captured.out == f"Логин: {test_user[0]}, Электронная почта: {test_user[1]}\n"
    
# Возможные варианты тестов:
"""
Тест добавления пользователя с существующим логином.
Тест успешной аутентификации пользователя.
Тест аутентификации несуществующего пользователя.
Тест аутентификации пользователя с неправильным паролем.
Тест отображения списка пользователей.
"""
