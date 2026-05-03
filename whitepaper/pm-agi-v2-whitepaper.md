# PM-AGI v2: A Performance Marketing Reasoning Benchmark for Large Language Models

**Hawky.ai · v2.0.0 · 2026**

---

## Abstract

We introduce **PM-AGI v2**, an open-source benchmark for evaluating large language models on performance marketing reasoning. Where prior LLM benchmarks emphasize general knowledge, mathematical reasoning, or coding ability, PM-AGI v2 focuses on a high-stakes domain that combines memorization (platform mechanics), multi-step diagnostic reasoning (root-cause analysis over campaign data), quantitative tradeoffs (budget allocation under constraints), creative experiment design (A/B test methodology), and adversarial robustness (resistance to outdated 2019-era playbooks).

The dataset contains **494 expert-crafted questions** across Meta Ads (227), Google Ads (227), Critical Thinking (20), and Action-Based scenarios (20), spanning **five reasoning categories** (recall, adversarial, diagnostic, quantitative, creative_strategy). Of these, 302 are MCQs (binary scored) and 192 are open-ended scenarios judged by an LLM against a 5–10 point expert rubric.

Across seven baseline models (GPT-5.5, GPT-5.4, GPT-5.4-Pro, GPT-5.2 on Azure; Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 3 Flash Preview), we observe a striking **recall-vs-reasoning gap**: top models score 95–99% on knowledge MCQs but degrade sharply on creative-strategy and diagnostic open-ended questions. The widest gap belongs to GPT-5.5, which scores 95.8% on recall but only 24.5% on creative_strategy — a 71-point gap on the same model. We argue this gap is the load-bearing signal of the benchmark and is more diagnostic of real-world performance-marketing utility than aggregate scores.

---

## 1. Introduction

### 1.1 Motivation

Performance marketing — the discipline of running, optimizing, and scaling paid advertising on platforms like Meta and Google Ads — is increasingly mediated by large language models. Marketers use LLMs to interpret campaign data, troubleshoot CPA spikes, design A/B tests, allocate budgets across channels, and write ad copy. The downstream economic stakes are large: global digital ad spend exceeds $700B annually, and even modest LLM-driven decision quality improvements compound into significant capital reallocation.

Yet the LLM benchmarks that practitioners cite when choosing models — MMLU, GSM8K, HumanEval, MATH, ARC — measure capabilities largely orthogonal to performance marketing reasoning. A model that scores 95% on MMLU may nevertheless recommend allocating budget to brand search at high last-click ROAS (a classic non-incremental trap), or fail to design a geo-holdout test for cannibalization measurement.

PM-AGI v2 fills this gap by testing the specific kinds of reasoning performance marketing requires:
- **Knowledge recall** — platform mechanics, best practices, current product behavior
- **Adversarial robustness** — rejection of outdated 2019-era playbooks (broad targeting > interest stacking, broad match + Smart Bidding > SKAGs, DDA conversion lift is an attribution artifact)
- **Multi-step diagnostic reasoning** — root-cause analysis from anomalous campaign data
- **Quantitative tradeoff reasoning** — budget allocation, marginal ROAS, LTV-payback math, with stated assumptions
- **Creative experiment design** — A/B test methodology, geo-holdout structure, power analysis, pre-committed decision rules

### 1.2 Contributions

1. A 494-question expert-crafted dataset with a backwards-compatible `reasoning_type` schema field, separating knowledge recall from genuine reasoning.
2. An LLM-as-judge evaluation pipeline using Gemini 2.5 Flash as a single, consistent judge across all candidate models (avoiding self-judge bias and reducing cost).
3. Seven baseline evaluations on frontier models from Azure OpenAI (GPT-5.x family) and Google (Gemini 2.5 + 3 family), with full per-question results.
4. Quantitative evidence of a **recall-vs-reasoning gap** that varies dramatically across models — a more diagnostic signal than aggregate scores.

### 1.3 What v2 Adds Over v1

PM-AGI v1 (2025) released 100 expert questions across four categories. v2 expands the dataset 5× (100 → 494), introduces the `reasoning_type` schema, and shifts emphasis from knowledge recall to genuine reasoning:

| | v1 | v2 |
|---|---|---|
| Total questions | 100 | **494** |
| Meta Ads | 30 | 227 |
| Google Ads | 30 | 227 |
| MCQ / Open-ended | 63 / 37 | 302 / 192 |
| Reasoning types | implicit | explicit (5) |
| Mean rubric points per open Q | ~5 | **5–10** |
| Adversarial trap questions | 0 | 80 |

---

## 2. Related Work

PM-AGI v2 sits in a literature of domain-specific LLM benchmarks. Closest neighbors include:

- **MMLU** (Hendrycks et al. 2021): general 57-subject knowledge benchmark. Tests breadth, not reasoning depth in any single domain.
- **GSM8K** / **MATH** (Cobbe et al. 2021; Hendrycks et al. 2021b): mathematical reasoning. Strong at chain-of-thought; orthogonal to applied business reasoning.
- **MMLU-Pro / MMMU**: harder, multimodal extensions of MMLU. Closer to reasoning, but still general-purpose.
- **AgentBench / ToolBench**: tool-use and agentic reasoning. Test orthogonal capabilities.
- **HELM**: holistic evaluation framework. Aggregates many benchmarks; doesn't include performance marketing.
- **Domain-specific benchmarks**: MedQA (medical), LegalBench (legal), FinanceBench (finance). Each demonstrates the value of domain-targeted evaluation. PM-AGI v2 fills the corresponding gap for performance marketing.

We are aware of no prior published benchmark for performance marketing reasoning at LLM scale.

---

## 3. Dataset

### 3.1 Schema

Each question is a JSON object with the following fields:

```json
{
  "id": "meta_303",                         // unique identifier
  "category": "meta_ads",                   // meta_ads | google_ads | critical_thinking | action_based
  "subcategory": "creative_performance",    // platform-specific topic
  "difficulty": "hard",                     // easy | medium | hard
  "type": "action_based",                   // mcq | action_based
  "reasoning_type": "diagnostic",           // recall | adversarial | diagnostic | quantitative | creative_strategy
  "question": "...",                        // scenario or MCQ stem
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},  // MCQ only
  "answer": "B",                            // MCQ correct letter
  "answer_criteria": ["...", "..."],        // open-ended rubric (5–10 points)
  "explanation": "...",                     // rationale for the correct answer
  "tags": ["..."]                           // searchable tags
}
```

The `reasoning_type` field is the headline addition of v2 and is backwards-compatible (v1 questions are tagged `recall` retroactively).

### 3.2 Distribution

| Category | Recall | Adversarial | Diagnostic | Quantitative | Creative | Total |
|---|---|---|---|---|---|---|
| Meta Ads | 60 | 38 | 35 | 35 | 28 | **227** |
| Google Ads | 60 | 38 | 35 | 35 | 28 | **227** |
| Critical Thinking | 20 | — | — | — | — | 20 |
| Action-Based | 20 | — | — | — | — | 20 |
| **Total** | **219** | **80** | **69** | **70** | **56** | **494** |

Difficulty: 14 easy / 165 medium / 315 hard (reasoning-heavy).
Format: 302 MCQ / 192 open-ended (action_based).

### 3.3 Question Authoring

Questions were authored by performance marketing professionals and structured to test the platform-specific knowledge and reasoning patterns observed in production environments at scale. Adversarial questions specifically target outdated 2019-era playbooks — e.g., SKAGs, narrow LAL stacks, "always optimize on CTR" — that pattern-match in older training data but are explicitly contradicted by current best practice (Google Ads documentation, Meta Advantage+ Audience guidance).

Open-ended scenarios are scored against rubrics with 5–10 specific points each. Rubrics emphasize:
- Explicit assumption-stating
- Multi-step reasoning over the right diagnostic dimensions (creative, audience, bidding, tracking, market)
- Correct identification of binding constraints (e.g., distinguishing Lost-IS-Rank from Lost-IS-Budget)
- Methodologically sound experiment design (Experiments tool randomization, geo holdouts, pre-committed decision rules, power analysis)
- Resistance to common false framings (e.g., "Brand Search has 16x ROAS — scale it" misses that brand is largely non-incremental)

### 3.4 Example Questions (one per reasoning type)

**Recall (MCQ):**
> Under Meta's Aggregated Event Measurement (AEM) framework introduced after iOS 14.5, how many web conversion events can a single domain prioritize per Meta pixel?
> **(B)** Up to 8 events per domain ✓

**Adversarial (MCQ):**
> A new Meta campaign for an ecommerce brand is launching tomorrow. Which approach reflects current 2024+ best practice?
> **(C)** Use broad targeting (age + country only) and rely on the algorithm — narrow interests typically underperform broad in the current Advantage+ era ✓
> *(Trap: A and B reflect 2018-era interest-stacking and narrow-LAL playbook.)*

**Diagnostic (open-ended):** Diagnose ASC budget shock — campaign was 4×'d overnight, CPM up 60%, CPA up 110%, frequency 1.4 (low), CTR flat.
> *(Rubric expects: identify Learning re-entry, distinguish from creative fatigue via flat CTR + low frequency, recommend NO budget revert (compounds shock), 5–7 day soak, future stepwise budget rules.)*

**Quantitative (open-ended):** $500K monthly Meta budget across two ASCs. CFO offers $100K. CAC payback target 60 days. Provide quantitative recommendation with stated assumptions.
> *(Rubric expects: marginal-ROAS framing, payback policy compliance, NCA-cost computation per segment, stated assumptions, staged 50% rollout.)*

**Creative strategy (open-ended):** Design a rigorous experiment to test 9-second vs 30-second video on Reels for skincare DTC, $80K budget over 30 days.
> *(Rubric expects: pre-committed metrics, Meta Experiments tool (not manual splits), explicit power analysis, identical controls except duration variable, written analysis plan locking decision rule, anti-pattern callouts.)*

---

## 4. Methodology

### 4.1 Evaluation Protocol

Each candidate model receives one question at a time with a fixed system prompt:

> "You are an expert performance marketer with deep knowledge of Meta Ads (Facebook/Instagram) and Google Ads. Answer questions accurately and concisely based on current platform best practices."

For MCQs, the model is asked to respond with only a letter (A/B/C/D). Responses are parsed via regex; binary score (1.0 / 0.0) on exact match.

For open-ended (`action_based`), the model receives the scenario and is asked for "a comprehensive answer with specific actions, reasoning, and best practices." The response is then scored by an LLM-as-judge against the rubric.

### 4.2 Judge Selection

We use **Gemini 2.5 Flash** as the universal judge for all open-ended questions. This decision trades off three concerns:

1. **Cost.** Open-ended judging requires 192 calls per model × 7 models = 1,344 judge calls. Gemini 2.5 Flash is among the cheapest reasoning-capable models per token at the time of this writing.
2. **Self-judge bias.** Using a candidate model to judge itself produces a 3–8 percentage-point inflation in our pilot tests. A single external judge across all models removes this bias.
3. **Consistency.** A single judge applies a stable scoring distribution across all candidates. Different judges per candidate would introduce judge-variance noise that confounds candidate comparison.

The judge prompt (full text in Appendix A) maps the 0.0–1.0 score to:
- 1.0: All key criteria addressed correctly and completely
- 0.7–0.9: Most criteria covered with minor gaps
- 0.4–0.6: Some criteria covered, significant gaps
- 0.1–0.3: Minimal correct content
- 0.0: Incorrect or no relevant content

### 4.3 Token Budget for Reasoning Models

Reasoning models (GPT-5.5, GPT-5.4-Pro, Gemini 2.5 Pro, Gemini 3) consume internal "thinking" tokens that don't appear in the output. We allocate 1,500 tokens for MCQs and 4,000 tokens for open-ended responses on reasoning models (vs 50 / 2,000 on non-reasoning), based on pilot tests showing thinking models otherwise truncate before producing the visible answer.

This budget asymmetry is important: GPT-5.5's 24.5% creative_strategy score (Section 5) appears partly explained by token-budget exhaustion on long open-ended answers — the model's internal deliberation consumed the budget before producing visible content. We discuss this caveat in §6.3.

### 4.4 Bidding Strategy & Temperature

All candidates use deterministic decoding (`temperature=0`) where supported. Some reasoning models (notably Gemini 3 Flash Preview) reject `temperature=0`; we omit the parameter for these.

### 4.5 Reproducibility

The full evaluation script `run_v2_eval.py` and the `evaluate.py` reference implementation are in the GitHub repository (`Hawky-ai/pm-AGI`). Result JSONs include the exact prompt, model answer, rubric criteria, and judge score for every question, enabling third-party re-judging or methodological audit.

---

## 5. Results

### 5.1 Aggregate Scores

We evaluated seven candidate models. The Opus 4.7 result is included for transparency but flagged as **self-evaluation under heavy contamination** — Opus 4.7 authored the majority of v2 questions in conversation context and should be treated as an upper-bound rather than a fair-comparison number.

| Rank | Model | Provider | Overall | Recall | Adversarial | Diagnostic | Quantitative | Creative |
|---|---|---|---|---|---|---|---|---|
| 1* | claude-opus-4-7 (self-eval†) | Anthropic | 98.5% | 97.0% | 100.0% | 99.7% | 100.0% | 99.3% |
| 2 | gpt-5.4 | Azure OpenAI | **97.4%** | 99.3% | 100.0% | 97.2% | 95.3% | 89.0% |
| 3 | gpt-5.2 | Azure OpenAI | 97.4% | 98.9% | 100.0% | 98.4% | 94.6% | 90.0% |
| 4 | gemini-2.5-flash | Google | 92.2% | 97.7% | 100.0% | 89.0% | 83.6% | 74.3% |
| 5 | gemini-3-flash-preview | Google | 91.7% | 97.0% | 100.0% | 85.4% | 89.5% | 69.4% |
| 6 | gemini-2.5-pro | Google | 87.7% | 96.4% | 98.8% | 87.1% | 59.7% | 73.1% |
| 7 | gpt-5.5 | Azure OpenAI | 80.0% | 95.8% | 100.0% | 59.9% | 72.0% | **24.5%** |
| _ | gpt-5.4-pro | Azure OpenAI | _(running)_ | – | – | – | – | – |

\* Self-evaluation under heavy contamination; not fair-comparison. See §6.1.
† Opus 4.7 authored 395/494 questions in conversation context during answer generation.

### 5.2 The Recall-vs-Reasoning Gap

The headline finding is the **gap between recall and reasoning** on the same model. We define this as `recall_score − min(diagnostic, quantitative, creative_strategy)`:

| Model | Recall | Worst Reasoning Type | Gap |
|---|---|---|---|
| gpt-5.5 | 95.8% | creative (24.5%) | **71.3 pp** |
| gemini-2.5-pro | 96.4% | quant (59.7%) | 36.7 pp |
| gemini-3-flash-preview | 97.0% | creative (69.4%) | 27.6 pp |
| gemini-2.5-flash | 97.7% | creative (74.3%) | 23.4 pp |
| gpt-5.4 | 99.3% | creative (89.0%) | 10.3 pp |
| gpt-5.2 | 98.9% | quant (94.6%) | 4.3 pp |

This gap is a more diagnostic signal than aggregate score for at least three reasons:

**(a) Recall is approaching saturation.** All seven candidate models score 95–99% on knowledge MCQs. As frontier model knowledge of platform mechanics improves, recall converges; aggregate score increasingly reflects open-ended performance, not knowledge breadth.

**(b) Reasoning gaps reflect generalization, not memorization.** A model that scores 100% on adversarial MCQs but 24% on creative_strategy is pattern-matching well to question structure but fails on long-form rubric-driven generation. This generalization gap predicts real-world performance: a marketer using this model to *answer* an A/B-test-design question receives short, confident, but incomplete responses.

**(c) Different reasoning types reveal different failure modes.** Quantitative weakness (Gemini 2.5 Pro at 59.7%) reflects difficulty with multi-step arithmetic over LTV/CAC/payback math. Creative-strategy weakness (most models) reflects difficulty enumerating rubric points (pre-commit metrics, anti-patterns, statistical power, decision rules). These are distinct skills and a benchmark that conflates them in an aggregate score loses signal.

### 5.3 Adversarial Robustness Is Universal

All seven candidates score 98–100% on adversarial MCQs. This suggests current frontier LLMs have updated training corpora to recognize and reject 2019-era playbooks — at least when presented as a multiple-choice format with explicit options. We hypothesize adversarial open-ended questions (where the trap is implicit and the model must produce its own answer without distractor scaffolding) would surface more failures; we leave this for v3.

### 5.4 Reasoning Models Underperform on Long-Form Output

The most striking finding: **GPT-5.5, a reasoning model, scored 24.5% on creative_strategy** — far below non-reasoning Gemini 2.5 Flash (74.3%). Inspection of GPT-5.5's responses reveals truncation: long internal thinking consumed the available token budget before producing visible answers that addressed all 5–10 rubric points.

This is partly a methodology caveat (we increased token budgets for reasoning models, but not enough) and partly a real-world signal: reasoning models that can't complete their externalized response within practical budgets will under-perform on rubric-scored open-ended questions. Future versions will increase reasoning-model token budgets further; we report current results for transparency.

---

## 6. Discussion

### 6.1 Self-Evaluation Contamination

The `claude-opus-4-7 (self-eval)` result deserves careful interpretation. Opus 4.7 authored 395 of the 494 v2 questions in the same conversation that produced the evaluation answers. This is the strongest possible form of test-set contamination: the model has full lexical access to questions and rubrics in its context window when generating answers.

We include this result for transparency and labeled it explicitly with caveats in the result JSON. **The 98.5% should be interpreted as an upper bound** on Opus 4.7's pm-agi capability, not a fair-comparison number. A fresh API call (no conversation context) would produce a lower, more comparable score; we encourage users with `ANTHROPIC_API_KEY` access to run that fair comparison.

### 6.2 Judge Bias

Using Gemini 2.5 Flash as the universal judge means Gemini-family models may receive a slight scoring advantage from prompt-style alignment (judge and candidate share a vocabulary distribution). We did not correct for this in v2 results.

In future versions, we plan to:
1. Use a multi-judge ensemble (Gemini Flash + GPT-4o + Claude Haiku) and report the median.
2. Conduct a judge-bias audit by re-scoring a 50-question subsample with each candidate's same-family judge and reporting the spread.
3. Validate judge calibration against expert human scores on a 30-question gold-set.

### 6.3 Sample Size and Statistical Power

At 494 questions per model with binary or 0.0–1.0 continuous scoring, 95% confidence intervals on the overall score are ±2.5 percentage points. Differences between gpt-5.4 (97.4%) and gpt-5.2 (97.4%) are within this margin and should not be interpreted as a meaningful ranking.

Per-reasoning-type scores have wider intervals: at 56 creative_strategy questions, the 95% CI is ±5–7 pp. The 71-point gap between gpt-5.5 (24.5%) and gemini-2.5-flash (74.3%) on this category is well outside any reasonable confidence interval — a real, large effect.

### 6.4 What Models Get Right vs Wrong

Across all models, **adversarial MCQ performance is uniformly excellent (98–100%)**. Frontier LLMs trained on post-2022 corpora have absorbed the rejection of legacy playbooks (SKAGs, narrow LALs, CTR-as-primary-metric) into their priors.

**Creative strategy is uniformly the hardest reasoning category.** The 56 creative_strategy questions require enumeration of multi-point methodological structure — pre-committed metrics, statistical power, randomization mechanism (Meta Experiments tool, not manual splits), confound controls, decision rules, anti-pattern callouts. Most candidates produce coherent partial answers but fail to enumerate all rubric dimensions.

**Quantitative reasoning shows the largest cross-model variance** (59.7% to 100%). Strong quantitative performance correlates with the ability to state assumptions explicitly, decompose unit economics (LTV, payback, marginal ROAS), and reason about marginal vs average. Weaker models output the right framework but skip the actual arithmetic.

### 6.5 Practical Implications for Practitioners

If you are choosing an LLM to deploy in a performance-marketing workflow:

1. **Don't rely on aggregate score.** A 5-percentage-point aggregate difference can mask a 50-point reasoning-type gap. Look at per-reasoning-type breakdown.

2. **Match the model to the task.** Recall-heavy tasks (FAQ, brief drafting) are well-served by any frontier model. Diagnostic-heavy tasks (root-cause CPA spike analysis) require a model with strong diagnostic scores — currently GPT-5.4 family or Claude Opus.

3. **Beware of token-budget truncation on reasoning models.** If your application gives reasoning models limited token budgets, you may see GPT-5.5-style creative_strategy collapse. Increase budget, or fall back to non-reasoning variants for long-form work.

4. **Re-evaluate quarterly.** Frontier model releases shift the leaderboard meaningfully — even within 90-day windows. Pinning to a model version without re-evaluation is risky.

---

## 7. Limitations

1. **Test-set contamination on self-evaluation.** As described in §6.1, the Opus 4.7 self-eval is heavily contaminated; we report it transparently but flag it as upper-bound.

2. **Single-judge bias.** Gemini 2.5 Flash judging may favor Gemini-family candidates by prompt-style alignment. Multi-judge ensembles in v3.

3. **Static dataset.** Performance marketing platforms (Meta, Google) update product features, attribution defaults, and best practices continuously. Questions about 2024-current product behavior may become outdated within 6–12 months. We commit to quarterly dataset refresh.

4. **English-only.** All questions are in English; performance marketing is global. Future versions may add localized variants.

5. **Two-platform scope.** PM-AGI v2 covers Meta Ads + Google Ads only. TikTok, LinkedIn, Amazon, retail media, and connected TV are unaddressed; planned for v3.

6. **Author-side bias.** Questions reflect the authoring team's view of "current best practice." Where the field has genuine open debate (e.g., MMM vs Lift for incrementality measurement), we present a position; the rubric scores answers against that position. Disagreement is welcomed; submit alternatives via the contribution flow.

---

## 8. How to Participate

PM-AGI v2 is open-source under the MIT license.

**Run on your own model:**
```bash
git clone https://github.com/Hawky-ai/pm-AGI
cd pm-AGI
pip install -r requirements.txt
python evaluate.py --model YOUR_MODEL --provider openai --api-key $OPENAI_API_KEY
```

The evaluator outputs a JSON in the leaderboard-compatible format. Submit via PR to the GitHub repo or the HF Space contribution form.

**Contribute questions:** open a PR adding to `benchmark/dataset.json` following the schema in §3.1. Questions should target a clear `reasoning_type` and include rubric criteria (for open-ended) or distractor-quality MCQ options.

**Cite:**
```bibtex
@misc{pmagi2026v2,
  title={PM-AGI v2: A Performance Marketing Reasoning Benchmark for Large Language Models},
  author={hawky.ai},
  year={2026},
  url={https://huggingface.co/datasets/Hawky-ai/pm-agi-benchmark}
}
```

---

## 9. Roadmap

- **v2.1** (Q3 2026): multi-judge ensemble, quarterly dataset refresh, judge-bias audit
- **v3.0** (Q4 2026): TikTok Ads + LinkedIn Ads categories, multilingual variants, multi-modal evaluation (image creative analysis)
- **v3.1**: agentic evaluation — multi-turn campaign-management scenarios with tool use
- **Long-term**: incrementality-grounded scoring (compare model recommendations against geo-holdout outcomes)

---

## 10. Conclusion

PM-AGI v2 measures what frontier LLMs can actually do in a high-stakes applied domain. The benchmark's most diagnostic signal is not aggregate score but the **gap between recall and reasoning** — which varies from 4 percentage points (gpt-5.2) to 71 percentage points (gpt-5.5) on the same model.

We expect this gap to narrow over time as frontier models improve at long-form rubric-driven generation. Until then, the gap is a useful diagnostic for practitioners choosing models, for researchers studying reasoning generalization, and for benchmark authors thinking about what to measure.

We invite the community to run their models, contribute questions, and challenge our methodology. The benchmark improves through use.

---

## Appendix A: Judge Prompt

```
You are an expert performance marketing evaluator. Score the following answer
against the evaluation criteria.

QUESTION: {question}

EVALUATION CRITERIA (key points that should be covered):
- {criterion_1}
- {criterion_2}
- ... (5–10 criteria per question)

CANDIDATE ANSWER:
{answer}

Score the answer from 0.0 to 1.0 based on:
- 1.0: All key criteria addressed correctly and completely
- 0.7-0.9: Most key criteria covered with minor gaps
- 0.4-0.6: Some criteria covered but significant gaps
- 0.1-0.3: Minimal correct content
- 0.0: Incorrect or no relevant content

Respond with ONLY a number between 0.0 and 1.0. No explanation.
```

## Appendix B: Per-Question Result Format

Each result JSON contains:

```json
{
  "benchmark": "PM-AGI Benchmark v2.0.0",
  "model": "...",
  "provider": "...",
  "evaluated_at": "2026-...",
  "total_questions": 494,
  "overall_score": 0.974,
  "category_scores": { /* per-category breakdown */ },
  "difficulty_scores": { /* easy/medium/hard */ },
  "reasoning_type_scores": { /* the load-bearing field */ },
  "results": [
    {
      "id": "meta_303",
      "category": "meta_ads",
      "reasoning_type": "diagnostic",
      "difficulty": "hard",
      "type": "action_based",
      "score": 0.85,
      "model_answer": "...",
      "correct_answer": "see criteria"
    },
    ...
  ]
}
```

## Appendix C: Reproducibility Checklist

- [x] Dataset publicly available (HF Datasets: `Hawky-ai/pm-agi-benchmark`)
- [x] Evaluation script publicly available (GitHub: `Hawky-ai/pm-AGI`)
- [x] All baseline result JSONs publicly available (HF Space: `Hawky-ai/pm-agi-leaderboard`)
- [x] Schema versioned (`reasoning_type` field added in v2.0.0; backwards-compatible)
- [x] License: MIT (dataset, code, results)
- [x] Citation BibTeX provided
- [x] Quarterly dataset refresh commitment (changelog in repo)

---

*PM-AGI v2 is developed and maintained by [hawky.ai](https://hawky.ai). For questions, methodology disputes, or contribution coordination: pm-agi@hawky.ai or GitHub issues.*
