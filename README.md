# Context Generator

Quickly generate a context file to pass to AI using a tool like [llm-cli](https://github.com/simonw/llm).

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

6. The prompt will be generated to the `./output` directory with a date and time stamp. The prompt is also written to stdout so you can pipe it directly into llm-cli:
```
python generateContext.py --instructions "[instructions]" | llm -t grok --no-stream "instructions"
python generateContext.py --instructions "[instructions]" | llm "instructions"
```

## Diff Context Option

Another script will generate a diff between the current branch and a main branch in a repo indicated in an argument. The diff will be added to the contenxt, and you can ask for the LLM to assess the git diff.

```bash
python generateDiffContext.py \
  --instructions="Review my changes in the diff provided in context. I've added some other files for context as well. Please forus primarily on typos and other minor issues that would create unnecessary back-and-forth during the PR process." \
  --repo="/home/lou/repos/costco/gdx-ux-cnsw-my-account" \
  --main-branch=develop | llm -t grok "Please review"
```

## Why?

* Are there VS Code solutions for this? Yes. They are mostly buggy and use a ton of RAM.
* Or, you could just let Claude run roughshod over your repo, and clean up for a few months afterwards.
* This allows you to create a record of prompts and subtly modify and re-use them over time.
* Fork the repo to save your own instructions or modify the script.
