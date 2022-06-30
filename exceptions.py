class EndpointError(Exception):
    """Ошибка при доступе к ендпойнту."""

    pass


class HomeworksKeyError(Exception):
    """Отсутствие ключа homeworks."""

    pass


class HomeworksListError(Exception):
    """По ключу homeworks возвращается не список."""

    pass
