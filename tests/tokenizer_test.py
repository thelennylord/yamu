from src.tokenizer import tokenize
from src.tokens.SimpleCommand import SimpleCommand
from src.tokens.IndentationCommand import IndentationCommand

def test_output_length():
    commands = ["say foo", "say bar", "say far", "say boo"]
    tokens = tokenize(commands)
    assert len(tokens) == 4

def test_simple_command_token():
    commands = ["say abc"]
    tokens = tokenize(commands)
    assert isinstance(tokens[0], SimpleCommand)

def test_indentation_command_token():
    commands = ["execute as @a run", "    say abc"]
    tokens = tokenize(commands)
    assert isinstance(tokens[0], IndentationCommand)

def test_token_value():
    commands = ["say foo", "execute as @a run", "    say bar"]
    tokens = tokenize(commands)
    assert tokens[0].get_command() == "say foo"
    assert tokens[1].get_command() == "execute as @a run"

def test_indentation():
    commands = ["execute as @a run", "    say abc"]
    tokens = tokenize(commands)
    assert tokens[0].get_children()[0].get_command() == "say abc"

def test_invalid_indentation_space():
    commands = ["execute as @a run", " say abc"]
    try:
        tokenize(commands)
    except IndentationError:
        assert True
    else:
        assert False

def test_should_redo():
    commands = ["execute as @a run", "    redo"]
    tokens = tokenize(commands)
    assert tokens[0].should_redo() == True

def test_should_not_redo():
    commands = ["execute as @a run", "    say abc"]
    tokens = tokenize(commands)
    assert tokens[0].should_redo() == False

def test_indentation_children_length():
    commands = ["execute as @a run", "    say foo", "    say bar"]
    tokens = tokenize(commands)
    assert len(tokens[0].get_children()) == 2

# Should be modified once custom yamu classes are made
def test_non_indented_redo():
    commands = ["say abc", "redo"]
    try:
        tokenize(commands)
    except ValueError as error:
        if error.args[0] == "Command 'redo' must be indented in an execute command":
            assert True
        else:
            assert False
    else:
        assert False

def test_indentation_children():
    commands = ["execute as @a run", "    say foo", "    execute as @p run", "        say bar"]
    tokens = tokenize(commands)
    children = tokens[0].get_children()
    assert isinstance(children[0], SimpleCommand)
    assert isinstance(children[1], IndentationCommand)

def test_indentation_exit():
    commands = ["execute as @a run", "    say foo", "say bar"]
    tokens = tokenize(commands)
    assert isinstance(tokens[0], IndentationCommand)
    assert isinstance(tokens[1], SimpleCommand)

def test_inline_redo():
    commands = ["execute as @a run", "    execute as @e at @s run redo"]
    tokens = tokenize(commands)
    assert tokens[0].get_redo_condition() == "execute as @e at @s run "

def test_non_inline_redo():
    commands = ["execute as @a run", "    say abc"]
    tokens = tokenize(commands)
    assert tokens[0].get_redo_condition() == ""

def test_excess_indentation():
    commands = ["execute as @a run", "        say foo"]
    try:
        tokenize(commands)
    except IndentationError:
        assert True
    else:
        assert False

def test_invalid_indentation():
    commands = ["say foo", "    say bar"]
    try:
        tokenize(commands)
    except IndentationError:
        assert True
    else:
        assert False

# Should be removed once tokenizer uses brigadier
# Should be modified once yamu error classes are made
def test_invalid_command():
    commands = ["foo bar"]
    try:
        tokenize(commands)
    except ValueError as error:
        if error.args[0].startswith("Unknown or incomplete command, see below for error"):
            assert True
        else:
            assert False
    else:
        assert False

def test_ignore_comments():
    commands = ["say foo", "#far", "#boo", "say bar"]
    tokens = tokenize(commands)
    assert len(tokens) == 2
    assert tokens[0].get_command() == "say foo"
    assert tokens[1].get_command() == "say bar"

def test_ignore_empty_lines():
    commands = ["say foo", "", "say bar", ""]
    tokens = tokenize(commands)
    assert len(tokens) == 2
    assert tokens[0].get_command() == "say foo"
    assert tokens[1].get_command() == "say bar"