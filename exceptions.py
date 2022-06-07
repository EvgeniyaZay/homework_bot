class IncorrectAPIResponse(Exception):
    """Исключение для некорректного ответа API"""
    pass


class ExceptionApiStausCode(Exception):
    """Исключение сбоя запроса к API"""
    pass


class UnknownStatusHomeWork(Exception):
    """Исключение для неизвестного статуса домашки"""
    pass
