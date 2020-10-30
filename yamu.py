"""
    CLI script for yamu
"""

import os
import shutil
import sys
import time
import argparse
from pathlib import Path

from src.parser import Parser

def main():
    argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str)
    parser.add_argument("-o", "--output", type=str)
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"ERROR: Input path '{input_path}' does not exist.")
        return
    
    if not output_path.exists():
        print(f"ERROR: Output path '{output_path}' does not exist.")
        return
    
    if input_path.parent == output_path:
        output_path = output_path.joinpath("out")
    output_path = output_path.joinpath(input_path.name)
    
    start_time = time.process_time()
    print(f"Compiling at {output_path}...")

    # TODO Save compilation time by not recompiling unedited files in a datapack
    # by comparing compiled file timestamp and uncompiled file timestamp.
    # User can force compile all files by adding the --force argument
    if output_path.exists():
        shutil.rmtree(output_path, ignore_errors=True)
    
    shutil.copytree(input_path, output_path, ignore=shutil.ignore_patterns("*.mcfunctionx"))

    for file in input_path.joinpath("data").glob("**/*.mcfunctionx"):
        fc = Parser(file, input_path, output_path)
        fc.parse()
    
    print(f"Done! Took {(time.process_time() - start_time)*1000}ms to complete.")

if __name__ == "__main__":
    main()
