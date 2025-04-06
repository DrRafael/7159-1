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


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

def test_add_new_user_with_login(setup_database, connection):
    """Тест добавления нового пользователя с существующим логином."""
    add_user('testuser', 'testuser1@example.com', 'password1234')
    
    response = add_user('testuser', 'testuser2@example.com', 'password12345')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert not response, "Пользователь должен быть добавлен в базу данных."

def test_auth_user(setup_database, connection):
    """Тест auth нового пользователя."""
    add_user('testuser2', 'testuser2@example.com', 'password123456789')
    authenticate_user("testuser2","password123456789")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser2';")
    user = cursor.fetchone()
    assert user, "Пользователь не должен быть авторизован."

def test_auth_null_user(setup_database, connection):
    """Тест auth null пользователя."""
    add_user('testuser2', 'testuser2@example.com', 'password123456789')
    resp=authenticate_user("testuser1","password123456789")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser2';")
    user = cursor.fetchone()
    assert not resp, "Пользователь не должен быть авторизован."

def test_auth_user_wrong_pass(setup_database, connection):
    """Тест auth пользователя with wrong pass."""
    add_user('testuser2', 'testuser2@example.com', 'password123456789')
    resp=authenticate_user("testuser2","idkpassword")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser2';")
    user = cursor.fetchone()
    assert not resp, "Пользователь не должен быть авторизован."

def test_user_list(setup_database, connection):
    """Тест auth пользователя with wrong pass."""
    add_user('testuser1', 'testuser1@example.com', 'password1')
    add_user('testuser2', 'testuser2@example.com', 'password2')
    add_user('testuser3', 'testuser3@example.com', 'password3')

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser1';")
    user = cursor.fetchone()
    assert user, "Пользователь не должен быть авторизован."


# Возможные варианты тестов:
"""
Тест добавления пользователя с существующим логином. <
Тест успешной аутентификации пользователя. <
Тест аутентификации несуществующего пользователя.<
Тест аутентификации пользователя с неправильным паролем.<
Тест отображения списка пользователей.
"""