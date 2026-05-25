#!/bin/bash
# 纹图批量去背景 - 纯 Shell 版 (Remove.bg API)
# 用法: bash batch_removebg.sh <输入目录> [输出目录] [API_KEY]
#
# 示例:
#   bash batch_removebg.sh ./input ./output
#   bash batch_removebg.sh ./input ./output YOUR_API_KEY

INPUT_DIR="${1:-.}"
OUTPUT_DIR="${2:-./output}"
API_KEY="${3:-UDZGCeAvXC413qA7ck3eKuv7}"

# 备用 keys
# rKh5bL7kRUUv4pF7PGgAKUS9
# zPcBRZqYomHoiTR8VgtU5coM
# bNB1E7SLV9fsCRit7fxodrS9

mkdir -p "$OUTPUT_DIR"

echo "=== Remove.bg 批量去背景 ==="
echo "输入: $INPUT_DIR"
echo "输出: $OUTPUT_DIR"
echo "Key:  ${API_KEY:0:8}...${API_KEY: -4}"
echo ""

count=0
total=0
success=0

for f in "$INPUT_DIR"/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP} 2>/dev/null; do
    [ -f "$f" ] && ((total++))
done

echo "找到 $total 个图片"
echo ""

for f in "$INPUT_DIR"/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP} 2>/dev/null; do
    [ -f "$f" ] || continue
    ((count++))

    fname=$(basename "$f")
    name_noext="${fname%.*}"
    out_file="$OUTPUT_DIR/${name_noext}_nobg.png"

    printf "[%d/%d] %s... " "$count" "$total" "$fname"

    http_code=$(curl -s -o "$out_file" -w "%{http_code}" \
        -X POST \
        -H "X-Api-Key: $API_KEY" \
        -F "image_file=@$f" \
        -F "size=auto" \
        --max-time 120 \
        "https://api.remove.bg/v1.0/removebg")

    if [ "$http_code" = "200" ] && [ -f "$out_file" ] && [ -s "$out_file" ]; then
        out_size=$(stat -c%s "$out_file" 2>/dev/null || stat -f%z "$out_file" 2>/dev/null)
        echo "→ ${name_noext}_nobg.png ($((out_size / 1024))KB)"
        ((success++))
    else
        echo "失败 (HTTP $http_code)"
        [ -f "$out_file" ] && cat "$out_file" 2>/dev/null | head -c 200 && echo ""
        rm -f "$out_file"
        if [ "$http_code" = "402" ]; then
            echo "    额度用完，请切换 key"
            break
        fi
    fi
done

echo ""
echo "=== 完成 ==="
echo "成功: $success/$total"
