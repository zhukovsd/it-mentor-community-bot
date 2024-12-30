"""
Тест кейсы для тестов модуля parse_url_from_message.py из пакета src/google_sheet

Сами тесты находятся tests/google_sheet_tests/test_parse_url.py
"""
import pytest


@pytest.fixture
def approved_parse_url():
    url_samples = [
        "https://github.com/Asenim/Simulation_Console_App",
        "github.com/Asenim/Simulation_Console_App",
        "https://github.com/Asenim/Simulation_Console_App.!?",
        "github.com/Asenim/Simulation_Console_App()!.,",
    ]

    test_cases = []

    for url in url_samples:
        text_samples = [
            f"Сделал проект Simulation, ссылка на проект - {url}, Кому не сложно будет - посмотрите реализацию",
            f"Строка с двумя url, первая - https://random_url.com, вторая - {url}? и еще немного текста",
            ]
        for text_sample in text_samples:
            test_cases.append(text_sample)
            test_cases.append(url)

    return test_cases


@pytest.fixture
def skip_parse_url():
    test_cases = [
        '',
        'a',
        'Просто сообщение',
        'Клара у Карла съела кораллы',
        'Липовый url обманка - "https://github.',
        '- https://github.com - Еще один',
        'Без протокола - github.com',
        'github. - Второй без протокола '
    ]

    return test_cases
