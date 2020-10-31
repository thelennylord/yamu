class BaseToken:
    def __init__(self, command, parent=None) -> None:
        self.command = command
        self.parent = parent

    def get_command(self) -> str:
        return self.command

    def get_parent(self):
        return self.parent

    def get_type(self) -> str:
        raise NotImplementedError