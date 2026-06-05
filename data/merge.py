#!/usr/bin/env python3
"""data/wave*/ の各JSON({"researchers":[...]} or [...]) を統合し
data/researchers.json を生成する。name+affiliation先頭で重複排除。"""
import json
import glob
import os
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "researchers.json")


def norm_name(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.strip().lower()


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "data", "wave*", "*.json")))
    rows = []
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                d = json.load(f)
        except Exception as e:
            print(f"!! パース失敗 {fp}: {e}", file=sys.stderr)
            continue
        if isinstance(d, dict) and "researchers" in d:
            d = d["researchers"]
        if not isinstance(d, list):
            print(f"!! 形式不正 {fp}", file=sys.stderr)
            continue
        rows.extend(d)
        print(f"  + {os.path.relpath(fp, ROOT)}: {len(d)}")

    seen = {}
    dups = 0
    for r in rows:
        if not isinstance(r, dict) or not r.get("name"):
            continue
        key = norm_name(r.get("name", ""))
        if key in seen:
            dups += 1
            # 既存にawards/homepageが無く新規にあれば補完
            ex = seen[key]
            for k in ("awards", "homepage", "scholar", "dblp", "metrics", "origin", "country"):
                if not ex.get(k) and r.get(k):
                    ex[k] = r[k]
            continue
        seen[key] = r
    merged = list(seen.values())
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"統合完了: 入力 {len(rows)} → 重複{dups}件除外 → {len(merged)} 名 → {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
