"""
PM-AGI Leaderboard — hawky.ai
Performance Marketing LLM Benchmark
"""

import json
import os
from pathlib import Path

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ─── Paths ────────────────────────────────────────────────────────────────────
RESULTS_DIR = Path(__file__).parent / "results"
DATASET_PATH = Path(__file__).parent / "benchmark" / "dataset.json"

# ─── Constants ────────────────────────────────────────────────────────────────
PROVIDER_COLORS = {
    "OpenAI":      "#10a37f",
    "Anthropic":   "#c96442",
    "Google":      "#4285F4",
    "Meta":        "#1877F2",
    "Mistral AI":  "#6B46C1",
    "DeepSeek":    "#0EA5E9",
    "Other":       "#6B7280",
}

PROVIDER_LOGOS = {
    "OpenAI":    "🟢",
    "Anthropic": "🟠",
    "Google":    "🔵",
    "Meta":      "🔷",
    "Mistral AI":"🟣",
    "DeepSeek":  "🩵",
    "Other":     "⚪",
}

CATEGORY_LABELS = {
    "meta_ads":          "Meta Ads",
    "google_ads":        "Google Ads",
    "critical_thinking": "Critical Thinking",
    "action_based":      "Action-Based",
}

SUBCATEGORY_GROUPS = {
    "Meta Ads": [
        "campaign_structure", "audience_targeting", "bidding_strategy",
        "creative_performance", "measurement", "advantage_plus"
    ],
    "Google Ads": [
        "quality_score", "smart_bidding", "performance_max",
        "keyword_strategy", "attribution"
    ],
    "Critical Thinking": [
        "data_interpretation", "budget_allocation", "competitive_analysis"
    ],
    "Action-Based": [
        "campaign_optimization", "troubleshooting",
        "scaling_decisions", "reporting_insights"
    ],
}

SUBCATEGORY_LABELS = {
    "campaign_structure":   "Campaign Structure",
    "audience_targeting":   "Audience Targeting",
    "bidding_strategy":     "Bidding Strategy",
    "creative_performance": "Creative Performance",
    "measurement":          "Measurement & CAPI",
    "advantage_plus":       "Advantage+ / AI",
    "quality_score":        "Quality Score",
    "smart_bidding":        "Smart Bidding",
    "performance_max":      "Performance Max",
    "keyword_strategy":     "Keyword Strategy",
    "attribution":          "Attribution",
    "data_interpretation":  "Data Interpretation",
    "budget_allocation":    "Budget Allocation",
    "competitive_analysis": "Competitive Analysis",
    "campaign_optimization":"Campaign Optimization",
    "troubleshooting":      "Troubleshooting",
    "scaling_decisions":    "Scaling Decisions",
    "reporting_insights":   "Reporting & Insights",
}

CT_DIRECTION = {
    "data_interpretation": {
        "label": "Data Interpretation",
        "description": "Can the model read performance data, identify trends, and draw correct conclusions from metrics like CPA, ROAS, CTR, CPM, and conversion rate changes?",
        "strong_signal": "Strong models diagnose anomalies, separate signal from noise, and avoid premature conclusions.",
        "weak_signal": "Weaker models react to surface metrics without checking tracking, seasonality, or external causes.",
        "icon": "📊"
    },
    "budget_allocation": {
        "label": "Budget Allocation",
        "description": "Can the model make sound decisions about how to distribute budget across channels, campaigns, and time periods — balancing efficiency, scale, and growth?",
        "strong_signal": "Strong models understand marginal efficiency, channel interdependency, and LTV-based CPA targets.",
        "weak_signal": "Weaker models chase high ROAS and cut upper-funnel spend, undermining long-term growth.",
        "icon": "💰"
    },
    "competitive_analysis": {
        "label": "Competitive Analysis",
        "description": "Can the model interpret competitive signals (Auction Insights, Ad Library, CPM spikes) and respond strategically without overreacting?",
        "strong_signal": "Strong models identify root causes and respond with Quality Score improvement and surgical keyword defense.",
        "weak_signal": "Weaker models react emotionally, recommend blind bid increases, or ignore competitive context entirely.",
        "icon": "🏁"
    },
}

MEDALS = {0: "🥇", 1: "🥈", 2: "🥉"}

# ─── Data Loading ─────────────────────────────────────────────────────────────

def load_results() -> list[dict]:
    results = []
    if not RESULTS_DIR.exists():
        return results
    for f in sorted(RESULTS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            if "example_" not in f.name:
                results.append(data)
        except Exception:
            pass
    return sorted(results, key=lambda x: x.get("overall_score", 0), reverse=True)


# ─── Build Tables ─────────────────────────────────────────────────────────────

def build_main_df(results: list) -> pd.DataFrame:
    rows = []
    for i, r in enumerate(results):
        cat = r.get("category_scores", {})
        diff = r.get("difficulty_scores", {})
        provider = r.get("provider", "Other")
        logo = PROVIDER_LOGOS.get(provider, "⚪")
        rows.append({
            "Rank":              MEDALS.get(i, f"#{i+1}"),
            "Model":             r.get("model", "Unknown"),
            "Provider":          f"{logo} {provider}",
            "Overall ↑":         f"{r.get('overall_score',0)*100:.1f}%",
            "Meta Ads":          f"{cat.get('meta_ads',{}).get('score',0)*100:.1f}%",
            "Google Ads":        f"{cat.get('google_ads',{}).get('score',0)*100:.1f}%",
            "Critical Thinking": f"{cat.get('critical_thinking',{}).get('score',0)*100:.1f}%",
            "Action-Based":      f"{cat.get('action_based',{}).get('score',0)*100:.1f}%",
            "Easy":              f"{diff.get('easy',{}).get('score',0)*100:.1f}%",
            "Hard":              f"{diff.get('hard',{}).get('score',0)*100:.1f}%",
        })
    return pd.DataFrame(rows)


# ─── Charts ───────────────────────────────────────────────────────────────────

def chart_overall(results: list):
    models  = [r["model"] for r in results]
    scores  = [round(r["overall_score"] * 100, 1) for r in results]
    colors  = [PROVIDER_COLORS.get(r.get("provider","Other"), "#6B7280") for r in results]

    fig = go.Figure(go.Bar(
        x=scores, y=models, orientation="h",
        marker_color=colors,
        text=[f"{s}%" for s in scores],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Score: %{x}%<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text="Overall PM-AGI Score by Model", font=dict(size=16)),
        xaxis=dict(title="Score (%)", range=[0, 105], gridcolor="#f0f0f0"),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=60, t=50, b=40),
        height=380,
        font=dict(family="Inter, sans-serif", size=12),
    )
    return fig


def chart_category_radar(results: list, selected_models: list):
    categories = ["Meta Ads", "Google Ads", "Critical Thinking", "Action-Based"]
    cat_keys   = ["meta_ads", "google_ads", "critical_thinking", "action_based"]

    fig = go.Figure()
    for r in results:
        if r["model"] not in selected_models:
            continue
        scores = [round(r.get("category_scores",{}).get(k,{}).get("score",0)*100, 1) for k in cat_keys]
        scores += [scores[0]]
        cats_closed = categories + [categories[0]]
        color = PROVIDER_COLORS.get(r.get("provider","Other"), "#6B7280")
        fig.add_trace(go.Scatterpolar(
            r=scores, theta=cats_closed,
            fill="toself", name=r["model"],
            line=dict(color=color, width=2),
            fillcolor=color.replace(")", ",0.1)").replace("rgb","rgba") if "rgb" in color else color + "22",
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100], gridcolor="#e5e7eb")),
        title=dict(text="Category Radar — Model Comparison", font=dict(size=15)),
        showlegend=True,
        legend=dict(x=1.05, y=1),
        paper_bgcolor="white",
        height=420,
        font=dict(family="Inter, sans-serif"),
        margin=dict(l=40, r=120, t=60, b=40),
    )
    return fig


def chart_difficulty(results: list):
    models   = [r["model"] for r in results]
    easy     = [round(r.get("difficulty_scores",{}).get("easy",{}).get("score",0)*100,1) for r in results]
    medium   = [round(r.get("difficulty_scores",{}).get("medium",{}).get("score",0)*100,1) for r in results]
    hard     = [round(r.get("difficulty_scores",{}).get("hard",{}).get("score",0)*100,1) for r in results]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="🟢 Easy",   x=models, y=easy,   marker_color="#22c55e"))
    fig.add_trace(go.Bar(name="🟡 Medium", x=models, y=medium, marker_color="#f59e0b"))
    fig.add_trace(go.Bar(name="🔴 Hard",   x=models, y=hard,   marker_color="#ef4444"))
    fig.update_layout(
        barmode="group",
        title=dict(text="Score by Difficulty Level", font=dict(size=15)),
        xaxis=dict(tickangle=-25),
        yaxis=dict(title="Score (%)", range=[0,105], gridcolor="#f0f0f0"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=380,
        font=dict(family="Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=70, b=80),
    )
    return fig


def chart_mcq_vs_action(results: list):
    models = [r["model"] for r in results]
    mcq    = [round(r.get("type_scores",{}).get("mcq",{}).get("score",0)*100,1) for r in results]
    action = [round(r.get("type_scores",{}).get("action_based",{}).get("score",0)*100,1) for r in results]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="📝 MCQ (Knowledge)", x=models, y=mcq,    marker_color="#6366f1"))
    fig.add_trace(go.Bar(name="⚡ Action-Based (Reasoning)", x=models, y=action, marker_color="#f97316"))
    fig.update_layout(
        barmode="group",
        title=dict(text="Knowledge vs. Reasoning — MCQ vs Action-Based", font=dict(size=15)),
        xaxis=dict(tickangle=-25),
        yaxis=dict(title="Score (%)", range=[0,105], gridcolor="#f0f0f0"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=380,
        font=dict(family="Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=70, b=80),
    )
    return fig


def chart_subcategory_heatmap(results: list):
    all_subs = [s for subs in SUBCATEGORY_GROUPS.values() for s in subs]
    models   = [r["model"] for r in results]
    z        = []
    for r in results:
        row = [round(r.get("subcategory_scores",{}).get(s, 0)*100, 1) for s in all_subs]
        z.append(row)

    labels = [SUBCATEGORY_LABELS.get(s, s) for s in all_subs]

    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=models,
        colorscale=[[0,"#fee2e2"],[0.5,"#fef9c3"],[1,"#dcfce7"]],
        zmin=50, zmax=100,
        text=[[f"{v}%" for v in row] for row in z],
        texttemplate="%{text}",
        hoverongaps=False,
        colorbar=dict(title="Score %")
    ))
    fig.update_layout(
        title=dict(text="Subcategory Heatmap — All Models", font=dict(size=15)),
        xaxis=dict(tickangle=-40, side="bottom"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=max(300, 60 + 50*len(models)),
        font=dict(family="Inter, sans-serif", size=11),
        margin=dict(l=10, r=20, t=60, b=160),
    )
    return fig


def chart_ct_subcategory(results: list):
    ct_subs = SUBCATEGORY_GROUPS["Critical Thinking"]
    labels  = [SUBCATEGORY_LABELS[s] for s in ct_subs]
    fig = go.Figure()
    for r in results:
        scores = [round(r.get("subcategory_scores",{}).get(s,0)*100,1) for s in ct_subs]
        color  = PROVIDER_COLORS.get(r.get("provider","Other"), "#6B7280")
        fig.add_trace(go.Bar(
            name=r["model"], x=labels, y=scores,
            marker_color=color,
            text=[f"{s}%" for s in scores],
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group",
        title=dict(text="Critical Thinking — Subcategory Breakdown", font=dict(size=15)),
        yaxis=dict(title="Score (%)", range=[0,105], gridcolor="#f0f0f0"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=420,
        font=dict(family="Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=80, b=60),
    )
    return fig


def chart_provider_avg(results: list):
    provider_data: dict = {}
    for r in results:
        p = r.get("provider", "Other")
        provider_data.setdefault(p, []).append(r["overall_score"] * 100)
    providers = list(provider_data.keys())
    avgs = [round(sum(v)/len(v), 1) for v in provider_data.values()]
    colors = [PROVIDER_COLORS.get(p, "#6B7280") for p in providers]

    fig = go.Figure(go.Bar(
        x=providers, y=avgs,
        marker_color=colors,
        text=[f"{a}%" for a in avgs],
        textposition="outside",
    ))
    fig.update_layout(
        title=dict(text="Average Score by AI Provider", font=dict(size=15)),
        yaxis=dict(title="Avg Score (%)", range=[0,105], gridcolor="#f0f0f0"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=350,
        font=dict(family="Inter, sans-serif"),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


# ─── Critical Thinking Analysis Cards ────────────────────────────────────────

def ct_analysis_html(results: list) -> str:
    html = ""
    for key, info in CT_DIRECTION.items():
        scores_by_model = []
        for r in results:
            score = r.get("subcategory_scores", {}).get(key, 0)
            scores_by_model.append((r["model"], score))
        scores_by_model.sort(key=lambda x: x[1], reverse=True)

        top_model, top_score = scores_by_model[0] if scores_by_model else ("N/A", 0)
        avg_score = sum(s for _, s in scores_by_model) / len(scores_by_model) if scores_by_model else 0

        bar_rows = ""
        for model, score in scores_by_model:
            pct = round(score * 100, 1)
            provider = next((r.get("provider","Other") for r in results if r["model"] == model), "Other")
            color = PROVIDER_COLORS.get(provider, "#6B7280")
            bar_rows += f"""
            <div style="display:flex; align-items:center; margin:6px 0; gap:10px;">
              <span style="width:180px; font-size:12px; color:#374151; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{model}</span>
              <div style="flex:1; background:#f3f4f6; border-radius:4px; height:18px; position:relative;">
                <div style="width:{pct}%; background:{color}; border-radius:4px; height:100%;"></div>
              </div>
              <span style="width:45px; text-align:right; font-size:12px; font-weight:600; color:#111827;">{pct}%</span>
            </div>"""

        html += f"""
        <div style="background:white; border:1px solid #e5e7eb; border-radius:12px; padding:24px; margin-bottom:20px; box-shadow:0 1px 3px rgba(0,0,0,0.06);">
          <div style="display:flex; align-items:flex-start; gap:16px; margin-bottom:16px;">
            <span style="font-size:2em;">{info['icon']}</span>
            <div>
              <h3 style="margin:0 0 6px 0; font-size:1.1em; color:#111827;">{info['label']}</h3>
              <p style="margin:0; color:#6b7280; font-size:0.9em; line-height:1.5;">{info['description']}</p>
            </div>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px;">
            <div style="background:#f0fdf4; border-radius:8px; padding:12px;">
              <div style="font-size:0.75em; color:#16a34a; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">✅ Strong Models Do This</div>
              <div style="font-size:0.85em; color:#166534;">{info['strong_signal']}</div>
            </div>
            <div style="background:#fef2f2; border-radius:8px; padding:12px;">
              <div style="font-size:0.75em; color:#dc2626; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">⚠️ Weaker Models Do This</div>
              <div style="font-size:0.85em; color:#991b1b;">{info['weak_signal']}</div>
            </div>
          </div>
          <div style="display:flex; gap:16px; margin-bottom:16px;">
            <div style="background:#eff6ff; border-radius:8px; padding:10px 16px; text-align:center;">
              <div style="font-size:0.75em; color:#2563eb; font-weight:600;">Top Model</div>
              <div style="font-size:1em; font-weight:700; color:#1e40af;">{top_model}</div>
              <div style="font-size:0.85em; color:#3b82f6;">{round(top_score*100,1)}%</div>
            </div>
            <div style="background:#f5f3ff; border-radius:8px; padding:10px 16px; text-align:center;">
              <div style="font-size:0.75em; color:#7c3aed; font-weight:600;">Avg Score</div>
              <div style="font-size:1em; font-weight:700; color:#5b21b6;">{round(avg_score*100,1)}%</div>
              <div style="font-size:0.85em; color:#8b5cf6;">All Models</div>
            </div>
          </div>
          <div>{bar_rows}</div>
        </div>"""
    return html


# ─── Stats Bar ────────────────────────────────────────────────────────────────

def stats_html(results: list) -> str:
    n_models   = len(results)
    top        = results[0]["model"] if results else "—"
    top_score  = f"{results[0]['overall_score']*100:.1f}%" if results else "—"
    avg        = sum(r["overall_score"] for r in results)/len(results)*100 if results else 0

    return f"""
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:16px 0;">
      <div style="background:white; border:1px solid #e5e7eb; border-radius:10px; padding:16px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
        <div style="font-size:1.8em; font-weight:800; color:#1e40af;">{n_models}</div>
        <div style="font-size:0.8em; color:#6b7280; margin-top:2px;">Models Evaluated</div>
      </div>
      <div style="background:white; border:1px solid #e5e7eb; border-radius:10px; padding:16px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
        <div style="font-size:1.8em; font-weight:800; color:#16a34a;">100</div>
        <div style="font-size:0.8em; color:#6b7280; margin-top:2px;">Benchmark Questions</div>
      </div>
      <div style="background:white; border:1px solid #e5e7eb; border-radius:10px; padding:16px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
        <div style="font-size:1.8em; font-weight:800; color:#7c3aed;">{top_score}</div>
        <div style="font-size:0.8em; color:#6b7280; margin-top:2px;">Best Score ({top})</div>
      </div>
      <div style="background:white; border:1px solid #e5e7eb; border-radius:10px; padding:16px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
        <div style="font-size:1.8em; font-weight:800; color:#ea580c;">{avg:.1f}%</div>
        <div style="font-size:0.8em; color:#6b7280; margin-top:2px;">Average Across Models</div>
      </div>
    </div>"""


# ─── App ──────────────────────────────────────────────────────────────────────

CSS = """
body { font-family: 'Inter', sans-serif !important; background: #f8fafc !important; }
.gradio-container { max-width: 1200px !important; margin: 0 auto; }
footer { display: none !important; }
.tab-nav button { font-size: 14px !important; font-weight: 500 !important; }
.tab-nav button.selected { border-bottom: 2px solid #1e40af !important; color: #1e40af !important; }
h1, h2, h3 { font-family: 'Inter', sans-serif !important; }
.gr-button-primary { background: #1e40af !important; }
"""

HEADER = """
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #2563eb 100%);
     padding: 32px 28px 24px; border-radius: 14px; margin-bottom: 8px; color: white;">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
    <div>
      <div style="font-size:0.8em; font-weight:600; letter-spacing:1.5px; opacity:0.75; text-transform:uppercase; margin-bottom:6px;">hawky.ai</div>
      <h1 style="margin:0 0 8px; font-size:2em; font-weight:800; letter-spacing:-0.5px;">PM-AGI Benchmark 🎯</h1>
      <p style="margin:0; opacity:0.85; font-size:1em; max-width:600px; line-height:1.5;">
        The first open-source LLM benchmark for <strong>Performance Marketing</strong> —
        evaluating Meta Ads, Google Ads, critical thinking, and real-world action-based scenarios.
      </p>
    </div>
    <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
      <a href="https://huggingface.co/datasets/Hawky-ai/pm-agi-benchmark" target="_blank"
         style="background:rgba(255,255,255,0.15); color:white; text-decoration:none;
                padding:6px 14px; border-radius:6px; font-size:0.82em; font-weight:500; border:1px solid rgba(255,255,255,0.25);">
        🤗 Dataset
      </a>
      <a href="https://github.com/Hawky-ai/pm-AGI" target="_blank"
         style="background:rgba(255,255,255,0.15); color:white; text-decoration:none;
                padding:6px 14px; border-radius:6px; font-size:0.82em; font-weight:500; border:1px solid rgba(255,255,255,0.25);">
        ⭐ GitHub
      </a>
    </div>
  </div>
  <div style="display:flex; gap:10px; margin-top:20px; flex-wrap:wrap;">
    <span style="background:rgba(255,255,255,0.15); padding:4px 12px; border-radius:20px; font-size:0.8em;">🟦 Meta Ads</span>
    <span style="background:rgba(255,255,255,0.15); padding:4px 12px; border-radius:20px; font-size:0.8em;">🟩 Google Ads</span>
    <span style="background:rgba(255,255,255,0.15); padding:4px 12px; border-radius:20px; font-size:0.8em;">🟨 Critical Thinking</span>
    <span style="background:rgba(255,255,255,0.15); padding:4px 12px; border-radius:20px; font-size:0.8em;">🟥 Action-Based</span>
    <span style="background:rgba(255,255,255,0.15); padding:4px 12px; border-radius:20px; font-size:0.8em;">100 Questions</span>
    <span style="background:rgba(255,255,255,0.15); padding:4px 12px; border-radius:20px; font-size:0.8em;">MIT License</span>
  </div>
</div>
"""

SUBMIT_MD = """
## 📤 Submit Your Model to the Leaderboard

### Step 1 — Clone & Install
```bash
git clone https://github.com/Hawky-ai/pm-AGI
cd pm-AGI
pip install -r requirements.txt
```

### Step 2 — Run Evaluation
```bash
# OpenAI
python evaluate.py --model gpt-4o --provider openai --api-key YOUR_KEY

# Anthropic
python evaluate.py --model claude-opus-4-6 --provider anthropic --api-key YOUR_KEY

# Any OpenAI-compatible (Together AI, Fireworks, Ollama, etc.)
python evaluate.py --model llama-3.3-70b --provider openai-compatible --base-url YOUR_URL --api-key YOUR_KEY

# Specific category only
python evaluate.py --model YOUR_MODEL --provider openai --category meta_ads
```

### Step 3 — Submit
Open a **Pull Request** to [github.com/Hawky-ai/pm-AGI](https://github.com/Hawky-ai/pm-AGI) adding your result file from `results/YOUR_MODEL_timestamp.json`.

---

### Evaluation Scoring

| Question Type | How Scored |
|---|---|
| MCQ (63 questions) | 1.0 if correct letter, 0.0 otherwise |
| Action-Based (37 questions) | 0.0–1.0 via LLM-as-judge against expert rubric |

**Overall Score** = weighted average across all 100 questions.
"""

ABOUT_MD = """
## ℹ️ About PM-AGI

**PM-AGI** is the first open-source benchmark specifically designed to evaluate how well LLMs perform in **performance marketing** — the discipline of running, optimizing, and analyzing paid advertising campaigns.

### Why This Matters
LLMs are increasingly used by performance marketers to analyze data, draft strategies, troubleshoot campaigns, and make optimization decisions. PM-AGI measures whether they can actually do this reliably.

### Categories

| Category | Questions | What It Tests |
|---|---|---|
| 🟦 **Meta Ads** | 30 | Campaign structure, audience targeting, bidding strategy, creative performance, CAPI/measurement, Advantage+ |
| 🟩 **Google Ads** | 30 | Search campaigns, Smart Bidding, Quality Score, Performance Max, keyword strategy, attribution |
| 🟨 **Critical Thinking** | 20 | Data interpretation, budget allocation decisions, competitive analysis |
| 🟥 **Action-Based** | 20 | Real-world scenarios: optimization, troubleshooting, scaling, reporting |

### Difficulty
- 🟢 **Easy** (9 questions) — Foundational definitions and concepts
- 🟡 **Medium** (50 questions) — Applied platform mechanics
- 🔴 **Hard** (41 questions) — Complex trade-offs, multi-variable diagnosis, expert-level strategy

### Roadmap
- [ ] TikTok Ads category
- [ ] LinkedIn Ads category
- [ ] Amazon Ads category
- [ ] Multilingual benchmark
- [ ] Automated CI evaluation pipeline

---

Built by [hawky.ai](https://hawky.ai) · MIT License · [GitHub](https://github.com/Hawky-ai/pm-AGI)
"""


def create_app():
    results = load_results()
    all_models = [r["model"] for r in results]

    with gr.Blocks(title="PM-AGI Leaderboard | hawky.ai", css=CSS, theme=gr.themes.Soft()) as app:

        gr.HTML(HEADER)
        stats_display = gr.HTML(stats_html(results))

        with gr.Tabs():

            # ── Tab 1: Leaderboard ──────────────────────────────────────────
            with gr.Tab("🏆 Leaderboard"):
                gr.Markdown("### Full Rankings — All Models")
                with gr.Row():
                    refresh_btn = gr.Button("🔄 Refresh", size="sm", variant="secondary", scale=0)
                leaderboard_table = gr.DataFrame(
                    value=build_main_df(results),
                    interactive=False,
                    wrap=True,
                )
                gr.Plot(value=chart_overall(results), label="")

                with gr.Row():
                    with gr.Column():
                        gr.Plot(value=chart_difficulty(results), label="")
                    with gr.Column():
                        gr.Plot(value=chart_mcq_vs_action(results), label="")

                def refresh_all():
                    r = load_results()
                    return build_main_df(r), stats_html(r), chart_overall(r), chart_difficulty(r), chart_mcq_vs_action(r)

                refresh_btn.click(
                    refresh_all,
                    outputs=[leaderboard_table, stats_display, gr.Plot(), gr.Plot(), gr.Plot()]
                )

            # ── Tab 2: Category Deep Dive ───────────────────────────────────
            with gr.Tab("📊 Category Deep Dive"):
                gr.Markdown("### Compare models across all 4 categories and subcategories")

                with gr.Row():
                    model_selector = gr.CheckboxGroup(
                        choices=all_models,
                        value=all_models[:4],
                        label="Select models to compare"
                    )

                radar_plot = gr.Plot(value=chart_category_radar(results, all_models[:4]))
                heatmap_plot = gr.Plot(value=chart_subcategory_heatmap(results))

                model_selector.change(
                    lambda sel: chart_category_radar(results, sel),
                    inputs=model_selector,
                    outputs=radar_plot
                )

            # ── Tab 3: Provider Comparison ──────────────────────────────────
            with gr.Tab("🏢 Provider Comparison"):
                gr.Markdown("### Average performance by AI provider")
                gr.Plot(value=chart_provider_avg(results))

                gr.Markdown("---\n### Provider Details")
                provider_rows = {}
                for r in results:
                    p = r.get("provider", "Other")
                    provider_rows.setdefault(p, []).append({
                        "Model": r["model"],
                        "Overall": f"{r['overall_score']*100:.1f}%",
                        "Meta Ads": f"{r.get('category_scores',{}).get('meta_ads',{}).get('score',0)*100:.1f}%",
                        "Google Ads": f"{r.get('category_scores',{}).get('google_ads',{}).get('score',0)*100:.1f}%",
                    })
                for provider, rows in provider_rows.items():
                    logo = PROVIDER_LOGOS.get(provider, "⚪")
                    gr.Markdown(f"#### {logo} {provider}")
                    gr.DataFrame(value=pd.DataFrame(rows), interactive=False)

            # ── Tab 4: Critical Thinking ────────────────────────────────────
            with gr.Tab("🧠 Critical Thinking"):
                gr.Markdown("""
### Critical Thinking — Direction & Analysis

This section breaks down how models perform across the 3 critical thinking subcategories,
and explains **what direction** strong vs. weak models take in each reasoning dimension.
""")
                gr.Plot(value=chart_ct_subcategory(results), label="")
                gr.HTML(ct_analysis_html(results))

            # ── Tab 5: Submit ───────────────────────────────────────────────
            with gr.Tab("📤 Submit Your Model"):
                gr.Markdown(SUBMIT_MD)

            # ── Tab 6: About ────────────────────────────────────────────────
            with gr.Tab("ℹ️ About"):
                gr.Markdown(ABOUT_MD)

        gr.HTML("""
        <div style="text-align:center; padding:20px 16px 8px; color:#9ca3af; font-size:0.82em; border-top:1px solid #f3f4f6; margin-top:16px;">
            <strong>PM-AGI Benchmark</strong> by
            <a href="https://hawky.ai" target="_blank" style="color:#1e40af;">hawky.ai</a>
            &nbsp;·&nbsp; MIT License
            &nbsp;·&nbsp; <a href="https://github.com/Hawky-ai/pm-AGI" target="_blank" style="color:#1e40af;">GitHub</a>
            &nbsp;·&nbsp; <a href="https://huggingface.co/datasets/Hawky-ai/pm-agi-benchmark" target="_blank" style="color:#1e40af;">Dataset</a>
        </div>
        """)

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch()
