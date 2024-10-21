class UrlSerialize:
    def __init__(self, list_all_data_from_link):
        """
        Сериализатор работающий непосредственно с url
        позволяющий получить нам владельца репозитория
        и имя репозитория, что бы в дальнейшем работать с этим object
        :param list_all_data_from_link: Список содержащий информацию извлеченную из url
        """
        self.__list_all_data_from_link = list_all_data_from_link
        self.owner_repo = list_all_data_from_link[0]
        self.repository_name = list_all_data_from_link[1]

