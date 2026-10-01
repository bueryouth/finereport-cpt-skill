# 帆软 FineReport 11 · CPT 报表生成技能包（使用说明）

本技能包基于 **FineReport 11 官方 demo（240 个 .cpt + 144 个 .fvs 实测）** 与 **此前 utools 插件已沉淀的知识** 深度拆解构建，用于：按自然语言需求**生成 / 编写 / 修改**可直接导入 FineReport 设计器即用的 `.cpt` 报表文件，并支持批量产出。

## 安装位置

技能包安装到对应 AI 工具的技能目录（如 `~/.pi/agents/skills/` 或 `C:\Users\<用户>\skills\`），安装后目录为 `finereport-cpt-skill/`。

已按标准 SKILL.md 格式安装（frontmatter 合规、quick_validate 通过），后续会话中当你说"生成一个 XX 报表 / 写个 cpt / 这个 cpt 怎么改"时会自动触发本技能。

## 技能包目录结构

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 技能主入口：能力总览、5 步工作流、快速上手示例、模板导航、边界说明 |
| `references\cpt-structure.md` | 《cpt 结构与语法规则》：18 节结构手册，每节附 demo 真实 XML 片段与来源，含"与常见认知的差异"19 条与常用 XPath 表 |
| `references\feature-catalog.md` | 《cpt 功能特征目录》：15 类目录全量 grep 统计（数据集/控件/图表/JS事件/超链接/工具栏/填报/公式/样式/权限…） |
| `references\features.md` | 《九大能力专题》：脚本、JS、Java、入库、工具栏、按钮、事件、样式、公式，每项含原理+写法+模板引用 |
| `references\generator-guide.md` | 生成器 JSON 规格完整参考手册（字段/示例/CLI/rawXml 透传） |
| `scripts\generate_cpt.py` | 生成器：JSON 规格 → .cpt（UTF-8 无 BOM、LF、零缩进、CDATA、随机模板 UUID） |
| `scripts\validate_cpt.py` | 验证器：XML 良构 + 结构模式校验（对照 demo 抽取的 schema）+ 编码检查，输出逐文件报告 |
| `scripts\cpt_schema.py` | 结构常量/白名单（TableData class、O 的 t 值、控件/图表 class 前缀、顶层节点顺序） |
| `assets\templates\` | 8 个可直接导入的 .cpt 模板 + 《模板说明.md》（覆盖矩阵、修改要点） |
| `assets\examples\` | 4 组 JSON 规格 + 生成产物样例（基础查询/参数联动/填报入库/图表） |

## 三种用法

### 用法 A：基于现成模板改造（最快）
1. 从 `assets\templates\` 挑一个最接近需求的模板（见下方清单）；
2. 让 AI 按你的需求改标题、SQL、参数、样式；
3. 用设计器打开复核后部署。

### 用法 B：写 JSON 规格 → 生成器 → 验证器
```powershell
python finereport-cpt-skill/scripts/generate_cpt.py spec.json out.cpt
python finereport-cpt-skill/scripts/validate_cpt.py out.cpt
```
- 规格格式见 `references\generator-guide.md`，可直接参照 `assets\examples\spec_*.json` 改写；
- 支持：SQL/内置数据集、参数与控件、单元格/合并/扩展、公式、命名样式与条件属性、JS 事件、超链接、按钮、工具栏、填报入库（智能提交）、VanChart 图表、脚本、Java 自定义函数引用；
- 复杂能力（如深度的图表配置）可用规格中的 `rawXml` 透传注入真实 XML 片段。

### 用法 C：咨询 cpt 结构 / 标签含义
直接问，AI 会读取 `references\cpt-structure.md` 与 `feature-catalog.md` 回答，所有说法均可溯源到 demo 真实文件。

## 模板清单（assets\templates\）

| 模板 | 覆盖能力 | 数据依赖 |
|---|---|---|
| 01_基础查询报表.cpt | 公式、样式、SQL 查询 | FRDemo |
| 02_参数联动报表.cpt | 参数/控件/事件(级联)/公式 | FRDemo |
| 03_填报入库报表.cpt | **入库**、工具栏、按钮、公式 | FRDemo（up 表） |
| 04_图表报表.cpt | 图表（柱图+饼图）、样式 | FRDemo |
| 05_按钮JS事件报表.cpt | **JS**、按钮、事件、公式、超链接 | FRDemo |
| 06_样式定制报表.cpt | **样式**（条件属性高亮） | FRDemo |
| 07_脚本报表.cpt | **脚本**（afterload/单元格 JS）、按钮、事件 | FRDemo |
| 08_Java自定义函数报表.cpt | **Java**（=MySum(...)）、公式、样式 | 预览需装对应函数插件 |

九项能力（脚本/JS/Java/入库/工具栏/按钮/事件/样式/公式）每项均有知识文档说明 + 至少一个模板。

## 验证流程（每个生成的 cpt 必须跑）

```powershell
python finereport-cpt-skill/scripts/validate_cpt.py <cpt文件或目录> -r
```
校验：XML 良构（报行号）→ 根节点/节点顺序/class 白名单/AttrMark → 编码（无 BOM、UTF-8）。全部通过后再交付导入。

## 关键约定（与 demo 实测一致，勿偏离）

- 根节点 `<WorkBook>`，UTF-8 无 BOM、LF、零缩进、无 DOCTYPE；
- 用户可见文本与 SQL 用 CDATA；`class` 属性 = Java 类全限定名；
- 行高/列宽单位 EMU（914400=1 英寸）；节点顺序敏感：TableDataMap → Report → ReportParameterAttr → StyleList → AttrMark；
- `.fvs`（决策报表）是 ZIP 压缩包（内部 `editor.tpl` 根节点 `<Duchamp>`），与 .cpt 不同格式；
- 11.0 新引擎模板另存为 `.cptx`（压缩包），本技能生成/解析的是 .cpt。

## 关联项目参考

技能包吸收了此前分析项目中沉淀的知识（详见技能包内 `references\related-projects.md`）：

| 项目 | 定位 | 与技能包的协作方式 |
|---|---|---|
| `finereport-cpt-main` | SQL 驱动：从带 `AS` 别名的 SQL 生成基础 cpt（`scripts\gen_cpt.py`）、只同步 SQL/参数不动布局（`sync_sql.py`）、交付前静态校验（`check_cpt.py`） | 手上有现成 SQL 时优先走这条路；其 20 条静态校验规则已移植进本技能的 `validate_cpt.py` |
| `fineReport-builder-main` | Agent 构建器：基于真实模板（信贷合同分析 148KB/172KB）的筛选组件/数据列增删改 + Excel 转换 + Web 界面 | 深度改造复杂模板时参考其 JSON 中间层配置与模板注解（`templates\CPT_TEMPLATE_ANNOTATION.md`） |

吸收的关键知识（已写入技能包）：对齐值正确映射（0=居中/2=左/4=右）、BoundsWidget 必须包裹参数面板控件、样式表按索引引用只追加、`Format` 在 Style 首位、`full="true"` 命名样式表头居中坑、`FineColor` hor/ver 需写 -1/-1、必填校验用 `EMSG`+`allowBlank` 子节点、`ClassTableData`/`RecursionTableData` 数据集类型。

## 素材与分析产物

- 官方 demo：FineReport 11.0 安装目录下的 `reportlets/demo/` 子目录（240 cpt + 144 fvs，15 个目录全量特征提取 + 每目录抽样深读）；
- 分析产物存放于本地 `.build/` 过程目录中（含 scratch 子目录），仅用于开发阶段参考：
  - `utools-digest.md` — utools 插件知识拆解摘要
  - `demo-structure.md` — 结构采样初稿
  - `feature-catalog.md` — 特征目录初稿
  - `related-projects-digest.md` — 关联项目深读
  - `verification-report.md` — 验收报告
- 关联项目知识已吸收进本技能包，不再依赖外部路径。

## 已知边界

- 生成产物通过结构校验，但建议部署前在设计器打开复核一次（图表/填报等复杂节点建议用模板底稿改）；
- 内置数据集的行数据（RowData）是 FineReport 专有压缩格式，生成器只产出合法空壳，真实行数据需在设计器回填；
- demo 240 个 cpt 中无"脚本型数据集"节点，脚本能力以报表级 afterload JS 与单元格事件 JS 为载体；
- SQL 模板统一使用 FRDemo 连接（FineReport 内置示例库）；若你的环境连接名不同，导入后改数据集连接即可。
