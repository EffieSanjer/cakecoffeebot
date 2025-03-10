class PlaceException(Exception):
    """ Базовая ошибка для заведения """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PlaceNotFoundException(PlaceException):
    """ Ошибка, если заведение не найдено """

    def __init__(self):
        super().__init__(f"Заведение не найдено.")


class PlaceAlreadyExistsException(PlaceException):
    """ Ошибка, если такое заведение уже существует """

    def __init__(self):
        super().__init__(f"Заведение уже существует.")
