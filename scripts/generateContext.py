#!/usr/bin/env python3

import argparse
import os
import sys
import datetime

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
    """Gets the file extension without the leading dot."""
    _, ext = os.path.splitext(filepath)
    return ext[1:] if ext else ""

def read_file_content(filepath, is_optional=False):
    """
    Reads content of a file, returns content or error/info message.
    If is_optional is True and file not found, returns a specific message.
    """
    display_name = os.path.basename(filepath) # Get filename for messages
    try:
        # Expand ~user constructs if present
        expanded_path = os.path.expanduser(filepath)

        if not os.path.exists(expanded_path):
            if is_optional:
                return f"[Optional file not found: {display_name}]"
            else:
                # Return error with the original path user provided for clarity
                return f"Error: File not found at '{filepath}'"

        if not os.path.isfile(expanded_path):
             return f"Error: Path is not a file: '{filepath}'"

        if os.path.getsize(expanded_path) == 0:
             return f"[File is empty: {display_name}]"

        with open(expanded_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError: # Fallback, though os.path.exists should catch it
         if is_optional:
            return f"[Optional file not found: {display_name}]"
         else:
            return f"Error: File not found at '{filepath}'"
    except Exception as e:
        # Return error with the original path user provided
        return f"Error reading file '{filepath}': {e}"

def main():
    # --- 1. Parse Command Line Arguments ---
    parser = argparse.ArgumentParser(
        description="Generate a Markdown prompt including context from full file paths."
    )
    parser.add_argument(
        "--instructions",
        required=True,
        help="The specific request or question for the prompt.",
        metavar='"Your Question/Request"'
    )
    args = parser.parse_args()
    basic_request = args.instructions

    # --- Ensure Output Directory Exists ---
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"Ensured output directory exists: '{OUTPUT_DIR}'")
    except OSError as e:
        print(f"Error: Could not create output directory '{OUTPUT_DIR}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- Generate Output Filename ---
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"prompt_{timestamp}.md"
    output_filepath = os.path.join(OUTPUT_DIR, output_filename)
    print(f"Output will be saved to: '{output_filepath}'")

    # --- 2. Read Generic Instructions ---
    print(f"Reading generic instructions from '{GENERIC_INSTRUCTIONS_FILE}'...")
    generic_instructions = read_file_content(GENERIC_INSTRUCTIONS_FILE, is_optional=False)
    if generic_instructions.startswith("Error:") or generic_instructions.startswith("[File is empty"):
        print(generic_instructions, file=sys.stderr)
        # Decide how critical this is. Exit or provide placeholder?
        # sys.exit(1) # Exit if required
        generic_instructions = "[Could not load required generic instructions file]" # Placeholder if continuing

    # --- 3. Read Optional Terminal Output ---
    print(f"Reading optional terminal output from '{TERMINAL_OUTPUT_FILE}'...")
    terminal_output_content = read_file_content(TERMINAL_OUTPUT_FILE, is_optional=True)
    if terminal_output_content.startswith("Error reading file"): # Log actual read errors
         print(terminal_output_content, file=sys.stderr)

    # --- 4. Read Context File List (Now Expects Full Paths) ---
    print(f"Reading list of full file paths from '{CONTEXT_FILES_LIST_FILE}'...")
    full_file_paths = [] # List to store the full paths from the file
    included_files_list_content = [] # For the bulleted list in output (using basename)

    # Read context list - this file IS required
    context_list_content = read_file_content(CONTEXT_FILES_LIST_FILE, is_optional=False)
    if context_list_content.startswith("Error:") or context_list_content.startswith("[File is empty"):
        print(context_list_content, file=sys.stderr)
        sys.exit(1) # Exit if the context list file is missing or empty

    try:
        raw_paths = [line.strip() for line in context_list_content.splitlines() if line.strip() and not line.strip().startswith('#')]

        if not raw_paths:
             print(f"Error: No valid file paths found in '{CONTEXT_FILES_LIST_FILE}'.", file=sys.stderr)
             sys.exit(1)

        for path in raw_paths:
            expanded_path = os.path.expanduser(path) # Handle ~
            # Optional: Warn if path doesn't seem absolute, though we proceed anyway
            if not os.path.isabs(expanded_path):
                print(f"Warning: Path may not be absolute, using as provided: '{path}'", file=sys.stderr)
            full_file_paths.append(expanded_path) # Store the potentially expanded path
            # Use basename for the markdown list for readability
            included_files_list_content.append(f"* `{os.path.basename(path)}`")

    except Exception as e: # Catch other potential errors during list processing
        print(f"Error processing file paths from '{CONTEXT_FILES_LIST_FILE}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- 5. Read Content of Context Files ---
    print("Reading context files specified by full paths...")
    # List to store tuples of (display_name, content, extension)
    context_data = []
    for full_path in full_file_paths:
        display_name = os.path.basename(full_path) # Use filename for display
        print(f"  Processing: {full_path}")
        # Context files are essential, so treat errors seriously (is_optional=False)
        content = read_file_content(full_path, is_optional=False)
        if content.startswith("Error:") or content.startswith("[File is empty"): # Check for read errors/empty
             print(f"  Warning: {content}", file=sys.stderr) # Print warning but continue gathering context
        extension = get_file_extension(full_path)
        context_data.append((display_name, content, extension)) # Store basename for heading

    # --- 6. Generate Output Markdown ---
    print(f"Generating output Markdown file '{output_filepath}'...")
    try:
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            # Basic Request
            outfile.write("# Basic Request\n\n")
            outfile.write(f"{basic_request}\n\n")

            # Generic Instructions
            outfile.write("## Generic Instructions\n\n")
            outfile.write(f"{generic_instructions}\n\n")

            # Terminal Output
            outfile.write("## Terminal Output\n\n")
            outfile.write("```text\n")
            outfile.write(f"{terminal_output_content}\n")
            outfile.write("```\n\n")

            # Context Header
            outfile.write("## Context\n\n")

            # List of Included Files (Using Basenames)
            outfile.write("### List of Included Files\n\n")
            if included_files_list_content:
                 outfile.write("\n".join(included_files_list_content))
            else:
                 # This case shouldn't happen due to earlier checks, but good to have
                 outfile.write("* *No valid file paths found in input list.*")
            outfile.write("\n\n")

            # Individual File Contents (Using Basenames for Headers)
            for display_name, content, extension in context_data:
                outfile.write(f"#### {display_name}\n\n") # Use basename for heading
                outfile.write(f"```{extension}\n")
                outfile.write(f"{content}\n") # Write content or error/info message for this specific file
                outfile.write("```\n\n")

        print(f"Successfully generated '{output_filepath}'")

    except Exception as e:
        print(f"Error writing output file '{output_filepath}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
