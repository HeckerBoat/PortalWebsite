"""
综合测试脚本：冒烟测试、功能测试、SIT 集成测试、UAT 验收测试
使用 Python 标准库 urllib，无需额外依赖。
运行：python tests/test_all.py
"""
import json
import urllib.request
import urllib.error
import urllib.parse
import sys

BASE_URL = "http://127.0.0.1:5001"
PASS = 0
FAIL = 0


def req(method, path, data=None, token=None):
    """发送 HTTP 请求并返回 (status_code, body_dict)。"""
    # URL 编码路径中的非 ASCII 字符（如中文文件名）
    # 先解码避免重复编码，再统一编码
    parsed = urllib.parse.urlsplit(path)
    decoded_path = urllib.parse.unquote(parsed.path)
    encoded_path = urllib.parse.quote(decoded_path)
    if parsed.query:
        encoded_path += "?" + parsed.query
    url = f"{BASE_URL}{encoded_path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, {"_raw": raw}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"_raw": raw}


def assert_eq(name, actual, expected):
    global PASS, FAIL
    if actual == expected:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}: 期望 {expected!r}, 实际 {actual!r}")


def assert_true(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}: 条件不成立")


# ==================== 冒烟测试 ====================
def test_smoke():
    print("\n" + "=" * 50)
    print("【冒烟测试】")
    print("=" * 50)

    # 健康检查
    code, body = req("GET", "/api/health")
    assert_eq("健康检查状态码", code, 200)
    assert_eq("健康检查 code", body.get("code"), 0)

    # 前端页面可访问
    code, body = req("GET", "/")
    assert_eq("前端页面可访问", code, 200)
    assert_true("前端页面包含标题", "HTML 自动管理平台" in body.get("_raw", ""))

    # 静态 HTML 可访问
    code, _ = req("GET", "/static/html/AI%E6%82%AC%E6%B5%AE%E5%8A%A9%E6%89%8B.html")
    assert_eq("静态HTML文件可访问", code, 200)


# ==================== 功能测试 ====================
def test_functional():
    print("\n" + "=" * 50)
    print("【功能测试】")
    print("=" * 50)

    token = None

    # 1. 管理员登录
    code, body = req("POST", "/api/auth/login", {"account": "admin", "password": "1q2w3e4r"})
    assert_eq("管理员登录 code", body.get("code"), 0)
    token = body["data"]["token"]
    assert_true("获取到 token", bool(token))

    # 2. 注册新用户
    code, body = req("POST", "/api/auth/register", {
        "username": "testuser_func", "password": "123456", "email": "func@test.com"
    })
    assert_eq("注册用户 code", body.get("code"), 0)

    # 3. 新用户登录
    code, body = req("POST", "/api/auth/login", {"account": "testuser_func", "password": "123456"})
    assert_eq("新用户登录 code", body.get("code"), 0)
    user_token = body["data"]["token"]

    # 4. 获取当前用户信息
    code, body = req("GET", "/api/auth/me", token=user_token)
    assert_eq("获取当前用户 code", body.get("code"), 0)
    assert_eq("当前用户名", body["data"]["username"], "testuser_func")

    # 5. 扫描同步
    code, body = req("POST", "/api/html/scan", token=token)
    assert_eq("扫描同步 code", body.get("code"), 0)

    # 6. HTML 列表
    code, body = req("GET", "/api/html/list", token=token)
    assert_eq("HTML列表 code", body.get("code"), 0)
    assert_true("列表非空", len(body["data"]) > 0)

    # 7. 编辑 HTML
    first_id = body["data"][0]["id"]
    code, body = req("PUT", f"/api/html/{first_id}", {"description": "功能测试描述"}, token=token)
    assert_eq("编辑HTML code", body.get("code"), 0)

    # 8. 用户列表（管理员）
    code, body = req("GET", "/api/users", token=token)
    assert_eq("用户列表 code", body.get("code"), 0)

    # 9. 系统配置写入
    code, body = req("PUT", "/api/config/test_key", {"value": "test_value", "description": "测试"}, token=token)
    assert_eq("配置写入 code", body.get("code"), 0)

    # 10. 系统配置读取
    code, body = req("GET", "/api/config/test_key", token=token)
    assert_eq("配置读取 code", body.get("code"), 0)
    assert_eq("配置值正确", body["data"]["value"], "test_value")

    # 11. 删除测试用户
    code, body = req("GET", "/api/users?keyword=testuser_func", token=token)
    uid = body["data"][0]["id"]
    code, body = req("DELETE", f"/api/users/{uid}", token=token)
    assert_eq("删除测试用户 code", body.get("code"), 0)

    return token


# ==================== SIT 集成测试 ====================
def test_sit(admin_token):
    print("\n" + "=" * 50)
    print("【SIT 集成测试】")
    print("=" * 50)

    # 场景：注册用户 -> 登录 -> 扫描 -> 查看列表 -> 编辑 -> 删除记录 -> 确认删除
    # 1. 注册
    req("POST", "/api/auth/register", {"username": "sit_user", "password": "123456", "email": "sit@test.com"})

    # 2. 登录
    code, body = req("POST", "/api/auth/login", {"account": "sit_user", "password": "123456"})
    assert_eq("SIT-用户登录", body.get("code"), 0)
    user_token = body["data"]["token"]

    # 3. 未登录访问受保护接口应 401
    code, body = req("GET", "/api/html/list")
    assert_eq("SIT-未登录被拒绝", code, 401)

    # 4. 普通用户访问用户管理应 403
    code, body = req("GET", "/api/users", token=user_token)
    assert_eq("SIT-普通用户无用户管理权限", code, 403)

    # 5. 扫描后列表与数据库一致
    req("POST", "/api/html/scan", token=user_token)
    code, body = req("GET", "/api/html/list", token=user_token)
    count = len(body["data"])
    assert_true("SIT-列表有数据", count > 0)

    # 6. 编辑后重新列表确认更新
    fid = body["data"][0]["id"]
    req("PUT", f"/api/html/{fid}", {"title": "SIT修改标题"}, token=user_token)
    code, body = req("GET", f"/api/html/{fid}", token=user_token)
    assert_eq("SIT-编辑后标题更新", body["data"]["title"], "SIT修改标题")

    # 7. 配置写入后读取一致
    req("PUT", "/api/config/sit_key", {"value": "sit_value"}, token=user_token)
    code, body = req("GET", "/api/config/sit_key", token=user_token)
    assert_eq("SIT-配置读写一致", body["data"]["value"], "sit_value")

    # 8. 清理：管理员删除测试用户
    code, body = req("GET", "/api/users?keyword=sit_user", token=admin_token)
    if body["data"]:
        uid = body["data"][0]["id"]
        req("DELETE", f"/api/users/{uid}", token=admin_token)


# ==================== UAT 验收测试 ====================
def test_uat(admin_token):
    print("\n" + "=" * 50)
    print("【UAT 验收测试】")
    print("=" * 50)

    # UAT1: 核心需求 - 自动扫描生成URL
    code, body = req("POST", "/api/html/scan", token=admin_token)
    assert_eq("UAT-扫描成功", body.get("code"), 0)

    code, body = req("GET", "/api/html/list", token=admin_token)
    files = body["data"]
    assert_true("UAT-扫描到HTML文件", len(files) > 0)

    # 验证每个文件都有 URL
    for f in files:
        assert_true(f"UAT-文件 {f['filename']} 有URL", bool(f.get("url")))
        assert_true(f"UAT-文件 {f['filename']} URL格式正确", f["url"].startswith("/static/html/"))

    # UAT2: URL 可访问
    first = files[0]
    code, _ = req("GET", first["url"])
    assert_eq(f"UAT-URL可访问 {first['filename']}", code, 200)

    # UAT3: 标题自动提取
    has_title = any(f.get("title") for f in files)
    assert_true("UAT-自动提取页面标题", has_title)

    # UAT4: 增删改查
    fid = files[0]["id"]
    req("PUT", f"/api/html/{fid}", {"description": "UAT验收测试"}, token=admin_token)
    code, body = req("GET", f"/api/html/{fid}", token=admin_token)
    assert_eq("UAT-修改描述成功", body["data"]["description"], "UAT验收测试")

    # UAT5: 管理员权限
    code, body = req("GET", "/api/users", token=admin_token)
    assert_eq("UAT-管理员可查看用户列表", body.get("code"), 0)

    # UAT6: 配置持久化
    req("PUT", "/api/config/uat_theme", {"value": "dark"}, token=admin_token)
    code, body = req("GET", "/api/config/uat_theme", token=admin_token)
    assert_eq("UAT-配置持久化", body["data"]["value"], "dark")

    # 清理 UAT 测试配置
    req("DELETE", "/api/config/uat_theme", token=admin_token)
    req("DELETE", "/api/config/sit_key", token=admin_token)
    req("DELETE", "/api/config/test_key", token=admin_token)


def main():
    global PASS, FAIL
    print("开始执行测试...")
    print(f"目标地址: {BASE_URL}")

    test_smoke()
    admin_token = test_functional()
    test_sit(admin_token)
    test_uat(admin_token)

    print("\n" + "=" * 50)
    print(f"测试完成：通过 {PASS}，失败 {FAIL}")
    print("=" * 50)

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
