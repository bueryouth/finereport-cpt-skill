---
name: finereport-cpt
description: 生成、解析与修改帆软 FineReport 11 报表模板（.cpt 文件）的完整技能包。可根据自然语言需求直接产出可导入 FineReport 设计器即用的 .cpt 文件，覆盖 SQL/内置数据集、参数与控件、单元格与扩展、公式与汇总、样式与条件属性、JS 事件、超链接、按钮与工具栏、填报入库（智能提交）、VanChart 图表、数据集脚本与 Java 自定义函数。内置 8 个现成模板、JSON 规格转 cpt 的 Python 生成器、以及 XML 良构与结构模式校验器。当用户要求生成/编写/修改帆软 cpt 报表、把数据需求变成 FineReport 模板、批量产出报表、或询问 cpt 文件结构、标签含义、填报入库写法、图表与 JS 事件配置时使用。
---

# 帆软 FineReport 11 · CPT 报表生成技能包

> 适用场景：用户要求生成、编写、修改帆软 .cpt 报表模板，把数据需求变成 FineReport 模板，批量产出报表，或询问 cpt 文件结构、标签含义、填报入库写法、图表与 JS 事件配置。
> 一句话摘要：本技能包把自然语言报表需求转化为可直接导入 FineReport 11 设计器使用的 .cpt 文件；一切结构写法以官方 demo 实测为准，先选模板改、再写规格生成、最后跑校验器。

## 能力总览

本技能包覆盖 FineReport 11 普通报表（.cpt）从数据源到交互的完整建模能力，全部写法经过官方 demo（240 个 cpt）实测核对：

- **数据集**：SQL 数据集（按连接名引用 FRDemo）、内置数据集、数据集内动态拼参（${...} 公式）、跨数据集传参。
- **参数与控件**：报表参数默认值、参数面板（下拉框/下拉树/日期/单选组/复选/文本数字框）、查询提交按钮。
- **单元格与扩展**：表头文本、数据集列绑定、纵向/横向扩展、左父格/上父格、分组（FunctionGrouper）与汇总（SummaryGrouper + SumFunction）、合并（cs/rs）、斜线表头。
- **公式与汇总**：以等号开头的单元格公式，聚合、算术、日期、SQL 取数、权限函数，系统变量 $fr_username / $fine_username / $fr_authority。
- **样式与条件属性**：StyleList 字体/边框/背景/对齐/数字日期格式，条件属性高亮（斑马纹、强制分页、动态换控件）。
- **JS 事件**：afterinit / click / statechange / afteredit / startload / afterload / writesuccess 等，支持带公式参数的监听器。
- **超链接**：报表钻取超链接（ReportletHyperlink）与网页超链接（WebHyperlink），可带参、弹窗。
- **按钮与工具栏**：内置提交/校验/增删行/分页/打印/导出按钮，单元格自由按钮 FreeButton，自定义 JS 按钮。
- **填报入库**：ReportWriteAttr + BuiltInSQLSubmiter + IntelliDMLConfig 智能提交（按主键 insert/update），字段绑定单元格/公式/常量，提交条件公式。
- **图表**：VanChart 图表单元格（饼/柱/折线/面积/仪表盘/散点/气泡/地图/热力），ChartDefinition 数据绑定。
- **脚本**：数据集 SQL 内公式拼参、单元格公式变量、前端 JS 脚本三类写法。
- **Java 自定义函数/类**：公式中调用自定义函数（继承 AbstractFunction），插件 plugin.xml 注册与类部署方式。

## 工作流总览

按五步执行，不要跳步：

1. **分析需求**：读用户需求，确认报表类型（列表/分组/交叉/填报/图表）、数据源表与字段、过滤参数、是否入库、是否需要图表或 JS。拿不准数据连接名时，默认用 FRDemo 并在交付说明中提示用户改连接。
2. **选模板或写 JSON 规格**：需求与现有模板接近时，直接复制 `assets/templates/` 下最接近的模板改；全新结构或批量产出时，编写 JSON 规格文件（字段约定见 `references/generator-guide.md`）。
3. **生成**：改模板 = 直接编辑复制出来的 .cpt；新生成 = 运行 `scripts/generate_cpt.py 规格.json -o 输出.cpt`。
4. **验证**：必须运行 `scripts/validate_cpt.py 输出.cpt`，读验证报告，有错就改，改完再验，直到零错误。
5. **交付导入**：把 .cpt 文件交付给用户，说明数据连接依赖、参数默认值、以及"建议在设计器打开复核一遍"。

## 快速上手

### 示例 A：基于现成模板改造成"销量分析报表"

1. 复制模板：

```powershell
Copy-Item "C:\Users\Administrator\skills\finereport-cpt-skill\assets\templates\01_基础查询报表.cpt" "E:\out\销量分析报表.cpt"
```

2. 用文本编辑器打开 `E:\out\销量分析报表.cpt`，在数据集块内把 Query 的 SQL 改成目标查询，把单元格里的列名改成目标字段名。
3. 验证：

```powershell
python "C:\Users\Administrator\skills\finereport-cpt-skill\scripts\validate_cpt.py" "E:\out\销量分析报表.cpt"
```

4. 零错误后，把该文件放入 FineReport 设计器的 reportlets 目录或直接拖进设计器打开复核。

### 示例 B：写 JSON 规格 → 生成 → 验证

1. 编写规格文件 `E:\specs\order.json`（字段含义见 `references/generator-guide.md`），声明数据集、参数、单元格网格、样式与汇总公式。
2. 生成：

```powershell
python "C:\Users\Administrator\skills\finereport-cpt-skill\scripts\generate_cpt.py" "E:\specs\order.json" -o "E:\out\订单查询报表.cpt"
```

3. 验证：

```powershell
python "C:\Users\Administrator\skills\finereport-cpt-skill\scripts\validate_cpt.py" "E:\out\订单查询报表.cpt"
```

4. 报告显示 XML 良构通过、必填节点齐全、坐标无重叠后交付；否则按报告指出的行列号或节点名回改规格并重新生成。

## 模板库导航

模板均位于 `assets/templates/`，复制后改造最快：

| 文件名 | 覆盖能力 | 数据依赖 |
|---|---|---|
| 01_基础查询报表.cpt | SQL 数据集、表头、纵向分组、Sum 汇总、合计行公式 | FRDemo 连接 |
| 02_参数联动报表.cpt | 参数面板、下拉框/下拉树控件、多值查询、动态拼 SQL | FRDemo 连接 |
| 03_填报入库报表.cpt | 填报控件、智能提交 IntelliDMLConfig、工具栏提交/校验按钮 | FRDemo 连接 |
| 04_图表报表.cpt | VanChart 图表单元格、饼图/柱形图数据绑定 | FRDemo 连接 |
| 05_按钮JS事件报表.cpt | FreeButton、afterinit/click/statechange 事件、弹窗交互 | FRDemo 连接 |
| 06_样式定制报表.cpt | StyleList 字体/边框/背景/对齐、条件属性斑马纹高亮 | 内置数据，无连接依赖 |
| 07_脚本报表.cpt | 数据集内公式拼参、单元格公式变量、前端 JS 脚本 | FRDemo 连接 |
| 08_Java自定义函数报表.cpt | 公式调用自定义函数、插件类注册与部署说明 | 需另行部署对应 Java 插件 |

## 生成器使用

生成器细节（JSON 规格全部字段、CLI 参数、坐标系与样式索引规则）见 `references/generator-guide.md`。要点速记：

- CLI：`generate_cpt.py 规格.json -o 输出.cpt`，支持 `--encoding utf-8`。
- JSON 规格顶层四段：datasets（数据集）、parameters（报表参数）、grid（单元格网格，0 基行列）、styles（样式表）。
- 单元格坐标 0 基（c=列、r=行），公式以等号开头，扩展方向 dir 0=纵向、1=横向。
- 生成器输出与 demo 风格一致：UTF-8 无 BOM、零缩进、LF 换行。

## 验证流程

每次生成或修改后**必须**运行校验器，不得跳过：

```powershell
python "C:\Users\Administrator\skills\finereport-cpt-skill\scripts\validate_cpt.py" 目标.cpt
```

验证器做两层检查：

1. **XML 良构**：能否被标准 XML 解析器完整解析（标签配对、CDATA 闭合、属性引号）。
2. **结构模式**：根节点 WorkBook 存在、数据集块完整、Report 内行列尺寸与单元格列表齐全、每个单元格含值节点与扩展节点、填报配置的字段坐标在网格内。

读报告：通过项列在 PASS 段，错误项列在 FAIL 段并给出行列号或节点名。**不过即改**：按 FAIL 项回改 JSON 规格或模板源文件，重新生成，再次验证，直到无 FAIL。验证器不检查的事项（SQL 能否跑通、样式视觉效果），一律在交付说明里提示用户到设计器复核。

## 参考文档导航

`references/` 下四份文档，按需读取，不必全部通读：

- **cpt-structure.md**：写新报表、改 XML、报错定位时读。覆盖文件级约定、每个节点的真实 XML 片段、单元格/样式/公式/JS/超链接/工具栏/填报/图表/权限写法，以及与常见教程认知的差异清单。
- **feature-catalog.md**：需要确认某个 class 名/事件名/按钮类是否真实存在、想看出现频次时读。按特征类别给出 grep 统计与示例文件路径，是"查证类名"的检索手册。
- **features.md**：做某个专题（脚本、JS、Java 自定义函数、入库、工具栏、按钮、事件、样式、公式）前读。每个专题给出原理、写法要点、对应模板引用与注意事项。
- **related-projects.md**：需要批量 SQL 驱动出表、参考 JSON 中间层规格、或遇到样式/校验类隐蔽坑时读。

## 关联项目参考

两个只读参考项目位于 `E:\mis-workspace\08-fanruan\report-cpt-skill\`，吸收其工程做法，不复制代码：

- **finereport-cpt（SQL 驱动生成器）**：`finereport-cpt-main\`，gen/sync/fix/check 四脚本，从定稿 SQL 生成/同步/断言校验 cpt。批量同构报表时参考其思路。
- **fineReport-builder（真实模板构建器）**：`fineReport-builder-main\`，Agent 按 JSON 中间层配置（data_sources/filter_controls/cells/styles）改造真实模板。复杂布局改造时参考其结构化规格。

详细定位、JSON 格式、20 条校验规则与冲突处理记录见 `references/related-projects.md`。

## 已知边界与注意事项

- **.fvs 不是 cpt**：决策报表/大屏文件 .fvs 是 ZIP 压缩包（PK 头），内部主模板叫 editor.tpl、根节点是 Duchamp，不是 WorkBook。本技能包只产出普通报表 .cpt，不生成 .fvs。
- **cptx 与 cpt 的区别**：cptx 是 11.0 新引擎的压缩包格式（原 cpt + 编译后关系缓存）。本技能包产出的是纯 XML 的经典 .cpt；遇到 cptx 先在设计器另存为明文 cpt 再处理。
- **模板依赖 FRDemo 连接**：所有模板示例的数据集默认指向内置演示连接 FRDemo。换到生产环境时，必须把 DatabaseName 改成实际数据连接名，并核对表名字段名。
- **生成后在设计器打开复核**：校验器只保证 XML 合法与结构完整，不替代引擎渲染。交付前提示用户用设计器打开预览一遍，重点看扩展方向、汇总值、填报字段映射。
- **cpt 文本风格**：UTF-8 无 BOM、无 DOCTYPE、所有标签顶格零缩进、LF 换行。不要用常规 XML 美化工具格式化后写回——FineReport 虽能读，但版本 diff 会失控。
- **不要编造节点名**：一切结构以 `references/cpt-structure.md` 收录的实测片段为准；demo 中未出现过的类型（如存储过程数据集）不要自行生成。
- **full="true" 命名样式会导致表头只居中一半**：full="true" 让帆软按样式库/主题整块覆盖 XML 属性；自定义样式一律匿名（不带 style_name/full/border_source）。
- **FineColor 的 hor/ver 必须写 -1/-1**：hor/ver 是主题配色盘行列索引，任一非负则忽略 color 字面值，预览变成主题灰。
- **必填校验是 EMSG + allowBlank 子节点，不是属性**：必须作为独立子节点写在 DateAttr/TextAttr 之前；写成 allowBlank="false" 属性不报错但完全不生效。
