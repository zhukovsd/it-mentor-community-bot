from github import Github
import requests

# Authentication is defined via github.Auth
from github import Auth
from env import API_FGP_GITHUB, USER_NAME_PARSING_REPO

# Используемый токен авторизации
auth = Auth.Token(API_FGP_GITHUB)
# user_name для получения данных конкретного пользователя
username = USER_NAME_PARSING_REPO  # 'Asenim'


def info_target_line_in_file_info(auth_obj, user_name: str, repository_name: str, file_path: str, line_str_in: str):
    """
    Ищем конкретную строчку в конкретном файле
    :param auth_obj: auth_obj: Объект класса Token из пакета github.Auth
        наш токен авторизации.
    :param user_name: Имя пользователя человека в репозиторий которого
        мы лезем за получением информации.
    :param repository_name: Имя репозитория по которому получаем информацию.
    :param file_path: Путь к файлу в репозитории к которому
        мы получаем доступ и из которого извлекаем информацию.
    :param line_str_in: Строка которую ищем (Её Вхождение)
    :return:
    """
    pass


def info_target_file_info(auth_obj, user_name: str, repository_name: str, file_path: str):
    """
    Получаем информацию о конкретном файле.
    :param auth_obj: auth_obj: Объект класса Token из пакета github.Auth
        наш токен авторизации.
    :param user_name: Имя пользователя человека в репозиторий которого
        мы лезем за получением информации.
    :param repository_name: Имя репозитория по которому получаем информацию.
    :param file_path: Путь к файлу в репозитории к которому
        мы получаем доступ и из которого извлекаем информацию.
    :return:
    """
    with Github(auth=auth_obj) as connect_github:
        received_repo = connect_github.get_user(user_name).get_repo(repository_name).get_contents(file_path)
        print(received_repo.__dict__)
        print(received_repo.decoded_content.decode('utf-8').split('\n'))
        connect_github.close()


def info_target_repo_info(auth_obj, user_name: str, repository_name: str):
    """
    Получаем информацию по конкретному репозиторию
    :param auth_obj: объект класса Token из пакета github.Auth
        Наш токен авторизации.
    :param user_name: Имя пользователя человека в репозиторий которого
        мы лезем за получением информации.
    :param repository_name: Имя репозитория по которому получаем информацию
    :return:
    """
    with Github(auth=auth_obj) as connect_github:
        received_repo = connect_github.get_user(user_name).get_repo(repository_name)  #.get_repos(repository_name)
        print(received_repo)
        print(received_repo)
        connect_github.close()


def info_repo_name(auth_obj, user_name: str):
    """
    Получаем информацию о имени репозиториев у конкретного пользователя
    :param auth_obj: объект класса Token из пакета github.Auth
        Наш токен авторизации.
    :param user_name: Имя пользователя человека в репозиторий которого
        мы лезем за получением информации.
    :return:
    """
    connect_github = Github(auth=auth_obj)
    for repo in connect_github.get_user(user_name).get_repos():
        print(repo.name)

    connect_github.close()


if __name__ == '__main__':
    # info_repo_name(auth_obj=auth, user_name=username)
    repo_name = 'currency-exchange-api'
    # info_target_repo_info(auth_obj=auth, user_name=username,
    #                       repository_name=repo_name)
    file = 'src/main/java/pet/project/servlet/exchange/ExchangeRateServlet.java'
    info_target_file_info(auth_obj=auth, user_name=username,
                          repository_name=repo_name, file_path=file)
