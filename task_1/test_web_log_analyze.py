# test_web_log_analyze.py

from datetime import datetime
from pathlib import Path
import pytest

import web_log_analyze


VALID_LOGS = """127.0.0.1 - - [16/Feb/2026:10:00:00 +0000] "GET /index HTTP/1.1" 200 123
192.168.1.1 - - [16/Feb/2026:10:05:00 +0000] "POST /login HTTP/1.1" 404 321
127.0.0.1 - - [17/Feb/2026:11:00:00 +0000] "PUT /api HTTP/1.1" 500 111
10.0.0.1 - - [17/Feb/2026:12:00:00 +0000] "DELETE /user HTTP/1.1" 204 0
127.0.0.1 - - [17/Feb/2026:13:00:00 +0000] "HEAD /health HTTP/1.1" 200 10
"""

INVALID_LOG = 'INVALID LINE\n'


@pytest.fixture
def change_test_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def create_access_log(content: str):
    Path("access.log").write_text(content, encoding="utf-8")


def test_file_not_found(change_test_dir, capsys):
    with pytest.raises(SystemExit) as exc:
        web_log_analyze.file_analyze()

    captured = capsys.readouterr()

    assert exc.value.code == 1
    assert "Файл access.log не найден" in captured.out


def test_successful_analysis(change_test_dir, capsys):
    create_access_log(VALID_LOGS)

    web_log_analyze.file_analyze()

    captured = capsys.readouterr()

    output = captured.out

    assert "=== Топ-3 активных IP ===" in output
    assert "127.0.0.1: 3 запрос(ов/a)" in output
    assert "192.168.1.1: 1 запрос(ов/a)" in output

    assert "GET: 1" in output
    assert "POST: 1" in output
    assert "PUT: 1" in output
    assert "DELETE: 1" in output

    assert "errors.log (2 записей)" in output

    errors_content = Path("errors.log").read_text(encoding="utf-8")

    assert '404' in errors_content
    assert '500' in errors_content


def test_invalid_log_line(change_test_dir, capsys):
    create_access_log(INVALID_LOG)

    web_log_analyze.file_analyze()

    captured = capsys.readouterr()

    assert "Неизвестный формат логов" in captured.out
    assert "Не удалось распарсить строку" in captured.out


def test_filter_by_date(change_test_dir, capsys):
    create_access_log(VALID_LOGS)

    date = datetime.strptime("2026-02-16", "%Y-%m-%d")

    web_log_analyze.file_analyze(date)

    captured = capsys.readouterr()

    output = captured.out

    assert "=== Фильтрация по дате 2026-02-16 ===" in output
    assert "Найдено записей за указанную дату: 2" in output


def test_main_with_invalid_argument(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["web_log_analyze.py", "--wrong"]
    )

    with pytest.raises(SystemExit) as exc:
        web_log_analyze.main()

    captured = capsys.readouterr()

    assert exc.value.code == 1
    assert "Неизвестный аргумент" in captured.out


def test_main_with_invalid_date(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["web_log_analyze.py", "--date=invalid-date"]
    )

    with pytest.raises(SystemExit) as exc:
        web_log_analyze.main()

    captured = capsys.readouterr()

    assert exc.value.code == 1
    assert "Неверный формат даты" in captured.out


def test_main_with_too_many_arguments(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["web_log_analyze.py", "arg1", "arg2"]
    )

    with pytest.raises(SystemExit) as exc:
        web_log_analyze.main()

    captured = capsys.readouterr()

    assert exc.value.code == 1
    assert "Невозможное количество аргументов" in captured.out