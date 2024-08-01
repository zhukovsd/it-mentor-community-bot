from github import Github
from github import Auth
from env import API_FGP_GITHUB, USER_NAME_PARSING_REPO, FILE_PATH, REPO_NAME


class InfoTargetDataFromGitHub:
    def __init__(self, api_fgp_github: str):
        """
        Класс позволяет доставать информацию c помощью GitHubREST API
         по запросу из github
        :param api_fgp_github: Принимает API ключ сгенерированный в
            github -> setting -> developer setting.
            Следует передавать через .env
        """
        self.__auth_object = Auth.Token(api_fgp_github)

    def info_target_file_info(self, user_name: str, repository_name: str, file_path: str):
        """
        Получаем информацию о конкретном файле.
        :param user_name: Имя пользователя человека в репозиторий которого
            мы лезем за получением информации.
        :param repository_name: Имя репозитория по которому получаем информацию.
        :param file_path: Путь к файлу в репозитории к которому
            мы получаем доступ и из которого извлекаем информацию.
        :return:
        """
        with Github(auth=self.__auth_object) as __connect_github:
            __received_repo = __connect_github.get_user(user_name).get_repo(repository_name).get_contents(file_path)
            print(__received_repo.__dict__)
            print(__received_repo.html_url, 'для получения ссылки на файл')
            # Получение всего контента из файла
            print(__received_repo.decoded_content.decode('utf-8').split('\n'))
            for i in __received_repo.decoded_content.decode('utf-8').split('\n'):
                print(i)
            __connect_github.close()

    def info_target_repo_info(self, user_name: str, repository_name: str):
        """
        Получаем информацию по конкретному репозиторию
        :param user_name: Имя пользователя человека в репозиторий которого
            мы лезем за получением информации.
        :param repository_name: Имя репозитория по которому получаем информацию
        :return:
        """
        with Github(auth=self.__auth_object) as __connect_github:
            __received_repo = __connect_github.get_user(user_name).get_repo(repository_name)  # .get_repos(repository_name)
            print(__received_repo.__dict__)
            print(__received_repo)
            print(__received_repo.name)
            print(__received_repo.html_url)
            __connect_github.close()

    def info_repo_name(self, user_name: str):
        """
        Получаем информацию об имени репозиториев у конкретного пользователя.
        :param user_name: Имя пользователя человека в репозиторий которого
            мы лезем за получением информации.
        :return:
        """
        with Github(auth=self.__auth_object) as __connect_github:
            for repo in __connect_github.get_user(user_name).get_repos():
                print(repo.name)

            __connect_github.close()


if __name__ == '__main__':
    info_targ_data_from_github = InfoTargetDataFromGitHub(api_fgp_github=API_FGP_GITHUB)
