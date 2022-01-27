from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from main import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                  HTTP_422_UNPROCESSABLE_ENTITY, STATUS_OK, app, db_proxy)

client = TestClient(app, raise_server_exceptions=False)
db_proxy.enable_test_mode()
db_proxy.flush_db()   

def test_add_visited_links_view():
    """
        Проверяет правильность работы /visited_links
    """
    response = client.post(
        "/visited_links", 
        json={
            "links": [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
            ]
        }
    )

    assert response.json() == STATUS_OK

def test_add_visited_links_view_bad_link():
    """
        Проверяет правильность валидации /visited_links
    """
    response = client.post(
        "/visited_links",
        json = {
            "links": [
                "https://ya.ru",
                "привет, я ссылка!",
                "htt:/ссылка.рф"
            ]
        }
    )
    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {"status": "ValueError: 'привет, я ссылка!' must me a 'url' or 'domain'"}


def test_visited_domains_view():
    """
        Проверяет правильность работы /visited_domains
    """
    db_proxy.flush_db()
    test_add_visited_links_view()
    a = (datetime.utcnow() - timedelta(hours=5)).strftime("%s")
    b = (datetime.utcnow() + timedelta(hours=5)).strftime("%s")
    response = client.get(
        f'/visited_domains?from={a}&to={b}',
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()
    domains = data.get('domains')

    assert sorted(domains) == sorted(['ya.ru', 'funbox.ru', 'stackoverflow.com'])

def test_clear_visited_domains_view():
    """
        Проверяет правильность работы /visited_domains при чистой БД
    """
    a = (datetime.utcnow() - timedelta(hours=5)).strftime("%s")
    b = (datetime.utcnow() + timedelta(hours=5)).strftime("%s")
    db_proxy.flush_db()
    response = client.get(
        f'/visited_domains?from={a}&to={b}',
    )
    data = response.json()
    domains = data.get('domains')
    assert [] == domains


def test_visited_domains_view_bad_timerange():
    """
        Проверяет валидацию временных рамок
    """
    a = (datetime.utcnow() - timedelta(hours=5)).strftime("%s")
    b = (datetime.utcnow() + timedelta(hours=5)).strftime("%s")
    response = client.get(
        f'/visited_domains?from={b}&to={a}',
    )

    assert response.status_code == HTTP_400_BAD_REQUEST





