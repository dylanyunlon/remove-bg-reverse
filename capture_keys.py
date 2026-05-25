#!/usr/bin/env python3
"""
纹图 API Key 抓取器
===================
用法：
  1. 先启动纹图（带调试端口）:
     "C:\Program Files\comqpxntool\纹图.exe" --remote-debugging-port=9222

  2. 运行本脚本:
     python capture_keys.py

  3. 在纹图里随便做一个操作（压缩一张图或去个背景）

  4. 脚本会自动抓取 API Keys 并保存

依赖: pip install websocket-client requests
"""

import json
import time
import threading
import requests
import websocket

# 禁用 SSL 警告
import urllib3
urllib3.disable_warnings()

captured_keys = {}
captured_responses = {}


def on_message(ws, message):
    """处理 CDP 消息"""
    data = json.loads(message)
    method = data.get("method", "")

    if method == "Network.responseReceived":
        url = data["params"]["response"]["url"]
        request_id = data["params"]["requestId"]

        # 检测是否是我们关心的 API
        interesting = [
            "getRandomTinyKeyData", "getRandomRmvKeyData",
            "getRmvKeyData", "getTinyKeyData",
            "auth/local", "multiusers",
            "getPixianQpsEntry", "getztcode"
        ]

        for keyword in interesting:
            if keyword in url:
                # 获取响应体
                ws.send(json.dumps({
                    "id": int(time.time() * 1000),
                    "method": "Network.getResponseBody",
                    "params": {"requestId": request_id}
                }))

                print(f"\n{'='*60}")
                print(f"[截获] {url}")
                captured_responses[request_id] = url
                break

    # 处理响应体
    if "result" in data and "body" in data.get("result", {}):
        req_id_key = None
        for rid, url in list(captured_responses.items()):
            req_id_key = rid
            break

        if req_id_key:
            body = data["result"]["body"]
            url = captured_responses.pop(req_id_key, "unknown")
            try:
                body_json = json.loads(body)
                print(f"[响应] URL: {url}")
                print(f"[数据] {json.dumps(body_json, indent=2, ensure_ascii=False)[:500]}")

                # 自动提取 key
                if "TinyKey" in url or "tinifykey" in url.lower():
                    extract_key(body_json, "TinyPNG")
                elif "RmvKey" in url or "rmvkey" in url.lower():
                    extract_key(body_json, "RemoveBG")
                elif "auth/local" in url and "jwt" in body_json:
                    captured_keys["jwt"] = body_json["jwt"]
                    print(f"\n  >>> JWT Token: {body_json['jwt'][:50]}...")
            except json.JSONDecodeError:
                print(f"[响应] {body[:200]}")
            print(f"{'='*60}")


def extract_key(data, label):
    """从响应中提取 API Key"""
    if isinstance(data, dict):
        # 递归搜索所有可能的 key 字段
        for k, v in data.items():
            if k.lower() in ('key', 'apikey', 'api_key', 'apitoken'):
                captured_keys[label] = v
                print(f"\n  >>> {label} API Key: {v}")
                return
            if isinstance(v, (dict, list)):
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            extract_key(item, label)
                else:
                    extract_key(v, label)
        # 如果找不到明确的key字段，打印完整结构
        if label not in captured_keys:
            print(f"\n  >>> {label} 完整数据 (请手动提取key):")
            print(f"      {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")


def on_error(ws, error):
    print(f"[错误] {error}")


def on_close(ws, code, reason):
    print(f"[断开] code={code}, reason={reason}")


def on_open(ws):
    print("[+] 已连接到纹图 DevTools")
    print("[*] 启用网络监控...")

    # 启用 Network domain
    ws.send(json.dumps({"id": 1, "method": "Network.enable"}))
    print("[*] 等待纹图的网络请求...")
    print("[*] 请在纹图中执行操作（压缩图片/去背景等）\n")


def main():
    print("=" * 60)
    print("  纹图 API Key 抓取器")
    print("=" * 60)

    # 获取 DevTools WebSocket URL
    try:
        resp = requests.get("http://127.0.0.1:9222/json", timeout=5)
        targets = resp.json()
    except Exception as e:
        print(f"\n[!] 无法连接到纹图 DevTools")
        print(f"    请先启动纹图：")
        print(f'    "C:\\Program Files\\comqpxntool\\纹图.exe" --remote-debugging-port=9222')
        print(f"\n    错误: {e}")
        return

    # 找到主页面
    ws_url = None
    for t in targets:
        if t.get("type") == "page":
            ws_url = t["webSocketDebuggerUrl"]
            print(f"[+] 找到纹图窗口: {t.get('title', 'unknown')}")
            break

    if not ws_url:
        # 用 browser endpoint
        ws_url = f"ws://127.0.0.1:9222/devtools/browser/{targets[0]['id']}" if targets else None
        if not ws_url:
            print("[!] 找不到可用的 DevTools target")
            return

    print(f"[+] WebSocket: {ws_url}")

    # 连接
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # 运行（Ctrl+C 退出）
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("  抓取结果汇总")
        print("=" * 60)
        if captured_keys:
            for label, key in captured_keys.items():
                print(f"  {label}: {key}")
        else:
            print("  未捕获到任何 Key")
            print("  提示：请在纹图中执行一次图片操作再试")
        print("=" * 60)

        # 保存到文件
        if captured_keys:
            with open("wentu_keys.json", "w") as f:
                json.dump(captured_keys, f, indent=2, ensure_ascii=False)
            print(f"\n  已保存到 wentu_keys.json")


if __name__ == '__main__':
    main()
