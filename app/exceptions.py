class NotFoundError(Exception):
    """El recurso pedido no existe."""

    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message)
        self.message = message


class ConflictError(Exception):
    """La operación choca con datos existentes (por ejemplo, un slug repetido)."""

    def __init__(self, message: str = "Conflicto con datos existentes"):
        super().__init__(message)
        self.message = message


class ExternalServiceError(Exception):
    """Falló el Builder o la API de métricas."""

    def __init__(self, message: str = "Falló un servicio externo"):
        super().__init__(message)
        self.message = message
