#!/usr/bin/env python3

import argparse
import os
import sys
import datetime
from io import StringIO

# --- Determine Paths Relative to the Script ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'input')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'output')

# --- Configuration ---
GENERIC_INSTRUCTIONS_FILE = os.path.join(INPUT_DIR, "generic-instructions.md")
CONTEXT_FILES_LIST_FILE = os.path.join(INPUT_DIR, "prompt-context-files.txt")
TERMINAL_OUTPUT_FILE = os.path.join(INPUT_DIR, "terminal-output.txt")
# --- End Configuration ---

def get_file_extension(filepath):
    _, ext = os.path.splitext(filepath)
    return ext[1:] if ext else ""

def read_file_content(filepath, is_optional=False):
    display_name = os.path.basename(filepath)
    try:
        expanded_path = os.path.expanduser(filepath)

        if not os.path.exists(expanded_path):
            return f"[Optional file not found: {display_name}]" if is_optional else f"Error: File not found at '{filepath}'"

        if not os.path.isfile(expanded_path):
            return f"Error: Path is not a file: '{filepath}'"

        if os.path.getsize(expanded_path) == 0:
            return f"[File is empty: {display_name}]"

        with open(expanded_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{filepath}': {e}"

def main():
    parser = argparse.ArgumentParser(description="Generate a Markdown prompt including context from full file paths.")
    parser.add_argument("--instructions", required=True, help="The specific request or question for the prompt.", metavar='"Your Question/Request"')
    args = parser.parse_args()
    basic_request = args.instructions

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"prompt_{timestamp}.md"
    output_filepath = os.path.join(OUTPUT_DIR, output_filename)

    generic_instructions = read_file_content(GENERIC_INSTRUCTIONS_FILE, is_optional=False)
    terminal_output_content = read_file_content(TERMINAL_OUTPUT_FILE, is_optional=True)
    context_list_content = read_file_content(CONTEXT_FILES_LIST_FILE, is_optional=False)

    if context_list_content.startswith("Error:") or context_list_content.startswith("[File is empty"):
        print(context_list_content, file=sys.stderr)
        sys.exit(1)

    raw_paths = [line.strip() for line in context_list_content.splitlines() if line.strip() and not line.strip().startswith('#')]
    if not raw_paths:
        print(f"Error: No valid file paths found in '{CONTEXT_FILES_LIST_FILE}'.", file=sys.stderr)
        sys.exit(1)

    full_file_paths = []
    included_files_list_content = []
    for path in raw_paths:
        expanded_path = os.path.expanduser(path)
        full_file_paths.append(expanded_path)
        included_files_list_content.append(f"* `{os.path.basename(path)}`")

    context_data = []
    for full_path in full_file_paths:
        display_name = os.path.basename(full_path)
        content = read_file_content(full_path, is_optional=False)
        extension = get_file_extension(full_path)
        context_data.append((display_name, content, extension))

    buffer = StringIO()

    def write_line(s):
        buffer.write(s + '\n')

    write_line("# Basic Request\n")
    write_line(basic_request + "\n")

    write_line("## Generic Instructions\n")
    write_line(generic_instructions + "\n")

    write_line("## Terminal Output\n")
    write_line("```text")
    write_line(terminal_output_content)
    write_line("```\n")

    write_line("## Context\n")
    write_line("### List of Included Files\n")
    write_line("\n".join(included_files_list_content) + "\n")

    for display_name, content, extension in context_data:
        write_line(f"#### {display_name}\n")
        write_line(f"```{extension}")
        write_line(content)
        write_line("```\n")

    markdown_content = buffer.getvalue()

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"[✔] Wrote to: {output_filepath}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(markdown_content)

if __name__ == "__main__":
    main()
