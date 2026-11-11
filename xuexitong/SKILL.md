---
name: xuexitong
version: "1.0.2"
author: "842720301wh-ship-it"
display_name: 学习通课程助手
display_name_en: Xuexitong Course Assistant
description: 使用学习通（超星、尔雅、泛雅）账号查询课程与章节进度，执行指定课程的任务点，按配置调用题库或兼容 OpenAI 的模型处理章节测验。适用于学习通课程管理和任务执行。
description_zh: 查询学习通课程与章节进度，执行指定课程任务点，按配置调用题库或 AI 模型处理章节测验，支持进度续跑与完成状态核验。
description_en: Query Chaoxing Xuexitong courses and chapter progress, process selected course tasks and quizzes with configured question banks or AI models, resume progress, and verify completion.
---

# 学习通

使用随包 Python 程序操作用户指定的课程。所有路径相对于本技能目录；配置、账号和输出路径使用当前用户的实际路径。

## 准备

需要 Python 3.13+，以及到学习通和所选题库服务的网络连接。Python 和第三方依赖不包含在包内。在可写工作目录创建虚拟环境，用其中的 Python 安装本技能 `requirements.txt`：

```text
python -m venv /实际工作目录/.venv
<虚拟环境Python> -m pip install -r /实际技能目录/requirements.txt
<虚拟环境Python> /实际技能目录/scripts/run.py check
```

Windows 的虚拟环境 Python 位于 `.venv/Scripts/python.exe`，其他系统位于 `.venv/bin/python`。

将 `config.example.ini` 复制到用户工作目录后填写账号和密码。需要模型答题时填写 `provider=AI`、`endpoint`、`key`、`model`；端点按服务商要求填写完整基础地址。只执行非测验任务时可将 `provider` 留空。其他题库保留原接口，可按需修改 `[tiku]`。

## 使用

统一入口为 `scripts/run.py`。以下命令中的 `python` 使用已安装依赖的虚拟环境 Python。

```text
python /实际技能目录/scripts/run.py courses --config /实际工作目录/config.ini
python /实际技能目录/scripts/run.py audit --config /实际工作目录/config.ini
python /实际技能目录/scripts/run.py run --config /实际工作目录/config.ini
```

- `courses`：登录并列出课程名称和 ID，不执行任务。课程不明确时先查询，依据用户选择填写 `course_list`，多个 ID 用英文逗号分隔。
- `audit`：读取所选课程的章节和任务卡片，不执行学习或答题。可用 `--chapter-prefix "1.1"` 筛选需检查卡片的章节；默认检查全部。
- `run`：处理指定课程的视频、音频、文档、阅读、章节测验和平台可用的直播任务。默认顺序执行，从平台已记录进度续跑；不自动开启签到。

`speed` 范围为 1–2；`jobs` 范围为 1–4。顺序解锁课程保持 `sequential=true`。`notopen_action=continue` 可跳过未开放章节并继续处理，但跳过项仍计为未完成。

测验默认 `auto_submit=true`：题库或模型失败时也会填入兜底答案并提交，答案不保证正确。用户要求仅保存时，将 `auto_submit=false`、`submit=false`；要求按覆盖率提交时，将 `auto_submit=false`、`submit=true` 并设置 `cover_rate`。仅保存或待批阅任务可能阻塞后续章节。

AI 每个模型首次失败后按 `ai_retry_times` 重试，耗尽后才使用 `fallback_model`；备用模型留空即不切换，不跨服务商共享密钥。模型名称使用用户所选服务实际支持的 ID。

## 输出与结果

运行数据默认写入配置文件旁的 `.xuexitong/<配置路径哈希>/`，也可用 `--state-dir` 指定独立目录。账号配置、Cookie、日志和答案缓存只保留在用户工作目录，不放入共享技能包，不在回复中展示密钥或 Cookie。

依据退出码和平台最新状态报告结果。只有出现“平台完成状态核验通过”且程序正常退出，才报告课程完成；保存答案、处理结束、章节跳过均不等于平台完成。遇到密码错误、验证码或无法解析的页面，报告阻塞原因，不无限重跑。

源码来自用户提供的 SuperStar 项目，保留原文件中的作者及来源标注。
