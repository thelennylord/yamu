import json
import re
from json.decoder import (
    BACKSLASH,
    FLAGS,
    WHITESPACE,
    WHITESPACE_STR,
    JSONDecodeError,
    JSONDecoder,
    _decode_uXXXX,
)

from brigadier import LiteralMessage
from brigadier.exceptions import SimpleCommandExceptionType

WORD = re.compile(r"((?:[0-9a-zA-Z_+\-]*))", FLAGS)

# Modification of:
# https://github.com/python/cpython/blob/master/Lib/json/scanner.py#L15


def _modified_py_make_scanner(context):
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = re.compile(
        r"([+-]?(?:0|[1-9]\d*))([bls])?(\.\d+)?([df])?", FLAGS
    ).match
    match_word = WORD.match
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    def _scan_once(string, idx):
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration(idx) from None

        if nextchar == '"':
            return parse_string(string, idx + 1, strict)
        elif nextchar == "'":
            return parse_string(string, idx + 1, strict, termin="'")
        elif nextchar == "{":
            return parse_object(
                (string, idx + 1),
                strict,
                _scan_once,
                object_hook,
                object_pairs_hook,
                memo,
            )
        elif nextchar == "[":
            return parse_array((string, idx + 1), _scan_once)
        elif nextchar == "t" and string[idx : idx + 4] == "true":
            return True, idx + 4
        elif nextchar == "f" and string[idx : idx + 5] == "false":
            return False, idx + 5

        m = match_number(string, idx)
        if m is not None:
            integer, int_type, frac, frac_type = m.groups()
            if (int_type and frac_type) or (int_type and frac):
                raise StopIteration(idx)

            if frac:
                if frac_type is not None and (not frac_type in ("f", "d")):
                    raise StopIteration(idx)

                res = parse_float(integer + (frac or ""))
            else:
                if int_type is not None:
                    # Should 0b and 1b be converted to True and False?
                    if int_type == "b":
                        if integer == "0":
                            return False, idx + 2
                        if integer == "1":
                            return True, idx + 2
                    elif not int_type in ("l", "s"):
                        raise StopIteration(idx)

                res = parse_int(integer)
            return res, m.end()

        m = match_word(string, idx)
        if m is not None:
            value = m.groups()[0]
            return value, idx + len(value)
        else:
            raise StopIteration(idx)

    def scan_once(string, idx):
        try:
            return _scan_once(string, idx)
        finally:
            memo.clear()

    return scan_once


# Modification of:
# https://github.com/python/cpython/blob/master/Lib/json/decoder.py#L69


def _modified_py_scanstring(s, end, strict=True, _b=BACKSLASH, _m=None, *, termin='"'):
    """Scan the string s for a JSON string. End is the index of the
    character in s after the quote that started the JSON string.
    Unescapes all valid JSON string escape sequences and raises ValueError
    on attempt to decode an invalid string. If strict is False then literal
    control characters are allowed in the string.
    Returns a tuple of the decoded string and the index of the character in s
    after the end quote."""
    if _m is None:
        _m = re.compile(r"(.*?)([" + termin + r"\\\x00-\x1f])", FLAGS).match

    chunks = []
    _append = chunks.append
    begin = end - 1
    while 1:
        chunk = _m(s, end)
        if chunk is None:
            raise JSONDecodeError("Unterminated string starting at", s, begin)
        end = chunk.end()
        content, terminator = chunk.groups()
        # Content is contains zero or more unescaped string characters
        if content:
            _append(content)
        # Terminator is the end of string, a literal control character,
        # or a backslash denoting that an escape sequence follows
        if terminator == termin:
            break
        elif terminator != "\\":
            if strict:
                # msg = "Invalid control character %r at" % (terminator,)
                msg = "Invalid control character {0!r} at".format(terminator)
                raise JSONDecodeError(msg, s, end)
            else:
                _append(terminator)
                continue
        try:
            esc = s[end]
        except IndexError:
            raise JSONDecodeError("Unterminated string starting at", s, begin) from None
        # If not a unicode escape sequence, must be in the lookup table
        if esc != "u":
            try:
                char = _b[esc]
            except KeyError:
                msg = "Invalid \\escape: {0!r}".format(esc)
                raise JSONDecodeError(msg, s, end)
            end += 1
        else:
            uni = _decode_uXXXX(s, end)
            end += 5
            if 0xD800 <= uni <= 0xDBFF and s[end : end + 2] == "\\u":
                uni2 = _decode_uXXXX(s, end + 1)
                if 0xDC00 <= uni2 <= 0xDFFF:
                    uni = 0x10000 + (((uni - 0xD800) << 10) | (uni2 - 0xDC00))
                    end += 6
            char = chr(uni)
        _append(char)
    return "".join(chunks), end


def _NBTObject(
    s_and_end,
    strict,
    scan_once,
    object_hook,
    object_pairs_hook,
    memo=None,
    _w=WHITESPACE.match,
    _ws=WHITESPACE_STR,
):
    s, end = s_and_end
    pairs = []
    pairs_append = pairs.append
    # Backwards compatibility
    if memo is None:
        memo = {}
    memo_get = memo.setdefault
    # Use a slice to prevent IndexError from being raised, the following
    # check will raise a more specific ValueError if the string is empty
    nextchar = s[end : end + 1]
    # Normally we expect nextchar == '"'
    in_quotes = True
    if nextchar != '"':
        if nextchar in _ws:
            end = _w(s, end).end()
            nextchar = s[end : end + 1]
        # Trivial empty object
        if nextchar == "}":
            if object_pairs_hook is not None:
                result = object_pairs_hook(pairs)
                return result, end + 1
            pairs = {}
            if object_hook is not None:
                pairs = object_hook(pairs)
            return pairs, end + 1
        elif nextchar != '"':
            in_quotes = False
    end += 1
    while True:
        currentchar = s[end - 1]
        if currentchar == '"':
            in_quotes = True
            quote_type = '"'
        elif currentchar == "'":
            in_quotes = True
            quote_type = "'"
        else:
            in_quotes = False
            quote_type = None

        if in_quotes is True:
            key, end = _modified_py_scanstring(s, end, strict, termin=quote_type)
        else:
            m = WORD.match(s, end - 1)
            if m is not None:
                key = m.groups()[0]
                end = end + len(key) - 1
            else:
                raise JSONDecodeError("Illegal property name", s, end)
        key = memo_get(key, key)
        # To skip some function call overhead we optimize the fast paths where
        # the JSON key separator is ": " or just ":".
        if s[end : end + 1] != ":":
            end = _w(s, end).end()
            if s[end : end + 1] != ":":
                if s[end] != '"':
                    raise JSONDecodeError("Expecting ':' delimiter", s, end)
                else:
                    raise JSONDecodeError(
                        "Expecting property name enclosed in double quotes", s, end - 1
                    )
        end += 1

        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

        try:
            value, end = scan_once(s, end)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        pairs_append((key, value))
        try:
            nextchar = s[end]
            if nextchar in _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        except IndexError:
            nextchar = ""
        end += 1

        if nextchar == "}":
            break
        elif nextchar != ",":
            raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        end = _w(s, end).end()
        nextchar = s[end : end + 1]
        end += 1

    if object_pairs_hook is not None:
        result = object_pairs_hook(pairs)
        return result, end
    pairs = dict(pairs)
    if object_hook is not None:
        pairs = object_hook(pairs)
    return pairs, end


def NBTArray(s_and_end, scan_once, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = s_and_end
    values = []
    nextchar = s[end : end + 1]
    if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end : end + 1]
    # Look-ahead for trivial empty array
    if nextchar == "]":
        return values, end + 1
    _append = values.append
    _type = None
    while True:
        try:
            value, end = scan_once(s, end)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        if _type is None:
            _type = type(value)

        if type(value) == _type:
            _append(value)
        else:
            raise JSONDecodeError(
                "Expecting value to be "
                + _type.__name__
                + ", got "
                + type(value).__name__,
                s,
                end - 1,
            )
        nextchar = s[end : end + 1]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end : end + 1]
        end += 1
        if nextchar == "]":
            break
        if nextchar == ";":
            if len(values) == 1:
                if value in ("I", "B", "L"):
                    # TODO: Implement checks for types via their suffix
                    _type = int
                    values.clear()
                else:
                    raise JSONDecodeError("Invalid NBT TAG type", s, end - 1)
            else:
                raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        elif nextchar != ",":
            raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

    return values, end


class JSONDecodeError(JSONDecodeError):
    pass


class NBTObjectDecoder(JSONDecoder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parse_string = _modified_py_scanstring
        self.parse_object = _NBTObject
        self.parse_array = NBTArray
        self.scan_once = _modified_py_make_scanner(self)


class NBTObject:
    def parse(self, reader):
        first_char = reader.read()
        initial_pos = reader.get_cursor()
        data = first_char
        if first_char in ("{", "["):

            count = 1
            while reader.can_read() and count > 0:
                if count < 0:
                    raise SimpleCommandExceptionType(
                        LiteralMessage("Expected opening bracket")
                    ).create_with_context(reader)

                char = reader.read()
                if char in ("{", "["):
                    count += 1
                elif char in ("}", "]"):
                    count -= 1

                data += char
        else:
            while reader.can_read() and reader.peek() != " ":
                data += reader.read()

        print(data)

        try:
            self.obj = json.loads(data, cls=NBTObjectDecoder)
        except JSONDecodeError as error:
            reader.cursor = initial_pos + error.pos
            raise SimpleCommandExceptionType(
                LiteralMessage(error.msg)
            ).create_with_context(reader)
        return self
