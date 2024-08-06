class ItemNotFoundException(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"Error: {self.message} | Code: {self.error_code}"
