#!/usr/bin/env python3
"""researchers.json を単一の真実源として README.md と docs/research-notes.md を生成する。

使い方:
    python3 data/gen.py            # data/researchers.json から生成
データ駆動: 手作業でREADME/notesを編集せず、本スクリプトの再実行で反映する。
"""
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "researchers.json")
README = os.path.join(ROOT, "README.md")
NOTES = os.path.join(ROOT, "docs", "research-notes.md")

# 分野コード → (emoji, 見出し, 表示順)
FIELDS = [
    ("ml",        "🧠", "機械学習 (NeurIPS / ICML / ICLR / UAI / ACML)"),
    ("theory-ml", "📐", "学習理論 (COLT / ALT / AISTATS)"),
    ("tcs",       "🧮", "理論計算機科学 (FOCS / STOC / SODA / ICALP / STACS / ESA)"),
    ("nn",        "🕸️", "ニューラルネットワーク (ICANN / IJCNN / ICONIP)"),
    ("ai",        "🤖", "人工知能 (IJCAI / AAAI / ECAI / PRICAI / IAAI / KES / ILP)"),
    ("dm",        "⛏️", "データマイニング (KDD / ICDM / WSDM / CIKM / PAKDD / SDM / ECMLPKDD)"),
    ("db",        "🗄️", "データベース (SIGMOD / VLDB / ICDE / EDBT / PODS)"),
    ("cv",        "👁️", "コンピュータビジョン (CVPR / ICCV / ECCV / BMVC / ICPR / ACCV)"),
    ("cg",        "🎨", "コンピュータグラフィックス (SIGGRAPH / SIGGRAPH Asia)"),
    ("nlp",       "💬", "自然言語処理 (ACL / EMNLP / NAACL / CoNLL / COLING / EACL)"),
    ("speech",    "🔊", "音声信号処理 (InterSpeech / ICASSP)"),
    ("ir",        "🔍", "情報検索 (SIGIR / TREC / ECIR / AIRS)"),
    ("hci",       "🖥️", "ヒューマンコンピュータインタラクション (CHI / UIST / CSCW / IUI)"),
    ("web",       "🌐", "World Wide Web (WWW / ICWSM / WI)"),
    ("ec",        "🧬", "進化計算 (GECCO / CEC)"),
    ("agents",    "🦾", "マルチエージェント (AAMAS / PRIMA)"),
    ("kr",        "📚", "知識表現 / セマンティックWeb (ISWC / KR)"),
    ("rs",        "🛒", "推薦システム / HCOMP (RecSys / HCOMP)"),
    ("rl",        "🎮", "強化学習 (NeurIPS / ICML / ICLR)"),
    ("robotics",  "🦿", "ロボティクス / Embodied AI (ICRA / IROS / RSS / CoRL)"),
]
FIELD_ORDER = {code: i for i, (code, _, _) in enumerate(FIELDS)}
FIELD_TITLE = {code: f"{emoji} {title}" for code, emoji, title in FIELDS}

INDUSTRY_KEYS = [
    "Google", "DeepMind", "Meta", "FAIR", "Microsoft", "OpenAI", "Anthropic",
    "NVIDIA", "Amazon", "Apple", "IBM", "Adobe", "Baidu", "Alibaba", "Tencent",
    "Huawei", "ByteDance", "Salesforce", "Netflix", "Bell Labs", "Yahoo",
    "Samsung", "Intel", "Qualcomm", "Sony", "Bosch", "Nuance", "Cohere",
    "Mistral", "xAI", "Allen Institute", "AI2", "Toyota Research", "Snap",
]


def s(v):
    """list/None/str を表示用文字列に正規化。"""
    if v is None:
        return ""
    if isinstance(v, list):
        return ", ".join(str(x) for x in v if x)
    return str(v)


def slugify(title):
    """GitHubのアンカー生成規則に従う。小文字化→英数字(CJK含む)/空白/ハイフン以外を除去
    (絵文字・記号は除去)→空白をハイフンに。連続ハイフンは圧縮しない(GitHub準拠)。"""
    t = title.lower()
    out = [ch for ch in t if ch.isalnum() or ch in (" ", "-")]
    return "".join(out).replace(" ", "-")


COUNTRY_NORM = {
    "united states": "USA", "united states of america": "USA", "us": "USA",
    "u.s.": "USA", "u.s.a.": "USA", "america": "USA",
    "united kingdom": "UK", "u.k.": "UK", "england": "UK", "britain": "UK",
    "korea": "South Korea", "republic of korea": "South Korea",
    "people's republic of china": "China", "prc": "China", "p.r. china": "China",
    "the netherlands": "Netherlands",
}


def norm_country(c):
    c = s(c).strip()
    if not c:
        return ""
    # 「A/B」「A・B」等の複合は先頭を採用
    first = re.split(r"[/・,;|]", c)[0].strip()
    return COUNTRY_NORM.get(first.lower(), first)


def is_industry(aff):
    return any(k.lower() in (aff or "").lower() for k in INDUSTRY_KEYS)


def fmt_entry(r):
    name = s(r.get("name", "?")).strip()
    hp = s(r.get("homepage")) or s(r.get("scholar")) or s(r.get("dblp")) or ""
    name_md = f"[{name}]({hp})" if hp else name
    aff = s(r.get("affiliation")).strip()
    country = s(r.get("country")).strip()
    origin = s(r.get("origin")).strip()
    loc = country
    if origin and origin != country:
        loc = f"{country}{'・' if country else ''}出身:{origin}".strip("・")
    topics = s(r.get("topics")).strip()
    contrib = s(r.get("key_contributions")).strip()
    awards = s(r.get("awards")).strip()
    metrics = s(r.get("metrics")).strip()

    parts = [f"**{name_md}**"]
    head = aff
    if loc:
        head = f"{aff}（{loc}）" if aff else f"（{loc}）"
    if head:
        parts.append(head)
    tail = []
    if topics:
        tail.append(topics)
    if contrib:
        tail.append(contrib)
    seg = "；".join(tail)
    line = " — ".join(parts)
    if seg:
        line += f" — {seg}"
    extra = []
    if awards:
        extra.append(f"🏆{awards}")
    if metrics:
        extra.append(f"📊{metrics}")
    if extra:
        line += " " + " · ".join(extra)
    return f"- {line}"


def sort_key(r):
    # 受賞ありを先に、その後 name 昇順
    return (0 if r.get("awards") else 1, r.get("name", "").lower())


def load():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "researchers" in data:
        data = data["researchers"]
    return data


def gen_readme(rows, as_of):
    by_field = defaultdict(list)
    for r in rows:
        by_field[r.get("primary_field", "ml")].append(r)

    present = [c for c, _, _ in FIELDS if by_field.get(c)]
    out = []
    out.append("# Awesome AI Researchers [![Awesome](https://awesome.re/badge.svg)](https://awesome.re) [![License: CC0-1.0](https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg)](LICENSE)")
    out.append("")
    out.append("> AI関連の各分野で**継続的に影響力ある仕事をしている研究者**を、研究サーベイの出発点として横断的にキュレーションしたリストです。所属・所在国・出身を幅広く調査し、アカデミアと産業界の双方、古典的巨匠から現役トップまでを対象としています。")
    out.append("")
    out.append(f"**収録数: {len(rows)} 名** / {len(present)} 分野（最終更新: {as_of}）")
    out.append("")
    out.append("## 凡例 / 収録基準")
    out.append("")
    out.append("以下のいずれかを満たす研究者を収録（分野ごとに基準は調整、例外を許容）:")
    out.append("")
    out.append("- トップカンファレンス/ジャーナルで**継続的に**影響力ある論文を出版")
    out.append("- 毎年複数本を主要会議に通している（prolific）/ 被引用数が非常に多い")
    out.append("- 分野の**基礎を成す重要な仕事**（古典・ブレイクスルー）をした")
    out.append("- 主要受賞（Turing / Gödel / Nevanlinna / Test-of-Time / 各学会 Fellow 等）")
    out.append("")
    out.append("各エントリは `氏名 — 所属（所在国・出身） — 研究テーマ；代表的貢献 🏆受賞 📊指標` の形式。被引用数・h-indexは概算です。")
    out.append("")
    out.append("> 詳細なメタデータ・全調査結果・分野別/地域別の統計は [docs/research-notes.md](docs/research-notes.md)、収集手法は [docs/best-practice.md](docs/best-practice.md) を参照。")
    out.append("")
    out.append("## 目次")
    out.append("")
    for c in present:
        title = FIELD_TITLE[c]
        out.append(f"- [{title}](#{slugify(title)}) ({len(by_field[c])})")
    out.append("")
    for c in present:
        title = FIELD_TITLE[c]
        out.append(f"## {title}")
        out.append("")
        for r in sorted(by_field[c], key=sort_key):
            out.append(fmt_entry(r))
        out.append("")
    out.append("## 貢献 / Contributing")
    out.append("")
    out.append("掲載基準を満たす研究者の追加・修正は歓迎します。`data/researchers.json` を編集し `python3 data/gen.py` を実行してください（README/notesは自動生成です。直接編集しないこと）。")
    out.append("")
    out.append("## License")
    out.append("")
    out.append("[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](LICENSE) — CC0 1.0（パブリックドメイン）。")
    out.append("")
    return "\n".join(out)


def gen_notes(rows, as_of):
    out = []
    out.append("# 調査ノート（research-notes.md）")
    out.append("")
    out.append(f"`data/researchers.json`（最終更新: {as_of}）の全エントリと統計。READMEは分類済み一覧に徹し、本ノートに全メタデータ・出典・統計を集約する。")
    out.append("")
    # 統計
    out.append("## 統計")
    out.append("")
    out.append(f"- 総収録数: **{len(rows)}** 名")
    fc = Counter(r.get("primary_field", "?") for r in rows)
    out.append("")
    out.append("### 分野別")
    out.append("")
    out.append("| 分野 | 人数 |")
    out.append("|:--|--:|")
    for c, _, _ in FIELDS:
        if fc.get(c):
            out.append(f"| {FIELD_TITLE[c]} | {fc[c]} |")
    other = {k: v for k, v in fc.items() if k not in FIELD_ORDER}
    for k, v in sorted(other.items()):
        out.append(f"| {k} | {v} |")
    out.append("")
    # 地域別（所在国）
    cc = Counter(norm_country(r.get("country")) or "不明" for r in rows)
    out.append("### 所在国別（現所属拠点・上位）")
    out.append("")
    out.append("| 国 | 人数 |")
    out.append("|:--|--:|")
    for k, v in cc.most_common(30):
        out.append(f"| {k} | {v} |")
    out.append("")
    # 出身国別（多様性の実態）
    oc = Counter(norm_country(r.get("origin")) or "不明/未記載" for r in rows)
    out.append("### 出身/国籍別（多様性の実態・上位）")
    out.append("")
    out.append("> `country`(現所属拠点)は米国に集中するが、`origin`(出身)で見ると地理的多様性が高い。")
    out.append("")
    out.append("| 出身 | 人数 |")
    out.append("|:--|--:|")
    for k, v in oc.most_common(30):
        out.append(f"| {k} | {v} |")
    out.append("")
    # 産学
    ind = sum(1 for r in rows if is_industry(r.get("affiliation", "")))
    out.append("### 産業界 / アカデミア（所属キーワードによる概算）")
    out.append("")
    out.append(f"- 産業界に関与: 約 **{ind}** 名")
    out.append(f"- 主にアカデミア: 約 **{len(rows) - ind}** 名")
    out.append("")
    # 全エントリ表
    out.append("## 全エントリ")
    out.append("")
    by_field = defaultdict(list)
    for r in rows:
        by_field[r.get("primary_field", "?")].append(r)
    ordered = sorted(by_field.keys(), key=lambda c: FIELD_ORDER.get(c, 999))
    for c in ordered:
        out.append(f"### {FIELD_TITLE.get(c, c)}")
        out.append("")
        out.append("| 氏名 | 所属 | 所在/出身 | 研究テーマ | 代表的貢献 | 受賞 | 指標 | 収録理由 | 出典 |")
        out.append("|:--|:--|:--|:--|:--|:--|:--|:--|:--|")
        for r in sorted(by_field[c], key=sort_key):
            cells = [
                s(r.get("name")),
                s(r.get("affiliation")),
                "/".join(x for x in [s(r.get("country")), s(r.get("origin"))] if x),
                s(r.get("topics")),
                s(r.get("key_contributions")),
                s(r.get("awards")),
                s(r.get("metrics")),
                s(r.get("inclusion_reason")),
                s(r.get("sources")),
            ]
            cells = [x.replace("|", "\\|").replace("\n", " ") for x in cells]
            out.append("| " + " | ".join(cells) + " |")
        out.append("")
    return "\n".join(out)


def main():
    rows = load()
    # 重複排除（name+affiliation 正規化）
    seen = {}
    for r in rows:
        key = (r.get("name", "").strip().lower(), (r.get("affiliation", "")[:20]).strip().lower())
        if key not in seen:
            seen[key] = r
    rows = list(seen.values())
    as_of = os.environ.get("AS_OF", "2026-06-05")
    with open(README, "w", encoding="utf-8") as f:
        f.write(gen_readme(rows, as_of))
    with open(NOTES, "w", encoding="utf-8") as f:
        f.write(gen_notes(rows, as_of))
    print(f"生成完了: {len(rows)} 名 → README.md, docs/research-notes.md")


if __name__ == "__main__":
    main()
