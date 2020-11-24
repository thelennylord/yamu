from brigadier.LiteralMessage import LiteralMessage
from brigadier.exceptions.SimpleCommandExceptionType import SimpleCommandExceptionType
from brigadier.suggestion import empty_suggestion
from brigadier.exceptions import BuiltInExceptions
from brigadier import StringReader
import math


class Range:
    def parse(self, reader: StringReader):
        remaining = reader.get_remaining()
        if remaining[:2] == "..":
            # Skip two times
            reader.set_cursor(reader.get_cursor() + 2)
            self.minimum = -math.inf
            self.maximum = reader.read_float()
        else:
            self.minimum = self._read_float(reader)
            if reader.can_read() and reader.peek() == ".":
                reader.skip()
                if reader.can_read() and reader.is_allowed_number(reader.peek()):
                    self.maximum = reader.read_float()
                else:
                    self.maximum = math.inf
            else:
                self.maximum = self.minimum

        if self.minimum > self.maximum:
            raise SimpleCommandExceptionType(
                LiteralMessage("Minimum cannot be greater than maximum")
            ).create_with_context(reader)

        return self

    def _read_float(self, reader):
        start = reader.get_cursor()
        result = ""
        while reader.can_read():
            char = reader.peek()
            if char == ".":
                reader.skip()
                if reader.can_read() and reader.peek() == ".":
                    break
                result += char
            elif char.isdigit() or char == "+" or char == "-":
                reader.skip()
                result += char
            else:
                break
        if not result:
            raise BuiltInExceptions.reader_expected_float().create_with_context(reader)

        # Verify result is a valid float
        try:
            return float(result)
        except ValueError:
            reader.set_cursor(start)
            raise BuiltInExceptions.reader_invalid_float().create_with_context(
                reader, result
            )

    def list_suggestions(self, builder):
        return empty_suggestion()

    def get_examples(self):
        return ["1..", "-41.51..37", "..4.5"]
