def parse_url_from_message(message: str):
    """
    Извлекает url из сообщения пользователя.
    Может удалять query параметры ссылки, так как для очистки
    c помощью clear_url_of_char "?" используется - replace
    :param message: Передаем reply сообщение пользователя,
        чей проект добавляем в итоги месяца.
    :return:
    """
    # Шаблон извлекаемой ссылки
    url_samples: list[str] = [
        "https://github.com/",
        "github.com/"
        ]
    list_message_words = message.split()

    for sample_url in url_samples:
        for word in list_message_words:
            if len(word) <= len(sample_url):
                continue
            slice_word = word[: len(sample_url)]
            if slice_word == sample_url:
                a_clean_url = __clear_url_of_char(word)
                result_url = __create_base_url_form(a_clean_url)
                return result_url


def __clear_url_of_char(word: str):
    """
    Очищаем url от лишних символов в начале и конце строки
    :param word:
    :return:
    """
    chars_for_cleaning = ["!", ",", "(", ")", "?"]
    new_word = word

    for cfc in chars_for_cleaning:
        new_word = new_word.replace(cfc, "")

    new_word = new_word.strip(".")
    return new_word


def __create_base_url_form(url: str):
    """
    Функция приводит url без протокола к стандартному виду.
    Пример:
        Из "github.com/violaceusflame/simulation"
        В "https://github.com/violaceusflame/simulation"
    :return:
    """
    protocol = "https://"

    if protocol != url[: len(protocol)]:
        new_url = f"{protocol}{url}"
        return new_url

    return url


if __name__ == "__main__":
    message_text = """
    Привет! Закончил работу над легендарной Симуляцией на Java.
Буду рад обоснованной, sdfsdfdsafdfsfasfasfasdfas критике и предложениям по улучшению. В некоторых местах есть спорные моменты. Я умышленно их оставил на суд ревьювера. Также хотелось бы услышать общее впечатление по реализации и по стилю написания кода.
https://github.com/violaceusflame/simulation!?,!.?,!?!,,.?.
    """
    message_text2 = """
        Привет! Закончил работу над легендарной Симуляцией на Java.
    Буду рад обоснованной, sdfsdfdsafdfsfasfasfasdfas критике и предложениям по улучшению. В некоторых местах есть спорные моменты. Я умышленно их оставил на суд ревьювера. Также хотелось бы услышать общее впечатление по реализации и по стилю написания кода.
    github.com/violaceusflame/simulation!?,!.?,!?!,,.?.
        """
    old_url = parse_url_from_message(message_text2)
    print(old_url)
    print(__create_base_url_form(old_url))
    old_url_2 = parse_url_from_message(message_text)
    print(old_url_2)
    print(__create_base_url_form(old_url_2))
