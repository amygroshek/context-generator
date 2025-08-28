#!/usr/bin/env python3

# python generateDiffContext.py \
#   --instructions="Review my changes" \
#   --repo="~/projects/my-repo" \
#   --main-branch=main | llm -t grok "Please review"

import argparse
import os
import sys
import datetime
import subprocess
from io import StringIO

# --- Determine Paths Relative to the Script ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'input')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'output')

# --- Configuration ---
GENERIC_INSTRUCTIONS_FILE = os.path.join(INPUT_DIR, "generic-instructions.md")
# --- End Configuration ---

def run_git_command(repo_path, args):
    """Run a git command and return stdout, or raise error."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {' '.join(e.cmd)}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

def get_git_diff(repo_path, main_branch):
    """Return the diff between current branch and main_branch."""
    # Find current branch
    current_branch = run_git_command(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    if current_branch == main_branch:
        return f"[Current branch is {main_branch}; no diff to show]"

    # Generate diff
    diff_output = run_git_command(repo_path, ["diff", f"{main_branch}...{current_branch}"])
    if not diff_output.strip():
        return "[No changes between current branch and main branch]"
    return diff_output

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
    parser = argparse.ArgumentParser(description="Generate a Markdown prompt including git diff context.")
    parser.add_argument("--instructions", required=True, help="The specific request or question for the prompt.")
    parser.add_argument("--repo", required=True, help="Path to the git repository.")
    parser.add_argument("--main-branch", default="main", help="The name of the main branch (default: main).")
    args = parser.parse_args()

    basic_request = args.instructions
    repo_path = os.path.abspath(os.path.expanduser(args.repo))
    main_branch = args.main_branch

    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print(f"Error: '{repo_path}' is not a valid git repository.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"prompt_diff_{timestamp}.md"
    output_filepath = os.path.join(OUTPUT_DIR, output_filename)

    generic_instructions = read_file_content(GENERIC_INSTRUCTIONS_FILE, is_optional=False)
    diff_content = get_git_diff(repo_path, main_branch)

    buffer = StringIO()
    def write_line(s): buffer.write(s + '\n')

    write_line("# Basic Request\n")
    write_line(basic_request + "\n")

    write_line("## Generic Instructions\n")
    write_line(generic_instructions + "\n")

    write_line("## Git Diff\n")
    write_line(f"Diff between current branch and `{main_branch}`:\n")
    write_line("```diff")
    write_line(diff_content)
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
