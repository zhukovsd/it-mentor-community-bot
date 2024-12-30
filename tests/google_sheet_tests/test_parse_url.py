"""
Тестируем модуль parse_url_from_message.py из пакета src/google_sheet

Тест кейсы для текущего модуля расположены в фикстурах по пути:
    tests/fixtures/google_sheet_fixtures в модуле parse_url_fixtures.py
"""
from src.google_sheet.parse_url_from_message import parse_url_from_message
from tests.fixtures.google_sheet_fixtures.parse_url_fixtures import (
    approved_parse_url, skip_parse_url
)


def test_approved_parse_url(approved_parse_url):
    for test_case in approved_parse_url:
        result_parse = parse_url_from_message(test_case)
        assert result_parse == 'https://github.com/Asenim/Simulation_Console_App'


def test_skip_parse_url(skip_parse_url):
    for test_case in skip_parse_url:
        result_parse = parse_url_from_message(test_case)
        assert result_parse is None
