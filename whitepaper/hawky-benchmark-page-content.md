# hawky.ai/benchmark — Page Content & Structure

**Purpose:** marketing landing page for PM-AGI v2 benchmark. Audience: marketers, ML engineers, CMOs evaluating AI products. The leaderboard itself lives on the HF Space; this page is the **brand front door** that drives traffic to the leaderboard, dataset, and whitepaper.

This document provides copy + structure + design direction. Your designer can lay it out in any framework (Next.js, Astro, Webflow, plain HTML).

**Suggested URL:** `hawky.ai/benchmark` (or `pm-agi.hawky.ai`)

**Suggested page length:** ~1,800 words (3-4 minute read), single scrolling landing page.

---

## SECTION 1 — HERO

**Layout:** Full-width hero, dark gradient background (matching HF Space header colors `#1e3a8a → #2563eb`). Centered content, max-width 800px.

**Eyebrow (small, uppercase, letter-spaced):**
> AN OPEN BENCHMARK BY HAWKY.AI

**Headline (large, bold, ~48-64px):**
> The first reasoning benchmark for performance marketing AI.

**Subheadline (~20px, lighter weight):**
> 494 expert questions. 5 reasoning categories. 7 frontier models tested. The recall-vs-reasoning gap reveals what your AI actually knows — and where it fails.

**Primary CTA button:** "View live leaderboard →" (links to HF Space)
**Secondary CTA button (text link):** "Read the whitepaper" (links to PDF/markdown)

**Beneath CTAs — three stat chips on a row:**
- `494` Expert Questions
- `7` Models Tested
- `5` Reasoning Categories

**Visual:** subtle animated graph/grid background, or a small isometric illustration suggesting "benchmark / leaderboard." Don't overdesign — the headline is the hero.

---

## SECTION 2 — WHY THIS MATTERS

**Layout:** 2-column on desktop, stacked on mobile. Left: heading + body. Right: a single illustrative chart or quote block.

**Heading:**
> Why "smart AI" doesn't mean "good marketing AI"

**Body (3 paragraphs, ~150 words):**

When you choose an LLM for your marketing team, you probably look at MMLU, GSM8K, or "AI rankings" articles. Those benchmarks measure general knowledge, math, and code — not whether a model understands attribution windows, brand-search incrementality, or how to design an A/B test that survives auction overlap.

A model can score 95% on MMLU and still recommend doubling Brand Search budget at 18× ROAS — a classic non-incremental trap that destroys capital. We've seen models confidently propose "switch to Last-Click attribution for cleanest reporting" — exactly the wrong move for a brand investing in upper-funnel.

PM-AGI is the benchmark we built to measure what actually matters: **the reasoning your team relies on every day.**

**Right column (chart placeholder):** a simple horizontal bar chart showing the recall-vs-reasoning gap for one or two named models, with a callout. Example:

```
GPT-5.5
  Recall (knowledge MCQs)        ████████████████████  95.8%
  Creative strategy (open-ended) ███                   24.5%
  ↑ a 71-point gap on the same model
```

Caption beneath: "Aggregate scores hide where models actually break."

---

## SECTION 3 — THE FIVE REASONING CATEGORIES

**Layout:** 5 stacked cards or a horizontal scroll. Each card: icon, title, description, sample question, what strong models do.

**Section heading:**
> What we measure

**Subhead:**
> PM-AGI v2 splits performance-marketing reasoning into five distinct skills — each tested separately, each scored independently.

### Card 1 — RECALL
- **Icon:** book / brain
- **Title:** Knowledge Recall
- **Subtitle:** Platform mechanics, current best practices
- **Description:** Tests whether the model knows how Meta and Google Ads actually work today. AEM event limits, tROAS Learning Phase mechanics, attribution defaults.
- **Sample:** *"Under Meta's AEM framework introduced after iOS 14.5, how many web conversion events can a single domain prioritize?"*
- **Strong models:** 95-99%. This category is approaching saturation across frontier LLMs.

### Card 2 — ADVERSARIAL
- **Icon:** shield / target
- **Title:** Adversarial / Trap Questions
- **Subtitle:** Resistance to outdated 2019-era playbooks
- **Description:** Tests whether the model rejects obsolete advice that still pattern-matches in older training data — SKAGs, narrow lookalike stacking, "always optimize CTR".
- **Sample:** *"Should you stack 5–7 detailed interest audiences in one ad set to maximize specificity?"* (correct answer: no — broad targeting outperforms in the modern Advantage+ era)
- **Strong models:** 98-100%. Frontier LLMs have updated training corpora.

### Card 3 — DIAGNOSTIC
- **Icon:** stethoscope / search
- **Title:** Diagnostic Reasoning
- **Subtitle:** Multi-step root-cause analysis
- **Description:** Given anomalous campaign data (CPA spike, ROAS drop, tracking weirdness), reason through audience, creative, bidding, and tracking causes to identify the actual root cause.
- **Sample:** *"ASC budget was raised 4× overnight. Within 36 hours: CPM up 60%, CPA up 110%, frequency 1.4 (low), CTR flat. Diagnose."* (correct: budget shock + Learning re-entry, NOT creative fatigue)
- **Strong models:** 87-99%. Top models excel at distinguishing fatigue from budget shock; weak models conflate them.

### Card 4 — QUANTITATIVE
- **Icon:** calculator / chart
- **Title:** Quantitative Tradeoffs
- **Subtitle:** Budget allocation, math, stated assumptions
- **Description:** Multi-step quantitative reasoning over LTV, CAC payback, marginal ROAS, channel-mix decisions. Strong models state their assumptions; weak models skip the arithmetic.
- **Sample:** *"$500K Meta budget across two ASCs. CFO offers $100K. CAC payback target 60 days. Provide quantitative recommendation with stated assumptions."*
- **Strong models:** 95-100%. Largest cross-model variance: Gemini 2.5 Pro drops to 60% on this category.

### Card 5 — CREATIVE STRATEGY
- **Icon:** lightbulb / palette
- **Title:** Creative & Experiment Design
- **Subtitle:** A/B test methodology, experiment rigor
- **Description:** Design rigorous experiments — pre-committed metrics, statistical power, randomization, decision rules. The hardest category for every frontier LLM.
- **Sample:** *"Design an experiment to test 9-second vs 30-second video on Reels. Brand: skincare DTC. Budget: $80K over 30 days."*
- **Strong models:** 89-99%. Creative strategy is the load-bearing reasoning category in production deployments.

---

## SECTION 4 — LIVE LEADERBOARD PREVIEW

**Layout:** Embed an iframe of the HF Space, OR build a static preview with link to live version. Recommended: static preview that always shows current top 5, with "view full leaderboard →" linking to HF.

**Section heading:**
> Live results from 7 frontier models

**Subhead:**
> Tested on Azure OpenAI (GPT-5.x family), Google (Gemini 2.5 + 3 family), and Anthropic (self-eval, with explicit caveats).

### Top of leaderboard (static preview)

| # | Model | Provider | Overall | Best Category | Worst Category |
|---|---|---|---|---|---|
| 1 | **GPT-5.4** | Azure OpenAI | 97.4% | Recall (99.3%) | Creative (89.0%) |
| 2 | GPT-5.2 | Azure OpenAI | 97.4% | Recall (98.9%) | Creative (90.0%) |
| 3 | Gemini 2.5 Flash | Google | 92.2% | Adversarial (100%) | Creative (74.3%) |
| 4 | Gemini 3 Flash Preview | Google | 91.7% | Adversarial (100%) | Creative (69.4%) |
| 5 | Gemini 2.5 Pro | Google | 87.7% | Adversarial (98.8%) | **Quant (59.7%)** |

**Below table:** "View full leaderboard with reasoning-type breakdowns and submit your own model →" [Button → HF Space]

**Design direction:** the table should be visually scannable — bold the Overall column, color-code the worst-category cell (red for <70%, yellow for 70–85%, green for 85%+).

---

## SECTION 5 — THE HEADLINE FINDING

**Layout:** Full-width section with a bold visual quote/finding. Centered, max-width ~700px.

**Section heading:** (small, uppercase)
> THE LOAD-BEARING INSIGHT

**Pull quote / finding (large, bold):**
> The same frontier model can score 95% on knowledge questions and 24% on creative-strategy questions.

**Below in body text:**
> Aggregate benchmark scores hide where models actually break. The recall-vs-reasoning gap is the diagnostic signal that matters. We measure it for every model on the leaderboard.

**Suggested visual:** a stylized horizontal bar chart showing the gap visually for 2-3 named models. The visual is the headline.

---

## SECTION 6 — METHODOLOGY HIGHLIGHTS

**Layout:** 3-column on desktop. Each column: icon + ~50-word block.

**Section heading:**
> Built for rigor, open for replication

### Column 1 — Expert-crafted dataset
494 questions authored by performance marketing professionals. Each open-ended question has a 5-10 point rubric. Adversarial questions specifically target outdated playbooks. Fully versioned, MIT-licensed, on Hugging Face.

### Column 2 — Single-judge consistency
Open-ended responses scored by Gemini 2.5 Flash as the universal judge — same judge across all candidates. Eliminates self-judge bias and ensures fair cross-model comparison. Multi-judge ensemble planned for v3.

### Column 3 — Reproducible & transparent
All 494 questions, all 7 result JSONs, all judge prompts, all scoring rubrics are public. Run the eval on your own model in ~30 min via the open-source `evaluate.py`. Submit your results via PR.

**Below the columns, a small links row:**
[GitHub Repository] [Dataset on HF] [Live Leaderboard] [Whitepaper PDF]

---

## SECTION 7 — RUN ON YOUR OWN MODEL

**Layout:** Code block + 3 steps. Centered, mono-spaced for the code.

**Section heading:**
> Test your model in 30 minutes

**Step 1 — Clone the repo:**
```bash
git clone https://github.com/Hawky-ai/pm-AGI
cd pm-AGI && pip install -r requirements.txt
```

**Step 2 — Run the eval:**
```bash
python evaluate.py \
  --model YOUR_MODEL \
  --provider openai \
  --api-key $OPENAI_API_KEY
```

**Step 3 — Submit your result:**
> Result JSON saves to `results/`. Submit via PR or the HF Space form. Approved results appear on the live leaderboard within 24h.

**CTA button:** "Get started on GitHub →"

---

## SECTION 8 — WHO IT'S FOR

**Layout:** 3 cards, equal width. Personas + value prop.

**Section heading:**
> Who PM-AGI is for

### For ML Researchers & Engineers
- A new domain-specific reasoning benchmark covering adversarial robustness, multi-step diagnostic, quantitative tradeoffs, and experiment-design rigor.
- Citable evaluation; reproducible methodology; per-question result JSONs for re-judging.
- Fills the gap left by general-purpose benchmarks like MMLU and HumanEval.

### For CMOs & Marketing Leaders
- Vendor-neutral evidence on which AI models actually understand performance marketing.
- A framework for evaluating LLM-powered marketing tools your team or vendors propose.
- Quarterly refresh — current with platform updates.

### For Product Teams Building AI Marketing Tools
- A standardized way to demonstrate your model's capability to enterprise customers.
- Run on your fine-tuned or in-house model; appear on the leaderboard.
- A way to track progress over time as you improve your model.

---

## SECTION 9 — FREQUENTLY ASKED QUESTIONS

**Layout:** Collapsed accordions, click-to-expand.

### Q: Why isn't Claude on the leaderboard?
A: Claude was self-evaluated under heavy contamination — the same Claude Opus 4.7 model that authored 80% of v2 questions. We report it transparently as a self-eval (98.5% with caveats) but treat it as upper-bound, not fair-comparison. We invite the community to run a fair Claude evaluation; we'll add it to the leaderboard.

### Q: How do you prevent test-set contamination on future model releases?
A: Quarterly dataset refresh + a held-out v3 question set will be used after each major model release. We also publish dataset diffs so the community can verify what's been added.

### Q: Why Gemini 2.5 Flash as judge — won't it favor Gemini candidates?
A: Possibly a small bias. We chose it for cost and consistency. v3 will use a multi-judge ensemble (Gemini Flash + GPT-4o + Claude Haiku) and report the median.

### Q: Can I trust a 1-point difference on the leaderboard?
A: No. 95% confidence interval on overall scores is ±2.5 percentage points. Treat differences <5pp as ties.

### Q: How do I contribute questions?
A: Open a PR to `benchmark/dataset.json` on the GitHub repo. Each question needs: hypothesis (what it tests), rubric (for open-ended), or distractor-quality MCQ options.

### Q: Will pm-agi expand beyond Meta + Google?
A: Yes, in v3 (Q4 2026): TikTok Ads, LinkedIn Ads, retail media. Reach out if you want to co-author specific platform expansions.

### Q: Do you offer enterprise consulting?
A: Hawky.ai offers AI strategy consulting for performance marketing teams. The benchmark is open-source; consulting helps you operationalize what it reveals. Email pm-agi@hawky.ai.

---

## SECTION 10 — FOOTER CTA

**Layout:** Full-width, dark background, centered.

**Headline:** Ready to test your AI?

**Two buttons:**
- Primary: "View live leaderboard" → HF Space
- Secondary: "Read the whitepaper" → PDF link

**Below buttons (small text):** "MIT License · Open Source · pm-agi@hawky.ai"

---

## SECTION 11 — STANDARD FOOTER

Standard hawky.ai footer with:
- Logo + tagline
- Navigation: Product, Pricing, Benchmark, Docs, Blog, About, Contact
- Social links: GitHub, Twitter/X, LinkedIn
- Legal: Privacy, Terms, Cookies
- Copyright

---

# Design Direction Summary

**Tone:** Confident, evidence-based, slightly rigorous. Not hype-y. Not academic-dry. Think: Stripe documentation meets a16z thesis writeup.

**Color palette suggestion:**
- Primary: deep blue (#1e3a8a) → bright blue (#2563eb) — matches the HF Space header
- Accent: amber/gold for callouts and "the gap" visualizations
- Neutral: warm white (#fafafa), text dark (#111827)
- Use red sparingly (only for "low scores" or warnings)

**Typography:**
- Headlines: a strong sans-serif — Inter Display, Söhne, or similar
- Body: Inter or System default
- Code blocks: JetBrains Mono or system mono
- Avoid serifs unless used for emphasis quotes

**Visual elements:**
- The recall-vs-reasoning gap chart is the signature visual. Use it twice: once in the hero/section 2, once in section 5.
- Avoid stock photos. Use simple geometric illustrations or data-as-visual (chart elements as decoration).
- Generous whitespace. Section padding ≥120px desktop, ≥80px mobile.

**Animation:**
- Subtle entrance fades on scroll.
- The hero number stats can count up on first view.
- Bar charts can animate in on scroll.
- Don't over-animate; rigor is the brand voice.

**Mobile:**
- All multi-column sections should stack on mobile.
- Hero headline should remain prominent on mobile (don't shrink below 36px).
- The leaderboard table should scroll horizontally on mobile (don't truncate).

**Performance:**
- Static page (no client-side rendering for content). Next.js with SSG, Astro, or Webflow.
- Total page weight target: <500KB transferred.
- Lighthouse performance score target: 95+.

**SEO:**
- Title: "PM-AGI Benchmark — Performance Marketing AI Reasoning Test | hawky.ai"
- Meta description: "The first open benchmark for evaluating AI on performance marketing reasoning. 494 expert questions across Meta + Google Ads. See how GPT, Gemini, and Claude rank."
- Open Graph image: a screenshot of the leaderboard with the recall-vs-reasoning gap chart visible.

**Accessibility:**
- WCAG 2.1 AA minimum. Color contrast checked. Keyboard navigation works. Alt text on all visuals.

---

## Asset Production Checklist for Designer

- [ ] Hero illustration (subtle, geometric — not figurative)
- [ ] OG / social share image (1200×630 PNG)
- [ ] Favicon
- [ ] Recall-vs-reasoning gap chart (production version, not the ASCII placeholder)
- [ ] 5 category icons (recall / adversarial / diagnostic / quantitative / creative)
- [ ] Provider logos (OpenAI, Google, Anthropic) for the leaderboard preview
- [ ] Whitepaper PDF (use the existing markdown source, render with a clean PDF style)

---

## Content Gaps / Followups

After launch, consider adding:
- **Industry-specific verticals page:** "/benchmark/saas", "/benchmark/dtc-ecommerce" with the 50 most-relevant questions per vertical.
- **Model spotlight blog posts:** "Why GPT-5.5 collapses on creative strategy" — deep dive into specific findings.
- **Quarterly refresh announcement page:** changelog of dataset updates.
- **Methodology video** (5-min explainer with the founder/lead researcher walking through the recall-vs-reasoning gap).
- **Case study:** a brand that switched models based on PM-AGI findings and saw measurable improvement.

These are content marketing assets, not core launch requirements.

---

*All copy in this document is authored content for hawky.ai/benchmark. Designer is free to adapt headlines, restructure sections, and tighten copy as needed for design constraints. The structure and core findings should remain intact.*
