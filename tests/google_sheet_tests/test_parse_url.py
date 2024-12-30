from src.google_sheet.parse_url_from_message import parse_url_from_message
from tests.fixtures.parse_url_fixtures import (
    approved_parse_url,
    skip_parse_url
)


def test_approved_parse_url(approved_parse_url):
    for test_case in approved_parse_url:
        result_parse = parse_url_from_message(test_case)
        assert result_parse == 'https://github.com/Asenim/Simulation_Console_App'


def test_skip_parse_url(skip_parse_url):
    for test_case in skip_parse_url:
        result_parse = parse_url_from_message(test_case)
        assert result_parse is None
