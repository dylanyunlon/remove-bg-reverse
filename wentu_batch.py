#!/usr/bin/env python3
"""
纹图 (WenTu) 批量图片处理脚本
================================
功能：去背景、压缩(TinyPNG)
用法：python wentu_batch.py --help

依赖安装：pip install requests tinify

原理：
  1. 用激活码登录纹图 Strapi 后端，获取 JWT
  2. 用 JWT 从后端获取第三方 API Key（TinyPNG / Pixian / 佐糖）
  3. 直接用这些 Key 调用第三方 API 批量处理图片
"""

import os
import sys
import json
import time
import argparse
import hashlib
import ssl
import glob
from pathlib import Path
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# ============================================================
# 纹图后端配置 (从逆向分析获取)
# ============================================================
SERVERS = [
    "https://139.196.209.2:443/api",
    "https://43.128.79.132:443/api",
]
# 登录密码是固定的 MD5 (所有用户相同)
LOGIN_PASSWORD = "6ff44354168e5ab8bf922929524397e4"

# 内嵌的自签名客户端证书 (从 background.jsc 提取)
CLIENT_CERT_PEM = """-----BEGIN CERTIFICATE-----
MIIDdjCCAl4CCQCBbQpRSgtAHjANBgkqhkiG9w0BAQUFADCBfTELMAkGA1UEBhMC
Q04xCzAJBgNVBAgMAkhCMQswCQYDVQQHDAJXSDEQMA4GA1UECgwHbWludHJlZTEP
MA0GA1UECwwGY2xpZW50MRIwEAYDVQQDDAltaW5jbGllbnQxHTAbBgkqhkiG9w0B
CQEWDjMxMzRjbGllbnQuY29tMB4XDTIzMDgyMDA0NDQwMDlaFw0zMzA4MTcwNDQ0
MDA5WjCBfTELMAkGA1UEBhMCQ04xCzAJBgNVBAgMAkhCMQswCQYDVQQHDAJXSDEQ
MA4GA1UECgwHbWludHJlZTEPMA0GA1UECwwGY2xpZW50MRIwEAYDVQQDDAltaW5j
bGllbnQxHTAbBgkqhkiG9w0BCQEWDjMxMzRjbGllbnQuY29tMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEAy/PVtp6eGfjERa4gpL/W5s+0aCh7y4ifqIR6
Q8sSzghgDRGuhRyMXchKLc6nYmQLiWdvUKZkDzqTvvpx1cxzlf74n+/n1NbWTzSE
uiXLxh/Vc4ke79gxVHnsGeyWoSl5iWzqMVkdrH0NYoo1upmH9bl21SoZe+clnjHF
2Je3E0Z6T1t9t/wbQhO+CKQK48IvITo5nkbHrKd0Bs+2ou1gaemcbdU5ISra6xvU
lxPkQSh2zft7krhx5ts5Dn74eMREtHGYmHk2OtvBGEAOeKv3qO6VaNSHQkrdCUXX
tdaWFkWuiXVzvDWcgtx4kU3ok/PUhhi03NogYArUAqML79/3iwIDAQABMA0GCSqG
SIb3DQEBBQUAA4IBAQCWhYS1MHoInDUPDw2a/QdW91OL0zusbh74Asv2/Zq8m+xJ
5vHhfjsB3GU8c7xZy/e5UJlIGvKATtfFHwOk01FTYvxKjoLg6XMhSfThZ/IeZI0u
pB7+RYT/Cq1VOlFl3VgY1tJ2bm+0Ya3LpPJ/Q5ihzLOeVH7/UeoJEvtJ2m0NAxt
+gGm81x32RHV0VFhATkc7z4T8l9gEmCGDlvff+Ludin/hoQeL+r6qxGi/2Wivcee
QqaaBE9SRCqW1LlYa+kI8YBytF38TC4cTncdynJJQepJMPuukvoH5K+SO3/wyRIg
N/wRdJit2ktRJB0lvXjSrSPb3IqGfkofCwkK6kgJJvLFjg==
-----END CERTIFICATE-----"""

CLIENT_KEY_PEM = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAy/PVtp6eGfjERa4gpL/W5s+0aCh7y4ifqIR6Q8sSzghgDRGu
hRyMXchKLc6nYmQLiWdvUKZkDzqTvvpx1cxzlf74n+/n1NbWTzSEuiXLxh/Vc4ke
79gxVHnsGeyWoSl5iWzqMVkdrH0NYoo1upmH9bl21SoZe+clnjHF2Je3E0Z6T1t9
t/wbQhO+CKQK48IvITo5nkbHrKd0Bs+2ou1gaemcbdU5ISra6xvUlxPkQSh2zft7
krhx5ts5Dn74eMREtHGYmHk2OtvBGEAOeKv3qO6VaNSHQkrdCUXXtdaWFkWuiXVz
vDWcgtx4kU3ok/PUhhi03NogYArUAqML79/3iwIDAQABAoIBADt8fCo0q5hxqXWV
ayoCVkDt9fWnUSw1RjVAUpTxZyO256UIMjna8MntqE0KCGI3QfIqvBnu3iJe+Hbs
f0VXo6LtQkEL7Td0Df/+FnRgz8WSxWQ0a1STXxf/k7CgA/MvsKY3oTsRfgkwVDYY
j8FERJaUKKfV5qbv7VXtuIILBjfVgdR3UkQqUcQLOdUOsLXG0LqKDTRoroGykL3H
sFMlWG4AybrGFLD178/vvONdBbQINBiFDpSTm63Xi+HVeALhVA1VP8Mo8cPXd66Ca
Q8aQUzqAFluJPyXpzCK40BwcSUeotHdbkvqIbPyAOAsYtTceIq/Xs3sFLr82n8Vcp
MCJvkiECgYEA+J2gMiUYe2PFGBcY13gYxruAt7zupssqgVjD/9uSkxyq5k43yONO
611EHW9OWXX0S9JecF2hCc1avO5NFOXG0mp/2mH7eOVYcvM/AOszVHh782JIy90C
zvQGN+e0lSvD7u/4LmYsigp0BTW39S5HLm4OhXpTaR07yTiIZodmggDsCgYEA0gKb
justm78AiPWx3t7vBiNfK5PdStJ+HR/x7CDVFukeQRqyyB1mfFlPRhJqIOcbAk0B7
0JneqWBJll330vl6WbMtD7mfiJvwWMHt0VPDa8ZzBJWB1pUJSDfeXfajU0FEADtR
WaNNSfybvksoKw2CDcUvDEV5xeW4cb8g5PghwPECgYEAihCnRRG6vdNTQiSZhBdK
0xqPyfnfIruS+E/+UNl0VcRG2C0555LrRY3+5MXKYgGuZ+kEzyv/4XysVl2UavWa
POR2wos6B+ddgDFzVHQqKlcVHYRbT1ocNutlGBVtb2fStLzJXlSZLqXYclKRpuTp
iIyaEfdiHNWn1GI1j99Wtb8CgYAMUWLWayyJe3eGqsoK2NRtNlsMOwV62rCQpFqD
DLzeRDxOKOr4S2VtZdUwNfAvk1zQRkP85EmPHbqzOyfCFCf9AulttrgIzby3OAi+
8m7P73/nkO1grLUyqzQ7xq+lvnpCmTgYTd/Gqy5nZvkgLVangB1WVuzhkqvS4Cc
JxQTwQKBgBr4KiJTpEMhkaLlwqlSn9CpBXP8TCPSXov9sTwr6J2vJ8OizBY6P+1k
yWr/bu6YCDsHK0/d9nTK6EGRr1RJVF7FVqQxNK3+hU+GZv+WMDAiXDSXjDjD3qTEa
+mwdmi3DGQhImQJ5rUubD+x5CqJkB3qupioJFlaufVeQLEySTickp+
-----END RSA PRIVATE KEY-----"""


class NoCertVerifyAdapter(HTTPAdapter):
    """跳过 SSL 证书验证的 HTTP Adapter"""
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        # 加载客户端证书
        try:
            import tempfile
            self._cert_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
            self._cert_file.write(CLIENT_CERT_PEM)
            self._cert_file.close()
            self._key_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
            self._key_file.write(CLIENT_KEY_PEM)
            self._key_file.close()
            ctx.load_cert_chain(self._cert_file.name, self._key_file.name)
        except Exception:
            pass  # 无客户端证书也尝试连接
        kwargs['ssl_context'] = ctx
        super().init_poolmanager(*args, **kwargs)


class WentuAPI:
    """纹图后端 API 客户端"""

    def __init__(self, active_code: str, server_url: str = None):
        self.active_code = active_code
        self.jwt_token = None
        self.user_id = None
        self.user_data = None

        # 创建 session，跳过证书验证
        self.session = requests.Session()
        self.session.mount('https://', NoCertVerifyAdapter())
        self.session.verify = False

        # 禁用 SSL 警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 选择服务器
        if server_url:
            self.base_url = server_url
        else:
            self.base_url = self._find_working_server()

    def _find_working_server(self) -> str:
        """尝试找到可用的服务器"""
        for server in SERVERS:
            try:
                print(f"[*] 尝试连接 {server} ...")
                resp = self.session.get(
                    f"{server}/qappconfigs?filters[jsonKey][$eq]=gptchat",
                    timeout=10
                )
                if resp.status_code in (200, 401, 403):
                    print(f"[+] 服务器可用: {server}")
                    return server
            except Exception as e:
                print(f"[-] {server} 连接失败: {e}")
        raise ConnectionError("所有服务器均不可用")

    def login(self) -> str:
        """Step 1: 登录获取 JWT Token"""
        print(f"\n[*] 正在登录...")
        resp = self.session.post(
            f"{self.base_url}/auth/local",
            json={
                "identifier": self.active_code,
                "password": LOGIN_PASSWORD
            },
            timeout=15
        )
        data = resp.json()
        if "jwt" in data:
            self.jwt_token = data["jwt"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.jwt_token}"
            })
            print(f"[+] 登录成功! JWT: {self.jwt_token[:30]}...")
            return self.jwt_token
        else:
            raise Exception(f"登录失败: {data}")

    def get_user_info(self) -> dict:
        """Step 2: 查询用户信息"""
        print(f"[*] 获取用户信息...")
        resp = self.session.get(
            f"{self.base_url}/multiusers",
            params={"filters[activeCode][$eq]": self.active_code},
            timeout=15
        )
        data = resp.json()
        if "data" in data and data["data"]:
            user = data["data"][0]
            self.user_id = user.get("id")
            self.user_data = user.get("attributes", user)
            quota = self.user_data
            print(f"[+] 用户 ID: {self.user_id}")
            print(f"    月用量: {quota.get('monthUsedCount', '?')}/{quota.get('monthMaxCount', '?')}")
            print(f"    有效期至: {quota.get('limitDate', '?')}")
            return self.user_data
        raise Exception(f"获取用户信息失败: {data}")

    def get_tinypng_key(self) -> str:
        """Step 3a: 获取 TinyPNG API Key"""
        print(f"[*] 获取 TinyPNG Key...")
        resp = self.session.post(
            f"{self.base_url}/ztinifykeybase/getRandomTinyKeyData",
            json={"count": 1},
            timeout=15
        )
        data = resp.json()
        print(f"[+] TinyPNG Key 响应: {json.dumps(data, ensure_ascii=False)[:200]}")
        # 从响应中提取 API key (具体字段需要根据实际响应调整)
        if isinstance(data, dict):
            # 可能的字段名: key, apiKey, data[0].key 等
            for k in ['key', 'apiKey', 'api_key', 'data']:
                if k in data:
                    val = data[k]
                    if isinstance(val, list) and val:
                        val = val[0]
                    if isinstance(val, dict):
                        for kk in ['key', 'apiKey', 'api_key']:
                            if kk in val:
                                return val[kk]
                    elif isinstance(val, str):
                        return val
        return json.dumps(data)

    def get_removebg_key(self) -> str:
        """Step 3b: 获取去背景 API Key"""
        print(f"[*] 获取去背景 Key...")
        resp = self.session.post(
            f"{self.base_url}/zzrmvkeybase/getRandomRmvKeyData",
            json={"count": 1},
            timeout=15
        )
        data = resp.json()
        print(f"[+] 去背景 Key 响应: {json.dumps(data, ensure_ascii=False)[:200]}")
        if isinstance(data, dict):
            for k in ['key', 'apiKey', 'api_key', 'data']:
                if k in data:
                    val = data[k]
                    if isinstance(val, list) and val:
                        val = val[0]
                    if isinstance(val, dict):
                        for kk in ['key', 'apiKey', 'api_key']:
                            if kk in val:
                                return val[kk]
                    elif isinstance(val, str):
                        return val
        return json.dumps(data)

    def report_usage(self, tool_type: str, count: float = 1):
        """Step 5: 上报使用量"""
        if not self.user_id:
            return
        try:
            current = self.user_data or {}
            used = current.get('monthUsedCount', 0) + count
            self.session.put(
                f"{self.base_url}/multiusers/{self.user_id}",
                json={"data": {"monthUsedCount": used, "toolType": tool_type}},
                timeout=10
            )
        except Exception:
            pass  # 上报失败不影响主流程


def batch_tinypng(api_key: str, input_dir: str, output_dir: str):
    """使用 TinyPNG API 批量压缩图片"""
    import tinify
    tinify.key = api_key

    os.makedirs(output_dir, exist_ok=True)
    files = []
    for ext in ('*.png', '*.jpg', '*.jpeg', '*.webp'):
        files.extend(glob.glob(os.path.join(input_dir, ext)))
        files.extend(glob.glob(os.path.join(input_dir, ext.upper())))

    print(f"\n[*] 找到 {len(files)} 个图片文件")
    for i, f in enumerate(files, 1):
        fname = os.path.basename(f)
        out_path = os.path.join(output_dir, fname)
        try:
            print(f"[{i}/{len(files)}] 压缩: {fname} ...", end=" ", flush=True)
            source = tinify.from_file(f)
            source.to_file(out_path)
            orig_size = os.path.getsize(f)
            new_size = os.path.getsize(out_path)
            ratio = (1 - new_size / orig_size) * 100
            print(f"✓ {orig_size//1024}KB → {new_size//1024}KB ({ratio:.1f}% 节省)")
        except Exception as e:
            print(f"✗ 失败: {e}")


def batch_removebg(api_key: str, input_dir: str, output_dir: str):
    """使用佐糖 API 批量去背景"""
    os.makedirs(output_dir, exist_ok=True)
    files = []
    for ext in ('*.png', '*.jpg', '*.jpeg', '*.webp'):
        files.extend(glob.glob(os.path.join(input_dir, ext)))
        files.extend(glob.glob(os.path.join(input_dir, ext.upper())))

    print(f"\n[*] 找到 {len(files)} 个图片文件")

    for i, f in enumerate(files, 1):
        fname = Path(f).stem + "_nobg.png"
        out_path = os.path.join(output_dir, fname)
        try:
            print(f"[{i}/{len(files)}] 去背景: {os.path.basename(f)} ...", end=" ", flush=True)

            # Step 1: 提交任务
            with open(f, 'rb') as img:
                resp = requests.post(
                    "https://techsz.aoscdn.com/api/tasks/visual/segmentation",
                    headers={"X-API-Key": api_key},
                    files={"image_file": img},
                    timeout=30
                )
            task = resp.json()
            if task.get("status") != 200 and "data" not in task:
                print(f"✗ 提交失败: {task}")
                continue

            # Step 2: 等待结果 (如果是异步)
            task_data = task.get("data", {})
            result_url = task_data.get("image", task_data.get("result_url", ""))

            if not result_url and "task_id" in task_data:
                # 异步模式，轮询结果
                task_id = task_data["task_id"]
                for attempt in range(30):
                    time.sleep(2)
                    poll = requests.get(
                        f"https://techsz.aoscdn.com/api/tasks/visual/{task_id}",
                        headers={"X-API-Key": api_key},
                        timeout=15
                    ).json()
                    if poll.get("data", {}).get("state") == "completed":
                        result_url = poll["data"]["image"]
                        break

            if result_url:
                img_data = requests.get(result_url, timeout=30).content
                with open(out_path, 'wb') as out:
                    out.write(img_data)
                print(f"✓ 保存至 {fname} ({len(img_data)//1024}KB)")
            else:
                print(f"✗ 无结果URL: {task}")

        except Exception as e:
            print(f"✗ 失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="纹图批量处理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 第一步：获取 API Keys（只需运行一次）
  python wentu_batch.py --keys-only -c YOUR_ACTIVE_CODE

  # 用获取到的 key 批量压缩
  python wentu_batch.py tinify -k TINYPNG_KEY -i ./input -o ./output

  # 用获取到的 key 批量去背景
  python wentu_batch.py removebg -k API_KEY -i ./input -o ./output

  # 一步到位（自动获取key并处理）
  python wentu_batch.py tinify -c YOUR_ACTIVE_CODE -i ./input -o ./output
        """
    )
    parser.add_argument('-c', '--code', help='纹图激活码')
    parser.add_argument('-k', '--key', help='直接提供第三方 API Key (跳过纹图后端)')
    parser.add_argument('-i', '--input', default='./input', help='输入图片目录')
    parser.add_argument('-o', '--output', default='./output', help='输出目录')
    parser.add_argument('--server', help='指定服务器地址 (默认自动选择)')
    parser.add_argument('--keys-only', action='store_true', help='只获取 API Keys，不处理图片')
    parser.add_argument('action', nargs='?', choices=['tinify', 'removebg', 'info'],
                        default='info', help='操作: tinify=压缩, removebg=去背景, info=查看信息')

    args = parser.parse_args()

    # ---- 只获取 Keys ----
    if args.keys_only or args.action == 'info':
        if not args.code:
            parser.error("需要提供激活码 (-c)")
        api = WentuAPI(args.code, args.server)
        api.login()
        api.get_user_info()
        print("\n" + "=" * 50)
        tinypng_key = api.get_tinypng_key()
        removebg_key = api.get_removebg_key()
        print("\n" + "=" * 50)
        print("获取到的 API Keys (保存好，可以反复使用):")
        print(f"  TinyPNG Key: {tinypng_key}")
        print(f"  去背景 Key:  {removebg_key}")
        print("=" * 50)
        return

    # ---- 批量处理 ----
    api_key = args.key
    if not api_key:
        if not args.code:
            parser.error("需要提供激活码 (-c) 或 API Key (-k)")
        api = WentuAPI(args.code, args.server)
        api.login()
        api.get_user_info()
        if args.action == 'tinify':
            api_key = api.get_tinypng_key()
        else:
            api_key = api.get_removebg_key()

    if args.action == 'tinify':
        batch_tinypng(api_key, args.input, args.output)
    elif args.action == 'removebg':
        batch_removebg(api_key, args.input, args.output)


if __name__ == '__main__':
    main()
