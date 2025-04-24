# RPLA Hero Character Benchmarking

A framework for benchmarking AI models on their understanding of fictional characters across multiversal contexts.

## Overview

This project evaluates how well different AI models understand and represent fictional characters across various contexts. By testing models against a diverse set of character-based tasks, we assess their ability to:

1. Maintain canonical knowledge
2. Reason through moral dilemmas in-character
3. Recall character-specific knowledge
4. Generate authentic character quotes

## Tasks

### Character Dilemma
Tests how models handle moral decision-making consistent with a character's established values and personality when faced with difficult scenarios.

### Canon Events
Evaluates models' understanding of canonical events in a character's history and their significance.

### Character Knowledge
Assesses models' recall of character-specific facts, relationships, abilities, and backstory.

### Character Quotes
Tests models' ability to generate authentic-sounding dialogue that matches a character's voice and speech patterns.

## Supported Models

- Gemini 2 (with and without thinking)
- Claude Opus (o3)
- Claude Sonnet 3.7 (37)
- Claude Sonnet 3.5 (v3) 
- Claude 3 Haiku (r1)
- Claude 3 Haiku Zero (r1_zero)

## Data

Character data is sourced from `all_character_data.csv`, containing comprehensive information about fictional characters from various universes.

## Usage

### Generating Answers

```bash
python generate_answer.py --model MODEL_NAME --output OUTPUT_PATH --task TASK_TYPE [options]
```

#### Required Arguments

- `--model`: AI model to use (gemini2, gemini2-thinking, r1, r1_zero, o3, v3, 37)
- `--output`: Path to save the JSONL output
- `--task`: Task type (dilemma, knowledge, canon, quote)

#### Optional Arguments

- `--csv`: Path to input CSV file (default: all_character_data.csv)
- `--apierror`: Flag to retry failed API calls
- `--inputfile`: JSONL file to reprocess
- `--cot`: Use Chain-of-Thought for dilemma and canon tasks
- `--eval_save`: Save evaluation results
- `--cc`: Clean consequences in dilemma task

### Examples

Generate responses for canonical events using Claude 3 Haiku:
```bash
python generate_answer.py --model r1 --output ./generated_results/r1/canon_r1_rep2.jsonl --task canon
```

Generate dilemmas with Gemini 2 using thinking mode:
```bash
python generate_answer.py --model gemini2_flash_thinking --output ./generated_results/gemini2/dilemma_gemini2_flash_thinking_rep1.jsonl --task dilemma
```

Reprocessing failed API calls:
```bash
python generate_answer.py --model r1_zero --output ./generated_results/r1_zero/dilemma_r1_zero_rep1_fixed.jsonl --task dilemma --apierror True --inputfile ./generated_results/r1_zero/dilemma_r1_zero_rep1.jsonl
```

Generate canon events with chain-of-thought reasoning:
```bash
python generate_answer.py --model o3_mini --output ./generated_results/o3/canon_o3_mini_rep1.jsonl --task canon --cot
```

### Analysis

Run analysis after collecting all model responses:
```bash
python -m main
```

This performs:
1. Dilemma analysis grouped by character
2. Canon event analysis grouped by character
3. Scoring analysis across all tasks

## Project Structure

```
.
├── all_character_data.csv
├── generate_answer.py
├── main.py
├── scripts/
│   ├── analysis.py
│   └── ...
├── generated_results/
│   ├── gemini2/
│   ├── r1/
│   ├── r1_zero/
│   ├── o3/
│   └── ...
└── README.md
```

## Results

The benchmark results are stored in the `generated_results` directory, organized by model. Analysis outputs provide insights into each model's performance across tasks and character types.
