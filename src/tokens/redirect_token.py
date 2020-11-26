from .base_token import BaseToken


class RedirectToken(BaseToken):
    def __init__(self, command, ln, parent) -> None:
        super().__init__(command, parent)
        self.ln = ln
    
    def get_ln(self):
        return self.ln

    def get_type(self) -> str:
        return "redirect"