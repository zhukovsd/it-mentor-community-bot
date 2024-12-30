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
        text_sample = f"Сделал проект Simulation, ссылка на проект - {url}, Кому не сложно будет - посмотрите реализацию"
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
