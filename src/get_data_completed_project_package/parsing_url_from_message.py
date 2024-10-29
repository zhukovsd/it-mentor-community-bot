def parsing_url_from_message(message: str):
    """
    Извлекает url из сообщения пользователя.
    Может удалять query параметры ссылки, так как для очистки
    c помощью clear_url_of_char "?" используется - replace
    :param message: Передаем reply сообщение пользователя,
        чей проект добавляем в итоги месяца.
    :return:
    """
    # Шаблон извлекаемой ссылки
    sample_url = 'https://github.com'
    list_message_words = message.split()

    for word in list_message_words:
        if len(word) >= len(sample_url):
            slice_word = word[:len(sample_url)]
            if slice_word == sample_url:
                # result_url = word.replace(',', '')
                result_url = __clear_url_of_char(word)
                return result_url
        else:
            continue


def __clear_url_of_char(word: str):
    """
    Очищаем url от лишних символов в начале и конце строки
    :param word:
    :return:
    """
    chars_for_cleaning = ['!', ',', '(', ')', '?']
    new_word = word

    for cfc in chars_for_cleaning:
        new_word = new_word.replace(cfc, '')

    new_word = new_word.strip('.')
    return new_word


if __name__ == '__main__':
    message_text = """
    Привет! Закончил работу над легендарной Симуляцией на Java.
Буду рад обоснованной, sdfsdfdsafdfsfasfasfasdfas критике и предложениям по улучшению. В некоторых местах есть спорные моменты. Я умышленно их оставил на суд ревьювера. Также хотелось бы услышать общее впечатление по реализации и по стилю написания кода.
https://github.com/violaceusflame/simulation!?,!.?,!?!,,.?.
    """
    print(parsing_url_from_message(message_text))
