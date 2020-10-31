from .tokenizer import tokenize
import os

class Compiler:
    def __init__(self, file, input_path, output_path, *, debug=False) -> None:
        self.file = file
        self.input_path = input_path
        self.output_path = output_path.joinpath(file.parent.relative_to(input_path))
        self.debug = debug

        self.file_parent = file.parent
        self.file_name = file.with_suffix("").name

        self.lambda_count = 0
        
        rel_path = self.file_parent.relative_to(input_path.joinpath("data"))
        path_tuple = rel_path.parts[2:]
        namespace = rel_path.parts[0]
        if path_tuple: 
            self.minecraft_path = f"{namespace}:{'/'.join(path_tuple)}/"
        else:
            self.minecraft_path = f"{namespace}:"

        # Create necessary directories from output path
        if not self.debug and not self.output_path.exists():
            os.makedirs(self.output_path, exist_ok=True)

    def compile(self):
        output = []
        with open(self.file, "r") as f:
            contents = [line.rstrip() for line in f if line.rstrip()]
            parsed_commands = None
            try:
                parsed_commands = tokenize(contents)
            except:
                print(self.file)
                raise

            for node in parsed_commands:
                if node.get_type() == "simple":
                    output.append(node.command)
                elif node.get_type() == "intented":
                    output.append(self.paginate_file(node))
        
        if self.debug:
            return output
        
        with self.output_path.joinpath(f"{self.file_name}.mcfunction").open(mode="w+") as f:
            f.write(("\n").join(output))
        return True
        

    def paginate_file(self, node):
        res = []
        name = f"{self.file_name}_ln{self.lambda_count:03d}"
        self.lambda_count += 1
        for child in node.get_children():
            if child.get_type() == "simple":
                res.append(child.command)
            elif child.get_type() == "intented":
                res.append(self.paginate_file(child))
        
        if node.should_redo():
            res.append(f"{node.get_redo_condition()}{node.command} function {self.minecraft_path}{name}")
        
        if self.debug:
            return (res, f"{node.command} function {self.minecraft_path}{name}")

        with self.output_path.joinpath(f"{name}.mcfunction").open(mode="w+") as f:
            f.write(("\n").join(res))
        return f"{node.command} function {self.minecraft_path}{name}"