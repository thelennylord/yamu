from brigadier.suggestion import empty_suggestion


class Vector2:
    def __init__(self, *, fractions=True):
        self.fractions = fractions

    def parse(self, reader):
        values = [None, None]
        for i in range(2):
            if not reader.can_read():
                break
            if reader.peek() == "~":
                _type = "relative"
                reader.skip()
            elif reader.peek() == "^":
                _type = "local"
                reader.skip()
            else:
                _type = "absolute"

            values[i] = (
                reader.read_float() if self.fractions else reader.read_int(),
                _type,
            )
            reader.skip()

        self.x = {"value": values[0][0], "type": values[0][1]}
        self.y = {"value": values[1][0], "type": values[2][1]}

        return self

    def list_suggestions(self, builder):
        return empty_suggestion()

    def get_examples(self):
        return ["42.3 5 -53", "-23 ~51 -782", "^ ^2 ^"]
