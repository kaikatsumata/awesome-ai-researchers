# Awesome AI Researchers — 作成のベストプラクティスと調査手法

本ドキュメントは、AI研究者(人物)の awesome list を構築する過程で得た、再利用可能な指針である。
「リストのリスト」を作った [awesome-awesome](https://github.com/) の知見を、**人物キュレーション**向けに翻案した。

---

## 1. 人物リスト特有の設計原則

### リポジトリ(物)ではなく人物が対象 → 検証手段が変わる
- GitHub API のような単一の権威ソースが無い。代わりに **公式ページ / Google Scholar / DBLP /
  各学会 Fellow一覧 / 受賞公式発表** を複合的に突き合わせて実在・実績を確認する。
- 被引用数・h-index は時点で変動し出典でばらつく。**必ず「概算」と明示**し、過度に精密に書かない。

### 「なぜ載っているか」を構造化する（inclusion_reason）
- awesome list は主観に流れやすい。各人に `inclusion_reason`（基礎貢献 / 高被引用 / 受賞 / prolific 等）
  を持たせ、収録の透明性を担保する。READMEには出さず research-notes に残してもよい。

### 所在(country)と出身(origin)を分離する
- `country`（現所属拠点）は米国に強く集中する。これだけ見ると多様性が無いように見える。
- `origin`（出身/国籍）を別フィールドで持つと、**実際の地理的多様性**（中国・インド・イスラエル・
  日本・欧州各国・南米 等）が可視化できる。統計は両軸でレポートする。
- 国籍・出身は機微情報でもあるため「分かる範囲」に留め、強制しない（空を許容）。

### 分野は1次配置 + 横断タグ
- `ml`/`nn`/`rl`/`ai` は重なる。READMEの配置先は `primary_field` 1つに正規化しつつ、
  `fields[]`（横断）と `topics`（研究テーマの自由記述）で実態を表す。
- ユーザ要望により **研究テーマ(`topics`) は必須**（読者が「何の人か」を即把握できる）。

---

## 2. データ駆動パイプライン

`data/researchers.json`（単一の真実源）→ `data/gen.py` → `README.md` + `docs/research-notes.md`。

- 手作業でMarkdownを編集しない。**JSONを直し gen.py を再実行**して反映する。
- 収集は波(wave)ごとに `data/wave<N>/<group>.json` に分割出力し、`data/merge.py` で統合・重複排除。
- 重複排除は **氏名のNFKD正規化**（アクセント記号除去）で行い、既存に欠けるフィールドは後勝ちで補完。
- README は分類済み一覧に徹し、**全メタデータ・出典・統計は research-notes.md** に逃がす。

---

## 3. 調査手法（網羅性の担保）

### (A) 分野ごとの並列 fan-out
- ユーザ指定の会議群を 9 グループ程度に束ね（ml+理論 / TCS / AI+NN / DM+DB / CV+CG / NLP /
  音声+IR / HCI+Web / 進化計算+エージェント+KR+推薦）、**分野ごとに調査エージェントを並列起動**。
- 各エージェントは 40〜60 名を構造化JSONで直接ファイルに書き出す（巨大テキストの受け渡しを回避）。
- 1巡(wave 1)で約 450 名が集まる。

### (B) 受賞・Fellow一覧からの掃き出し
- 分野ごとの権威ある受賞リストを起点にすると、古典的巨匠を体系的に拾える。
  - 機械学習/AI: Turing Award, AAAI/IJCAI Fellow, Computers & Thought, ACM Fellow
  - 理論: Gödel Prize, Knuth Prize, Nevanlinna/Abacus Medal, Abel Prize
  - DB: SIGMOD Edgar F. Codd Innovations Award, VLDB Test-of-Time
  - DM: SIGKDD Innovation Award
  - CV: PAMI Distinguished Researcher, Marr Prize, Longuet-Higgins Prize
  - 音声: ISCA Medal、IR: Gerard Salton Award、HCI: CHI Academy
  - 進化計算: IEEE CIS Pioneer、エージェント: AAMAS Influential Paper、KR: SWSA Ten-Year

### (C) 多様性ギャップの能動的な穴埋め
- wave 1 後に **所在国/出身国の分布を集計**し、薄い地域（南米・アフリカ・中東・東南アジア・
  東欧、現地拠点のインド等）を名指しで追加調査する波を回す。
- 産業界（DeepMind/FAIR/MSR/OpenAI/Anthropic/NVIDIA/Adobe/Baidu/Alibaba/Tencent 等）と
  アカデミアの双方を必ず含める。

### (D) 反復で逓減を観測し飽和で止める
- wave ごとの新規追加数の逓減を見る。重複率が高くなり新規がほぼ出なくなったら飽和とみなし終了。
- 「専用の決定版が存在しない/薄い」領域は **水増しせず薄いまま明記**する（誠実さ）。

### (E) 実在確認と正直な報告
- 故人は明記（例: Jian Sun 2022、Xiaoou Tang 2023、David Blei は存命など取り違え注意）。
- 捏造URL・存在しない受賞を排除。不確実な細部（受賞年・所属詳細）は控えめに。

---

## まとめ（チェックリスト）

- [ ] `Awesome <Topic>` 命名・Awesomeバッジ・CC0ライセンス
- [ ] 目次・分野カテゴリ・1人1行・並び順(受賞→氏名)の一貫性
- [ ] `topics`(研究テーマ)必須、`inclusion_reason` で収録の透明性
- [ ] `country`(所在) と `origin`(出身) を分離し両軸で多様性を集計
- [ ] 被引用数は「概算」明示、実在は公式/Scholar/DBLP/受賞で複合検証
- [ ] データ駆動（researchers.json → gen.py）、README と notes を分離
- [ ] 分野fan-out → 受賞リスト掃き出し → 多様性ギャップ穴埋め → 飽和確認
- [ ] 故人・取り違え・捏造を排し、薄い領域は薄いまま明記
