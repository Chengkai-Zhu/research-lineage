[English](README.md) · [简体中文](README.zh-CN.md)

# LitDelta

**看懂研究如何推进：改变了什么、在什么条件下成立、证据在哪里。**

仓库名为 `litdelta`，产品名为 LitDelta；安装包和 skill 继续使用 `research-lineage`。`litdelta`、
`research-lineage` 和 `python -m research_lineage` 使用同一套本地工具。

[在线试用 LitDelta](https://chengkaizhu.site/litdelta/) ·
[下载完整离线集合](https://chengkaizhu.site/litdelta/offline.zip) ·
[下载当前预览版 Skill](https://chengkaizhu.site/litdelta/downloads/research-lineage-skill-0.2.0.zip)

无需安装即可阅读结果比较、按作者追踪脉络，以及保留 PARTIAL 状态的真实 52 篇论文研究案例。
离线集合解压后打开 `START-HERE.html`；研究新主题则将 Skill 交给你的研究助手运行。

读完比较后，点击 **Save this explanation**，即可将附带条件、精确来源与审阅状态的说明复制到笔记或下载为 Markdown。在 **Use your own paper** 中填入论文或问题，还可选择梳理发展、比较方法或准备组会，复制专属研究请求交给研究助手。输入只在当前页面处理，网站不会上传它，也不会代替助手执行研究。
预览版工具包与最新的已标记 Release 分开提供。

安装当前 checkout 后，可运行 `litdelta demo --example comparisons --out output/comparisons`，
打开 `output/comparisons/map.html`。这个限定范围的例子展示同一论文中的层级并行性、
总工作量、生成依赖和翻译质量；它是结果比较阅读案例，完整研究流程另由 #14/#12 验证。
查看[来源与阅读任务](examples/attention-comparisons/README.md)及
[浏览器预览构建与验证](docs/litdelta.md#browser-preview)，包括下载文件的校验方法。

**从一个方向出发，读懂研究如何发展。**

[![CI](https://github.com/Chengkai-Zhu/litdelta/actions/workflows/ci.yml/badge.svg)](https://github.com/Chengkai-Zhu/litdelta/actions/workflows/ci.yml)

一个把**研究方向或单篇论文**整理成清晰研究脉络的 **Agent Skill**。给 AI 一句话，得到有来源依据、可离线浏览与分享的交互地图。

> 请整理 quantum signal processing 这个方向的发展历史。

也可以只提供论文链接、DOI、标题或 PDF，让它梳理这篇论文背后的研究发展。

[安装 Skill](docs/quickstart.md#use-the-standalone-skill) · [实际研究案例](#实际研究案例) · [研究工具说明](docs/research-tools.md)

下述新版功能已合并到 `main`，**0.2 暂未发布 Release**。目前已发布的安装包仍为 [v0.1.1](https://github.com/Chengkai-Zhu/litdelta/releases/tag/v0.1.1)。

![先看发展脉络，需要时再展开细节](docs/assets/reading-overview.png)

## 先读懂脉络，再深入探索

- **先看故事。** 用简短导读和带来源的关键变化，说明这个方向如何发展。
- **知道下一篇读什么。** 沿建议路线阅读，再按需探索完整地图。
- **随时核查依据。** 点开关系，查看论文的确切版本、证据位置及成立条件。
- **完整保存结果。** 导出单个离线 HTML，以及 SVG、JSON 和核查报告；筛选不会丢弃导出证据。

宿主 AI 使用自己的检索和文档工具完成研究，内置 Python 工具负责准备输入、校验记录和生成阅读页面。本地核心不要求账号或付费服务。运行 Skill 需要 Python 3.11+，打开导出的 HTML 只需要浏览器。

## 使用 Skill

使用 Python 3.11+ 从源码构建当前独立 Skill：

```sh
git clone https://github.com/Chengkai-Zhu/litdelta.git
cd litdelta
python scripts/package_skill.py --out dist
```

将 `dist/research-lineage-skill-0.2.0.zip` 中的 `research-lineage` 文件夹解压到宿主的技能目录，参见[安装说明](docs/quickstart.md)。然后提供研究方向或论文：

> 使用 research-lineage，整理 quantum signal processing 的发展历史。

> 使用 research-lineage，从 https://arxiv.org/abs/2408.13687v1 这篇论文出发，梳理它背后的研究发展。

Skill 会选择合理范围，并跟随你的语言。无需填写 ID、日期、文献列表或 JSON。只提供标题时会先核对论文身份；私有附件默认在本地读取，额外上传需要你的明确授权。当前阅读器控件为英文，研究内容可以使用中文。

研究覆盖不设默认论文数量配额。宿主会追溯前序与后续研究，记录候选取舍和有来源依据的研究分支，在简洁首页背后保留完整的收录文献。[研究运行检查](docs/research-tools.md#recorded-research-coverage)会将记录缺失显示为部分完成或失败；通过检查不代表科学完整性已获认证。

## 实际研究案例

| 输入 | 阅读脉络 | 证据范围 |
| --- | --- | --- |
| 一个方向 | [QSP 到 QSVT](docs/sources.md) | 8 篇论文，以摘要为依据的草稿 |
| 一个新问题 | [句子向量到注意力机制](examples/nmt-attention/README.md) | 6 篇原始论文，核对到具体章节 |
| 单篇论文，独立 Agent | [表面码独立研究记录](docs/test-reports/surface-code-rerun/README.md) · [交互报告](docs/test-reports/surface-code-rerun/report.html) | 52 项工作，实际检索与候选日志；一项关键全文缺口保留为 PARTIAL |
| 编写好的示意案例 | [表面码量子存储器](examples/surface-code/README.md) | 4 项工作的阅读路径；单输入研究验收已在 #12 重新打开 |

这些案例是有范围限制的研究历史，标注仍待学术审核。来源核对和软件测试通过，不代表科学结论已经得到独立专家认证。真实外部审阅与参与者实验仍保留在[待办 #10](https://github.com/Chengkai-Zhu/litdelta/issues/10)。

<details>
<summary>直接使用 Python 工具</summary>

```sh
git clone https://github.com/Chengkai-Zhu/litdelta.git
cd litdelta
python -m pip install .
research-lineage demo --out output/demo
```

打开 `output/demo/map.html`。运行内置示例不需要网络或模型密钥。

```sh
research-lineage start "quantum signal processing" --out output/topic
# 宿主 AI 检索来源并填写空白草稿；start 不会编造研究地图。
research-lineage validate output/topic/map.json
research-lineage build output/topic/map.json --out output/topic/reading
```

[数据格式](skills/research-lineage/references/data-guide.md) · [检索、身份核对与评测命令](docs/research-tools.md)

</details>

## 参与贡献

修正一个假设、补充更准确的来源位置，或添加经过核查的研究脉络。请保留不确定性与论文版本信息。

```sh
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests scripts skills
python scripts/package_skill.py --out dist
```

[产品设计](docs/design/skill-first-reading.md) · [验收记录](docs/test-reports/skill-first-workflow.md) · [路线图](docs/roadmap.md) · [贡献指南](CONTRIBUTING.md)

如果它帮助你理解了一个方向，欢迎分享地图或给仓库点一个 Star，让更多研究者发现它。

## 许可

[Apache-2.0](LICENSE)。论文版权归原权利人所有；仓库仅包含原创整理和来源链接，不分发论文全文。
