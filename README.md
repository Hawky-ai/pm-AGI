# PM-AGI Benchmark 🎯

**The first open-source LLM benchmark for Performance Marketing.**

Developed by [hawky.ai](https://hawky.ai) — evaluating how well LLMs reason, plan, and act in real-world performance marketing scenarios across **Meta Ads** and **Google Ads**.

[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-Dataset-yellow)](https://huggingface.co/datasets/hawky-ai/pm-agi-benchmark)
[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-Leaderboard-blue)](https://huggingface.co/spaces/hawky-ai/pm-agi-leaderboard)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What is PM-AGI?

PM-AGI measures LLM performance across four critical dimensions of performance marketing:

| Category | Description |
|---|---|
| **Meta Ads** | Facebook/Instagram campaign structure, targeting, bidding, creative, measurement |
| **Google Ads** | Search, Smart Bidding, Quality Score, Performance Max, attribution |
| **Critical Thinking** | Data interpretation, budget decisions, competitive analysis |
| **Action-Based** | Given a real scenario — what do you do? Optimization, troubleshooting, scaling |

---

## Benchmark Stats (v2)

| Metric | Value |
|---|---|
| Total Questions | 494 |
| Meta Ads Questions | 227 |
| Google Ads Questions | 227 |
| Critical Thinking Questions | 20 |
| Action-Based Questions | 20 |
| Question Types | MCQ (302), Action-Based / Open-Ended (192) |
| Difficulty Levels | Easy (14), Medium (165), Hard (315) |
| Reasoning Types | Recall (219), Adversarial (80), Diagnostic (69), Quantitative (70), Creative Strategy (56) |

---

## Quick Start

```bash
git clone https://github.com/Hawky-ai/pm-AGI
cd pm-agi-benchmark
pip install -r requirements.txt
```

### Run evaluation on any model

```bash
# Evaluate using OpenAI
python evaluate.py --model gpt-4o --provider openai --api-key YOUR_KEY

# Evaluate using Anthropic
python evaluate.py --model claude-opus-4-6 --provider anthropic --api-key YOUR_KEY

# Evaluate using any OpenAI-compatible endpoint
python evaluate.py --model llama-3.3-70b --provider openai-compatible --base-url YOUR_URL --api-key YOUR_KEY

# Run only a specific category
python evaluate.py --model gpt-4o --provider openai --category meta_ads
```

### Results are saved to `results/` and can be submitted to the leaderboard.

---

## Dataset Format

Each question in `benchmark/dataset.json` follows this schema:

```json
{
  "id": "meta_001",
  "category": "meta_ads",
  "subcategory": "bidding_strategy",
  "difficulty": "medium",
  "type": "mcq",
  "reasoning_type": "recall",
  "question": "...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "answer": "B",
  "explanation": "...",
  "tags": ["roas", "value_optimization"]
}
```

**Question Types:**
- `mcq` — Multiple choice, single correct answer
- `action_based` — Scenario with expected actions/reasoning, evaluated by LLM-judge against `answer_criteria` rubric

**Reasoning Types (v2):**
- `recall` — Platform knowledge & best practices
- `adversarial` — Trap questions with plausible outdated-playbook distractors
- `diagnostic` — Multi-step root-cause reasoning
- `quantitative` — Math + tradeoffs + stated assumptions
- `creative_strategy` — Experiment design, A/B methodology, iteration systems

---

## Evaluation Scoring

| Type | Scoring |
|---|---|
| MCQ | 1.0 if exact match, 0.0 otherwise |
| Action-Based / Open-Ended | LLM-as-judge (0.0–1.0) against `answer_criteria` rubric |

**Overall Score** = weighted average across all categories.

**v2 Result Output** — beyond the overall + per-category breakdown, evaluate.py now reports per-reasoning-type scores so you can see whether your model's strength is recall vs diagnostic vs adversarial vs quantitative vs creative-strategy reasoning.

```
By Reasoning Type:
  recall                 92.4%  (219 questions)
  adversarial            54.1%  (80 questions)
  diagnostic             61.8%  (69 questions)
  quantitative           58.7%  (70 questions)
  creative_strategy      68.4%  (56 questions)
```

The recall-vs-reasoning gap is the load-bearing signal of the benchmark.

---

## Submitting Results to the Leaderboard

1. Run evaluation: `python evaluate.py --model YOUR_MODEL --provider YOUR_PROVIDER`
2. A result file is saved to `results/YOUR_MODEL_results.json`
3. Open a PR to this repo adding your result file, OR submit via the HF Space form.

---

## Leaderboard

Visit the live leaderboard: [huggingface.co/spaces/hawky-ai/pm-agi-leaderboard](https://huggingface.co/spaces/hawky-ai/pm-agi-leaderboard)

---

## Contributing

We welcome contributions to the benchmark dataset! See [CONTRIBUTING.md](CONTRIBUTING.md).

- Adding new questions: follow the schema above and open a PR to `benchmark/dataset.json`
- New categories (TikTok Ads, LinkedIn Ads coming soon)
- Translations

---

## Citation

```bibtex
@misc{pmagi2025,
  title={PM-AGI: A Performance Marketing Benchmark for Large Language Models},
  author={hawky.ai},
  year={2025},
  url={https://github.com/Hawky-ai/pm-AGI}
}
```

---

## License

MIT License — see [LICENSE](LICENSE).

Built with ❤️ by the [hawky.ai](https://hawky.ai) team.
