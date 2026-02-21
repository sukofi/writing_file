#!/usr/bin/env python3
"""
h2直下画像生成スクリプト
- KWフォルダを引数で指定
- Vertex AI Imagen 3 で画像生成
- 16:9 アスペクト比、圧縮して保存・HTMLへ挿入
"""

import os
import re
import sys
import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # scripts/ の親 = プロジェクトルート
DAIKICHI_IMAGE = PROJECT_ROOT / "00.共通素材" / "daikichi_kyusyu.png"


def load_config(kw_dir: Path) -> tuple[Path, Path, Path]:
    """KWフォルダからHTML・プロンプト・画像先を取得"""
    html_files = list(kw_dir.glob("初稿：*.html"))
    if not html_files:
        alt_html = kw_dir / "初稿_新.html"
        if alt_html.exists():
            html_files = [alt_html]
    if not html_files:
        raise FileNotFoundError(f"初稿HTML（初稿：*.html または 初稿_新.html）が見つかりません: {kw_dir}")
    html_file = html_files[0]
    prompts_file = kw_dir / "image_prompts.yaml"
    if not prompts_file.exists():
        raise FileNotFoundError(f"image_prompts.yaml が見つかりません: {kw_dir}")
    images_dir = kw_dir / "images"
    images_dir.mkdir(exist_ok=True)
    return html_file, prompts_file, images_dir


def yaml_to_prompt(yaml_text: str, currency_mode: bool = True) -> str:
    """YAML形式のプロンプトをImagen用の英文プロンプトに変換"""
    lines = yaml_text.strip().split("\n")
    parts = []
    for line in lines:
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            if key == "avoid":
                continue
            if key and val:
                parts.append(val)
    base = " ".join(parts)
    prefix = (
        "Japanese 10000 yen banknote, ten thousand yen note, highest denomination. NOT 1000 yen, NOT 5000 yen. NOT US dollar. "
        if currency_mode
        else ""
    )
    # Imagen 3 高品質化: 4K, HDR, professional photography, sharp focus（公式ガイド準拠）
    quality = "4K HDR professional photograph, sharp focus, high detail, controlled studio lighting, "
    return (
        f"{quality}"
        f"16:9 aspect ratio. "
        f"{prefix}"
        f"{base} "
        f"Do not reproduce any real currency design, logos, or identifiable security features. "
        f"Abstract representation only."
    )


def generate_with_google_genai(prompt: str, output_path: Path) -> bool:
    """Vertex AI Imagen 3 で画像生成（google-cloud-aiplatform 使用）"""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        return False

    # ADC 利用時はクォータプロジェクトが必要（403 回避）
    if "GOOGLE_CLOUD_QUOTA_PROJECT" not in os.environ:
        os.environ["GOOGLE_CLOUD_QUOTA_PROJECT"] = project

    # Imagen は us-central1 を推奨（asia-northeast1 で DNS エラーになる環境あり）
    location = "us-central1"

    try:
        import vertexai
        from vertexai.vision_models import ImageGenerationModel

        vertexai.init(project=project, location=location)

        for model_id in (
            "imagen-3.0-generate-002",
            "imagen-3.0-generate-001",
            "imagen-3.0-fast-generate-001",
            "imagegeneration@006",
            "imagegeneration@002",
        ):
            try:
                model = ImageGenerationModel.from_pretrained(model_id)
                response = model.generate_images(
                    prompt=prompt,
                    number_of_images=1,
                    aspect_ratio="16:9",
                )
                if response and response.images:
                    out = output_path.with_suffix(".png")
                    response.images[0].save(str(out))
                    return True
            except Exception as ex:
                print(f"    {model_id}: {ex}", flush=True)
                continue
    except Exception as e:
        print(f"  Vertex AI error: {e}", flush=True)
    return False


def compress_image(input_path: Path, quality: int = 85, max_width: int = 1920) -> Path:
    """画像を圧縮してJPEG保存"""
    try:
        from PIL import Image

        img = Image.open(input_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        w, h = img.size
        if w > max_width:
            ratio = max_width / w
            img = img.resize((max_width, int(h * ratio)), Image.Resampling.LANCZOS)
        output_path = input_path.with_suffix(".jpg")
        img.save(output_path, "JPEG", quality=quality, optimize=True)
        if output_path != input_path and input_path.exists():
            input_path.unlink()
        return output_path
    except Exception as e:
        print(f"  Compression warning: {e}")
        return input_path


def update_html(html_file: Path, alt_to_src: dict) -> None:
    """HTML内のimgタグのsrcを更新"""
    text = html_file.read_text(encoding="utf-8")
    for alt, src in alt_to_src.items():
        text = re.sub(
            rf'<img class="aligncenter size-full" src="" alt="{re.escape(alt)}"',
            f'<img class="aligncenter size-full" src="{src}" alt="{alt}"',
            text,
            count=1,
        )
    html_file.write_text(text, encoding="utf-8")


def main():
    if len(sys.argv) < 2:
        print("使い方: python generate_h2_images.py <KWフォルダパス>")
        print("例: python generate_h2_images.py \"01.対策KW/一万円札 ホログラムなし\"")
        sys.exit(1)

    kw_dir = Path(sys.argv[1]).resolve()
    if not kw_dir.is_dir():
        print(f"エラー: フォルダが見つかりません: {kw_dir}")
        sys.exit(1)

    try:
        from dotenv import load_dotenv
        load_dotenv(SCRIPT_DIR / ".env")
        load_dotenv(kw_dir / ".env")
    except ImportError:
        pass

    try:
        html_file, prompts_file, images_dir = load_config(kw_dir)
    except FileNotFoundError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    prompts_data = yaml.safe_load(prompts_file.read_text(encoding="utf-8"))
    prompts = prompts_data["prompts"]
    currency_mode = prompts_data.get("currency_mode", True)

    alt_to_src = {}
    for i, item in enumerate(prompts):
        pid = item["id"]
        alt = item["alt"]
        item_currency = item.get("currency_mode", currency_mode)
        prompt_en = yaml_to_prompt(item["yaml"], item_currency)
        output_path = images_dir / f"{pid}.png"

        print(f"\n[{i+1}/{len(prompts)}] {item['h2'][:40]}...", flush=True)

        success = False
        if output_path.exists():
            print(f"  既存: {output_path}", flush=True)
            success = True
        elif item.get("use_fixed") and DAIKICHI_IMAGE.exists():
            import shutil
            shutil.copy(DAIKICHI_IMAGE, output_path.with_suffix(".png"))
            success = True
            print(f"  固定画像を使用: {DAIKICHI_IMAGE.name}", flush=True)
        else:
            print("  Vertex AI 画像生成中...", flush=True)
            success = generate_with_google_genai(prompt_en, output_path)

        if success:
            compressed = compress_image(output_path)
            rel_path = f"images/{compressed.name}"
            alt_to_src[alt] = rel_path
            print(f"  OK: {rel_path}", flush=True)
        else:
            print("  SKIP: API未設定またはエラー", flush=True)

    if alt_to_src:
        update_html(html_file, alt_to_src)
        print(f"\nHTML更新完了: {len(alt_to_src)} 枚の画像を挿入", flush=True)
    else:
        print("\n画像が生成されませんでした。", flush=True)


if __name__ == "__main__":
    main()
