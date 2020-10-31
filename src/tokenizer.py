from .tokens.literal_token import LiteralToken
from .tokens.indentation_token import IndentationToken


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

    for command in commands:
        redo_condition = ""

        if not command: continue
        if command.lstrip()[0] == COMMENT: continue

        indent = calculate_indent(command)
        if indent is None:
            raise IndentationError(f"Improper indentation spacing at {command}<--[HERE]")
        command = command.lstrip()
        if indent:
            if indent == level:
                # TODO: Validate execute...run using brigadier
                if command[:8] == "execute " and command[-4:] == " run":
                    current_node.append(IndentationToken(command, current_node))
                    level += 1
                    current_node = current_node.get_children()[-1]
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
                    current_node = current_node.get_children()[-1]
                    continue
            else:
                raise IndentationError(f"Illegal indentation detected at {command}<--[HERE]")
        else:
            current_node = result
            level = 0

        if command[:8] == "execute ":
            if command[-4:] == " run":
                current_node.append(IndentationToken(command))
                level += 1
                current_node = current_node[-1]
                continue
            elif command[-9:] == " run redo":
                redo_condition = command[:-4]
                command = "redo"
        
        # TODO: Implement all vanilla commands into brigadier
        if command.split(" ")[0] in DEFAULT_COMMANDS:
            parent = current_node if indent else None
            current_node.append(LiteralToken(command, parent))
        elif command == "redo":
            if not indent:
                raise ValueError("Command 'redo' must be indented in an execute command")
            
            parent_node = current_node.get_parent()
            if parent_node is None:
                parent_node = result[-1]
            else:
                parent_node = parent_node.get_children()[-1]
            
            parent_node.set_redo(True)
            if redo_condition:
                parent_node.set_redo_condition(redo_condition)
        else:
            raise ValueError(f"Unknown or incomplete command, see below for error\n{command.split(' ')[0]}<--[HERE]")
    return result