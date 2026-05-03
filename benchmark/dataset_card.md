---
license: mit
task_categories:
- question-answering
- text-generation
language:
- en
tags:
- performance-marketing
- meta-ads
- google-ads
- benchmark
- evaluation
- llm-evaluation
- advertising
- reasoning
pretty_name: PM-AGI Benchmark v2
size_categories:
- n<1K
---

# PM-AGI Benchmark v2 🎯

**The open-source LLM reasoning benchmark for Performance Marketing.**

Developed by [hawky.ai](https://hawky.ai) — evaluating how well LLMs **reason** about real-world **Meta Ads** and **Google Ads** scenarios. v2 (494 questions) is built to surface the gap between knowledge recall and genuine reasoning.

## Dataset Summary (v2)

PM-AGI v2 contains **494 expert-crafted questions** across 4 categories and **5 reasoning types**:

| Category | Questions | Focus |
|---|---|---|
| Meta Ads | 227 | Campaign structure, targeting, bidding, creative, CAPI, Advantage+, iOS/SKAN, attribution |
| Google Ads | 227 | Search, Smart Bidding, PMax, Quality Score, attribution, Demand Gen, feed quality |
| Critical Thinking | 20 | Cross-cutting data interpretation, budget decisions, competitive analysis |
| Action-Based | 20 | Real-world optimization scenarios |

## Reasoning Types (v2 — what kind of thinking each question tests)

| Reasoning Type | Questions | What It Tests |
|---|---|---|
| `recall` | 219 | Platform knowledge & best-practice MCQs |
| `adversarial` | 80 | Trap questions defeating pattern-match on outdated 2019-era playbooks |
| `diagnostic` | 69 | Multi-step root-cause reasoning over anomalous campaign data |
| `quantitative` | 70 | Budget allocation, marginal ROAS, LTV math, stated assumptions |
| `creative_strategy` | 56 | A/B test design, experiment methodology, iteration systems |

## Question Types

- **MCQ** (302 questions) — Single correct answer, scored 1.0 or 0.0
- **Action-Based** (192 questions) — Open scenario evaluated by LLM judge (0.0–1.0) against 5–10 expert rubric criteria per question

## Difficulty Distribution

- Easy: 14 questions
- Medium: 165 questions
- Hard: 315 questions (reasoning-heavy by design)

## Usage

```python
from datasets import load_dataset

ds = load_dataset("Hawky-ai/pm-agi-benchmark")
print(ds["test"][0])
```

## Evaluate a Model

```bash
git clone https://github.com/Hawky-ai/pm-AGI
cd pm-agi-benchmark
pip install -r requirements.txt
python evaluate.py --model gpt-4o --provider openai --api-key YOUR_KEY
```

## Leaderboard

🏆 [Live Leaderboard](https://huggingface.co/spaces/Hawky-ai/pm-agi-leaderboard)

## Citation

```bibtex
@misc{pmagi2025,
  title={PM-AGI: A Performance Marketing Benchmark for Large Language Models},
  author={hawky.ai},
  year={2025},
  url={https://huggingface.co/datasets/Hawky-ai/pm-agi-benchmark}
}
```

## License

MIT — see [LICENSE](https://github.com/Hawky-ai/pm-AGI/blob/main/LICENSE)
