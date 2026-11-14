# 学习通课程助手

把学习通（超星、尔雅、泛雅）的课程查询、进度核对和指定课程任务执行封装成 Agent Skill，供 Codex、WorkBuddy 及支持本地技能和 Python 脚本的 Agent 使用。

**需要 Python 3.13+ 和网络连接。** 技能包不包含 Python、第三方依赖、账号或模型额度。默认测验配置为全自动提交：题库或模型查询失败时也可能使用兜底答案提交，正确率不保证；仅保存答案时，请将 `auto_submit` 和 `submit` 都设为 `false`。

[GitHub 仓库](https://github.com/842720301wh-ship-it/xuexitong-skill) · [下载技能 ZIP](https://raw.githubusercontent.com/842720301wh-ship-it/xuexitong-skill/main/xuexitong.zip) · [技能指令](./xuexitong/SKILL.md)

## 可以做什么

| 能力 | 说明 |
| --- | --- |
| 查询课程 | 登录后列出课程名称和 ID，先选课程再执行 |
| 核对进度 | 读取章节和任务卡片，定位未完成或未开放任务 |
| 执行任务 | 处理指定课程的视频、音频、文档、阅读、章节测验及平台可用的直播任务 |
| 题库与 AI | 按配置调用题库或兼容 OpenAI 接口的模型，支持主模型重试和备用模型 |
| 进度续跑 | 根据平台最新记录跳过已完成任务；需要顺序解锁的课程逐章核验 |

是否完成以平台最新状态为准。仅保存、待批阅、跳过和程序处理结束，都不代表课程已完成。

## 下载安装

想让 Agent 帮你安装，可以直接复制本文末尾的安装提示词。

### Codex

将仓库中的 `xuexitong/` 子目录作为一个完整技能安装，技能名称为 `xuexitong`。可让内置 `$skill-installer` 从该 GitHub 子目录安装；需要手动安装时，将完整文件夹放到当前版本支持的技能目录。

当前官方文档列出的项目技能目录为 `.agents/skills/`，用户技能目录为 `~/.agents/skills/`。安装后应存在 `xuexitong/SKILL.md`，并能由 Codex 发现；未出现时可重新打开 Codex。具体目录以所用版本和安装器配置为准。[Codex 官方技能说明](https://learn.chatgpt.com/docs/build-skills)

安装技能后仍需按下文安装 Python 依赖。技能被发现与脚本运行环境就绪是两项检查。

### WorkBuddy

下载仓库中的 `xuexitong.zip`，在 WorkBuddy 的“技能 → 添加技能 → 上传技能”中导入本地 ZIP。不同版本菜单名称可能略有不同；导入后在已安装技能中确认“学习通课程助手”可用。[WorkBuddy 官方安装说明](https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills)

ZIP 已将 `SKILL.md` 放在根目录，并包含中英文名称、描述、版本和作者信息。上传到开放平台发布时，也使用这个 ZIP。[WorkBuddy 技能格式](https://open.workbuddy.cn/docs/skill)

### 其他 Agent

下载完整仓库，定位 `xuexitong/SKILL.md`，将整个 `xuexitong/` 文件夹安装到该 Agent 实际支持的技能目录。只有聊天、没有本地脚本执行能力的环境，无法直接运行这个技能。

## 本地运行

下载并解压仓库后，进入含有本 README 的仓库根目录。以下示例将虚拟环境和账号配置放在技能目录之外，适合直接在源码旁使用；通过 Agent 安装后，由 Agent 使用技能的实际安装路径执行同样步骤。

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r ./xuexitong/requirements.txt
& ./.venv/Scripts/python.exe ./xuexitong/scripts/run.py check

New-Item -ItemType Directory -Path ./workspace -Force | Out-Null
if (-not (Test-Path ./workspace/config.ini)) {
    Copy-Item ./xuexitong/config.example.ini ./workspace/config.ini
}
```

### macOS / Linux

```bash
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r ./xuexitong/requirements.txt
./.venv/bin/python ./xuexitong/scripts/run.py check

mkdir -p workspace
if [ ! -e workspace/config.ini ]; then
    cp xuexitong/config.example.ini workspace/config.ini
fi
```

编辑 `workspace/config.ini`。先填账号和密码，查询课程；再填所选课程 ID，以及需要使用的题库或模型配置。

| 配置项 | 填写方式 |
| --- | --- |
| `[common] username` / `password` | 当前使用者的学习通账号和密码 |
| `course_list` | 明确的课程 ID，多个 ID 用英文逗号分隔；查询课程时可以留空 |
| `speed` / `jobs` | 播放倍速 1–2，章节并发数 1–4 |
| `sequential` | 默认 `true`；需要顺序解锁的课程保持启用 |
| `[tiku] provider` | 默认 `AI`；不使用题库时留空，测验任务将无法完成 |
| `endpoint` / `key` / `model` | 使用 AI 时必填；基础地址和模型 ID 以服务商提供的信息为准 |
| `fallback_model` | 同一服务接口支持的备用模型，留空则不切换 |
| `auto_submit` / `submit` | 全自动提交默认均为 `true`；仅保存时均改为 `false` |
| `cover_rate` | 按覆盖率提交时使用；需设 `auto_submit=false`、`submit=true` |

查询课程、只读核对和执行任务的 PowerShell 示例：

```powershell
# 先查询课程名称与 ID
& ./.venv/Scripts/python.exe ./xuexitong/scripts/run.py courses --config ./workspace/config.ini

# 填好 course_list 后，只读核对章节和任务卡片
& ./.venv/Scripts/python.exe ./xuexitong/scripts/run.py audit --config ./workspace/config.ini

# 确认课程与提交模式后，执行指定课程任务
& ./.venv/Scripts/python.exe ./xuexitong/scripts/run.py run --config ./workspace/config.ini
```

macOS / Linux 将示例中的 `& ./.venv/Scripts/python.exe` 换为 `./.venv/bin/python`。

## 给 Agent 的使用示例

```text
使用学习通课程助手，读取我本地的账号配置，列出课程名称和 ID，先不要执行课程任务。
```

```text
使用学习通课程助手，只读核对我指定课程的章节进度，列出未完成、未开放和等待批阅的任务。
```

```text
使用学习通课程助手，按配置执行我选定的课程，从平台已记录的进度继续。测验只保存答案，不提交；结束后报告平台核验结果和仍未完成的章节。
```

## 运行数据和常见问题

账号配置留在使用者本机。Cookie、日志和答案缓存默认写入配置文件旁的 `.xuexitong/<配置路径哈希>/`，可用 `--state-dir` 指定独立目录。仓库 `.gitignore` 已忽略实际账号配置、运行数据和虚拟环境；发布时只保留空白的 `config.example.ini`。

| 情况 | 处理方式 |
| --- | --- |
| 提示 Python 版本不足 | 用 Python 3.13+ 创建虚拟环境，避免调用系统中的旧版本 |
| 提示缺少依赖 | 用执行技能的同一个 Python 安装 `requirements.txt` |
| AI 配置不完整 | 填写端点、密钥和模型；不使用题库时将 `provider` 留空 |
| 提示运行目录必须在技能目录外 | 将账号配置放到独立工作目录，不要直接运行技能目录内的示例配置 |
| 章节未开放、仅保存或待批阅 | 根据平台状态处理；不要将跳过或保存报告为课程完成 |
| 密码错误、验证码或页面解析失败 | 处理登录或平台变化，保留错误信息，避免反复重跑 |

## 来源与验证

根据 SuperStar 项目整理，保留原始代码中的作者及来源标注。仓库中的 `SKILL.md` 面向 Agent；本 README 面向使用者。

核心程序与启动入口已通过 97 项离线检查；这不代表已对所有课程、账号和平台页面完成在线验证。ZIP 采用浅层目录，压缩与解压体积均小于 3 MB，具体字节数和 SHA-256 见 [打包校验](./打包校验.json)。

## 自愿赞助

如果这个项目对你有帮助，欢迎通过微信赞赏支持维护。赞赏完全自愿，感谢支持。

<img src="./assets/sponsor.jpg" alt="微信赞赏码" width="280">

问题反馈请通过仓库问题，或加入QQ交流群：345353411。

## 安装提示词：复制给 Agent

仓库地址已写入下面的提示词，直接复制对应段落即可。安装任务只完成下载、技能安装和环境检查；配置账号并执行课程是后续独立任务。

### 发给 Codex

```text
请从 https://github.com/842720301wh-ship-it/xuexitong-skill.git 下载并安装学习通技能。

先读取仓库 README.md，技能源目录是 xuexitong/，技能名是 xuexitong。优先使用内置 $skill-installer，从该仓库 main 分支的 xuexitong 子目录安装；如没有该安装器，按当前 Codex 版本实际支持的技能目录安装完整文件夹，不要只复制 SKILL.md，也不要覆盖已有账号配置。

检查 Python 3.13+，在技能目录外创建独立虚拟环境，用其中的 Python 安装技能 requirements.txt，然后执行 scripts/run.py check。将 config.example.ini 复制到用户工作目录，已有配置则保留。此次不要登录学习通、填写账号或运行课程。

完成后告诉我技能实际安装路径、环境检查结果、配置文件位置和下一步如何让你查询课程。只有验证成功的项目才报告已完成；如需我在客户端导入或刷新技能，请给出准确步骤。
```

### 发给 WorkBuddy

```text
请帮我安装这个学习通技能：https://github.com/842720301wh-ship-it/xuexitong-skill.git 。

先读取仓库 README.md，下载仓库根目录的 xuexitong.zip。按当前 WorkBuddy 版本支持的方式安装，并确认“学习通课程助手”可用。能自动安装时请直接完成；如果必须由我在“技能 → 添加技能 → 上传技能”中导入，请把下载好的 ZIP 的绝对路径和导入步骤告诉我，不要把下载完成当作安装成功。

在可执行本地脚本的环境中检查 Python 3.13+，在技能目录外创建独立虚拟环境并安装 requirements.txt，执行 scripts/run.py check。把空白配置模板放入用户工作目录，保留已有配置。此次只安装和检查环境，不登录账号，也不执行课程。

最后报告下载位置、技能安装状态、环境检查结果，以及下一步如何让你查询课程。不要把账号、Cookie 或模型密钥写进技能安装目录。
```

### 发给其他支持技能的 Agent

```text
请从 https://github.com/842720301wh-ship-it/xuexitong-skill.git 下载学习通课程助手，先读取 README.md，再定位 xuexitong/SKILL.md。

检查你当前宿主支持的本地技能安装方式，把整个 xuexitong 文件夹安装到有效技能目录；如果宿主不支持技能注册，但能执行 Python，则在独立工作目录保留完整源码，并说明可以通过脚本调用。无法下载或执行脚本时，请说明具体缺少的能力。

检查 Python 3.13+，在技能目录外创建独立虚拟环境，安装 requirements.txt 并执行 scripts/run.py check。复制空白配置模板到用户工作目录，不覆盖已有配置。只完成安装和环境检查，不登录学习通、不执行课程。

完成后报告实际文件路径、可用的调用方式、环境检查结果，以及下一步需要我填写的本地配置。
```
