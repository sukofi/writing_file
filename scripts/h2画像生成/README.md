# h2画像生成

初稿HTMLの各h2直下に配置する画像を生成・圧縮・挿入するスクリプト。

## 使い方

```bash
cd scripts/h2画像生成
python generate_h2_images.py "01.対策KW/一万円札 ホログラムなし"
```

## 準備

- **API**: `.env` を `scripts/h2画像生成/` または KWフォルダに配置
  - `GOOGLE_CLOUD_PROJECT`（Vertex AI）または `GOOGLE_API_KEY`（Gemini API）
- **KWフォルダ内**: `image_prompts.yaml`、`初稿：〇〇.html`、h2直下に `<img src="" alt="..." />` のプレースホルダ
- **大吉訴求**: `00.共通素材/daikichi_kyusyu.png` を配置し、該当h2に `use_fixed: true` を付与

## 初回セットアップ

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
