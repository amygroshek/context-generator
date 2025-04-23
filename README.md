# Context Generator

Quickly generate a context file to pass to AI using a tool like (llm-cli)[https://github.com/simonw/llm].

## Quickstart

1. Clone the repo somewhere
2. Add your generic instructions to`./input/generic-instructions.md`. These will be appended to every prompt and should be generic instrcutions for the model.
3. Paste full paths of teach file to include for context into `./input/prompt-context-files.txt`. One path on each line.
4. If you have any terminal output, like failing unit tests, place that into `./input/terminal-output.txt`.
5. Run the script from the `./scripts` directory:

```
cd scripts
python generateContext.py --instructions "My specific request blah"
```

6. The prompt will be generated to the `./output` directory with a date and time stamp. The prompt is also written to stdout so you can pipe it directly into llm-cli: `python generateContext.py --instructions "I've got a failing unit test in the included test file. Please help me troubleshoot the issue." | llm -t grok`.

## Why?

* Are there VS Code solutions for this? Yes. They are mostly buggy and use a ton of RAM.
* Or, you could just let Claude run roughshod over your repo, and clean up for a few months afterwards.
* This allows you to create a record of prompts and subtly modify and re-use them over time.
* Fork the repo to save your own instructions or modify the script.