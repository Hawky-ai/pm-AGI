# PM-AGI v2: What Marketing Leaders Need to Know

**Hawky.ai · 2026 · Executive Brief**

---

## The headline

LLMs are now embedded in nearly every performance marketing workflow — analysis, troubleshooting, A/B test design, budget conversations with finance. **The model you choose meaningfully shapes the recommendations your team produces.** Yet existing benchmarks (MMLU, GSM8K, HumanEval) measure capabilities orthogonal to performance marketing: knowledge breadth, math, code. They don't tell you whether a model will recommend cutting Brand Search at 18× ROAS (the wrong call) or maintain it at impression-share-defense level (the right call).

**PM-AGI v2 measures exactly the reasoning your team needs.** We tested 7 frontier models across 494 expert-crafted questions in five reasoning categories. The findings have direct implications for which model to deploy, where, and what to expect.

---

## What we found

### 1. Aggregate scores are misleading

The headline number ("Model X scored 92%") hides where models actually struggle. We split the benchmark into five reasoning categories and surface the gap.

The same model can score:
- **95–99% on knowledge questions** (platform mechanics, best practices)
- **24–95% on creative strategy questions** (A/B test design, experiment methodology)

That gap is the load-bearing signal. A 5-point aggregate difference between models can mask a 50-point gap in the reasoning your team relies on.

### 2. The leaderboard (top 6 fair-comparison models)

| Rank | Model | Overall | Where It Wins | Where It Struggles |
|---|---|---|---|---|
| 1 | **GPT-5.4** | 97.4% | Diagnostic (97%), Quant (95%) | Creative strategy (89%) |
| 2 | **GPT-5.2** | 97.4% | Diagnostic (98%), Quant (95%) | Creative strategy (90%) |
| 3 | **Gemini 2.5 Flash** | 92.2% | Adversarial (100%) | Quant (84%), Creative (74%) |
| 4 | **Gemini 3 Flash Preview** | 91.7% | Adversarial (100%) | Creative strategy (69%) |
| 5 | **Gemini 2.5 Pro** | 87.7% | Adversarial (99%) | **Quantitative (60%)** |
| 6 | **GPT-5.5** | 80.0% | Adversarial (100%) | **Creative strategy (24.5%)** |

GPT-5.5 is a thinking model with token-budget collapse on long-form rubric questions — a real-world warning, not just a benchmark artifact. (Details in the technical whitepaper.)

### 3. Adversarial robustness is now table-stakes

All 7 frontier models score 98–100% on adversarial trap questions — the ones that test rejection of outdated 2019-era playbooks (SKAGs, narrow lookalikes, "always optimize on CTR"). This means: if your team is using *any* current frontier model, you can stop worrying about old-playbook contamination. That's a real win for the field over the past 24 months.

### 4. Creative strategy is uniformly the hardest category

Our 56 creative-strategy questions ask models to design rigorous experiments — pre-committed metrics, statistical power, randomization mechanism, decision rules, anti-pattern callouts. Even GPT-5.4 only hits 89%; weaker models drop to 24%.

**What this means for you:** if your team uses LLMs to design A/B tests or experiment methodology, you're in the area where models struggle most. Validate model output against a methodology checklist; don't accept "looks reasonable" without explicit assumption-stating, decision rules, and confound controls.

---

## What this means for you, in three decisions

### Decision 1: Which model to deploy in your team's daily workflow

**For mixed analytical work (root-cause analysis, optimization recommendations, copy):** GPT-5.4 family. Highest aggregate, narrowest gaps, robust across all reasoning types.

**For cost-sensitive volume work (FAQ, brief generation, routine reporting):** Gemini 2.5 Flash. 92% aggregate at fraction of the cost.

**Avoid for unstructured open-ended tasks:** GPT-5.5 in default token budgets. It's a strong reasoning model but consumes its token budget on internal deliberation, leaving truncated output. Use only with extended budgets or for short-form work.

### Decision 2: How to validate LLM-generated marketing recommendations

The recall-vs-reasoning gap means: confident-sounding model outputs may be 95% right (recall) or 25% right (creative strategy) on the same conversation. Build a habit of:

1. **Always ask "what's the metric, and how would we measure incrementality?"** Most models miss this on first pass; the strong ones add it on prompt.
2. **Demand stated assumptions.** Strong models say "assuming marginal ROAS at 80% of average and stable CPA targets…". Weaker models just give an answer.
3. **Look for anti-pattern callouts.** Strong models proactively flag what NOT to do ("don't read this test before day 14, don't optimize one cell more than the other"). Weaker models skip this.
4. **Reject recommendations without decision rules.** "Lower tROAS" is incomplete. "Lower tROAS by 10–15% per change with 7-day soak between, monitoring volume, hold for 14 days before deciding" is a complete recommendation.

### Decision 3: How to use this benchmark internally

If you're a CMO evaluating an internal AI initiative or a vendor pitching an LLM-powered product:

1. **Ask which models they use, and run the benchmark against them.** It's free and takes ~2 hours per model with the open-source evaluator.
2. **Look at per-category scores, not aggregates.** A 90% aggregate with 24% on creative strategy is fundamentally different from 90% with 80% on creative strategy.
3. **Re-evaluate quarterly.** Frontier models ship new versions every ~90 days. Pinning to a model without re-evaluation is risky.

---

## How to read the leaderboard responsibly

**What the score IS:** the proportion of questions the model answers correctly (MCQs) or the average rubric-score the LLM judge assigns (open-ended).

**What the score is NOT:** a measure of business outcomes. A model that scores 97% may produce recommendations that, when implemented, lose money — because real-world deployment depends on prompt design, output validation, and decision-making process around the model.

**Confidence intervals:** at 494 questions, overall scores have ±2.5pp 95% confidence intervals. A 1-2 point difference between models is likely noise. Differences ≥5pp are meaningful.

**Self-evaluation caveat:** the Claude Opus 4.7 result (98.5%) is a self-evaluation produced under heavy test contamination — Opus authored 80% of the v2 questions in the same conversation that produced the answers. We report it transparently and label it; treat it as upper-bound, not a fair comparison.

---

## What's next

PM-AGI v2 is open-source under the MIT license. It's hosted at:

- **Dataset:** [huggingface.co/datasets/Hawky-ai/pm-agi-benchmark](https://huggingface.co/datasets/Hawky-ai/pm-agi-benchmark)
- **Live leaderboard:** [huggingface.co/spaces/Hawky-ai/pm-agi-leaderboard](https://huggingface.co/spaces/Hawky-ai/pm-agi-leaderboard)
- **Code & contribution flow:** [github.com/Hawky-ai/pm-AGI](https://github.com/Hawky-ai/pm-AGI)

We commit to:
- **Quarterly dataset refresh** as platforms update product features
- **v3 expansion:** TikTok Ads + LinkedIn Ads + multimodal (image/video creative analysis)
- **Multi-judge ensemble** to reduce single-judge bias
- **Annual partner audit** with industry CMOs and ML researchers

If your organization wants to:
- Run the benchmark on a custom or fine-tuned model
- Contribute questions specific to your category or geography
- Co-author the v3 expansion

…reach out: pm-agi@hawky.ai

---

*Built by [hawky.ai](https://hawky.ai) — performance marketing AI, made measurable.*
