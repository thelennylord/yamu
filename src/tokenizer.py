import re

from .tokens.indentation_token import IndentationToken
from .tokens.literal_token import LiteralToken
from .tokens.redirect_token import RedirectToken


def calculate_indent(s):
    l = (len(s) - len(s.lstrip())) / 4
    if l % 1 == 0:
        return int(l)
    return None

def tokenize(commands):
    COMMENT = "#"
    DEFAULT_COMMANDS = ["advancement", "ban-ip", "banlist", "ban", "bossbar", "clear", "clone", "data", "datapack", "debug", "deop", "difficulty", "effect", 
        "me", "enchant", "execute", "experience", "xp", "fill", "forceload", "function", "gamemode", "gamerule", "give", "help", "kick", "kill", "list", 
        "locate", "loot", "msg", "tell", "w", "op", "pardon", "pardon-ip", "particle", "play", "playsound", "publish", "recipe", "reload", "replaceitem", "save-all", 
        "save-off", "save-on", "say", "schedule", "scoreboard", "seed", "setblock", "setidletimeout", "setspawn", "setworldspawn", "spawnpoint", "spectate", "spreadplayers",
        "stop", "stopsound", "summon", "tag", "team", "teammsg", "tm", "teleport", "tp", "tellraw", "time", "title", "weather", "whitelist", "worldborder"]
    
    result = []
    current_node = result
    level = 0
    ln = 0
    labels = {}
    unassigned_label = None
            
    for line, command in commands:
        # TODO: Make a base error class for all yamu errors
        # and transform legacy yamu error to the new error.
        redo_condition = ""

        if not command: continue
        if command.lstrip()[0] == COMMENT: continue

        indent = calculate_indent(command)
        if indent is None:
            raise IndentationError(f"Improper indentation spacing at line {line}\n{command}<--[HERE]")
        command = command.lstrip()
        if indent:
            if indent == level:
                # TODO: Validate execute...run using brigadier
                if command[:8] == "execute " and command[-4:] == " run":
                    current_node.append(IndentationToken(command, current_node))
                    level += 1
                    ln += 1
                    current_node = current_node.get_children()[-1]
                    
                    if unassigned_label is not None:
                        labels[unassigned_label["name"]] = {
                            "ln": unassigned_label["ln"],
                            "node": current_node
                        }
                        unassigned_label = None
                    continue
            elif indent < level:
                steps = level - indent
                for _ in range(steps):
                    current_node = current_node.get_parent()
                    level -= 1
                
                # TODO: Validate execute...run using brigadier
                if command[:8] == "execute " and command[-4:] == " run":
                    current_node.append(IndentationToken(command, current_node))
                    level += 1
                    ln += 1
                    current_node = current_node.get_children()[-1]
                    continue
            else:
                raise IndentationError(f"Illegal indentation detected at line {line}\n{command}<--[HERE]")
        else:
            current_node = result
            level = 0

        if (not " " in command) and command[-1] == ":":
            name = command[:-1]
            m = re.search(r"(^[A-Za-z_]{1})([A-Za-z])([a-zA-Z0-9_]+)", name)
            if m is not None:
                unassigned_label = {
                    "name": name,
                    "ln": ln,
                }
                continue
            else:
                raise SyntaxError(r"Label names must satisfy (^[A-Za-z_]{1})([A-Za-z])([a-zA-Z0-9_]+)")

        if command[:8] == "execute ":
            if command[-4:] == " run":
                current_node.append(IndentationToken(command))
                level += 1
                ln += 1
                current_node = current_node[-1]

                if unassigned_label is not None:
                    labels[unassigned_label["name"]] = {
                        "ln": unassigned_label["ln"],
                        "node": current_node
                    }
                    unassigned_label = None
                continue
            elif command[-9:] == " run redo":
                redo_condition = command[:-4]
                command = "redo"
            else:
                s = command.split(" ")
                if s[-2] == "redo":
                    redo_condition = " ".join(s[:-2]) + " "
                    command = "redo " + s[-1]

        # TODO: Implement all vanilla commands into brigadier
        if command.split(" ")[0] in DEFAULT_COMMANDS:
            parent = current_node if indent else None
            current_node.append(LiteralToken(command, parent))
        elif command[:4] == "redo":
            if not indent:
                raise ValueError("Command 'redo' must be indented in an execute command at line " + str(line))
            
            s = command.split(" ")
            parent_node = current_node.get_parent()
            if len(s) == 2:
                if not s[-1] in labels:
                    raise NameError(f"Unknown label '{s[-1]}' at line " + str(line))

                label = labels[s[-1]]
                node = label["node"]
                current_node.append(RedirectToken(redo_condition + node.get_command(), label["ln"], parent_node))
            elif len(s) == 1:

                if parent_node is None:
                    parent_node = result[-1]
                else:
                    parent_node = parent_node.get_children()[-1]
                
                parent_node.set_redo(True)
                if redo_condition:
                    parent_node.set_redo_condition(redo_condition)
            else:
                raise SyntaxError("Command 'redo' has more than 1 argument at line " + str(line))
        else:
            raise ValueError(f"Unknown or incomplete command at line {line}, see below for error\n{command.split(' ')[0]}<--[HERE]")
        
        if unassigned_label is not None:
            # TODO: Make error more informative
            raise SyntaxError("Label cannot be used on this command at line " + str(line))
    return result
