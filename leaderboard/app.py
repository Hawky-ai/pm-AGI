"""
PM-AGI Leaderboard — hawky.ai
Performance Marketing LLM Benchmark
"""

import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

import gradio as gr
import pandas as pd
import plotly.graph_objects as go

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE          = Path(__file__).parent
RESULTS_DIR   = BASE / "results"
DATASET_PATH  = BASE / "benchmark" / "dataset.json"
BENCHMARKS_PATH = BASE / "data" / "industry_benchmarks.json"
SUBMISSIONS_PATH = BASE / "data" / "question_submissions.json"

# ─── Constants ────────────────────────────────────────────────────────────────
PROVIDER_COLORS = {
    "OpenAI":     "#10a37f",
    "Anthropic":  "#c96442",
    "Google":     "#4285F4",
    "Meta":       "#1877F2",
    "Mistral AI": "#6B46C1",
    "DeepSeek":   "#0EA5E9",
    "Other":      "#6B7280",
}
PROVIDER_LOGOS = {
    "OpenAI":    "🟢", "Anthropic": "🟠", "Google": "🔵",
    "Meta":      "🔷", "Mistral AI": "🟣", "DeepSeek": "🩵", "Other": "⚪",
}
MEDALS = {0: "🥇", 1: "🥈", 2: "🥉"}

CATEGORIES = ["meta_ads", "google_ads", "critical_thinking", "action_based"]
CAT_LABELS  = {"meta_ads": "Meta Ads", "google_ads": "Google Ads",
               "critical_thinking": "Critical Thinking", "action_based": "Action-Based"}
CAT_ICONS   = {"meta_ads": "🟦", "google_ads": "🟩", "critical_thinking": "🟨", "action_based": "🟥"}

# v2: reasoning_type dimension — what kind of thinking each question tests
REASONING_TYPES = ["recall", "adversarial", "diagnostic", "quantitative", "creative_strategy"]
REASONING_LABELS = {
    "recall": "Knowledge Recall",
    "adversarial": "Adversarial / Trap",
    "diagnostic": "Diagnostic Reasoning",
    "quantitative": "Quantitative Tradeoffs",
    "creative_strategy": "Creative & Experiment Design",
}
REASONING_COLORS = {
    "recall": "#6B7280",
    "adversarial": "#DC2626",
    "diagnostic": "#2563EB",
    "quantitative": "#16A34A",
    "creative_strategy": "#7C3AED",
}
REASONING_DESC = {
    "recall": "Tests platform knowledge and best-practice recall. 'What is X?', 'Which setting does Y?'",
    "adversarial": "Trap questions with plausible distractors. Tests whether the model genuinely reasons vs. pattern-matches outdated 2019-era best practices.",
    "diagnostic": "Multi-step diagnostic reasoning. Given anomalous data, reason through audience, creative, bidding, tracking causes to a root cause.",
    "quantitative": "Budget allocation & quantitative tradeoffs. Math + strategy + stating assumptions. Marginal ROAS, incrementality, LTV-based targets.",
    "creative_strategy": "Creative strategy & experiment design. A/B test design, iteration plans, audience hypotheses, incrementality test setup.",
}

SUBCATEGORY_GROUPS = {
    "Meta Ads":         ["campaign_structure","audience_targeting","bidding_strategy","creative_performance","measurement","advantage_plus"],
    "Google Ads":       ["quality_score","smart_bidding","performance_max","keyword_strategy","attribution"],
    "Critical Thinking":["data_interpretation","budget_allocation","competitive_analysis"],
    "Action-Based":     ["campaign_optimization","troubleshooting","scaling_decisions","reporting_insights"],
}
SUB_LABELS = {
    "campaign_structure":"Campaign Structure","audience_targeting":"Audience Targeting",
    "bidding_strategy":"Bidding Strategy","creative_performance":"Creative Performance",
    "measurement":"Measurement & CAPI","advantage_plus":"Advantage+ / AI",
    "quality_score":"Quality Score","smart_bidding":"Smart Bidding",
    "performance_max":"Performance Max","keyword_strategy":"Keyword Strategy",
    "attribution":"Attribution","data_interpretation":"Data Interpretation",
    "budget_allocation":"Budget Allocation","competitive_analysis":"Competitive Analysis",
    "campaign_optimization":"Campaign Optimization","troubleshooting":"Troubleshooting",
    "scaling_decisions":"Scaling Decisions","reporting_insights":"Reporting & Insights",
}
CT_DIRECTION = {
    "data_interpretation": {
        "label": "Data Interpretation", "icon": "📊",
        "description": "Can the model read performance data, identify trends, and draw correct conclusions from CPA, ROAS, CTR, CPM, and conversion rate changes?",
        "strong": "Strong models diagnose anomalies, separate signal from noise, check tracking before assuming campaign issues, and avoid premature conclusions.",
        "weak":   "Weaker models react to surface metrics, recommend budget changes before checking tracking, and miss external factors like seasonality.",
    },
    "budget_allocation": {
        "label": "Budget Allocation", "icon": "💰",
        "description": "Can the model make sound decisions about distributing budget across channels, campaigns, and time periods — balancing efficiency, scale, and growth?",
        "strong": "Strong models understand marginal efficiency, channel interdependency, LTV-based CPA targets, and full-funnel thinking.",
        "weak":   "Weaker models chase highest ROAS and cut upper-funnel spend, undermining long-term growth and demand creation.",
    },
    "competitive_analysis": {
        "label": "Competitive Analysis", "icon": "🏁",
        "description": "Can the model interpret competitive signals (Auction Insights, Ad Library, CPM spikes) and respond strategically without overreacting?",
        "strong": "Strong models identify root causes, improve Quality Score as primary defense, and make surgical keyword protection decisions.",
        "weak":   "Weaker models recommend emotional bid increases or ignore competitive context entirely.",
    },
}

INDUSTRIES = [
    "ecommerce_all","ecommerce_fashion","ecommerce_beauty","ecommerce_home",
    "saas_b2b","saas_b2c","mobile_apps","real_estate",
    "fintech","health_wellness","education","travel","food_beverage","other"
]
METRICS = {
    "meta_ads":   ["CTR (%)","CPM (USD)","CPC (USD)","CPA (USD)","CPL (USD)","CPI (USD)","ROAS (x)","Hook Rate (%)","Hold Rate (%)"],
    "google_ads": ["CTR (%)","CPC (USD)","CPL (USD)","CPA (USD)","ROAS (x)","Quality Score (1-10)","Impression Share (%)"],
}

# ─── Data Loaders ─────────────────────────────────────────────────────────────

def load_json_clean(path):
    try:
        content = re.sub(r'//.*?\n', '\n', Path(path).read_text())
        return json.loads(content)
    except Exception:
        return {}

def load_results():
    rows = []
    if not RESULTS_DIR.exists():
        return rows
    for f in sorted(RESULTS_DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text())
            if "example_" not in f.name:
                rows.append(d)
        except Exception:
            pass
    return sorted(rows, key=lambda x: x.get("overall_score", 0), reverse=True)

def load_benchmarks():
    data = load_json_clean(BENCHMARKS_PATH)
    return data.get("benchmarks", [])

def load_submissions():
    data = load_json_clean(SUBMISSIONS_PATH)
    return data.get("submissions", [])

def save_submission(sub: dict):
    path = SUBMISSIONS_PATH
    data = load_json_clean(path) if path.exists() else {"version":"1.0.0","submissions":[]}
    data["submissions"].append(sub)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ─── Tables & Charts ──────────────────────────────────────────────────────────

def build_main_df(results):
    rows = []
    for i, r in enumerate(results):
        cat  = r.get("category_scores", {})
        diff = r.get("difficulty_scores", {})
        p    = r.get("provider", "Other")
        rows.append({
            "Rank":              MEDALS.get(i, f"#{i+1}"),
            "Model":             r.get("model","Unknown"),
            "Provider":          f"{PROVIDER_LOGOS.get(p,'⚪')} {p}",
            "Overall ↑":         f"{r.get('overall_score',0)*100:.1f}%",
            "Meta Ads":          f"{cat.get('meta_ads',{}).get('score',0)*100:.1f}%",
            "Google Ads":        f"{cat.get('google_ads',{}).get('score',0)*100:.1f}%",
            "Critical Thinking": f"{cat.get('critical_thinking',{}).get('score',0)*100:.1f}%",
            "Action-Based":      f"{cat.get('action_based',{}).get('score',0)*100:.1f}%",
            "Easy":              f"{diff.get('easy',{}).get('score',0)*100:.1f}%",
            "Hard":              f"{diff.get('hard',{}).get('score',0)*100:.1f}%",
        })
    return pd.DataFrame(rows)

def hex_to_rgba(hex_color, alpha=0.15):
    h = hex_color.lstrip("#")
    r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def chart_overall(results):
    models = [r["model"] for r in results]
    scores = [round(r["overall_score"]*100,1) for r in results]
    colors = [PROVIDER_COLORS.get(r.get("provider","Other"),"#6B7280") for r in results]
    fig = go.Figure(go.Bar(
        x=scores, y=models, orientation="h",
        marker_color=colors,
        text=[f"{s}%" for s in scores], textposition="outside",
        hovertemplate="<b>%{y}</b><br>Score: %{x}%<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text="Overall PM-AGI Score by Model", font=dict(size=15)),
        xaxis=dict(range=[0,108], gridcolor="#f0f0f0"),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10,r=60,t=50,b=30), height=380,
        font=dict(family="Inter, sans-serif", size=12),
    )
    return fig

def chart_radar(results, selected_models):
    cat_keys = ["meta_ads","google_ads","critical_thinking","action_based"]
    cats     = ["Meta Ads","Google Ads","Critical Thinking","Action-Based"]
    fig = go.Figure()
    for r in results:
        if r["model"] not in selected_models: continue
        color = PROVIDER_COLORS.get(r.get("provider","Other"),"#6B7280")
        scores = [round(r.get("category_scores",{}).get(k,{}).get("score",0)*100,1) for k in cat_keys]
        scores_c = scores + [scores[0]]
        cats_c   = cats + [cats[0]]
        fig.add_trace(go.Scatterpolar(
            r=scores_c, theta=cats_c, fill="toself", name=r["model"],
            line=dict(color=color, width=2),
            fillcolor=hex_to_rgba(color, 0.15),
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100], gridcolor="#e5e7eb")),
        title=dict(text="Category Radar", font=dict(size=14)),
        showlegend=True, paper_bgcolor="white", height=400,
        margin=dict(l=40,r=100,t=60,b=40),
        font=dict(family="Inter, sans-serif"),
    )
    return fig

def chart_difficulty(results):
    models = [r["model"] for r in results]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="🟢 Easy",   x=models, y=[round(r.get("difficulty_scores",{}).get("easy",{}).get("score",0)*100,1) for r in results], marker_color="#22c55e"))
    fig.add_trace(go.Bar(name="🟡 Medium", x=models, y=[round(r.get("difficulty_scores",{}).get("medium",{}).get("score",0)*100,1) for r in results], marker_color="#f59e0b"))
    fig.add_trace(go.Bar(name="🔴 Hard",   x=models, y=[round(r.get("difficulty_scores",{}).get("hard",{}).get("score",0)*100,1) for r in results], marker_color="#ef4444"))
    fig.update_layout(
        barmode="group", title=dict(text="Score by Difficulty", font=dict(size=14)),
        xaxis=dict(tickangle=-30), yaxis=dict(range=[0,108], gridcolor="#f0f0f0"),
        plot_bgcolor="white", paper_bgcolor="white", height=360,
        legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),
        margin=dict(l=40,r=20,t=70,b=90), font=dict(family="Inter, sans-serif"),
    )
    return fig

def chart_reasoning_types(results):
    """v2: per-model breakdown by reasoning_type — separates recall from genuine reasoning."""
    if not results:
        return go.Figure()
    models = [r["model"] for r in results]
    fig = go.Figure()
    for rt in REASONING_TYPES:
        scores = [round(r.get("reasoning_type_scores", {}).get(rt, {}).get("score", 0) * 100, 1) for r in results]
        fig.add_trace(go.Bar(
            name=REASONING_LABELS[rt],
            x=models,
            y=scores,
            marker_color=REASONING_COLORS[rt],
        ))
    fig.update_layout(
        barmode="group",
        title=dict(text="Score by Reasoning Type — Recall vs Real Reasoning", font=dict(size=14)),
        xaxis=dict(tickangle=-30),
        yaxis=dict(range=[0, 108], gridcolor="#f0f0f0"),
        plot_bgcolor="white", paper_bgcolor="white", height=420,
        legend=dict(orientation="h", y=1.15, x=1, xanchor="right"),
        margin=dict(l=40, r=20, t=80, b=110),
        font=dict(family="Inter, sans-serif"),
    )
    return fig

def reasoning_type_cards_html(results):
    """v2: explainer cards for each reasoning type with per-model rankings."""
    html = ""
    for rt in REASONING_TYPES:
        scores = [(r["model"], r.get("reasoning_type_scores", {}).get(rt, {}).get("score", 0)) for r in results]
        scores.sort(key=lambda x: x[1], reverse=True)
        top_model, top_score = scores[0] if scores else ("—", 0)
        avg = sum(s for _, s in scores) / len(scores) if scores else 0
        color = REASONING_COLORS[rt]
        bars = "".join([f"""
          <div style="display:flex;align-items:center;gap:8px;margin:5px 0;">
            <span style="width:170px;font-size:11.5px;color:#374151;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{m}</span>
            <div style="flex:1;background:#f3f4f6;border-radius:4px;height:16px;">
              <div style="width:{round(s*100,1)}%;background:{color};border-radius:4px;height:100%;"></div>
            </div>
            <span style="width:42px;text-align:right;font-size:11.5px;font-weight:600;color:#111827;">{round(s*100,1)}%</span>
          </div>""" for m, s in scores])
        html += f"""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:22px;margin-bottom:18px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
          <div style="display:flex;gap:14px;margin-bottom:14px;align-items:flex-start;">
            <div style="width:6px;background:{color};border-radius:3px;align-self:stretch;"></div>
            <div>
              <h3 style="margin:0 0 5px;font-size:1.05em;color:#111827;">{REASONING_LABELS[rt]}</h3>
              <p style="margin:0;color:#6b7280;font-size:0.88em;line-height:1.5;">{REASONING_DESC[rt]}</p>
            </div>
          </div>
          <div style="display:flex;gap:12px;margin-bottom:14px;">
            <div style="background:#eff6ff;border-radius:8px;padding:10px 16px;text-align:center;">
              <div style="font-size:0.72em;color:#2563eb;font-weight:600;">Top Model</div>
              <div style="font-size:0.95em;font-weight:700;color:#1e40af;">{top_model}</div>
              <div style="font-size:0.82em;color:#3b82f6;">{round(top_score*100,1)}%</div>
            </div>
            <div style="background:#f5f3ff;border-radius:8px;padding:10px 16px;text-align:center;">
              <div style="font-size:0.72em;color:#7c3aed;font-weight:600;">Avg All Models</div>
              <div style="font-size:0.95em;font-weight:700;color:#5b21b6;">{round(avg*100,1)}%</div>
            </div>
          </div>
          {bars}
        </div>"""
    return html

def chart_mcq_vs_action(results):
    models = [r["model"] for r in results]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="📝 MCQ", x=models, y=[round(r.get("type_scores",{}).get("mcq",{}).get("score",0)*100,1) for r in results], marker_color="#6366f1"))
    fig.add_trace(go.Bar(name="⚡ Action", x=models, y=[round(r.get("type_scores",{}).get("action_based",{}).get("score",0)*100,1) for r in results], marker_color="#f97316"))
    fig.update_layout(
        barmode="group", title=dict(text="Knowledge (MCQ) vs Reasoning (Action-Based)", font=dict(size=14)),
        xaxis=dict(tickangle=-30), yaxis=dict(range=[0,108], gridcolor="#f0f0f0"),
        plot_bgcolor="white", paper_bgcolor="white", height=360,
        legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),
        margin=dict(l=40,r=20,t=70,b=90), font=dict(family="Inter, sans-serif"),
    )
    return fig

def chart_heatmap(results):
    all_subs = [s for grp in SUBCATEGORY_GROUPS.values() for s in grp]
    labels   = [SUB_LABELS.get(s,s) for s in all_subs]
    models   = [r["model"] for r in results]
    z        = [[round(r.get("subcategory_scores",{}).get(s,0)*100,1) for s in all_subs] for r in results]
    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=models,
        colorscale=[[0,"#fee2e2"],[0.5,"#fef9c3"],[1,"#dcfce7"]],
        zmin=50, zmax=100,
        text=[[f"{v}%" for v in row] for row in z],
        texttemplate="%{text}",
        colorbar=dict(title="Score %")
    ))
    fig.update_layout(
        title=dict(text="Subcategory Performance Heatmap", font=dict(size=14)),
        xaxis=dict(tickangle=-40),
        plot_bgcolor="white", paper_bgcolor="white",
        height=max(320, 60+50*len(models)),
        margin=dict(l=10,r=20,t=60,b=170),
        font=dict(family="Inter, sans-serif", size=10),
    )
    return fig

def chart_ct(results):
    ct_subs = SUBCATEGORY_GROUPS["Critical Thinking"]
    labels  = [SUB_LABELS[s] for s in ct_subs]
    fig = go.Figure()
    for r in results:
        color = PROVIDER_COLORS.get(r.get("provider","Other"),"#6B7280")
        scores = [round(r.get("subcategory_scores",{}).get(s,0)*100,1) for s in ct_subs]
        fig.add_trace(go.Bar(name=r["model"], x=labels, y=scores, marker_color=color,
                             text=[f"{s}%" for s in scores], textposition="outside"))
    fig.update_layout(
        barmode="group", title=dict(text="Critical Thinking — Subcategory Breakdown", font=dict(size=14)),
        yaxis=dict(range=[0,108], gridcolor="#f0f0f0"),
        plot_bgcolor="white", paper_bgcolor="white", height=400,
        legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),
        margin=dict(l=40,r=20,t=80,b=50), font=dict(family="Inter, sans-serif"),
    )
    return fig

def chart_provider(results):
    pd_data: dict = {}
    for r in results:
        p = r.get("provider","Other")
        pd_data.setdefault(p,[]).append(r["overall_score"]*100)
    providers = list(pd_data.keys())
    avgs   = [round(sum(v)/len(v),1) for v in pd_data.values()]
    counts = [len(v) for v in pd_data.values()]
    colors = [PROVIDER_COLORS.get(p,"#6B7280") for p in providers]
    fig = go.Figure(go.Bar(
        x=providers, y=avgs, marker_color=colors,
        text=[f"{a}%<br>({c} model{'s' if c>1 else ''})" for a,c in zip(avgs,counts)],
        textposition="outside",
    ))
    fig.update_layout(
        title=dict(text="Average Score by AI Provider", font=dict(size=14)),
        yaxis=dict(range=[0,108], gridcolor="#f0f0f0"),
        plot_bgcolor="white", paper_bgcolor="white", height=350,
        margin=dict(l=40,r=20,t=60,b=40), font=dict(family="Inter, sans-serif"),
    )
    return fig

def chart_benchmarks(benchmarks, platform, industry):
    rows = [b for b in benchmarks if b["platform"]==platform and b["industry"]==industry]
    if not rows:
        fig = go.Figure()
        fig.add_annotation(text="No data for this selection", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    metrics = [b["metric"].upper() for b in rows]
    values  = [b["value"] for b in rows]
    units   = [b.get("unit","") for b in rows]
    color   = "#1e40af" if platform=="meta_ads" else "#16a34a"
    fig = go.Figure(go.Bar(
        x=metrics, y=values, marker_color=color,
        text=[f"{v} {u}" for v,u in zip(values,units)], textposition="outside",
    ))
    fig.update_layout(
        title=dict(text=f"{platform.replace('_',' ').title()} — {industry.replace('_',' ').title()} Benchmarks", font=dict(size=14)),
        yaxis=dict(gridcolor="#f0f0f0"),
        plot_bgcolor="white", paper_bgcolor="white", height=350,
        margin=dict(l=40,r=20,t=60,b=60), font=dict(family="Inter, sans-serif"),
    )
    return fig

# ─── HTML Components ──────────────────────────────────────────────────────────

def stats_html(results):
    n  = len(results)
    top = results[0]["model"] if results else "—"
    ts  = f"{results[0]['overall_score']*100:.1f}%" if results else "—"
    avg = sum(r["overall_score"] for r in results)/n*100 if results else 0
    bmarks = len(load_benchmarks())
    return f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:12px 0 20px;">
      {"".join([f'''<div style="background:white;border:1px solid #e5e7eb;border-radius:10px;padding:16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
        <div style="font-size:1.7em;font-weight:800;color:{c};">{v}</div>
        <div style="font-size:0.78em;color:#6b7280;margin-top:3px;">{l}</div></div>'''
      for v,l,c in [(str(n),"Models Evaluated","#1e40af"),(str(100),"Benchmark Questions","#16a34a"),(ts,f"Best Score ({top})","#7c3aed"),(str(bmarks),"Industry Benchmarks","#ea580c")]])}
    </div>"""

def ct_cards_html(results):
    html = ""
    for key, info in CT_DIRECTION.items():
        scores = [(r["model"], r.get("subcategory_scores",{}).get(key,0)) for r in results]
        scores.sort(key=lambda x: x[1], reverse=True)
        top_model, top_score = scores[0] if scores else ("—",0)
        avg = sum(s for _,s in scores)/len(scores) if scores else 0
        bars = "".join([f"""
          <div style="display:flex;align-items:center;gap:8px;margin:5px 0;">
            <span style="width:170px;font-size:11.5px;color:#374151;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{m}</span>
            <div style="flex:1;background:#f3f4f6;border-radius:4px;height:16px;">
              <div style="width:{round(s*100,1)}%;background:{PROVIDER_COLORS.get(next((r.get('provider','Other') for r in results if r['model']==m),'Other'),'#6B7280')};border-radius:4px;height:100%;"></div>
            </div>
            <span style="width:42px;text-align:right;font-size:11.5px;font-weight:600;color:#111827;">{round(s*100,1)}%</span>
          </div>""" for m,s in scores])
        html += f"""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:22px;margin-bottom:18px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
          <div style="display:flex;gap:14px;margin-bottom:14px;">
            <span style="font-size:1.8em;">{info['icon']}</span>
            <div>
              <h3 style="margin:0 0 5px;font-size:1.05em;color:#111827;">{info['label']}</h3>
              <p style="margin:0;color:#6b7280;font-size:0.88em;line-height:1.5;">{info['description']}</p>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">
            <div style="background:#f0fdf4;border-radius:8px;padding:11px;">
              <div style="font-size:0.72em;color:#16a34a;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:3px;">✅ Strong Models</div>
              <div style="font-size:0.84em;color:#166534;">{info['strong']}</div>
            </div>
            <div style="background:#fef2f2;border-radius:8px;padding:11px;">
              <div style="font-size:0.72em;color:#dc2626;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:3px;">⚠️ Weak Models</div>
              <div style="font-size:0.84em;color:#991b1b;">{info['weak']}</div>
            </div>
          </div>
          <div style="display:flex;gap:12px;margin-bottom:14px;">
            <div style="background:#eff6ff;border-radius:8px;padding:10px 16px;text-align:center;">
              <div style="font-size:0.72em;color:#2563eb;font-weight:600;">Top Model</div>
              <div style="font-size:0.95em;font-weight:700;color:#1e40af;">{top_model}</div>
              <div style="font-size:0.82em;color:#3b82f6;">{round(top_score*100,1)}%</div>
            </div>
            <div style="background:#f5f3ff;border-radius:8px;padding:10px 16px;text-align:center;">
              <div style="font-size:0.72em;color:#7c3aed;font-weight:600;">Avg All Models</div>
              <div style="font-size:0.95em;font-weight:700;color:#5b21b6;">{round(avg*100,1)}%</div>
            </div>
          </div>
          {bars}
        </div>"""
    return html

# ─── CSS & Header ─────────────────────────────────────────────────────────────

CSS = """
body { font-family: 'Inter', sans-serif !important; background: #f8fafc !important; }
.gradio-container { max-width: 1200px !important; margin: 0 auto; }
footer { display: none !important; }
.tab-nav button { font-size: 13.5px !important; font-weight: 500 !important; }
.tab-nav button.selected { border-bottom: 2px solid #1e40af !important; color: #1e40af !important; }
"""

HEADER = """
<div style="background:linear-gradient(135deg,#1e3a8a 0%,#1e40af 60%,#2563eb 100%);
  padding:28px 28px 22px;border-radius:14px;margin-bottom:4px;color:white;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;">
    <div>
      <div style="font-size:0.75em;font-weight:600;letter-spacing:1.5px;opacity:0.7;text-transform:uppercase;margin-bottom:5px;">hawky.ai</div>
      <h1 style="margin:0 0 7px;font-size:1.9em;font-weight:800;letter-spacing:-0.5px;">PM-AGI Benchmark 🎯</h1>
      <p style="margin:0;opacity:0.85;font-size:0.95em;max-width:580px;line-height:1.5;">
        The first open-source LLM benchmark for <strong>Performance Marketing</strong> —
        Meta Ads · Google Ads · Critical Thinking · Action-Based Scenarios.
      </p>
    </div>
    <div style="display:flex;flex-direction:column;gap:7px;align-items:flex-end;">
      <a href="https://huggingface.co/datasets/Hawky-ai/pm-agi-benchmark" target="_blank"
        style="background:rgba(255,255,255,0.15);color:white;text-decoration:none;
               padding:5px 13px;border-radius:6px;font-size:0.8em;font-weight:500;border:1px solid rgba(255,255,255,0.25);">
        🤗 Dataset
      </a>
      <a href="https://github.com/Hawky-ai/pm-AGI" target="_blank"
        style="background:rgba(255,255,255,0.15);color:white;text-decoration:none;
               padding:5px 13px;border-radius:6px;font-size:0.8em;font-weight:500;border:1px solid rgba(255,255,255,0.25);">
        ⭐ GitHub
      </a>
    </div>
  </div>
  <div style="display:flex;gap:8px;margin-top:18px;flex-wrap:wrap;">
    <span style="background:rgba(255,255,255,0.15);padding:3px 11px;border-radius:20px;font-size:0.78em;">v2 · 494 Questions</span>
    <span style="background:rgba(255,255,255,0.15);padding:3px 11px;border-radius:20px;font-size:0.78em;">🟦 Meta Ads · 227 Qs</span>
    <span style="background:rgba(255,255,255,0.15);padding:3px 11px;border-radius:20px;font-size:0.78em;">🟩 Google Ads · 227 Qs</span>
    <span style="background:rgba(255,255,255,0.15);padding:3px 11px;border-radius:20px;font-size:0.78em;">🧠 5 Reasoning Types</span>
    <span style="background:rgba(255,255,255,0.15);padding:3px 11px;border-radius:20px;font-size:0.78em;">MIT License · Open Source</span>
  </div>
</div>
"""

# ─── Submission Handlers ──────────────────────────────────────────────────────

def submit_question(category, subcategory, difficulty, q_type, question,
                    opt_a, opt_b, opt_c, opt_d, answer, criteria, explanation,
                    tags, name, email):
    if not question.strip():
        return "⚠️ Question text is required."
    if q_type == "mcq" and not answer.strip():
        return "⚠️ Answer (A/B/C/D) is required for MCQ questions."
    sub_id = f"{category[:4]}_{uuid.uuid4().hex[:6]}"
    sub = {
        "id": sub_id,
        "status": "pending",
        "type": q_type,
        "category": category,
        "subcategory": subcategory,
        "difficulty": difficulty,
        "question": question.strip(),
        "options": {"A": opt_a, "B": opt_b, "C": opt_c, "D": opt_d} if q_type == "mcq" else {},
        "answer": answer.strip().upper() if q_type == "mcq" else "",
        "answer_criteria": [c.strip() for c in criteria.split("\n") if c.strip()],
        "explanation": explanation.strip(),
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "submitter_name": name.strip() or "Anonymous",
        "submitter_email": email.strip(),
        "submitted_at": datetime.utcnow().isoformat() + "Z",
    }
    try:
        save_submission(sub)
        return f"✅ Submitted! ID: `{sub_id}`. Thank you — we'll review within 5–7 days."
    except Exception as e:
        return f"⚠️ Saved locally (read-only Space). Submit via GitHub PR: {e}"

def submit_benchmark(platform, industry, metric, value, unit, campaign_type, period, contributor):
    if not value or not metric:
        return "⚠️ Platform, industry, metric, and value are required."
    try:
        float_val = float(value)
    except ValueError:
        return "⚠️ Value must be a number."
    data = load_json_clean(BENCHMARKS_PATH) if BENCHMARKS_PATH.exists() else {"benchmarks": []}
    new_id = f"cb_{uuid.uuid4().hex[:6]}"
    data["benchmarks"].append({
        "id": new_id,
        "platform": platform,
        "industry": industry,
        "metric": metric.lower().replace(" ","_").replace("(","").replace(")","").replace("%","pct"),
        "value": float_val,
        "unit": unit,
        "campaign_type": campaign_type or "all",
        "period": period,
        "source": f"community_{contributor or 'anonymous'}",
    })
    try:
        with open(BENCHMARKS_PATH, "w") as f:
            json.dump(data, f, indent=2)
        return f"✅ Benchmark submitted! ID: `{new_id}`. Thank you for contributing data."
    except Exception:
        return f"✅ Received (read-only Space). Submit via GitHub PR to `data/industry_benchmarks.json`."

def submit_model_result(json_text, model_name, provider, notes):
    if not json_text or not json_text.strip():
        return "⚠️ Please paste your results JSON."
    try:
        data = json.loads(json_text.strip())
        if "overall_score" not in data:
            return "⚠️ Invalid results — missing 'overall_score' field. Run `evaluate.py` to generate."
        score = data.get("overall_score", 0) * 100
        total = data.get("total_questions", 0)
        return f"""✅ **Result validated!**

**Model:** {data.get('model', model_name)}
**Overall Score:** {score:.1f}%
**Questions:** {total}

**Next step:** Open a Pull Request to [github.com/Hawky-ai/pm-AGI](https://github.com/Hawky-ai/pm-AGI)
adding your JSON to the `results/` directory. It will appear on the leaderboard after merge.
"""
    except json.JSONDecodeError:
        return "⚠️ Invalid JSON. Please paste the raw output from `evaluate.py`."
    except Exception as e:
        return f"⚠️ Error: {e}"

# ─── Build App ────────────────────────────────────────────────────────────────

def create_app():
    results    = load_results()
    benchmarks = load_benchmarks()
    all_models = [r["model"] for r in results]
    industries_available = sorted(set(b["industry"] for b in benchmarks))

    with gr.Blocks(title="PM-AGI Leaderboard | hawky.ai", css=CSS, theme=gr.themes.Soft()) as app:

        gr.HTML(HEADER)
        stats_box = gr.HTML(stats_html(results))

        with gr.Tabs():

            # ── 1. Leaderboard ──────────────────────────────────────────────
            with gr.Tab("🏆 Leaderboard"):
                gr.Markdown("### Full Rankings")
                with gr.Row():
                    refresh_btn = gr.Button("🔄 Refresh", size="sm", variant="secondary", scale=0)
                lb_table = gr.DataFrame(value=build_main_df(results), interactive=False, wrap=True)
                overall_plot = gr.Plot(value=chart_overall(results))
                with gr.Row():
                    with gr.Column(): difficulty_plot = gr.Plot(value=chart_difficulty(results))
                    with gr.Column(): mcq_plot = gr.Plot(value=chart_mcq_vs_action(results))

                def do_refresh():
                    r = load_results()
                    return build_main_df(r), stats_html(r), chart_overall(r), chart_difficulty(r), chart_mcq_vs_action(r)
                refresh_btn.click(do_refresh, outputs=[lb_table, stats_box, overall_plot, difficulty_plot, mcq_plot])

            # ── 2. Category Deep Dive ───────────────────────────────────────
            with gr.Tab("📊 Category Deep Dive"):
                gr.Markdown("### Compare across categories and all subcategories")
                model_sel = gr.CheckboxGroup(choices=all_models, value=all_models[:5], label="Select models")
                radar_plot = gr.Plot(value=chart_radar(results, all_models[:5]))
                heatmap_plot = gr.Plot(value=chart_heatmap(results))
                model_sel.change(lambda sel: chart_radar(results, sel), inputs=model_sel, outputs=radar_plot)

            # ── 3. Provider Comparison ──────────────────────────────────────
            with gr.Tab("🏢 Providers"):
                gr.Markdown("### Average score by AI provider")
                gr.Plot(value=chart_provider(results))
                for provider, prows in {r.get("provider","Other"): [] for r in results}.items():
                    rows_p = [{"Model": r["model"],
                               "Overall": f"{r['overall_score']*100:.1f}%",
                               "Meta Ads": f"{r.get('category_scores',{}).get('meta_ads',{}).get('score',0)*100:.1f}%",
                               "Google Ads": f"{r.get('category_scores',{}).get('google_ads',{}).get('score',0)*100:.1f}%",
                               "Hard Qs": f"{r.get('difficulty_scores',{}).get('hard',{}).get('score',0)*100:.1f}%"}
                              for r in results if r.get("provider","Other") == provider]
                    if rows_p:
                        gr.Markdown(f"#### {PROVIDER_LOGOS.get(provider,'⚪')} {provider}")
                        gr.DataFrame(value=pd.DataFrame(rows_p), interactive=False)

            # ── v2: Reasoning Types ─────────────────────────────────────────
            with gr.Tab("🧠 Reasoning Types"):
                gr.Markdown("""
### Reasoning Type Analysis (v2)

PM-AGI v2 separates **knowledge recall** from genuine **reasoning**. A model that scores 90% on recall may score 50% on adversarial / diagnostic / quantitative / creative-strategy questions — that gap is what this benchmark is designed to surface.

Five reasoning categories:
- **Recall** — platform knowledge & best-practice MCQs
- **Adversarial** — trap questions with plausible distractors that pattern-match outdated playbooks
- **Diagnostic** — multi-step root-cause reasoning over anomalous campaign data
- **Quantitative** — budget allocation, marginal ROAS, LTV math, stated assumptions
- **Creative Strategy** — A/B test design, experiment methodology, iteration systems
""")
                gr.Plot(value=chart_reasoning_types(results))
                gr.HTML(reasoning_type_cards_html(results))

            # ── 4. Critical Thinking ────────────────────────────────────────
            with gr.Tab("🧠 Critical Thinking"):
                gr.Markdown("""
### Critical Thinking Analysis

How do models reason about performance marketing data, budget decisions, and competitive situations?
This section shows **what direction** strong vs weak models take — not just scores.
""")
                gr.Plot(value=chart_ct(results))
                gr.HTML(ct_cards_html(results))

            # ── 5. Industry Benchmarks ──────────────────────────────────────
            with gr.Tab("📈 Industry Benchmarks"):
                gr.Markdown("""
### Performance Marketing Industry Benchmarks

Real-world performance benchmarks across platforms and industries.
Community-contributed and curated by hawky.ai. Use the filters below to explore.
""")
                with gr.Row():
                    bench_platform = gr.Dropdown(
                        choices=["meta_ads", "google_ads"],
                        value="meta_ads", label="Platform"
                    )
                    bench_industry = gr.Dropdown(
                        choices=industries_available or INDUSTRIES,
                        value=industries_available[0] if industries_available else "ecommerce_fashion",
                        label="Industry"
                    )
                bench_plot = gr.Plot(value=chart_benchmarks(benchmarks, "meta_ads", industries_available[0] if industries_available else "ecommerce_fashion"))

                def update_bench(platform, industry):
                    return chart_benchmarks(load_benchmarks(), platform, industry)
                bench_platform.change(update_bench, inputs=[bench_platform, bench_industry], outputs=bench_plot)
                bench_industry.change(update_bench, inputs=[bench_platform, bench_industry], outputs=bench_plot)

                gr.Markdown("---")
                gr.Markdown("""
#### 📋 Full Benchmark Table
*Tip: Filter by platform or industry above to explore segments.*
""")
                if benchmarks:
                    bench_df = pd.DataFrame([{
                        "Platform": b["platform"].replace("_"," ").title(),
                        "Industry": b["industry"].replace("_"," ").title(),
                        "Metric": b["metric"].upper(),
                        "Value": f"{b['value']} {b.get('unit','')}",
                        "Campaign Type": b.get("campaign_type","all"),
                        "Period": b.get("period",""),
                    } for b in benchmarks])
                    gr.DataFrame(value=bench_df, interactive=False, wrap=True)

            # ── 6. Submit Data ──────────────────────────────────────────────
            with gr.Tab("📤 Contribute Data"):
                gr.Markdown("""
## Contribute to PM-AGI

Help grow the benchmark! You can contribute in 3 ways:

---
""")
                with gr.Tabs():

                    # 6a. Submit Question
                    with gr.Tab("🧩 Submit a Question"):
                        gr.Markdown("""
### Submit a New Benchmark Question

Contribute questions that test performance marketing knowledge.
All submissions are reviewed by the hawky.ai team before being added to the dataset.
""")
                        with gr.Row():
                            sq_category   = gr.Dropdown(choices=list(CAT_LABELS.keys()), value="meta_ads", label="Category *")
                            sq_subcategory = gr.Dropdown(
                                choices=["campaign_structure","audience_targeting","bidding_strategy",
                                         "creative_performance","measurement","advantage_plus",
                                         "quality_score","smart_bidding","performance_max",
                                         "keyword_strategy","attribution","data_interpretation",
                                         "budget_allocation","competitive_analysis",
                                         "campaign_optimization","troubleshooting","scaling_decisions","reporting_insights"],
                                value="campaign_structure", label="Subcategory *"
                            )
                        with gr.Row():
                            sq_difficulty = gr.Dropdown(choices=["easy","medium","hard"], value="medium", label="Difficulty *")
                            sq_type       = gr.Dropdown(choices=["mcq","action_based"], value="mcq", label="Question Type *")

                        sq_question = gr.Textbox(label="Question *", lines=3, placeholder="Enter your question here...")

                        with gr.Accordion("MCQ Options (fill if type = mcq)", open=True):
                            with gr.Row():
                                sq_a = gr.Textbox(label="Option A", placeholder="Option A")
                                sq_b = gr.Textbox(label="Option B", placeholder="Option B")
                            with gr.Row():
                                sq_c = gr.Textbox(label="Option C", placeholder="Option C")
                                sq_d = gr.Textbox(label="Option D", placeholder="Option D")
                            sq_answer = gr.Dropdown(choices=["A","B","C","D"], label="Correct Answer (MCQ only)")

                        sq_criteria    = gr.Textbox(label="Answer Criteria (action_based — one key point per line)", lines=5,
                                                    placeholder="Key point 1\nKey point 2\nKey point 3")
                        sq_explanation = gr.Textbox(label="Explanation *", lines=3,
                                                    placeholder="Why is this the correct answer?")
                        sq_tags        = gr.Textbox(label="Tags (comma-separated)", placeholder="roas, bidding, meta_ads")

                        gr.Markdown("---")
                        with gr.Row():
                            sq_name  = gr.Textbox(label="Your Name (optional)", placeholder="Jane Doe")
                            sq_email = gr.Textbox(label="Email (optional, for credit)", placeholder="jane@example.com")

                        sq_btn    = gr.Button("Submit Question", variant="primary")
                        sq_status = gr.Markdown("")

                        sq_btn.click(
                            submit_question,
                            inputs=[sq_category, sq_subcategory, sq_difficulty, sq_type,
                                    sq_question, sq_a, sq_b, sq_c, sq_d, sq_answer,
                                    sq_criteria, sq_explanation, sq_tags, sq_name, sq_email],
                            outputs=sq_status
                        )

                    # 6b. Submit Benchmark Data
                    with gr.Tab("📊 Submit Benchmark Data"):
                        gr.Markdown("""
### Contribute Industry Benchmark Data

Share anonymized performance benchmarks from your campaigns.
This helps build the most comprehensive performance marketing reference database.

**Data is anonymized** — no account names, client names, or identifying information needed.
""")
                        with gr.Row():
                            bm_platform = gr.Dropdown(choices=["meta_ads","google_ads","tiktok_ads","linkedin_ads"], value="meta_ads", label="Platform *")
                            bm_industry = gr.Dropdown(choices=INDUSTRIES, value="ecommerce_fashion", label="Industry *")
                        with gr.Row():
                            bm_metric   = gr.Dropdown(choices=METRICS["meta_ads"], label="Metric *")
                            bm_value    = gr.Textbox(label="Value *", placeholder="e.g. 1.24")
                            bm_unit     = gr.Textbox(label="Unit", placeholder="e.g. %, USD, x")
                        with gr.Row():
                            bm_campaign = gr.Dropdown(
                                choices=["all","prospecting","retargeting","lead_gen","app_installs",
                                         "search_brand","search_nonbrand","shopping","uac","pmax"],
                                value="all", label="Campaign Type"
                            )
                            bm_period   = gr.Dropdown(
                                choices=["2025_H1","2024_H2","2024_H1","2023_H2","2023_H1"],
                                value="2024_H2", label="Period"
                            )

                        def update_metrics(platform):
                            m = METRICS.get(platform, METRICS["meta_ads"])
                            return gr.Dropdown(choices=m, value=m[0])
                        bm_platform.change(update_metrics, inputs=bm_platform, outputs=bm_metric)

                        bm_contributor = gr.Textbox(label="Your Name / Handle (optional)", placeholder="@yourhandle")
                        bm_btn         = gr.Button("Submit Benchmark", variant="primary")
                        bm_status      = gr.Markdown("")

                        bm_btn.click(
                            submit_benchmark,
                            inputs=[bm_platform, bm_industry, bm_metric, bm_value,
                                    bm_unit, bm_campaign, bm_period, bm_contributor],
                            outputs=bm_status
                        )

                    # 6c. Submit Model Results
                    with gr.Tab("🤖 Submit Model Result"):
                        gr.Markdown("""
### Submit Your Model's Evaluation Results

Run our evaluator and submit your results to appear on the leaderboard.

```bash
git clone https://github.com/Hawky-ai/pm-AGI
cd pm-AGI
pip install -r requirements.txt

# Run evaluation
python evaluate.py --model YOUR_MODEL --provider openai --api-key YOUR_KEY

# Result saved to results/YOUR_MODEL_timestamp.json
```

Then upload the JSON file below to validate it, and open a Pull Request.
""")
                        with gr.Row():
                            mr_model    = gr.Textbox(label="Model Name", placeholder="gpt-4o, llama-3.3-70b, etc.")
                            mr_provider = gr.Dropdown(
                                choices=["OpenAI","Anthropic","Google","Meta","Mistral AI","DeepSeek","Other"],
                                value="OpenAI", label="Provider"
                            )
                        mr_file   = gr.Textbox(label="Paste results JSON", lines=8, placeholder='{\n  "model": "your-model",\n  "overall_score": 0.82,\n  ...\n}')
                        mr_notes  = gr.Textbox(label="Notes (optional)", placeholder="Quantization, prompting strategy, etc.")
                        mr_btn    = gr.Button("Validate & Submit", variant="primary")
                        mr_status = gr.Markdown("")

                        mr_btn.click(
                            submit_model_result,
                            inputs=[mr_file, mr_model, mr_provider, mr_notes],
                            outputs=mr_status
                        )

            # ── 7. About ────────────────────────────────────────────────────
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
## About PM-AGI Benchmark v2

**PM-AGI** is the open-source benchmark for evaluating LLMs on **performance marketing reasoning** — the discipline of running, optimizing, and scaling paid advertising on Meta and Google.

### Why v2 Matters
LLMs are increasingly used by performance marketers to analyse data, troubleshoot campaigns, and make optimization decisions. v1 (100 questions) measured baseline knowledge. **v2 (494 questions) is built to measure genuine reasoning** — multi-step diagnostic, quantitative tradeoff analysis, creative experiment design, and resistance to adversarial trap questions that pattern-match outdated 2019-era playbooks.

A model that scores 90% on knowledge recall may score 50% on diagnostic + adversarial — pm-agi v2 surfaces exactly that gap.

### Benchmark Structure (v2)

| Category | Qs | What It Tests |
|---|---|---|
| 🟦 **Meta Ads** | 227 | Campaign structure, targeting, bidding, creative, CAPI, Advantage+, iOS/SKAN, attribution |
| 🟩 **Google Ads** | 227 | Search, Smart Bidding, PMax, Quality Score, attribution, Demand Gen, feed quality |
| 🟨 **Critical Thinking** | 20 | Cross-cutting data interpretation, budget decisions, competitive analysis |
| 🟥 **Action-Based** | 20 | Real-world optimization scenarios, troubleshooting, scaling |

### Reasoning Types (v2)

| Type | Qs | What It Tests |
|---|---|---|
| 🔘 **Recall** | 219 | Platform knowledge, best-practice MCQs |
| 🔴 **Adversarial** | 80 | Trap questions — defeats pattern-matching on outdated playbooks |
| 🔵 **Diagnostic** | 69 | Multi-step root-cause reasoning over anomalous campaign data |
| 🟢 **Quantitative** | 70 | Budget allocation, marginal ROAS, LTV math, stated assumptions |
| 🟣 **Creative Strategy** | 56 | A/B test design, experiment methodology, iteration systems |

### Scoring
- **MCQ** (302 questions): 1.0 / 0.0 — exact match
- **Open-Ended** (192 questions): 0.0–1.0 — LLM-as-judge vs expert rubric (5–10 criteria per question)
- **Overall** = weighted average; per-category and per-reasoning-type breakdowns surface model strengths/weaknesses

### What's New in v2 (2026)
- 5x dataset expansion: 100 → 494 questions
- New `reasoning_type` schema field — separates recall from real reasoning
- Adversarial questions test whether models reject 2019-era playbooks (broad-match-+-Smart-Bidding > SKAGs, broad targeting > interest stacking, etc.)
- Quantitative open-ended questions require stating assumptions, not just answers
- Creative-strategy questions test experiment design rigor (Experiments tool, geo holdouts, power analysis, pre-committed decision rules)

### Roadmap
- [ ] Quarterly v2 dataset refresh as platform features evolve
- [ ] TikTok Ads category (v3)
- [ ] LinkedIn Ads category (v3)
- [ ] Amazon Ads category (v3)
- [ ] Multi-modal evaluation (image + creative analysis)
- [ ] Automated CI evaluation pipeline for new model releases

---

Built by [hawky.ai](https://hawky.ai) · MIT License · [GitHub](https://github.com/Hawky-ai/pm-AGI)
""")

        gr.HTML("""
        <div style="text-align:center;padding:18px 16px 6px;color:#9ca3af;font-size:0.8em;border-top:1px solid #f3f4f6;margin-top:14px;">
          <b>PM-AGI Benchmark</b> by <a href="https://hawky.ai" target="_blank" style="color:#1e40af;">hawky.ai</a>
          &nbsp;·&nbsp; MIT License
          &nbsp;·&nbsp; <a href="https://github.com/Hawky-ai/pm-AGI" target="_blank" style="color:#1e40af;">GitHub</a>
          &nbsp;·&nbsp; <a href="https://huggingface.co/datasets/Hawky-ai/pm-agi-benchmark" target="_blank" style="color:#1e40af;">Dataset</a>
        </div>
        """)

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
