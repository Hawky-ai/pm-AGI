#!/usr/bin/env python3
"""
Process community submissions from the HF contributions dataset.
Reviews pending question submissions and benchmark data, then merges approved ones.

Usage:
  python scripts/process_submissions.py --review          # List pending submissions
  python scripts/process_submissions.py --approve ID      # Approve a submission
  python scripts/process_submissions.py --reject ID       # Reject a submission
  python scripts/process_submissions.py --merge           # Merge all approved into dataset
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

DATASET_PATH    = Path("benchmark/dataset.json")
SUBMISSIONS_PATH = Path("data/question_submissions.json")
BENCHMARKS_PATH = Path("data/industry_benchmarks.json")


def load_json(path):
    with open(path) as f:
        content = re.sub(r'//.*?\n', '\n', f.read())
    return json.loads(content)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def list_pending():
    subs = load_json(SUBMISSIONS_PATH)
    pending = [s for s in subs["submissions"] if s.get("status") == "pending"]
    print(f"\n{len(pending)} pending submissions:\n")
    for s in pending:
        print(f"  [{s['id']}] {s['type']} | {s.get('category','')} | {s.get('difficulty','')} | {s.get('submitted_at','')[:10]}")
        print(f"         Q: {s.get('question','')[:80]}...")
        print()


def approve_submission(sub_id):
    subs = load_json(SUBMISSIONS_PATH)
    for s in subs["submissions"]:
        if s["id"] == sub_id:
            s["status"] = "approved"
            s["reviewed_at"] = datetime.utcnow().isoformat() + "Z"
            save_json(SUBMISSIONS_PATH, subs)
            print(f"✅ Approved: {sub_id}")
            return
    print(f"❌ Not found: {sub_id}")


def reject_submission(sub_id, reason=""):
    subs = load_json(SUBMISSIONS_PATH)
    for s in subs["submissions"]:
        if s["id"] == sub_id:
            s["status"] = "rejected"
            s["reject_reason"] = reason
            s["reviewed_at"] = datetime.utcnow().isoformat() + "Z"
            save_json(SUBMISSIONS_PATH, subs)
            print(f"✅ Rejected: {sub_id}")
            return
    print(f"❌ Not found: {sub_id}")


def merge_approved():
    subs    = load_json(SUBMISSIONS_PATH)
    dataset = load_json(DATASET_PATH)
    approved = [s for s in subs["submissions"] if s.get("status") == "approved"]

    if not approved:
        print("No approved submissions to merge.")
        return

    existing_ids = {q["id"] for q in dataset["questions"]}
    merged = 0

    for s in approved:
        q = {
            "id":           s["id"],
            "category":     s["category"],
            "subcategory":  s.get("subcategory", ""),
            "difficulty":   s["difficulty"],
            "type":         s["type"],
            "question":     s["question"],
            "options":      s.get("options", {}),
            "answer":       s.get("answer", ""),
            "answer_criteria": s.get("answer_criteria", []),
            "explanation":  s.get("explanation", ""),
            "tags":         s.get("tags", []),
            "submitted_by": s.get("submitter_name", "community"),
        }
        if q["id"] not in existing_ids:
            dataset["questions"].append(q)
            s["status"] = "merged"
            merged += 1
            print(f"  ✅ Merged: {q['id']} — {q['question'][:60]}...")

    dataset["total_questions"] = len(dataset["questions"])
    save_json(DATASET_PATH, dataset)
    save_json(SUBMISSIONS_PATH, subs)
    print(f"\n✅ Merged {merged} questions. Dataset now has {dataset['total_questions']} questions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--review",  action="store_true")
    parser.add_argument("--approve", metavar="ID")
    parser.add_argument("--reject",  metavar="ID")
    parser.add_argument("--reason",  default="")
    parser.add_argument("--merge",   action="store_true")
    args = parser.parse_args()

    if args.review:   list_pending()
    elif args.approve: approve_submission(args.approve)
    elif args.reject:  reject_submission(args.reject, args.reason)
    elif args.merge:   merge_approved()
    else:              parser.print_help()
