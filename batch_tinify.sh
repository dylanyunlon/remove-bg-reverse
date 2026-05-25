#!/bin/bash
# 纹图批量压缩 - 纯 Shell 版 (TinyPNG API)
# 用法: bash batch_tinify.sh <输入目录> [输出目录] [API_KEY]
#
# 示例:
#   bash batch_tinify.sh ./input ./output
#   bash batch_tinify.sh ./input ./output YOUR_API_KEY

INPUT_DIR="${1:-.}"
OUTPUT_DIR="${2:-./output}"
API_KEY="${3:-fDZ1B54SDGkV9gGGvN34SdfYwPfBhG9n}"

# 备用 keys (当前 key 用完时手动切换)
# Tk3nGS06s3BBZLSxjDx8C51VzWM2GD7f
# cp5s5HMY0Jw65pYHRVPVmX3LlwgkztPg
# bQ8tnh7jB1zVXmWMBbjPXCPj2Y3J593t

mkdir -p "$OUTPUT_DIR"

echo "=== TinyPNG 批量压缩 ==="
echo "输入: $INPUT_DIR"
echo "输出: $OUTPUT_DIR"
echo "Key:  ${API_KEY:0:8}...${API_KEY: -4}"
echo ""

count=0
total=0
success=0
total_saved=0

# 统计文件数
for f in "$INPUT_DIR"/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP} 2>/dev/null; do
    [ -f "$f" ] && ((total++))
done

echo "找到 $total 个图片"
echo ""

for f in "$INPUT_DIR"/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP} 2>/dev/null; do
    [ -f "$f" ] || continue
    ((count++))

    fname=$(basename "$f")
    orig_size=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null)
    orig_kb=$((orig_size / 1024))

    printf "[%d/%d] %s (%dKB)... " "$count" "$total" "$fname" "$orig_kb"

    # Step 1: 上传压缩
    response=$(curl -s -w "\n%{http_code}" \
        --user "api:$API_KEY" \
        --data-binary @"$f" \
        -H "Content-Type: application/octet-stream" \
        --max-time 60 \
        "https://api.tinify.com/shrink" 2>&1)

    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" != "201" ]; then
        echo "失败 (HTTP $http_code)"
        error=$(echo "$body" | grep -o '"message":"[^"]*"' | head -1)
        [ -n "$error" ] && echo "    $error"
        if [ "$http_code" = "429" ]; then
            echo "    额度用完，请切换 key"
            break
        fi
        continue
    fi

    # Step 2: 从响应中提取压缩后的 URL
    output_url=$(echo "$body" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -z "$output_url" ]; then
        echo "失败 (无下载URL)"
        continue
    fi

    # Step 3: 下载压缩后的文件
    curl -s -o "$OUTPUT_DIR/$fname" --max-time 60 "$output_url"

    if [ $? -eq 0 ] && [ -f "$OUTPUT_DIR/$fname" ]; then
        new_size=$(stat -c%s "$OUTPUT_DIR/$fname" 2>/dev/null || stat -f%z "$OUTPUT_DIR/$fname" 2>/dev/null)
        new_kb=$((new_size / 1024))
        saved=$((orig_size - new_size))
        total_saved=$((total_saved + saved))

        if [ "$orig_size" -gt 0 ]; then
            pct=$(( (orig_size - new_size) * 100 / orig_size ))
        else
            pct=0
        fi

        echo "→ ${new_kb}KB (节省 ${pct}%)"
        ((success++))
    else
        echo "下载失败"
    fi
done

echo ""
echo "=== 完成 ==="
echo "成功: $success/$total"
echo "总计节省: $((total_saved / 1024))KB"
