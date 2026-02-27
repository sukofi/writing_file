---
name: h2画像生成
description: 買取系SEO記事の初稿（初稿：[KW名].html）が完了した後、image_prompts.yamlをKWフォルダに作成・保存し、h2直下の画像を生成・圧縮・保存・HTML挿入する。初稿ごとにyaml作成が必須。Use when 初稿完了, 初稿ができた, h2画像生成, h2用画像を作成, image_prompts.yaml作成, or after drafting 初稿.html.
---

# h2画像生成：初稿完了時のフロー

初稿HTMLが完成したら、各h2直下に配置する画像を生成し、圧縮して保存・HTMLへ挿入する。

## フロー（生成→保存）

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. 準備                                                                  │
│    ├─ image_prompts.yaml（h2ごとのプロンプト）を確認・作成                 │
│    ├─ .env（GOOGLE_CLOUD_PROJECT または GOOGLE_API_KEY）を確認            │
│    └─ 初稿HTMLに <img src="" alt="..." /> のプレースホルダがあることを確認  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. 画像生成                                                              │
│    ├─ 大吉訴求h2（use_fixed: true）→ 00.共通素材/daikichi_kyusyu.png をコピー │
│    └─ その他h2 → Vertex AI Imagen 3 でプロンプトに基づき生成               │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. 圧縮                                                                  │
│    └─ JPEG品質85%、最大幅1920pxで保存                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. 保存・挿入                                                             │
│    ├─ images/img_01.jpg 〜 img_XX.jpg をKWフォルダ内 images/ に保存       │
│    └─ 初稿HTMLの src="" を images/img_XX.jpg に更新                       │
└─────────────────────────────────────────────────────────────────────────┘
```

## 実行手順

1. **scriptsフォルダへ移動**
   ```
   cd scripts/h2画像生成
   ```

2. **仮想環境のセットアップ**（初回のみ）
   ```
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **スクリプト実行**（KWフォルダパスを引数で指定）
   ```
   .venv/bin/python generate_h2_images.py "01.対策KW/一万円札 ホログラムなし"
   ```

4. **出力確認**  
   `images/` に img_01.jpg 〜 が保存され、初稿HTMLの `src=""` が自動更新されていることを確認

## ファイル配置

| 場所 | ファイル | 役割 |
|------|----------|------|
| `scripts/h2画像生成/` | `generate_h2_images.py` | 生成・圧縮・HTML更新スクリプト |
| `scripts/h2画像生成/` | `requirements.txt` | 依存パッケージ |
| `scripts/h2画像生成/` | `.env` | GOOGLE_CLOUD_PROJECT または GOOGLE_API_KEY |
| KWフォルダ内 | `image_prompts.yaml` | h2ごとの画像プロンプト |
| KWフォルダ内 | `初稿：[KW名].html` | 挿入先HTML |
| プロジェクトルート | `00.共通素材/daikichi_kyusyu.png` | 大吉訴求h2用固定画像 |

## 大吉訴求h2の固定画像

大吉訴求ブロック（例：紙幣の査定・買取は『買取大吉』にお任せ）のh2画像は**毎回固定画像を使用**する。

- **画像パス**: `00.共通素材/daikichi_kyusyu.png`
- **image_prompts.yaml**: 該当h2に `use_fixed: true` を付与
- スクリプトは `use_fixed: true` のときAPI生成をスキップし、固定画像をコピーする

## プロンプトのルール（image_prompts.yaml）

- **文脈解析**: 主役・雰囲気（清潔感・高級感・安心感）を判断
- **商標配慮**: 実物紙幣の精密再現は避け、質感・シルエットで表現
- **スタイル**: フォトリアル、スタジオライティング、16:9
- **一万円札の場合**: 「Japanese 10000 yen banknote」「ten thousand yen」「NOT 1000 yen, NOT 5000 yen」を明記（1000円札にならないよう）
- **Q&A見出し**: Q&Aの画像は**「Q&A」の文字を大きく入れて**、質問見出しだと一目で認識しやすくする。FAQアイコン・クエスチョンマークと組み合わせてもよい。**対策KWは含めない**（紙幣・商品名・品目などは指定しない）。

### お金・紙幣に関する記事の画像は「お金を必要としない」写真構成にする

**お金が「抜けた」画像にならないよう、そもそもお金が登場しないシーンを選ぶ。** 空のカウンター・ルーペだけの手・空のスリーブなどは「何かが欠けている」印象になる。見出しのテーマを、お金が最初から存在しない完結した写真で表現する。

| 見出しのテーマ | お金を必要としない写真構成 |
|----------------|----------------------------|
| 紹介・発行経緯 | 守礼門の風景、歴史的建造物の全景（ travel写真として完結） |
| 消えた・普及しなかった | 光が影に溶けていく、抽象的な移り変わり |
| 今も使える？法的有効性 | 二人の会話・相談シーン（取引ではない） |
| 地域で流通 | その地域の風景（沖縄なら海・ビーチ・守礼門） |
| 価値・買取相場 | 握手シーン、信頼・合意の雰囲気（鑑定物は写さない） |
| 高く売れる条件 | 白い蘭など丁寧に手入れされた花、大切に扱う雰囲気 |
| 入手方法 | 開いた扉と光、道が続く、アクセス・可能性のイメージ |
| まとめ | 窓からの golden hour、穏やかな結論の雰囲気 |

**avoid に必ず含める**: money, cash, banknote, currency, paper money, coins, bills

**YAMLの先頭に `currency_mode: false` を設置**する。これによりスクリプトが「Japanese 10000 yen banknote」プリフィックスを付加せず、代わりに「紙幣を一切含めない」旨の指示をプロンプト末尾に追加する。

### 汎用性を高めるルール

見出しタイトルや本文内容を連想しつつ、**他記事（他券種・他品目）でも使い回せる**画像になるようプロンプトを書く。

| 方針 | 具体例 |
|------|--------|
| **額面指定を控える** | 「2000 yen」「two thousand yen」など特定額面を避け、「Japanese banknote」「paper currency」「commemorative banknote」など汎用表現を使う |
| **見出しのテーマで組む** | 見出しの「概念」（紹介・普及・流通・査定・入手・まとめ等）を捉え、そのテーマを表す構図・雰囲気で表現する |
| **avoidは共通化** | 額面固有の指定（NOT 1000 yen...）をやめ、「Exact reproduction of banknote design」「identifiable security features」などに統一 |
| **地域特化は例外** | 沖縄など記事固有の地域テーマがある場合は、その地域の雰囲気を残してよい |

### 見出しテーマ別の汎用プロンプト例（お金を必要としない構成）

| 見出しのテーマ | 汎用的なsubject例（お金が登場しない完結したシーン） |
|----------------|--------------------------------------------------|
| 紹介・発行経緯 | Shureimon gate in Okinawa, traditional red gate against sky, travel photography |
| 消えた・普及しなかった | Soft sunlight fading into shadow, light and dark gradient, passage of time |
| 今も使える？法的有効性 | Two people in friendly conversation, helpful consultation, no transaction |
| 地域で流通 | Tropical beach or coastal scenery, warm island light（沖縄なら海・守礼門） |
| 価値・買取相場 | Two people shaking hands, professional agreement, trust and transparency |
| 高く売れる条件 | Single white orchid in ceramic pot, pristine and precious, care metaphor |
| 入手方法 | Open doorway with soft light, path leading forward, access and opportunity |
| Q&A・よくある質問 | Large bold Q&A text, FAQ section header, question mark icon |
| まとめ | Golden hour sunlight through window, warm peaceful room, conclusive mood |

## image_prompts.yaml の作成（初稿ごとに必須）

**初稿ごとに `image_prompts.yaml` を作成し、当該KWフォルダ内に保存する。**

- **保存場所**: `01.対策KW/[KWフォルダ]/image_prompts.yaml`
- **作成タイミング**: 初稿HTML完成後、画像生成実行前に作成する
- **作成手順**:
  1. 既存KWフォルダの `image_prompts.yaml` を参考にする
  2. 初稿HTMLの h2 一覧に合わせて、id・h2・alt・yaml を新規作成する
  3. 大吉訴求h2には `use_fixed: true` を付与
  4. Q&Aのh2には `currency_mode: false` を付与
  5. **汎用性重視**の場合は「Japanese banknote」「paper currency」など額面を特定しない表現を使う。一万円札など券種区別が重要な場合は従来どおり額面を明記。

## 初回セットアップ（新規記事）

1. **image_prompts.yaml をKWフォルダに作成・保存**（上記セクション参照）
2. 初稿HTMLの各h2直下に `<p><img class="aligncenter size-full" src="" alt="〇〇" /></p>` を配置
3. `.env` に Vertex AI または Gemini API の認証情報を設定
