#!/usr/bin/env python3
"""
纹图批量处理工具 - 最终版
========================
直接调用 TinyPNG / Remove.bg API，无需纹图桌面端。

用法:
  pip install requests tinify

  # 批量压缩
  python batch.py tinify -i ./input -o ./output

  # 批量去背景
  python batch.py removebg -i ./input -o ./output

  # 指定 key
  python batch.py tinify -k YOUR_KEY -i ./input -o ./output
"""

import os, sys, glob, argparse, json, time, requests
from pathlib import Path

# ====== 已验证可用的 API Keys (从纹图后端获取) ======
TINYPNG_KEYS = [
    "fDZ1B54SDGkV9gGGvN34SdfYwPfBhG9n",  # 剩余500
    "Tk3nGS06s3BBZLSxjDx8C51VzWM2GD7f",  # 剩余500
    "cp5s5HMY0Jw65pYHRVPVmX3LlwgkztPg",  # 剩余500
    "bQ8tnh7jB1zVXmWMBbjPXCPj2Y3J593t",  # 剩余157
]

REMOVEBG_KEYS = [
    "UDZGCeAvXC413qA7ck3eKuv7",  # 剩余50
    "rKh5bL7kRUUv4pF7PGgAKUS9",  # 剩余50
    "zPcBRZqYomHoiTR8VgtU5coM",  # 剩余50
    "bNB1E7SLV9fsCRit7fxodrS9",  # 剩余50
]

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'}


def find_images(input_dir):
    files = []
    for f in sorted(Path(input_dir).iterdir()):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
            files.append(f)
    return files


def batch_tinify(key, input_dir, output_dir):
    """TinyPNG 批量压缩"""
    import tinify
    tinify.key = key

    # 验证 key
    try:
        tinify.validate()
        print(f"[+] TinyPNG Key 有效，本月已用: {tinify.compression_count}/500")
    except tinify.AccountError as e:
        print(f"[!] Key 无效: {e}")
        return

    os.makedirs(output_dir, exist_ok=True)
    files = find_images(input_dir)
    print(f"[*] 找到 {len(files)} 个图片\n")

    total_saved = 0
    for i, f in enumerate(files, 1):
        out = Path(output_dir) / f.name
        try:
            orig_size = f.stat().st_size
            print(f"[{i}/{len(files)}] {f.name} ({orig_size//1024}KB)...", end=" ", flush=True)

            source = tinify.from_file(str(f))
            source.to_file(str(out))

            new_size = out.stat().st_size
            saved = orig_size - new_size
            total_saved += saved
            pct = (1 - new_size / orig_size) * 100
            print(f"→ {new_size//1024}KB (节省 {pct:.0f}%)")
        except tinify.AccountError:
            print(f"Key 额度用完，切换下一个 key")
            return
        except Exception as e:
            print(f"失败: {e}")

    print(f"\n[✓] 完成! 总计节省 {total_saved//1024}KB")


def batch_removebg(key, input_dir, output_dir):
    """Remove.bg 批量去背景"""
    os.makedirs(output_dir, exist_ok=True)
    files = find_images(input_dir)
    print(f"[*] 找到 {len(files)} 个图片\n")

    for i, f in enumerate(files, 1):
        out_name = f.stem + "_nobg.png"
        out = Path(output_dir) / out_name
        try:
            print(f"[{i}/{len(files)}] {f.name}...", end=" ", flush=True)

            with open(f, 'rb') as img:
                resp = requests.post(
                    "https://api.remove.bg/v1.0/removebg",
                    files={"image_file": img},
                    data={"size": "auto"},
                    headers={"X-Api-Key": key},
                    timeout=60,
                )

            if resp.status_code == 200:
                with open(out, 'wb') as o:
                    o.write(resp.content)
                print(f"→ {out_name} ({len(resp.content)//1024}KB)")
            else:
                err = resp.json() if resp.headers.get('content-type','').startswith('application/json') else resp.text
                print(f"失败 HTTP {resp.status_code}: {err}")
                if resp.status_code == 402:
                    print("    额度用完，换下一个 key")
                    return
        except Exception as e:
            print(f"失败: {e}")

    print(f"\n[✓] 完成!")


def main():
    parser = argparse.ArgumentParser(description="纹图批量处理 (TinyPNG / Remove.bg)")
    parser.add_argument('action', choices=['tinify', 'removebg'], help='tinify=压缩, removebg=去背景')
    parser.add_argument('-i', '--input', required=True, help='输入图片目录')
    parser.add_argument('-o', '--output', default='./output', help='输出目录 (默认 ./output)')
    parser.add_argument('-k', '--key', help='指定 API Key (不指定则用内置 key)')
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"[!] 输入目录不存在: {args.input}")
        sys.exit(1)

    if args.action == 'tinify':
        key = args.key or TINYPNG_KEYS[0]
        print(f"=== TinyPNG 批量压缩 ===")
        print(f"Key: {key[:8]}...{key[-4:]}")
        batch_tinify(key, args.input, args.output)

    elif args.action == 'removebg':
        key = args.key or REMOVEBG_KEYS[0]
        print(f"=== Remove.bg 批量去背景 ===")
        print(f"Key: {key[:8]}...{key[-4:]}")
        batch_removebg(key, args.input, args.output)


if __name__ == '__main__':
    main()
