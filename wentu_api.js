// wentu_api.js - 直接连接纹图后端获取 API Key
// 用法: node wentu_api.js [激活码]

const https = require('https');

const ACTIVE_CODE = process.argv[2] || 'K9YHWc5w25SIz48NJjp11x0a3U08n7pheuxss3V1EMej9MOxbgYt2JzN899a01e2';
const PASSWORD = '6ff44354168e5ab8bf922929524397e4';
const SERVERS = ['139.196.209.2', '43.128.79.132'];

const CERT_B64 = 'LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURkakNDQWw0Q0NRQzhiUXBSU2d0QUhqQU5CZ2txaGtpRzl3MEJBUVVGQURCOU1Rc3dDUVlEVlFRR0V3SkQKVGpFTE1Ba0dBMVVFQ0F3Q1NFSXhDekFKQmdOVkJBY01BbGRJTVJBd0RnWURWUVFLREFkdGFXNTBjbVZsTVE4dwpEUVlEVlFRTERBWmpiR2xsYm5ReEVqQVFCZ05WQkFNTUNXMXBibU5zYVdWdWRERWRNQnNHQ1NxR1NJYjNEUUVKCkFSWU9NekV6TkdOc2FXVnVkQzVqYjIwd0hoY05Nak13T0RJd01EUTBNREE1V2hjTk16TXdPREUzTURRME1EQTUKV2pCOU1Rc3dDUVlEVlFRR0V3SkRUakVMTUFrR0ExVUVDQXdDU0VJeEN6QUpCZ05WQkFjTUFsZElNUkF3RGdZRApWUVFLREFkdGFXNTBjbVZsTVE4d0RRWURWUVFMREFaamJHbGxiblF4RWpBUUJnTlZCQU1NQ1cxcGJtTnNhV1Z1CmRERWRNQnNHQ1NxR1NJYjNEUUVKQVJZT016RXpOR05zYVdWdWRDNWpiMjB3Z2dFaU1BMEdDU3FHU0liM0RRRUIKQVFVQUE0SUJEd0F3Z2dFS0FvSUJBUURMODlXMm5wNForTVJGcmlDa3Y5Ym16N1JvS0h2TGlKK3NoSHBEeXhMTwpDR0FORWE2RkhJeGR5RW90enFkaVpBdUpaMjlRcG1RUE9wTysrbkhWekhPVi92aWY3K2ZVMXRaUE5JUzZKY3ZHCkg5VnppUjd2MkRGVWVld1o3SmFoS1htSmJPb3hXUjJzZlExaWlqVzZtWWYxdVhiVktobDc1eVdlTWNYWWw3Y1QKUm5wUFczMjMvQnRDRTc0SXBBcmp3aThoT2ptZVJzZXNwM1FHejdhaTdXQnA2Wnh0MVRraEt0cnJHOVNYRStSQgpLSGJOKzN1U3VIWG0yemtPZnZoNHhFUzBjWmlZZVRZNjI4RVlRQTU0cS9lbzdwVm8xSWRDU3QwSlJkZTExcFlXClJhNkpkWE84Tlp5QzNIaVJUZWlUODlTR0dMVGMyaUJnQ3RRQ293dnYzL2VMQWdNQkFBRXdEUVlKS29aSWh2Y04KQVFFRkJRQURnZ0VCQUphRmhMVXdlZ2ljTlE4L0RacjlCMWIzVTR2VE82eHVYdmdDeThiOW1yeWI3RW5tOWVGKwpPd0hjWlR4enZGbkw5N2xRbVVnYThvQk8xOFVmQTZUUFVWTmkvRXFPY3VETmN5RVVFcWpnb2FSV0ZsaWdXM3VZCm44cjdoeEtibTY3N3hvUVdMKzZxVGFLejFkUUVGQWVSenZQaFB5WVc0QkpZaGc1YnozL2k2d2txT2Y3RGFNZmsKamhqTFplUTNPT3VMaC9ZUEI0cTB2cWp6QlY5WWYxQktOZFhSc0luTkFQNUpNTG1rdnhXWXRMdTJjNFQ3Vk4yUwoxNmdoU2NxQ1RsRmFxTEhwU1BHQmNyUmQvRXd1SEU1M0hjeXBDVWtQVWlsMDdVdjdrN1JJZ04vd1JkSml0Mmt0ClJKQjBsdlhqU3JTUGIzSXFHZmtvZkN3a0s2a2dKSnZMRmpnPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==';
const KEY_B64 = 'LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBeS9QVnRwNmVHZmpFUmE0Z3BML1c1cyswYUNoN3k0aWZySVI2UThzU3pnaGdEUkd1CmhSeU1YY2hLTGM2blltUUxpV2R2VUtaa0R6cVR2dnB4MWN4emxmNzRuKy9uMU5iV1R6U0V1aVhMeGgvVmM0a2UKNzlneFZIbnNHZXlXb1NsNWlXenFNVmtkckgwTllvbzF1cG1IOWJsMjFTb1plK2NsbmpIRjJKZTNFMFo2VDF0OQp0L3diUWhPK0NLUUs0OEl2SVRvNW5rYkhyS2QwQnMrMm91MWdhZW1jYmRVNUlTcmE2eHZVbHhQa1FTaDJ6ZnQ3CmtyaDE1dHM1RG43NGVNUkV0SEdZbUhrMk90dkJHRUFPZUt2M3FPNlZhTlNIUWtyZENVWFh0ZGFXRmtXdWlYVnoKdkRXY2d0eDRrVTNvay9QVWhoaTAzTm9nWUFyVUFxTUw3OS8zaXdJREFRQUJBb0lCQUR0OGZDb09xNWh4cVhXVgpheW9DVmtEdDlmV25VU3cxUmpWQVVwVHhaeU8yNTZVSU1qbmE4TW50d0UwS0NHSTNRZklxdkJudTNpSmUrSGJzCmYwVlhvNkx0UWtFTDdUZDBEZi8rRm5SZ3o4V1N4V1EwYTFTVFh4Zi9rN0NnQS9NdnNLWTNvVHNSZmdrd1ZEWVkKajhGRVJKYVVLS2ZWNXFidjdWWHR1SUlMQmpmVmdkUjNVa1F1VWNRTE9kVU9zTFhHMExxS0RUUm9yb0d5a0wzSApzRk1sV0c0QXlicmdGTEQxNzgvdnZORGJRSU5CaUZEcFNUbTYzWGkrSFZlQUxoVkExVlA4TW84Y1BYZDY2Q2FRCjhhUVV6cUFGbHVKUHlYcHpDSzQwQndjU1Vlb3RIZGJrdnFJYlB5QU9Bc1l0VGNlSXEvWHMzc0ZMcjgybjhWY3AKTUNKdmtpRUNnWUVBK0oyZ01pVVllMlBGR0JjWTEzZ1l4cnVBdDd6dXBzc3FnVmpELzl1U2t4eXE1azQzeU9OTQo2MTFFSFc5T1dYeDBTOUplY0YyaENjMWF2TzVORk9YZ21wLzJtSDdlT1ZZY3ZNL0FPc3pWSGg3ODJKSXk5MEN6CnZRR04rZTBsU3ZEN3UvNExtWXNpZ3AwQlRXMzlTNUhMbTRPaFhwVGFSMDd5VGlJWm9kbWdnRHNDZ1lFQTBnS2IKanVzbTc4QWlQV3gzdDd2QmlOZks1UGRTdEorSFIveDdDRFZGdWtlUVJxeXlCMW1mRmxQUmhKcUlPY2JBazBCNwowSm5lcVdCSmxsMzMwdmw2V2JNdEQ3bWZpSnZ3V01IdDBWUERhOFp6QkpXQjFwVUpTRGZlWGZhalUwRkVBRHRSCldhTk5TZnlidmtzb0t3MkNEY1V2REVWNXhlVzRjYjhnNVBnaHdQRUNnWUVBaWhDblJSRzZ2ZE5UUWlTWmhCZEsKMHhxUHlmbmZJcnVTK0UvK1VObDBWY1JHMkMwNTU1THJSWTMrNU1YS1lnR3VaK2tFenl2LzRYeXNWbDJVYXZXYQpQT1Iyd29zNkIrZGRnREZ6VkhRcUtsY1ZIWVJiVDFvY051dGxHQlZ0YjJmU3RMekpYbFNaTHFYWWNsS1JwdVRwCmlJeWFFZmRpSE5XbjFHSTFqOTlXdGI4Q2dZQU1VV0xXYXl5SmUzZUdxc29LMk5SdE5sc01Pd1Y2MnJDUXBGcUQKREx6ZVJEeE9LT3I0UzJWdFpkVXdOZkF2azF6UVJrUDg1RW1QSGJxek95ZkNGQ2Y5QXVsdHRyR0l6YnkzT0FpKwo4bTdQNzMvbmtPMWdyTFV5cXpRN3hxK2x2bnBDbVRnWVRkL0dxeTVuWnZrZ0xWYW5nQjFXVnV6aGtxdlM0Q2NKCnh4UVR3UUtCZ0JyNEtpSlRwRU1oa2FMbHdxbFNuOUNwQlhQOFRDUFNYb3Y5c1R3cjZKMnZKOE9pekJZNlArMWsKeVdyL2J1NFlDRHNISzAvZDluVEs2RUdScjFSSlY3RlZxUXhOSzMraFUrR1p2K1dNREFpWERTWGpEakQzcVRFYQorbXdkbWkzREdRaEltUUo1clV1YkQreDVDcUprQjNxdXBpSkZsYXVmVmVRTEV5U1Rpa3ArCi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg==';

const CLIENT_CERT = Buffer.from(CERT_B64, 'base64').toString('utf-8');
const CLIENT_KEY = Buffer.from(KEY_B64, 'base64').toString('utf-8');

function req(method, server, apiPath, body, jwt) {
    return new Promise((resolve, reject) => {
        const postData = body ? JSON.stringify(body) : null;
        const options = {
            hostname: server, port: 443, path: `/api${apiPath}`, method,
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            cert: CLIENT_CERT, key: CLIENT_KEY, rejectUnauthorized: false,
        };
        if (jwt) options.headers['Authorization'] = `Bearer ${jwt}`;
        if (postData && method !== 'GET') options.headers['Content-Length'] = Buffer.byteLength(postData);

        const r = https.request(options, (res) => {
            let data = '';
            res.on('data', c => data += c);
            res.on('end', () => {
                try { resolve({ status: res.statusCode, data: JSON.parse(data) }); }
                catch(e) { resolve({ status: res.statusCode, data }); }
            });
        });
        r.on('error', reject);
        r.setTimeout(15000, () => { r.destroy(); reject(new Error('timeout')); });
        if (postData && method !== 'GET') r.write(postData);
        r.end();
    });
}

async function tryGetKey(server, path, jwt) {
    // 尝试多种 HTTP 方法和参数格式
    const attempts = [
        { m: 'GET',  p: `${path}?count=1` },
        { m: 'GET',  p: path },
        { m: 'POST', p: path, body: { count: 1 } },
        { m: 'PUT',  p: path, body: { count: 1 } },
    ];
    for (const a of attempts) {
        try {
            const r = await req(a.m, server, a.p, a.body || null, jwt);
            if (r.status === 200) {
                console.log(`  ✓ [${a.m} ${a.p}] HTTP ${r.status}`);
                return r;
            }
            console.log(`  · [${a.m} ${a.p}] HTTP ${r.status}: ${JSON.stringify(r.data).substring(0, 80)}`);
        } catch(e) {
            console.log(`  · [${a.m} ${a.p}] 错误: ${e.message}`);
        }
    }
    return null;
}

async function main() {
    console.log('='.repeat(60));
    console.log('  纹图 API Key 获取工具 v2');
    console.log('='.repeat(60));
    console.log(`  激活码: ${ACTIVE_CODE.substring(0, 20)}...`);

    let server = SERVERS[0];
    let jwt = null;

    // 找服务器
    for (const s of SERVERS) {
        try {
            console.log(`\n[*] 尝试 ${s}...`);
            await req('GET', s, '/qappconfigs?filters[jsonKey][$eq]=test', null, null);
            server = s; console.log(`[+] 可用`); break;
        } catch(e) { console.log(`[-] 失败: ${e.message}`); }
    }

    // 登录
    console.log('\n[1] 登录...');
    const login = await req('POST', server, '/auth/local', { identifier: ACTIVE_CODE, password: PASSWORD });
    if (!login.data.jwt) { console.error('登录失败:', JSON.stringify(login.data)); process.exit(1); }
    jwt = login.data.jwt;
    console.log(`  ✓ JWT OK`);

    // 用户信息
    console.log('\n[2] 用户信息...');
    const user = await req('GET', server, `/multiusers?filters[activeCode][$eq]=${ACTIVE_CODE}`, null, jwt);
    if (user.data.data?.[0]) {
        const u = user.data.data[0], a = u.attributes || u;
        console.log(`  ✓ ID: ${u.id} | 用量: ${a.monthUsedCount}/${a.monthMaxCount} | 到期: ${a.limitDate}`);
    }

    // 获取 TinyPNG Key - 尝试多种方式
    console.log('\n[3] TinyPNG Key (尝试多种方式)...');
    const tinyResult = await tryGetKey(server, '/ztinifykeybase/getRandomTinyKeyData', jwt);
    if (tinyResult) console.log('  数据:', JSON.stringify(tinyResult.data, null, 2));

    // 也试试直接获取 key 列表
    console.log('\n[3b] TinyPNG Keys (直接查询集合)...');
    try {
        const r = await req('GET', server, '/ztinifykeys?pagination[pageSize]=3&sort=leftCount:desc', null, jwt);
        if (r.status === 200 && r.data.data) {
            console.log(`  ✓ 找到 ${r.data.data.length} 个 key:`);
            r.data.data.forEach(k => {
                const a = k.attributes || k;
                console.log(`    ID:${k.id} | key: ${a.key || a.apiKey || a.tinyKey || '(看下面完整数据)'} | 剩余: ${a.leftCount}`);
            });
            if (r.data.data[0]) {
                console.log('\n  第一条完整数据:');
                console.log('  ' + JSON.stringify(r.data.data[0], null, 2).replace(/\n/g, '\n  '));
            }
        } else {
            console.log(`  HTTP ${r.status}:`, JSON.stringify(r.data).substring(0, 200));
        }
    } catch(e) { console.log(`  ✗ ${e.message}`); }

    // 获取去背景 Key
    console.log('\n[4] 去背景 Key (尝试多种方式)...');
    const rmvResult = await tryGetKey(server, '/zzrmvkeybase/getRandomRmvKeyData', jwt);
    if (rmvResult) console.log('  数据:', JSON.stringify(rmvResult.data, null, 2));

    // 也试试直接获取 key 列表
    console.log('\n[4b] 去背景 Keys (直接查询集合)...');
    try {
        const r = await req('GET', server, '/zzrmvkeys?pagination[pageSize]=3&sort=leftCount:desc', null, jwt);
        if (r.status === 200 && r.data.data) {
            console.log(`  ✓ 找到 ${r.data.data.length} 个 key:`);
            r.data.data.forEach(k => {
                const a = k.attributes || k;
                console.log(`    ID:${k.id} | key: ${a.key || a.apiKey || a.rmvKey || '(看下面完整数据)'} | 剩余: ${a.leftCount}`);
            });
            if (r.data.data[0]) {
                console.log('\n  第一条完整数据:');
                console.log('  ' + JSON.stringify(r.data.data[0], null, 2).replace(/\n/g, '\n  '));
            }
        } else {
            console.log(`  HTTP ${r.status}:`, JSON.stringify(r.data).substring(0, 200));
        }
    } catch(e) { console.log(`  ✗ ${e.message}`); }

    // Pixian
    console.log('\n[5] Pixian 配置...');
    try {
        const r = await req('GET', server, '/base/getPixianQpsEntry', null, jwt);
        console.log('  ', JSON.stringify(r.data, null, 2));
    } catch(e) { console.log(`  ✗ ${e.message}`); }

    // 也获取 ztcode
    console.log('\n[6] ztcode...');
    for (const m of ['GET', 'POST']) {
        try {
            const r = await req(m, server, '/base/getztcode', m === 'POST' ? {} : null, jwt);
            if (r.status === 200) {
                console.log(`  [${m}] ✓`, JSON.stringify(r.data, null, 2));
                break;
            }
            console.log(`  [${m}]`, r.status, JSON.stringify(r.data).substring(0, 100));
        } catch(e) { console.log(`  [${m}] ✗ ${e.message}`); }
    }

    console.log('\n' + '='.repeat(60));
    console.log('完成! 在上面的输出中找到包含 API key 的字段');
    console.log('='.repeat(60));
}

main().catch(err => { console.error('错误:', err.message); process.exit(1); });