# 关联项目参考

> 适用场景：需要更工程化地批量生成/同步/校验 cpt、想参考 JSON 中间层规格、或遇到本技能包生成器未覆盖的坑（full=true、hor/ver、allowBlank 写法）时，查阅两个外部成熟项目的做法。
> 一句话摘要：本文消化两个只读参考项目（finereport-cpt SQL 驱动生成器、fineReport-builder 真实模板构建器），提炼可复用的 20 条校验规则与关键写法，并记录与本技能包的冲突处理结论。
>
> 项目根目录：`E:\mis-workspace\08-fanruan\report-cpt-skill\`，均只读参考，不随本技能包分发。

---

## 1. 项目 A：finereport-cpt（SQL 驱动生成 / 同步 / 校验）

- **定位**：`report-cpt-skill\finereport-cpt-skill-main\`，四个 Python 脚本串起"定稿 SQL → 新建/改造 → 自检 → 交付"，只让 SQL 决定表头与参数，其余按实测骨架填充。
- **CLI**：
  - 新建：`python gen_cpt.py 报表_SQL.sql -o 报表.cpt -c 连接名`
  - 只改 SQL（不动外观）：`python sync_sql.py 报表.cpt 报表_SQL.sql`
  - 就地改列宽/格式/面板/样式：`python fix_cpt.py 报表.cpt --width --format --panel --style 设计器.cpt --dry-run`
  - 断言式交付自检：`python check_cpt.py out/ -c 连接名 --sql-dir out`
- **核心设计原则**：
  1. 不凭直觉手写 XML，用脚本产出 + 断言自检（结构写错不报 XML 错，而是反序列化 ClassCastException、设计器静默降级成空白 WorkBook）。
  2. SQL 是源头：每个输出列必须显式 `AS 中文别名`，参数占位符 `${param}` 决定查询面板。
  3. 改已有报表绝不重新生成：改 SQL 走 sync_sql（只换 Query+参数），改外观走 fix（只动指定项），保留用户在设计器里调过的合并/条件属性/图表。
  4. 设计器产物是格式最终裁判：手写细节与设计器不一致，用户下次保存就被重写掉。

## 2. 项目 B：fineReport-builder（Agent + 真实模板构建器）

- **定位**：`report-cpt-skill\fineReport-builder-main\`，ReAct Agent + 双记忆 + 基于真实模板：自然语言需求 → JSON 配置 → 以真实 cpt 模板为底复制/清空节点再填字段，不从 SQL 裸生成。
- **JSON 中间层配置概要**（顶层五段）：
  - `data_sources`：database 型（name/database/sql/column_mapping）或 class 型（class_name 指向 Java 类，即 cpt 的 ClassTableData + ClassTableDataAttr，return_fields + parameter_template；入参模板 `""`=从筛选取值、有值=写死、`[]`=数组型）。
  - `filter_controls`：label/code/type（TextEditor/DateEditor/ComboBox/TreeComboBoxEditor/ComboCheckBox/NumberEditor）/default_value/options。
  - `cells`：静态文本（column/row/value/style_index）或数据列（value_type=DSColumn/data_source/column_name/expand_dir）。
  - `styles`：horizontal_alignment（**0=中,2=左,4=右**）/font.name.style.size.color/background/border/format。
  - `title` / `sheet_name`。
- **真实模板特征**：148KB 管理分析表（20 数据集、149 格、max r=19）与 172KB 明细表（22 数据集、max c=37）；大量使用 ClassTableData + NameTableData 引用 + RecursionTableData 递归树；样式统计为表头/数据 ha="2" 左、金额 ha="4" 右。

## 3. 可直接复用的知识

### 3.1 校验规则清单（20 条，源自项目 A check_cpt.py）

1. XML 必须可解析——解析不过的文件设计器降级成空白模板。
2. 必须有 DatabaseName；不得残留示例连接；指定连接名必须一致。
3. 内嵌 SQL 与同名 SQL 文件一致（防改了 SQL 忘同步）。
4. 逐数据集比对：每个 TableData 的 Parameters 名集合 == 其 SQL 里 `${...}` 集合（剥注释后），按数据集分别比、不合并。
5. 报表级参数（ParameterUI 之后裸 Parameter）不重复；写了的必须在某个数据集 SQL 里真用到。
6. 有 SQL 参数就必须有 WParameterLayout；每个 Widget 必须是 BoundsWidget 且带 InnerWidget + BoundsAttr。
7. 控件名不重复；必须有一个 FormSubmitButton 查询按钮。
8. allowBlank 必须是独立子节点：写在 DateAttr/TextAttr 上当属性即失败。
9. 字典校验：ComboBox/Tree 类控件必须有 Dictionary；非 CustomDictionary 必须有 kiName/viName；树字典指向递归数据集名。
10. 递归数据集五节点齐全；markFields/parentmarkFields 是数字下标且不相等；不能自引用。
11. 样式下标不越界：每格 s < StyleList 的 Style 个数（按出现次序数，匿名也算）。
12. full="true" 分两档：自编名字必失败；内置名表头/默认在多级表头失败。
13. Format 必须是 Style 第一个子节点；不许空 Format。
14. 不许出现 textStyle（设计器不输出，写了靠不住）。
15. 数据绑定集中一行（行式折叠树/固定行报表例外，按其规则逐行校验）。
16. 表头行识别：大标题/单位行按"没盖满所有列"或"格数≤2 且有格跨过半表"判出，不参与表头外观比对。
17. 表头样式：必须引用样式 0；样式 0 必须加粗且 ha="0"（居中）；数据行不得引用样式 0。
18. 列宽放得下表头（中文 16px/字+20px 留白；--no-width-check 可降级软提示）。
19. SQL 常见问题：AS AS、空 divide(、JOIN/WHERE 里裸写未加引号的 ${param}。
20. 软提示（不失败）：未声明报表级参数、无控件的参数、字典指向模板外数据集、控件坐标重叠。

### 3.2 关键写法坑（本技能包已吸收进 cpt-structure.md）

- **BoundsWidget 必须包裹控件**：WParameterLayout 会把每个 Widget 子节点强转成 BoundsWidget，直接挂真实控件会 ClassCastException、模板变空白；真实控件放 InnerWidget，位置写外层 BoundsAttr。
- **样式表按索引引用、只追加末尾**：s 是 0 基下标，插中间会让已有引用错位。
- **Format 必须是 Style 第一个子节点**（FRFont 之前），否则读不到数字格式。
- **full="true" 命名样式导致表头居中问题**：full="true" 让帆软按样式库/主题整块覆盖 XML 属性，自编名字样式库里查不到则回落主题默认，表现为"一部分表头居中、另一部分没居中"。自定义样式一律匿名。
- **FineColor hor/ver 必须 -1/-1**：hor/ver 是主题配色盘行列索引，任一非负则忽略 color 字面值、预览成主题灰。
- **必填校验用 EMSG + allowBlank 子节点（非属性）且排在 DateAttr 前**：写成 DateAttr allowBlank="false" 属性不报错但完全不生效。

## 4. 与本技能包的协作方式

- **日常生成/小改**：用本技能包——复制 templates 模板改、或写 JSON 规格走 generate_cpt.py，再用 validate_cpt.py 校验。
- **批量 SQL 驱动出表**（一批同构报表、表头列名随 SQL 走）：参考项目 A 的 gen_cpt.py/sync_sql.py/check_cpt.py 思路，其 20 条校验规则已移植为 validate_cpt.py 的断言。
- **复杂布局/真实模板改造**（在已有设计器模板上改）：参考项目 B 的"清空目标节点再重填"与 JSON 中间层思路；本技能包不直接复制其美化缩进输出，仍保持零缩进 LF。
- **边界**：两个项目原文件只读；本技能包只吸收其结构知识与校验规则，不搬运其代码。

## 5. 冲突点处理记录

以 demo 实测为最高权威，三方不一致时的取舍：

| 冲突点 | 结论 |
|---|---|
| horizontal_alignment 取值 | 项目三方（反编译常量+真实模板统计）坐实 0=居中/2=左/4=右，修正了本包原误写；demo 表头 ha="0" 加粗惯例与此一致。 |
| 单位标定 | EMU/pt 换算三方自洽（1pt=12700 EMU）；补充项目 A 的 34290 EMU≈1 网格 px，消除"3 英寸 vs 80px"困惑。 |
| 版本号 | demo 采样 20170720/11.0.0，两项目用 20211223/11.5.0；非对错，新模板建议 11.5。 |
| 日期值序列化 | demo 存值是 epoch ms；项目 A 指出 returnDate=false 时回传格式化字符串。两种模式并存，已在文档说明。 |
| 样式命名 | 项目 A：自定义一律匿名；项目 B 真实模板带 style_name 但不带 full。结论：内置默认样式可带 full=true，自派生样式匿名。 |
| 输出缩进 | 项目 B 用 toprettyxml 美化；demo 实测零缩进 LF。以 demo 为准。 |

---

*本文基于 related-projects-digest.md（34.6KB 深读）提炼；原项目路径见文首，未做任何改动。*
