# Yet Another Minecraft Utility (yamu)
Improves the experience coding in Minecraft's mcfunction (Java edition only).<br>
**yamu is currently in alpha**

# Features (currently)
- Introduces indentation for execute commands.
- Introduces the `redo` command for execute commands.
- Allows execute commands to be labelled to change control flow.

# Features (planned)
- [ ] Syntax checks for commands
- [ ] Ability to create yamu packages, which acts like a custom command (like `redo`)

# Installation
**Requires Python 3.7 or higher**
```sh
# For linux or macOS
python3 -m pip install -e .

# For windows
py -3 -m pip install -e .
```

# Usage
Currently, yamu can only be used through the command line.<br><br>
yamu files are prefixed with `.mcfunctionx`. Before compiling a yamu file, it needs to be part of a datapack folder. The following command is used to compile:
```sh
yamu [-i <datapack path>] [-o <output path>]
```
To view all the list of possible commands using yamu, one can do the following:
```sh
yamu -h 
```

# Examples
yamu files needs to be prefixed with `.mcfunctionx`<br>
## Indentation
yamu allows the use of indentation in execute commands to simplify writing of code. The indentation is akin to Python's. To go in a level of an execute block, the command must have 4 spaces before it.

Input:
```mcfunction
# namespace:foo.mcfunctionx

say foo
execute as @a at @s run
    say bar
    say baz
```

Output:
```mcfunction
# namespace:foo.mcfunction
say foo
execute as @a at @s run function namespace:foo_ln000


# namespace:foo_ln000
say bar
say baz
```

## Looping in an execute command
yamu has a special command named `redo`, which helps looping in an execute command easier.

Input:
```mcfunction
# namespace:foo.mcfunctionx
execute as @a if score @s health matches 0.. run
    say alive
    redo

# redo can be used in an execute command too!
execute as @a if score @s coins matches 0.. run
    say not broke
    execute if score @s health matches 0.. run redo
```

Output:
```mcfunction
# namespace:foo.mcfunction
execute as @a if score @s health matches 0.. run function namespace:foo_ln000
execute as @a if score @s coins matches 0.. run function namespace:foo_ln001


# namespace:foo_ln000.mcfunction
say alive
execute as @a if score @s health matches 0.. run function namespace:foo_ln000


# namespace:foo_ln001.mcfunction
say not broke
execute if score @s health matches 0.. run execute as @a if score @s coins matches 0.. run function namespace:foo_ln001
```

## Using labels in redo command
Labels are used to mark an execute block. Labels are used in one of the arguments of the `redo` command to redo a labelled execute block. Label names must be alphanumerical and can contain underscores (_). However, they cannot begin with a number.

Input:
```mcfunction
bar:
execute if score @s health matches 0.. run
    execute if score @s coins matches ..0 run
        say broke
        redo bar
```

When you pass a label to the `redo` command, the execute block under the given label gets executed again. In this instance, we passed the label `bar` to the `redo` command. So, the execute block below the label `bar` will be executed again.

Output:
```mcfunction
# namespace:foo.mcfunction
execute if score @s health matches 0.. run function namespace:foo_ln000

# namespace:foo_ln000.mcfunction
execute if score @s coins matches ..0 run function namespace:foo_ln001

# namespace:foo_ln001.mcfunction
say broke
execute if score @s health matches 0.. run function namespace:foo_ln000
```

## License
[MIT](https://github.com/thelennylord/yamu/blob/master/LICENSE)