from src.tokenizer import tokenize
from src.tokens import LiteralToken, IndentationToken

def test_output_length():
    commands = ["say foo", "say bar", "say far", "say boo"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert len(tokens) == 4

def test_simple_command_token():
    commands = ["say abc"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert isinstance(tokens[0], LiteralToken)

def test_indentation_command_token():
    commands = ["execute as @a run", "    say abc"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert isinstance(tokens[0], IndentationToken)

def test_token_value():
    commands = ["say foo", "execute as @a run", "    say bar"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert tokens[0].get_command() == "say foo"
    assert tokens[1].get_command() == "execute as @a run"

def test_indentation():
    commands = ["execute as @a run", "    say abc"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert tokens[0].get_children()[0].get_command() == "say abc"

def test_invalid_indentation_space():
    commands = ["execute as @a run", " say abc"]
    try:
        tokenize([(i + 1, command) for i, command in enumerate(commands)])
    except IndentationError:
        assert True
    else:
        assert False

def test_should_redo():
    commands = ["execute as @a run", "    redo"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert tokens[0].should_redo() == True

def test_should_not_redo():
    commands = ["execute as @a run", "    say abc"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert tokens[0].should_redo() == False

def test_indentation_children_length():
    commands = ["execute as @a run", "    say foo", "    say bar"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert len(tokens[0].get_children()) == 2

# Should be modified once custom yamu classes are made
def test_non_indented_redo():
    commands = ["say abc", "redo"]
    try:
        tokenize([(i + 1, command) for i, command in enumerate(commands)])
    except ValueError as error:
        assert error.args[0].startswith("Command 'redo' must be indented in an execute command")
    else:
        assert False

def test_indentation_children():
    commands = ["execute as @a run", "    say foo", "    execute as @p run", "        say bar"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    children = tokens[0].get_children()
    assert isinstance(children[0], LiteralToken)
    assert isinstance(children[1], IndentationToken)

def test_indentation_exit():
    commands = ["execute as @a run", "    say foo", "say bar"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert isinstance(tokens[0], IndentationToken)
    assert isinstance(tokens[1], LiteralToken)

def test_inline_redo():
    commands = ["execute as @a run", "    execute as @e at @s run redo"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert tokens[0].get_redo_condition() == "execute as @e at @s run "

def test_non_inline_redo():
    commands = ["execute as @a run", "    say abc"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert tokens[0].get_redo_condition() == ""

def test_excess_indentation():
    commands = ["execute as @a run", "        say foo"]
    try:
        tokenize([(i + 1, command) for i, command in enumerate(commands)])
    except IndentationError:
        assert True
    else:
        assert False

def test_invalid_indentation():
    commands = ["say foo", "    say bar"]
    try:
        tokenize([(i + 1, command) for i, command in enumerate(commands)])
    except IndentationError:
        assert True
    else:
        assert False

# Should be removed once tokenizer uses brigadier
# Should be modified once yamu error classes are made
def test_invalid_command():
    commands = ["foo bar"]
    try:
        tokenize([(i + 1, command) for i, command in enumerate(commands)])
    except ValueError as error:
        assert error.args[0].startswith("Unknown or incomplete command")
    else:
        assert False

def test_ignore_comments():
    commands = ["say foo", "#far", "#boo", "say bar"]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert len(tokens) == 2
    assert tokens[0].get_command() == "say foo"
    assert tokens[1].get_command() == "say bar"

def test_ignore_empty_lines():
    commands = ["say foo", "", "say bar", ""]
    tokens = tokenize([(i + 1, command) for i, command in enumerate(commands)])
    assert len(tokens) == 2
    assert tokens[0].get_command() == "say foo"
    assert tokens[1].get_command() == "say bar"

def test_label_assignment():
    commands = ["foo:", "execute run", "    say bar"]
    tokenize([(i + 1, command) for i, command in enumerate(commands)])

def test_label_name_beginning_with_number():
    commands = ["1foo:", "execute run", "    say bar"]
    try:
        tokenize([(i + 1, command) for i, command in enumerate(commands)])
    except SyntaxError as error:
        assert error.args[0].startswith("Label names must satisfy")
    else:
        assert False

def test_label_name_containing_whitespaces():
    commands = ["foo bar:", "execute run", "    say baz"]
    try:
        tokenize([(i + 1, command) for i, command in enumerate(commands)])
    except ValueError as error:
        assert error.args[0].startswith("Unknown or incomplete command")
    else:
        assert False

def test_unknown_label():
    commands = ["execute run", "    redo foo"]
    try:
        tokenize([(i + 1, command) for i, command in enumerate(commands)])
    except NameError as error:
        assert error.args[0].startswith("Unknown label")
    else:
        assert False

def test_redo_having_more_arguments():
    commands = ["foo:", "execute run","    redo foo bar"]
    try:
        tokenize([(i + 1, command) for i, command in enumerate(commands)])
    except SyntaxError as error:
        assert error.args[0].startswith("Command 'redo' has more than 1 argument at line ")
    else:
        assert False