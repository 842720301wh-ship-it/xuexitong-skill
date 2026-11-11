"""学习通本地入口：环境检查、课程列表、只读核对和任务执行。"""
import argparse
import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULES = ("requests", "pyaes", "bs4", "lxml", "loguru", "fontTools",
           "openai", "tqdm", "httpx", "urllib3")


class UserError(ValueError):
    pass


def check_environment():
    if sys.version_info < (3, 13):
        raise UserError("需要 Python 3.13 或更高版本；请使用该版本创建的虚拟环境。")
    missing = [name for name in MODULES if importlib.util.find_spec(name) is None]
    if missing:
        raise UserError("缺少依赖：" + ", ".join(missing) + "；请安装 requirements.txt。")
    if not (ROOT / "resource/font_map_table.json").is_file():
        raise UserError("缺少字体映射资源，请重新解压完整技能包。")


def read_config(path, action):
    config = configparser.ConfigParser(interpolation=None)
    if not path.is_file():
        raise UserError("配置文件不存在；请复制 config.example.ini 后填写。")
    with path.open(encoding="utf-8-sig") as stream:
        config.read_file(stream)
    common = dict(config.items("common")) if config.has_section("common") else {}
    # Require credentials even with cookies so an expired session cannot prompt on stdin.
    if not all(common.get(key, "").strip() for key in ("username", "password")):
        raise UserError("请在 [common] 填写 username 和 password。")
    courses = common.get("course_list", "").strip()
    if action != "courses" and not re.fullmatch(r"[0-9]+(?:\s*,\s*[0-9]+)*", courses):
        raise UserError("请填写明确的 course_list；可先用 courses 查询课程 ID。")
    if action == "run":
        if not 1 <= float(common.get("speed", "1")) <= 2:
            raise UserError("speed 范围为 1–2。")
        if not 1 <= int(common.get("jobs", "1")) <= 4:
            raise UserError("jobs 范围为 1–4。")
        if common.get("notopen_action", "retry") not in ("retry", "continue"):
            raise UserError("notopen_action 仅支持 retry 或 continue。")
        tiku = dict(config.items("tiku")) if config.has_section("tiku") else {}
        providers = [item.strip() for item in tiku.get("provider", "").split(",") if item.strip()]
        allowed = {"AI", "SiliconFlow", "TikuYanxi", "TikuLike", "TikuAdapter", "TikuGo"}
        if set(providers) - allowed:
            raise UserError("题库 provider 无效。")
        if "AI" in providers and not all(tiku.get(key, "").strip() for key in ("endpoint", "key", "model")):
            raise UserError("使用 AI 时请填写 endpoint、key 和 model，或将 provider 留空。")
        if "SiliconFlow" in providers and not all(tiku.get(key, "").strip() for key in ("siliconflow_key", "siliconflow_model", "siliconflow_endpoint")):
            raise UserError("使用 SiliconFlow 时请填写其密钥、模型和端点。")
        if any(name in providers for name in ("TikuYanxi", "TikuLike")) and not tiku.get("tokens", "").strip():
            raise UserError("所选题库需要填写 tokens。")
        if "TikuAdapter" in providers and not tiku.get("url", "").strip():
            raise UserError("TikuAdapter 需要填写 url。")
    return common


def list_courses(config_path):
    from api.base import Account, Chaoxing
    common = read_config(config_path, "courses")
    client = Chaoxing(account=Account(common["username"], common["password"]))
    result = client.login(login_with_cookies=common.get("use_cookies", "false").lower() == "true")
    if not result.get("status"):
        raise UserError("登录失败，请检查账号密码或验证码要求。")
    courses = client.get_course_list()
    print(json.dumps([{"id": str(item["courseId"]), "title": item["title"]}
                      for item in courses], ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "courses", "audit", "run"))
    parser.add_argument("--config", type=Path, help="用户工作目录中的 INI 配置")
    parser.add_argument("--state-dir", type=Path, help="Cookie、日志和缓存保存目录")
    parser.add_argument("--chapter-prefix", nargs="+", default=[""])
    args = parser.parse_args()
    try:
        check_environment()
        if args.action == "check":
            if args.config:
                read_config(args.config.resolve(), "run")
            print("环境检查通过。" if not args.config else "环境和配置检查通过；未登录平台。")
            return 0
        if args.config is None:
            raise UserError("请通过 --config 指定配置文件。")
        config_path = args.config.resolve()
        read_config(config_path, args.action)
        digest = hashlib.sha256(str(config_path).encode("utf-8")).hexdigest()[:12]
        state_dir = (args.state_dir or config_path.parent / ".xuexitong" / digest).resolve()
        # Keep a shared skill installation free of private runtime files.
        if state_dir == ROOT or ROOT in state_dir.parents:
            raise UserError("运行目录必须位于技能目录之外；请将配置复制到用户工作目录。")
        state_dir.mkdir(parents=True, exist_ok=True)
        print("运行数据目录：" + str(state_dir), flush=True)
        os.chdir(state_dir)
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(ROOT))
        if args.action == "courses":
            list_courses(config_path)
            return 0
        script = ROOT / ("scripts/audit_progress.py" if args.action == "audit" else "main.py")
        command = [sys.executable, "-B", str(script), "--config", str(config_path)]
        if args.action == "audit":
            command += ["--chapter-prefix"] + args.chapter_prefix
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
        return subprocess.call(command, stdin=subprocess.DEVNULL, env=env)
    except UserError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (ValueError, OSError, configparser.Error):
        # Parse errors may contain secret-bearing source lines.
        print("配置或运行环境无效，请检查 INI 格式、参数和目录权限。", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
