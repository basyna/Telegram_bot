class ExceptionWithSendingError(Exception):
    """Ошибка с пересылкой сообщения боту."""

    pass


class SendingError(Exception):
    """Ошибка передачи сообщения боту."""

    pass


class EndpointError(Exception):
    """Ошибка при доступе к ендпойнту."""

    pass


class HomeworksKeyError(ExceptionWithSendingError):
    """Отсутствие необходимых ключей."""

    pass


class HomeworksTypeError(ExceptionWithSendingError):
    """По ключу homeworks возвращается не список."""

    pass
