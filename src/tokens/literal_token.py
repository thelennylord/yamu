from .base_token import BaseToken

class LiteralToken(BaseToken):
    def __init__(self, command, parent=None) -> None:
        super().__init__(command, parent)

    def get_type(self) -> str:
        return "literal"