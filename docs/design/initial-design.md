# Awesome AI Researchers — 設計ドキュメント

## 目的

研究サーベイにおいて良質な情報を提供することを目的とした、AI関連分野の **影響力ある研究者** の
キュレーションリスト(awesome list)を構築する。リポジトリの読者（研究者・学生・実務家）が、
分野ごとに「誰を追うべきか」「誰の仕事が基礎/最前線か」を即座に把握できることを目指す。

awesome-awesome（リストのリスト）の **データ駆動生成パイプライン** の知見を流用するが、
収集対象は GitHub リポジトリではなく **人物** である点が本質的に異なる。

## 収録基準（分野ごとに調整可、例外許容）

以下のいずれかを満たす研究者を収録対象とする:

- トップカンファレンス/ジャーナルで **継続的に** 影響力ある論文を出版している
- 毎年複数本を主要会議に通している（prolific）
- 被引用数が非常に多い（分野により h-index / 総被引用数の閾値は調整）
- 分野の **基礎を成す重要な仕事**（古典・ブレイクスルー）をした
- 主要な受賞歴（Turing Award, Nevanlinna, Gödel Prize, 各学会 Fellow, Test-of-Time 等）

例外は許容する（基準を厳密に満たさなくても歴史的・分野代表的に重要なら収録）。

## 調査範囲（人物の多様性）

所在国・出身地・国籍・研究機関・大学・企業を **幅広く** 調査する。北米/欧州偏重を避け、
アジア（日本・中国・韓国・インド・シンガポール等）、中東、南米、オセアニアも意識的に拾う。
産業界（Google DeepMind, Meta FAIR, Microsoft Research, OpenAI, Anthropic, NVIDIA 等）と
アカデミアの双方を対象とする。

## 対象分野（ユーザ指定の会議群に対応）

機械学習(NeurIPS/ICML/ICLR/UAI/ACML)、学習理論(COLT/ALT/AISTATS)、
理論計算機科学(FOCS/STOC/SODA/ICALP/STACS/ESA)、ニューラルネット(ICANN/IJCNN/ICONIP)、
人工知能(IJCAI/AAAI/ECAI/PRICAI/IAAI/KES/ILP)、
データマイニング(KDD/ICDM/PAKDD/SDM/DS/DSAA/ECMLPKDD/BigData/WSDM/CIKM)、
データベース(SIGMOD/VLDB/ICDE/EDBT/PODS)、
コンピュータビジョン(CVPR/ICCV/ECCV/ICIP/BMVC/ICPR/ACCV/SIGGRAPH)、
自然言語処理(ACL/EMNLP/NAACL/CoNLL/COLING/EACL/IJCNLP)、
音声信号処理(InterSpeech/ICASSP)、情報検索(SIGIR/TREC/ECIR/AIRS)、
HCI(CHI/UIST/CSCW/IUI)、WWW(WWW/ICWSM/WI)、進化計算(GECCO/CEC)、
エージェント(AAMAS/PRIMA)、知識表現(ISWC)、境界領域(RecSys/HCOMP)。

## データスキーマ（data/researchers.json）

各研究者を1オブジェクトとして配列に格納。codexレビュー＆ユーザ要望（研究分野を明示）を反映し、
**研究テーマ(`topics`)・収録理由(`inclusion_reason`)・出典(`sources`)** を持たせる。

```json
{
  "name": "Geoffrey Hinton",
  "primary_field": "ml",              // 主分野コード（README配置先, 下記分類）
  "fields": ["ml", "nn"],             // 横断分野（分野間の重なりに対応）
  "topics": "深層学習, 表現学習, ニューラルネット, ボルツマンマシン",  // 研究分野/テーマ（ユーザ要望・必須）
  "affiliation": "University of Toronto; Google (emeritus)",
  "country": "Canada",                // 現在の所在国（分かる範囲・空可）
  "origin": "United Kingdom",         // 出身/国籍（分かる範囲・空可）
  "venues": ["NeurIPS", "ICML", "Nature"],
  "key_contributions": "誤差逆伝播・AlexNet・capsule networks・ボルツマンマシン",
  "awards": "Turing Award 2018, Nobel物理学賞 2024, ACM/AAAI Fellow",
  "metrics": "被引用 80万+ / h-index 180+",  // 概数・「分かる範囲」と明示
  "inclusion_reason": "基礎貢献+受賞+超高被引用",  // なぜ載るか（awesome listの透明性）
  "homepage": "https://www.cs.toronto.edu/~hinton/",
  "scholar": "https://scholar.google.com/citations?user=JicYPdAAAAAJ",
  "dblp": "https://dblp.org/pid/10/3248.html",
  "sources": ["公式ページ", "Google Scholar", "Turing Award公式"]  // 実在確認の根拠
}
```

`name` + `affiliation` で重複判定するが、表記揺れ（アクセント記号・漢字/ローマ字）に注意。
矛盾時は homepage/scholar/dblp の一致を優先根拠とする。多様性は `country`/`origin` を
強制せず「分かる範囲」で集計し、research-notes.md で分野別・地域別・産学別の偏りをレポートする。

### 分野コード（field）

`ml`(機械学習), `theory-ml`(学習理論), `tcs`(理論計算機科学), `nn`(ニューラルネット),
`ai`(人工知能/探索/プランニング), `dm`(データマイニング), `db`(データベース),
`cv`(コンピュータビジョン), `cg`(グラフィックス), `nlp`(自然言語処理),
`speech`(音声), `ir`(情報検索), `hci`(HCI), `web`(WWW), `ec`(進化計算),
`agents`(マルチエージェント), `kr`(知識表現/セマンティックWeb), `rs`(推薦),
`robotics`(ロボティクス), `rl`(強化学習) など必要に応じ追加。

## 成果物

- **README.md**: 分野ごとに分類した研究者一覧。1人1行で
  「氏名 — 所属(国) — 代表的貢献/venue/受賞」を記載。目次・凡例・収録基準付き。
- **docs/research-notes.md**: 全調査結果・統計・メタデータ・出典・分野別の調査メモを集約。
- **data/researchers.json**: 構造化データ（生成パイプラインの単一の真実源）。
- **data/gen.py**: researchers.json → README.md + research-notes.md を生成。

## 調査手法（best-practice.md の fan-out を踏襲）

1. 分野群ごとに調査エージェントを並列起動（WebSearch/WebFetch で実在確認しながら収集）。
2. 各エージェントは構造化JSON（上記スキーマ）で研究者リストを返す。
3. 集約 → 重複排除（氏名+所属で正規化）→ researchers.json に統合。
4. 波(wave)を重ね、新規追加数の逓減を観測。飽和（新規がほぼ無い）で終了。
5. 産業/地域の偏りをメタチェックし、不足地域・不足分野を追加調査。

## 品質・誠実さ

- 捏造を排除。実在確認（公式ページ/Google Scholar/DBLP/学会fellow一覧）を伴う。
- 不確実な指標（被引用数等）は概数とし「分かる範囲」と明示。
- 「決定版が存在しない/カバーが薄い」ニッチは水増しせず明記。
- ライセンスは CC0（awesome list 慣例）。
