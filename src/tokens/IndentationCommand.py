from .SimpleCommand import SimpleCommand

class IndentationCommand(SimpleCommand):
    def __init__(self, command, parent=None) -> None:
        super().__init__(command, parent)
        self.children = []
        self.redo = False
        self.redo_condition = ""
    
    def get_children(self):
        return self.children

    def get_redo_condition(self):
        return self.redo_condition
    
    def set_redo_condition(self, condition):
        self.redo_condition = condition

    def append(self, child):
        self.children.append(child)

    def get_type(self):
        return "intented"
    
    def should_redo(self):
        return self.redo

    def set_redo(self, value):
        self.redo = value
    
