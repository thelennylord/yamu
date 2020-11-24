from brigadier import LiteralMessage
from brigadier.exceptions import DynamicCommandExceptionType
from brigadier.suggestion import empty_suggestion


class Time:
    def parse(self, reader):
        units = ("d", "s", "t")
        self.value = reader.read_int()
        if not reader.can_read():
            self.unit = "t"

        char = reader.peek()
        if char in units:
            self.unit = char
        else:
            raise DynamicCommandExceptionType(
                lambda u: LiteralMessage(f"Invalid unit '{u}'")
            ).create_with_context(self, char)

    def list_suggestions(self, builder):
        return empty_suggestion()

    def get_examples(self):
        return ["23d", "43s", "60t"]
