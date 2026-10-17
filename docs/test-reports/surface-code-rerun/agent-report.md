# 表面码阈值研究谱系：独立上下文运行报告

本次结果为 **PARTIAL**。已生成可离线打开的交互谱系图和完整研究记录；仍未取得独立全微波低阈值实验的全文，不能将该中心分支标记完成。原样技能包的审计 JSON 同样为 PARTIAL。

## 输入与执行边界

唯一种子为 [arXiv:2408.13687v1](https://arxiv.org/abs/2408.13687v1)，固定 2024-08-24 首次版本。研究日期及截止日期为 **2026-10-17（Asia/Shanghai）**，前向检查包含 2026 年十月可发现的工作。主线追溯稳定子、拓扑存储、重复症状测量、扩码、泄漏与相关突发、解码准确率与速度，以及直接的逻辑/平台后续。

这是新的对话上下文执行，使用共享文件系统；不声称操作系统沙箱隔离。只读取所给 packet 和本隔离运行目录；没有读取其他项目、已有作者谱系、仓库历史或另一代理的工作。model 字段为 null。父代理只补充执行授权、访问边界和用户的公开稿检索请求；其出版社访问观察没有被计为本执行器的来源读取。

## 实际覆盖

| 项目 | 观测数量 |
|---|---:|
| 作品 | 52 |
| 结果 | 54 |
| 关系 | 58 |
| 证据记录 | 55 |
| 候选 | 58 |
| 纳入 / 排除 / 延期 | 52 / 6 / 0 |
| 已获取全文并核对相关段落 / 仅摘要 | 49 / 3 |
| 参考集 | 6 |
| 研究分支 | 8（7 covered，1 gap） |
| 公开研究操作日志 | 95 |
| 全部 trace 条目 | 109 |
| 教学路线 / 概览转折点 | 9 / 5 |

95 是检索/打开/查找/元数据读取的日志记录数，**不是 95 次独立搜索查询，也不是 95 篇论文**。其中 49 条为带请求时间的 arXiv 元数据读取，46 条为 web 操作记录（包含拆出的失败部分）。批量查询的完整参数在 JSONL 中。所有 54 个结果和 58 条关系都为 proposed，合计 112 项等待学术评审；没有声称得到独立专家确认。

6 个参考集分别为种子正文/参考文献、Terhal 综述目录与相关章节、Roffe 阈值与容错章节、持续 RL 控制原文表格、AQ2 解码比较，以及新增逻辑门论文的引言/方法/参考文献。它们用于检查分支，结果证据仍指向各原始作品的实际版本与位置。

## 主要发现及需要保留的区别

- 种子 v1 的距离 3、5、7 标度给出 Λ=2.14±0.02；距离 7 的每周期逻辑错误率约为 0.143%。其 d=5 实时解码与此是另一项结果，端点延迟 63±17μs 尚不包括逻辑反馈。见[种子 §II、§V](https://arxiv.org/html/2408.13687v1)。
- 约 10^-10 的表观错误底限来自长时重复码实验，不能当作已测二维表面码错误率；剩余突发的原因在指定 v1 未确定。2026 年勘误更正重复码图的标注，未报告该数值结论改变。见[种子 §IV](https://arxiv.org/html/2408.13687v1)、[正式勘误](https://pmc.ncbi.nlm.nih.gov/articles/PMC13171424/)。
- 准确率、持续吞吐、反应时间和完整闭环是不同检验。AQ2、并行神经窗口、FPGA 闭环与种子的资源和任务定义分别保留，没有作跨实验数字排名。来源链接及定位见 map 和 source-index。
- 公开稿补查发现 [2607.01473v1](https://arxiv.org/html/2607.01473v1)：同一团队在 d=3 中以全部样本实现 Clifford 生成集，CNOT 平均门保真度为 0.643(2)，并明确把随码距增长的门抑错列为下一实验里程碑。它是不同作品，不能代替 PRL 全文。
- 新逻辑门论文又引出[六月格点手术实验](https://arxiv.org/html/2606.06598v1)和[魔法态培育实验](https://arxiv.org/html/2512.13908v1)。前者的泄漏剔除、无错后选择与转角符号选择需分层；后者约 10^-4 的误差上界对应约 8% 保留率，嫁接后的空闲误差另行评估。
- 理论培育的 v1 HTML 内页日期异常，改用[确切 PDF](https://arxiv.org/pdf/2409.17595v1)核对。地图保留其 §2.6 已知符号问题、§3.2 模拟外推和反馈延迟假设；未把理论成本当成实验性能。

以上为本执行器从来源作出的记录与编辑判断，非数学证明复核或实验复现。

## 未解决的中心缺口

[Experimental Quantum Error Correction below the Surface Code Threshold via All-Microwave Leakage Suppression](https://journals.aps.org/prl/abstract/10.1103/rqkg-dw31)，Tan He、Weiping Lin、Rui Wang、Yuan Li 等，PRL 135, 260601，DOI **10.1103/rqkg-dw31**，2025-12-22。

已读取官方摘要，记录 Λ=1.40(6) 等作者报告；全文样本处理、解码和完整条件仍未核对。先前直接 PDF、链接、harvest 和公开搜索失败均已记录。父代理通知官方页安全验证/授权障碍后，本执行器没有重试出版社。

用户随后要求寻找 arXiv 版本。精确题名、DOI、作者、英文/中文变体以及 USTC 官方作者/成果/新闻页的检索，仍**未确认对应 arXiv 或作者公开全文**。这不证明公开版本不存在。[USTC 官方新闻](https://news.ustc.edu.cn/info/1048/93556.htm)指向同一 DOI；新发现的 2607.01473 在参考文献中把 PRL 列为先前另一作品，身份不能合并。

分支 independent-replication 和 stop.unresolved_branch_ids 均保留该缺口。候选因有摘要证据已纳入；延期候选数为 0 并不表示无未完成工作。其他 covered 是本次范围内的证据覆盖判断，不是穷尽性证明。没有按论文数量或概览卡片数量停止研究。

## 执行例外与真实检查结果

- **CLI start 两次调用被策略拒绝。**之后没有再尝试 start，也没有代理执行、内联执行或替换路径运行它。原文、完整参数和工作目录保存在 execution-policy-events.json。
- 因此不存在 helper 生成的原始 brief。经后续明确授权，直接编写 research-brief.json 并标记 manual-fallback-not-helper-generated；它只保存种子和研究截止等信息，**不等价于 start 成功**。Skill 原步骤在本次存在明确的流程例外。
- --help 成功的事实保留。采集器首次 30 次请求已经写出 UTF-8 文件，但控制台打印遇到 GBK UnicodeEncodeError；后续 UTF-8 读取成功。没有把退出 1 包装成无错误运行。
- 最终 validate 实际成功，errors 为空；此前概览卡片挂了 5 条结果，超过合同上限，已调整为 4 条展示链接并保留所有语料。
- build 首次拒绝覆盖已有输出；随后在自己生成的 viewer 目录使用 --force 重建成功。原输出和参数在 verification-record.json。
- 在隐藏 IAB 页 http://127.0.0.1:8767/map.html 使用 mcp__cua_repl.js 完成 AX/DOM 交互检查：概览、来源与缺口、指定版本、结果条件、关系检查器及两个结果的条件比较可访问。一次 SVG 节点激活不受支持，通过普通检查器按钮完成关系查看。浏览器没有审批提示或拒绝。
- **截图返回 Unable to capture screenshot。**没有截图产物，也不声称像素级视觉验收。临时浏览器页已关闭，loopback 检查服务器已停止；交付 HTML 文件仍可离线打开。
- 原样 packet audit-research 的 JSON 为 **PARTIAL**：execution_provenance、cutoff_consistency、source_trail 为 PASS；research_completion 为 PARTIAL。**实际进程退出码是 1，文档写的 PARTIAL 退出码为 3**，两者差异没有隐藏或改写。
- 审计仅验证本地记录及跨文件一致性；不能认证真实工具调用、用户授权、分支选择、文献穷尽、科学真值或替代独立研究者。原样 packet 未修改；父代理可另外记录新版审计器复检差异。
- manifest 的时间区间绑定研究与渲染冻结阶段；审计执行在冻结之后，确切前后时钟与完整输出单独保存在 audit-packet-execution.json。

## 文件入口

- viewer/map.html：完整可离线交互谱系图。
- map.json：作品、结果、条件、关系和证据数据。
- research-log.json：参考集、候选决策、分支和停止判断。
- tool-trace.jsonl：实际查询、来源 URL、观察、时间与失败。
- source-index.md：52 项作品的实际读取版本与定位。
- run-manifest.json：7 个核心产物的 SHA-256 绑定和执行声明。
- prompt.md、research-brief.json、SKILL.md：原始调用/约束、手工 brief、实际技能入口快照。
- audit-packet.json / audit-packet-execution.json：审计结论及真实命令、时间、退出码。
- verification-record.json、execution-policy-events.json：构建/页面检查和拒绝原始记录。
- source-metadata.json、metadata-trace.jsonl、corpus-notes.json：来源元数据与提取工作记录。

这些研究日志是代理记录的观察，未经提供商认证。生成数据没有重新运行论文实验或模拟；未知条件用 null 或明确说明保留。下一步最重要的是取得 PRL 合法全文并核查独立复现分支，然后由领域研究者复核核心主张和方法关系。

