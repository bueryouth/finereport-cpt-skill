# 相关项目消化：finereport-cpt（A）+ fineReport-builder（B）

> 目的：深读两个只读参考项目，把其中可移植的校验规则、XML 结构知识、生成/同步流程、JSON 规格提炼出来，供本技能包（`C:\Users\Administrator\skills\finereport-cpt-skill\`，现有 `references/cpt-structure.md` 基于 240 个 11.0 demo 实测）吸收。
> 采样：项目 A = `report-cpt-skill/finereport-cpt-main/`（SQL 驱动生成/同步/校验）；项目 B = `report-cpt-skill/fineReport-builder-main/`（基于真实模板的 ReAct 构建器）。
> 本文摘录忠实：节点名/属性/字符串逐字（可略缩中间）；与本技能包 demo 实测不一致处单列「冲突点」。两个项目原文件未做任何改动。

---

## 1. 项目 A 总览与 CLI（脚本怎么用）

四个脚本覆盖「定稿 SQL → 新建/改造 → 自检 → 交付」，每步产物由下一步验证：

```
定稿 SQL ─┬─ 新建报表 ──────► gen_cpt.py ─┐
          ├─ 只改 SQL ───────► sync_sql.py ─┼─► check_cpt.py ─► 交付
          └─ 改列宽/格式/面板 ► fix_cpt.py ─┘        ▲ 不过就回去改
```

| 脚本 | 一句话职责 | 关键 CLI |
|---|---|---|
| `gen_cpt.py` | 从 SQL 生成整份 .cpt，只让 SQL 决定表头与参数，其余按实测骨架填充 | `python gen_cpt.py 报表_SQL.sql -o 报表.cpt -c 连接名` |
| `sync_sql.py` | 只把新 SQL 写进已有 cpt 的 `<Query>`，并同步参数节点，其余字节不动 | `python sync_sql.py 报表.cpt 报表_SQL.sql` |
| `fix_cpt.py` | 就地改造已有 cpt 的列宽/数字格式/样式表/参数面板，四项独立可选 | `python fix_cpt.py 报表.cpt --width --format --unit 万元 --panel --style 设计器.cpt --dry-run` |
| `check_cpt.py` | 断言式交付自检，任何一条不过抛 AssertionError | `python check_cpt.py out/ -c 连接名 --sql-dir out --exclude 示例.cpt` |

`gen_cpt.py` 完整参数（`argparse`，节选自 `main()`）：

- 位置参数 `sql`；`-o/--out`；`-c/--connection`（必填）
- `--date-params` / `--text-params`（逗号分隔，强制控件类型）
- `--labels query_month=数据月份,order_no=订单编号`
- `--unit {原值,万元,亿元}`（决定金额列小数位）；`--no-format`
- `--optional`（非必填，默认全部必填）
- `--tree-param 参数名=树数据集[:源数据集][,key=id][,view=name][,multi=true][,leaf=true]`（可重复）
- `--combo-param 参数名=数据集[,key=列][,view=列][,bind-first=true]`（可重复）
- `--date-format`（默认 `yyyyMM`）；`--default`（默认 `=MONTHDELTA(TODAY(), -1)`）；`--date-max`（默认 `=TODAY()`，空串取消）；`--date-min`
- `--multi-header`；`--level-sep`（默认 `_`）；`--head-fill RRGGBB=A1,C1:F2`（可重复）
- `--template 设计器产物.cpt`（以它的 StyleList 为准）；`--self-test`

四个脚本都支持 `--self-test`，内部用临时文件验证「好文件通过、每种坏法都被抓住」。

---

## 2. 项目 A 设计原则（逐条）

1. **不要凭直觉手写 XML，用已验证脚本产出 + 断言自检。** `.cpt` 节点对应帆软内部 Java 对象图，结构写错不报 XML 语法错，而是反序列化抛 `ClassCastException`，设计器把模板静默降级成空白 WorkBook。
2. **SQL 是源头，cpt 跟着 SQL 走。** 列名（`AS 中文别名`）与参数占位符（`${param}`）决定表头与查询面板；先定稿 SQL 再生成，不要倒过来。每个输出列必须显式 `AS` 别名（帆软按列名绑定，无 AS 的表达式列名由数据库决定、不可靠）。
3. **改已有报表绝不重新生成。** 用户在设计器里调过的合并单元格/条件属性/图表/页面设置，重新生成会全丢；改 SQL 走 `sync_sql.py`（只换 `<Query>`+参数节点），改外观走 `fix_cpt.py`（只动指定那项）。
4. **设计器产物是格式的最终裁判。** 手写与设计器不一致的细节，用户下次保存就被重写掉；跟随方式是 `gen_cpt.py --template` / `fix_cpt.py --style`，且会把模板里的命名样式一并转匿名。
5. **样式一律匿名（不带 `style_name`/`full`/`border_source`）。** `full="true"` 会让帆软拿样式库/主题定义整块覆盖 XML 属性，表现为「一部分表头居中、另一部分没居中」；自编名字样式库里查不到，回落主题默认，居中底色字号全丢。
6. **颜色 `hor="-1" ver="-1"`。** `FineColor` 的 hor/ver 是主题配色盘行列索引，任一非负帆软按索引取主题色、忽略 color 字面值（文件里写着正确颜色，预览却是主题灰）。
7. **增删样式只追加在末尾，不改中间。** 单元格按下标 `s="n"` 引用样式，插在中间会让所有已有引用错位；新样式一律 append 到 `</StyleList>` 前。
8. **常量从 jar / 示例模板查证，不靠猜。** `unzip fine-core-*.jar` + `javap -p -constants` 查 `horizontal_alignment`/`textStyle` 等；grep 帆软安装目录 `reportlets/` 找现成节点。这是该 skill「最值钱」的习惯。

---

## 3. 项目 A 关键 XML 结构知识

### 3.1 根骨架（`build_cpt()` 原样骨架，WorkBook 用新版 11.5）

注意：项目 A 生成器与项目 B 真实模板都用 **`xmlVersion="20211223" releaseVersion="11.5.0"`**，不是本技能包 demo 采样的 `20170720/11.0.0`。尾部多出一组我们文档未列的节点：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<WorkBook xmlVersion="20211223" releaseVersion="11.5.0">
<TableDataMap>
<TableData name="ds_main" class="com.fr.data.impl.DBTableData">
<Desensitizations desensitizeOpen="false"/>
<Parameters> ... </Parameters>
<Attributes maxMemRowCount="-1"/>
<Connection class="com.fr.data.impl.NameDatabaseConnection">
<DatabaseName><![CDATA[MY_CONN]]></DatabaseName>
</Connection>
<Query><![CDATA[...SQL...]]></Query>
<PageQuery><![CDATA[]]></PageQuery>
</TableData>
...递归数据集...
</TableDataMap>
<Report class="com.fr.report.worksheet.WorkSheet" name="sheet1">
<ReportPageAttr><HR/><FR/><HC/><FC/><USE REPEAT="false" PAGE="false" WRITE="false"/></ReportPageAttr>
<ColumnPrivilegeControl/><RowPrivilegeControl/>
<RowHeight defaultValue="723900"><![CDATA[...]]></RowHeight>
<ColumnWidth defaultValue="2743200"><![CDATA[...]]></ColumnWidth>
<CellElementList> ... </CellElementList>
<ReportAttrSet><ReportSettings headerHeight="0" footerHeight="0">
<PaperSetting/><FollowingTheme background="true"/>
<Background name="ColorBackground"><color><FineColor color="-1" hor="-1" ver="-1"/></color></Background>
</ReportSettings></ReportAttrSet>
<PrivilegeControl/>
</Report>
<ReportParameterAttr> ... </ReportParameterAttr>
<StyleList> ... </StyleList>
<DesensitizationList/>
<DesignerVersion DesignerVersion="LAA"/>
<PreviewType PreviewType="0"/>
<StrongestControlAttr class="com.fr.widgettheme.control.attr.WidgetDisplayEnhanceMarkAttr">
<StrongestControlAttr widgetEnhance="false"/></StrongestControlAttr>
<StrategyConfigsAttr class="com.fr.esd.core.strategy.persistence.StrategyConfigsAttr">
<StrategyConfigs><StrategyConfig dsName="ds_main" enabled="false" useGlobal="true" .../></StrategyConfigs>
</StrategyConfigsAttr>
<ForkIdAttrMark class="com.fr.base.iofile.attr.ForkIdAttrMark">
<ForkIdAttrMark forkId="00000000-0000-0000-0000-000000000000"/></ForkIdAttrMark>
<TemplateIdAttMark class="com.fr.base.iofile.attr.TemplateIdAttrMark">
<TemplateIdAttMark TemplateId="00000000-..."/></TemplateIdAttMark>
</WorkBook>
```

新增/补充节点（相对本技能包 `cpt-structure.md`）：
- 每个 `TableData` 都带 `<Desensitizations desensitizeOpen="false"/>`（脱敏占位）。
- `ReportPageAttr` 内有 `<USE REPEAT="false" PAGE="false" WRITE="false"/>`。
- `ReportAttrSet/ReportSettings` 内有 `<FollowingTheme background="true"/>` + 白底 `<Background>`。
- WorkBook 尾部在 `StyleList` 之后有：`<DesensitizationList/>`、`<StrongestControlAttr>`、`<StrategyConfigsAttr><StrategyConfig .../></StrategyConfigsAttr>`、`<ForkIdAttrMark>`（除我们已有的 `TemplateIdAttMark` 外多了 ForkId）。

### 3.2 参数面板 BoundsWidget 结构（最致命坑，本技能包已部分覆盖）

`WParameterLayout` 继承 `WAbsoluteLayout`，会把每个 `<Widget>` 子节点强转成 `WAbsoluteLayout$BoundsWidget`；直接挂真实控件 → `ClassCastException` → 模板变空白。真实控件放 `<InnerWidget>`，位置写外层 `<BoundsAttr>`：

```xml
<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">
<InnerWidget class="com.fr.form.ui.DateEditor">
<WidgetName name="query_month"/>
<LabelName name="数据月份"/>
<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="0.0" description="">
<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>
<PrivilegeControl/>
</WidgetAttr>
<EMSG><![CDATA[数据月份不允许为空]]></EMSG>
<allowBlank><![CDATA[false]]></allowBlank>
<DateAttr format="yyyyMM" enddatefm="=TODAY()"/>
<widgetValue>
<O t="XMLable" class="com.fr.base.Formula"><Attributes><![CDATA[=MONTHDELTA(TODAY(), -1)]]></Attributes></O>
</widgetValue>
</InnerWidget>
<BoundsAttr x="110" y="12" width="140" height="21"/>
</Widget>
```

要点（本技能包文档需补）：
- **必填校验是独立子节点 `<EMSG>` + `<allowBlank>`，且排在 `<DateAttr>`/`<TextAttr>` 之前**；写成 `<DateAttr allowBlank="false"/>` 属性不报错但完全不生效（最难发现的错）。
- `<WidgetAttr>` 固定带 `<MobileBookMark .../>` + `<PrivilegeControl/>`。
- 查询按钮：`<InnerWidget class="com.fr.form.parameter.FormSubmitButton">`，`<Text><![CDATA[查询]]></Text><Hotkeys><![CDATA[enter]]></Hotkeys>`。
- 标签控件：`<InnerWidget class="com.fr.form.ui.Label">`，`<widgetValue><O>数据月份：</O></widgetValue>`，`<LabelAttr verticalcenter="true" textalign="2" autoline="false"/>`。

### 3.3 参数两处声明（本技能包 §4 已述，补充位置细节）

| 位置 | 写法 | 缺失后果 |
|---|---|---|
| `<TableDataMap>/<TableData>/<Parameters>` 内 | `<Parameter><Attributes name="x"/><O><![CDATA[]]></O></Parameter>` | SQL `${x}` 取不到值 |
| `<ReportParameterAttr>` 内、`</ParameterUI>` **之后** | 同样的 `<Parameter>` 节点，但**没有 `<Parameters>` 包装**，裸放 | 不弹参数面板 |

两处节点串完全一样，区别只在有无 `<Parameters>` 外壳。

### 3.4 日期控件 DateAttr（本技能包需补）

```xml
<DateAttr format="yyyyMM"/>                                   <!-- 无范围 -->
<DateAttr format="yyyyMM" start="2026-01-01" end="2026-12-31"/>          <!-- 字面量 -->
<DateAttr format="yyyyMM" startdatefm="=MONTHDELTA(TODAY(), -12)" enddatefm="=TODAY()"/>  <!-- 公式 -->
```

- 字面量上下限写 `start`/`end`，公式写 `startdatefm`/`enddatefm`；两者都设时**字面量优先**（取自 `DateEditor.writeXML`）。公式写进 `end` 不报错但界面限制不生效。
- **不写 `returnDate`（默认 false）时控件返回格式化字符串**，SQL 里 `'${query_month}'` 加引号当字符串用即可，无需改成日期类型。这与本技能包 §4.3「日期值是 epoch 毫秒」是两种序列化模式（epoch ms 见于 `widgetValue/O t="Date"`，returnDate=false 时回传字符串）。

### 3.5 树 / 下拉控件与递归数据集（本技能包 §4.3 有 TreeComboBoxEditor，缺下面细节）

字典机制（`kiName`=回传 SQL 的列，`viName`=显示列，指反了用户看到一串 id）：

```xml
<Dictionary class="com.fr.data.impl.TableDataDictionary">
<FormulaDictAttr kiName="id" viName="name"/>
<TableDataDictAttr><TableData class="com.fr.data.impl.NameTableData"><Name><![CDATA[组织树]]></Name></TableData></TableDataDictAttr>
</Dictionary>
```

递归数据集（把拍平 id/name/parent_id 拍成树，自己不写 SQL）：

```xml
<TableData name="组织树" class="com.fr.data.impl.RecursionTableData">
<Desensitizations desensitizeOpen="false"/>
<markFields><![CDATA[0]]></markFields>
<parentmarkFields><![CDATA[2]]></parentmarkFields>
<markFieldsName><![CDATA[id]]></markFieldsName>
<parentmarkFieldsName><![CDATA[parent_id]]></parentmarkFieldsName>
<originalTableDataName><![CDATA[组织层级表]]></originalTableDataName>
</TableData>
```

- 下标（`markFields`=列号）与列名（`markFieldsName`）两套必须成对指同一列；写不一致不报错但树建不出来。
- 树控件 `<TreeAttr async="false" mutiSelect="true" selectLeafOnly="false"/>` + `<ReturnTypeAttr delimiter="," startSymbol="" endSymbol="" returnString="true"/>`（多选回传逗号串，SQL 侧必须 `splitByString(',','${org_id}')` 拆数组）。
- 普通下拉 `<ComboBox>` 无 TreeAttr；默认值可绑数据集第一行：`<widgetValue><databinding><![CDATA[{Name:年月表,Key:ym}]]></databinding></widgetValue>`。

### 3.6 样式表按索引引用 + 数字格式 + 颜色（重点）

- 单元格 `<C ... s="n">` 的 `s` 是 `<StyleList>` 中 `<Style>` 的**0 基下标**，匿名样式也占下标；增删样式只追加末尾。
- **`<Format>` 必须是 `<Style>` 的第一个子节点（在 `<FRFont>` 之前）**，放后面帆软读不到：

```xml
<Style imageLayout="1">
<Format class="com.fr.base.CoreDecimalFormat"><![CDATA[#,##0.00]]></Format>
<FRFont name="WenQuanYi Micro Hei" style="0" size="72"/>
<Background name="NullBackground"/><Border/>
</Style>
```

- 金额格式随单位：原值 `#,##0.00`、万元 `#,##0`、亿元 `#,##0.00`；比率 `0.00%`。
- 颜色 `FineColor` 一律 `hor="-1" ver="-1"`；`RRGGBB` → 有符号 32 位 ARGB（`0xFF000000|RGB`，超 2^31 折成负），如 `#8CDDFA → -7545350`、`#FFFF00 → -256`、白 `-1`。
- **表头默认 `horizontal_alignment="0"`（居中）+ `FRFont style="1"`（加粗）**；不写 `vertical_alignment`（设计器不输出，写了保存就丢）。

### 3.7 数据行 DSColumn 的完整节点（本技能包 §5.3 较简，补充）

```xml
<C c="0" r="1" s="2">
<O t="DSColumn">
<Attributes dsName="ds_main" columnName="订单编号"/>
<Condition class="com.fr.data.condition.ListCondition"/>
<Complex/>
<RG class="com.fr.report.cell.cellattr.core.group.FunctionGrouper">
<Attr divideMode="1"/>
</RG>
<Result><![CDATA[$$$]]></Result>
<Parameters/>
<cellSortAttr><sortExpressions/></cellSortAttr>
</O>
<PrivilegeControl/>
<Expand dir="0"><cellSortAttr/></Expand>
</C>
```

即：数据格比本技能包文档多了**空的 `<Condition ListCondition/>`**、`<RG>` 内的 `<Attr divideMode="1"/>`、`<Result>$$$</Result>`、以及 `<cellSortAttr>`/`<sortExpressions/>`。表头格则是 `<Expand><cellSortAttr/></Expand>`。

### 3.8 多级表头与表头底色

- 列别名用 `_` 分级：`归属我方_本年回款` → 两级；`~` 是去重后缀（`指标~分类` 显示「指标」，后缀仅用于区分列、判类型保留）。
- 合并：横向要求「父级路径也相同」才并（`外部_账龄_1年内` 与 `内部_账龄_1年内` 不并）；层数不足的列末级向下延伸靠 `rs` 跨满。
- 底色规格 `RRGGBB=A1,C1:F2`，行列按表头矩阵自身从 1 数；底色样式从表头样式派生、只换 `<Background>`，追加末尾。

---

## 4. 项目 A 校验规则清单（check_cpt.py，逐条；★=可直接移植到 validate_cpt.py）

1. ★ **XML 必须可 `ET.fromstring`**——解析不过的文件设计器降级成空白模板。
2. ★ **数据连接**：必须有 `DatabaseName`；不得残留 `FRDemo` 开头的示例连接（报「驱动器未找到」）；传了 `--connection` 则必须等于它。
3. ★ **内嵌 SQL 与同名 `报表名_SQL.sql` 一致**（防改了 SQL 忘同步）。
4. ★ **逐数据集比参数**：每个 `TableData` 的 `<Parameters>` 名集合 == 它自己 SQL 里 `${...}` 集合（先剥 `/* */` 与 `--` 注释）；不许重复参数节点。**按数据集分别比，不合并所有数据集**（树形报表多数据集，合并会假报警）。
5. ★ **报表级参数**：在 `</ParameterUI>` 与 `</ReportParameterAttr>` 之间，不许重复；写了的必须在某个数据集 SQL 里真用到（否则面板多一个没用的控件）。缺失只 ⚠ 不失败。
6. ★ **控件嵌套**：有 SQL 参数就必须有 `WParameterLayout`；每个 `<Widget>` 的 class 必须是 `WAbsoluteLayout$BoundsWidget`，且带 `<InnerWidget>` 与 `<BoundsAttr>`。
7. ★ **控件名不重复**；必须有一个 `FormSubmitButton`（查询按钮）。
8. ★ **`allowBlank` 必须是独立子节点**：在 `DateAttr`/`TextAttr`/`NumberAttr`/`TreeAttr` 上写成属性即失败（只在没有独立节点时判，两者并存是设计器正常产物）。
9. ★ **字典校验**：ComboBox/ComboCheckBox/TreeEditor/TreeComboBoxEditor 必须有 `<Dictionary>`；非 CustomDictionary 的必须有 `kiName`/`viName`；树控件字典必须指向 RecursionTableData 名而非拍平源表名；指向模板外数据集名只 ⚠（可能是服务端公共数据集）。
10. ★ **递归数据集**：`markFields`/`parentmarkFields`/`markFieldsName`/`parentmarkFieldsName`/`originalTableDataName` 五节点齐全；`markFields`/`parentmarkFields` 是数字下标且不相等；源数据集不能是自己（防无限递归）。
11. ★ **样式下标越界**：每个单元格 `s` < StyleList 中 `<Style>` 个数（按出现次序数，匿名也算）。
12. ★ **`full="true"` 分两档**：自编名字（样式库里没有）必失败；内置名 `表头/默认` 在多级表头失败、单级表头只 ⚠。
13. ★ **`<Format>` 必须是 `<Style>` 第一个子节点**（在 FRFont 前）；不许有空 Format 节点。
14. ★ **不许出现 `textStyle`**（设计器保存不输出，写了靠不住）。
15. ★ **数据绑定必须集中一行**（普通报表）；但**行式折叠树**（含 `FR_GEN_0`）允许连续 N 行（按 A 列树格切块，每块层号 0..levels-1 连续）；**固定行报表**（数据格全是 SummaryGrouper + 字面量过滤）也允许连续 N 行，且逐行校验：行标签格不绑数据集、数字格必须 SummaryGrouper+SumFunction 且不带 `Expand dir=`、同一行只过滤一个编码、编码全表唯一。
16. ★ **表头行识别**：数据行以上不全算表头；大标题/单位行按两条判据（① 该行没盖满所有列；② 格子数 ≤2 且有格跨过半表）命中任一条即标题/说明行，不参与表头外观比对。
17. ★ **表头样式**：必须引用样式 0；样式 0 必须加粗（FRFont style∈{1,3}）且 `horizontal_alignment="0"`（居中）；表头可引用多个样式但外观须与样式 0 同套（只换背景色），不得带数字格式；数据行不得引用样式 0。
18. ★ **列宽放得下表头**：每个表头文字格按「中文 16px/字 + 20px 留白」算所需宽，跨列标题按合并总宽比；不足则报换行（`--no-width-check` 降级为 ⚠）。
19. ★ **SQL 常见问题**：`AS AS`、空 `divide(`、JOIN/WHERE 里裸写未加引号的 `${param}`（空值会拼出语法错；例外 `${ds}.表名` 标识符前缀）。
20. ⚠ 软提示（不失败）：未声明报表级参数、无控件的参数、字典指向模板外数据集、控件坐标重叠（多套参数模板 currentIndex 切换）。

---

## 5. 项目 A 生成器工作流（SQL → cpt 步骤）

1. **剥注释**（`/* */`、`--`）→ 从最后一个顶层 `SELECT` 解析 `AS 别名`（跳过 CTE/子查询的 FROM），顺序即列顺序；列别名不许重复。
2. **抽参数** `${xxx}`，按出现顺序去重。
3. **推断列类型**（表头关键词，比率优先）：
   - 比率（率/占比/比例/系数）→ `0.00%`；人数（人数/人次）→ `#,##0`；整数（个数/笔数/数量…）→ `#,##0`；文本（名称/编号/部门/日期…）→ 无格式；金额（兜底）→ 随 `--unit`。
   - 账龄分段列（`0_6个月` 等）故意判成金额而非整数（区间内是金额不是月数）。
4. **推断参数控件类型**：参数名含 month/date/日期/月份 → DateEditor，其余 TextEditor；`--tree-param`/`--combo-param` 覆盖。
5. **建样式表**：下标 0 表头（加粗居中蓝底）、下标 1 默认；数字格式样式追加末尾；表头底色样式追加末尾。`enforce_header_look()` 兜底给样式 0 补加粗居中。
6. **算列宽**：`max(类型基准宽, 表头文字所需宽, 下限70px)`；多级表头先按末级定宽、跨列标题差额均摊。
7. **建单元格**：表头行（r=0 或多级 r=0..depth-1，相邻同名合并 cs/rs，被覆盖格不写节点）+ 数据行（r=depth，DSColumn 纵向扩展 dir=0）。
8. **建参数面板**：每参数一个 Label + 一个输入控件 + 末尾查询按钮，全部包 BoundsWidget，按 x 排布不重叠。
9. **拼 WorkBook**（§3.1 骨架）→ `ET.fromstring` 生成即验证 → LF 写出。
10. **后处理**：`sync_sql.py` 只换 `<Query>` CDATA + 重写两处参数节点（幂等）；`fix_cpt.py` 按开关改列宽/格式/样式/面板。

---

## 6. 项目 B 总览与架构

项目 B 是一个 **ReAct Agent + 双记忆 + 基于真实模板** 的构建器：
- **不是从 SQL 裸生成**，而是把用户需求（自然语言）→ 解析成 JSON 配置 → 以真实 cpt 模板（`templates/`）为底，复制/清空节点再填字段。
- **ReAct 循环**：思考→选动作（查记忆/读模板/改 XML/校验）→观察，直到模板满足需求。
- **双记忆**：`memory/templates/` 存两类典型模板的「JSON 配置」（`management.json` 管理分析、`detail.json` 明细），Agent 复用其结构而不是从零搭。
- **模板修改机制**（`agent/core.py` 实际实现）：按目标节点**清空后重新生成**（`o.text=...` / 重建子节点），而非深拷贝改字段；支持动态增删列、位置重算。`parsers/cpt_parser.py` 把 cpt 解析成「单元格坐标+值+样式」供 Agent 对照。
- **Excel 转换**：`数据模型设计.md` 描述从 Excel 列 → `column_mapping` → 数据列。
- **生成器写法差异**（`parsers/cpt_generator.py`）：用 `minidom.toprettyxml` **带缩进美化输出**（与项目 A/本技能包「零缩进 LF」相反），写完用正则把 CDATA 贴回；它写 `PreviewType PreviewType="2"`、`ForkIdAttrMark`、`DesensitizationList`、`ReportWebAttr>Title`。

> 注：项目 B 的 XML 产物偏「能跑即可」，其 `toprettyxml` 美化、`PreviewType=2` 与本技能包 demo 实测（零缩进、PreviewType=0）不一致，吸收时以项目 A 的实测骨架为准。

---

## 7. 项目 B JSON 配置格式（完整字段 + 真实样例）

### 7.1 顶层

```json
{
  "title": "报表标题",
  "sheet_name": "sheet名",
  "data_sources": [ ... ],
  "filter_controls": [ ... ],
  "cells": [ ... ],
  "styles": [ ... ]
}
```

### 7.2 data_sources（数据源）

**database 型**：
```json
{"name":"sales_data","type":"database","database":"cfs-report",
 "sql":"SELECT region, amount FROM sales WHERE date >= '${startDate}'",
 "column_mapping":{"A":"region","B":"amount"}}
```
**class 型**（Java 类数据集，项目 B 真实模板大量使用）：
```json
{"name":"CreditContractDetailData","type":"class",
 "class_name":"com.yocyl.fr.engine.tableData.finance.CreditContractDetailData",
 "return_fields":[{"name":"contractNo","type":"string","description":"合同编号"}],
 "parameter_template":{"orgId":"","startDate":"2026-03-02","indexInfo":[],"dimensions":[]}}
```
入参模板语义：`""` → 从筛选组件取值；有值 → 写死默认；`[]` → 数组型从筛选组件取。对应 cpt：`ClassTableData` + `<ClassTableDataAttr className="..."/>` + `<Parameters>`。

### 7.3 filter_controls（筛选组件）

| 字段 | 说明 |
|---|---|
| `label` | Label 控件显示文本 |
| `code` | 参数名（传给数据集） |
| `type` | TextEditor / DateEditor / ComboBox / TreeComboBoxEditor / ComboCheckBox / NumberEditor |
| `default_value` | 默认值 |
| `options` | 仅 ComboBox：`{key:显示文本}` 静态选项 |

真实样例（management.json 节选）：
```json
{"label":"组织机构","code":"orgId","type":"TreeComboBoxEditor","default_value":""}
{"label":"区域","code":"region","type":"ComboBox","options":{"east":"华东","south":"华南"}}
```
布局：每行 5 对（Label 89px + 输入 135px，间距 4px），`Label_X=10+col*(89+4+135+4)`，`Y=10+row*(28+8)`。

### 7.4 cells（单元格）

静态文本：`{"column":0,"row":0,"value":"区域","style_index":0}`
数据列：`{"column":0,"row":1,"value_type":"DSColumn","data_source":"sales_data","column_name":"region","expand_dir":0,"style_index":2}`

### 7.5 styles（自定义样式）

```json
{"name":"金额样式","horizontal_alignment":"4","font":{"name":"SimSun","style":"0","size":"80","color":"-8163329"},
 "background":"-1","border":true,"format":"#,##0.00"}
```
字段：`horizontal_alignment`（**0=中,2=左,4=右**）、`font.style`（0常规/1粗/2斜）、`font.size`（80=10pt，即 size/8=pt）、`background`（null 透明 / -1 白 / -1447425 蓝）、`format`。

---

## 8. 项目 B 模板注解要点（CPT_TEMPLATE_ANNOTATION.md 结构知识）

以 172KB 明细模板 `FinanceCreditContractAnalysisDetail.cpt` 为准的结构事实：

- WorkBook 一级顺序：`TableDataMap → ReportWebAttr(Title) → Report → ReportParameterAttr → StyleList`。
- **ClassTableData 结构**（核心新增类型，本技能包 §3 未覆盖）：
```xml
<TableData name="CreditContractDetailData" class="com.fr.data.impl.ClassTableData">
<Desensitizations desensitizeOpen="false"/>
<Parameters><Parameter><Attributes name="orgId"/><O><![CDATA[]]></O></Parameter>...</Parameters>
<ClassTableDataAttr className="com.yocyl.fr.engine.tableData.finance.CreditContractDetailData"/>
</TableData>
```
- 表头格合并：`<C c="0" r="0" rs="6" s="0">`（rs 跨 6 行）；数据格可带 `<CellGUIAttr adjustmode="2" showAsDefault="true"/>` + `<CellPageAttr/>`。
- 静态下拉字典：`<Dictionary class="com.fr.data.impl.CustomDictionary"><CustomDictAttr><Dict key="ZHSX" value="综合授信"/>...</CustomDictAttr></Dictionary>`。
- 行高列宽换算：**1 pt = 12700 EMU**；表头行高 1368000（≈107.7pt）、数据行 723900（57pt）、默认列宽 2743200（216pt）、数据列宽 4608000。
- 金额样式带 `<Format class="com.fr.base.CoreDecimalFormat" roundingMode="6">`（多了 `roundingMode="6"` 属性）。
- 真实模板样式带 `style_name`（如 `表头左列`/`表头`/`金额`），但**自定义样式实为匿名**；只有内置「默认」样式带 `full="true" border_source="-1"`。

---

## 9. 项目 B 两个真实模板特征（脚本统计）

| 项 | FinanceCreditContractAnalysis.cpt（管理分析，148KB） | FinanceCreditContractAnalysisDetail.cpt（明细，172KB） |
|---|---|---|
| WorkBook 版本 | 20211223 / 11.5.0 | 20211223 / 11.5.0 |
| 数据集总数 | 20（7 DBTableData / 6 ClassTableData / 2 RecursionTableData / 5 NameTableData） | 22（7 DB / 6 Class / 2 Recursion / 7 NameTableData） |
| 参数面板控件总数 | 35（15 Label / 5 ComboBox / 4 TextEditor / 2 TreeComboBoxEditor / 4 ComboCheckBox / 4 DateEditor / 2 FormSubmitButton） | 43（19 Label / 7 ComboBox / 5 TextEditor / 2 Tree / 4 ComboCheckBox / 4 DateEditor / 2 Submit） |
| 样式数 | 5（3 个 `ha="2"` 左对齐表头/数据，1 个 `ha="4"` 金额右对齐，1 个默认） | 6（3 左 / 1 右 / 1 `ha="0"` 居中 / 1 默认） |
| 单元格数 / 最大列 / 最大行 | 149 格，max c=9，max r=19 | 103 格，max c=37，max r=2 |
| DSColumn 绑定格 | 64 | 37 |
| ReportWebAttr 子节点 | Title / ServerPrinter / WebPageContent / WebViewContent | 同左 |

含义：真实生产模板**大量使用 ClassTableData + NameTableData 引用 + 递归树**，列数可达 37 列；管理分析表是多层交叉表（max r=19），明细表是宽表（max c=37、数据行 r=2）。

---

## 10. 与现有技能包的差异分析

### 10.1 已覆盖（本技能包 cpt-structure.md 已写对，无需改）
- WorkBook 根、TableDataMap/DBTableData/Query/PageQuery 骨架；`s` 是样式索引；BundsWidget 包控件；FormSubmitButton；ReportParameterAttr 挂 WorkBook 下；DSColumn + FunctionGrouper/SummaryGrouper；HR/FR/HC/FC；ReportWriteAttr 智能提交；图表 O t="CC"；无 BOM/无 DOCTYPE/LF。

### 10.2 新增价值（本技能包缺失或不完整，应补）
1. **必填校验 `<EMSG>` + `<allowBlank>` 独立子节点且排在 DateAttr 前**——本技能包只提 allowBlank，未提 EMSG 与顺序。
2. **DateAttr 字面量 `start/end` vs 公式 `startdatefm/enddatefm`**、`returnDate` 默认 false 返回字符串。
3. **`full="true"` 样式陷阱**（居中只一半）与 **`hor/ver` 主题色陷阱**（颜色被主题顶掉）——本技能包完全未提。
4. **`<Format>` 必须是 `<Style>` 第一个子节点**；textStyle 设计器不输出。
5. **RecursionTableData 五节点**（markFields/parentmarkFields/markFieldsName/parentmarkFieldsName/originalTableDataName）+ 树控件 ReturnTypeAttr delimiter。
6. **ComboBox databinding `{Name:ds,Key:col}`** 取首行默认值。
7. **数据行 DSColumn 的完整节点**（空 Condition、RG/Attr divideMode、Result $$$、cellSortAttr/sortExpressions）。
8. **ClassTableData**（Java 类数据集）与 **NameTableData** 引用——本技能包 §3.4 只说 NameTableData「图表/字典引用」，未说 ClassTableData。
9. **WorkBook 新版尾部节点**（DesensitizationList / StrongestControlAttr / StrategyConfigsAttr / ForkIdAttrMark）、ReportPageAttr 的 `<USE>`、每个 TableData 的 `<Desensitizations>`。
10. **多级表头 `_` 分级 + `~` 去重后缀 + 合并规则**、表头底色 `RRGGBB=区域` 规格。
11. **一整套断言式校验规则**（§4 的 20 条），可直接移植成 `validate_cpt.py`。
12. **修复器思路**（fix_cpt.py：只改指定项、保留用户设计器调整、幂等）与 **sync_sql.py**（只换 Query+参数）。
13. 项目 B 的 **JSON 中间层配置**（filter_controls/data_sources/cells/styles）可作为「需求→cpt」的结构化桥梁。
14. **ColWidthHighlightAction 动态列**（项目 B：`HighlightList>Highlight` 用列宽=0 隐藏列，公式 `INARRAY('表头',$cols)=0`）——本技能包未提。

### 10.3 冲突点（与本技能包 demo 实测不一致，需标注/复核）

**冲突 1（重要，疑似本技能包写错）：`horizontal_alignment` 取值。**
- 本技能包 `cpt-structure.md` §6.1：「`horizontal_alignment`：0=左、2=居中、4=右」。
- 项目 A（自称反编译 `fine-cbb-11.0.jar` 的 `Constants.class`）+ 项目 B `数据模型设计.md`/`CPT_TEMPLATE_ANNOTATION.md`（0=中,2=左,4=右）+ 本次真实模板脚本统计（表头/数据样式均 `ha="2"`、金额样式 `ha="4"`，management.json 标注 2=left、4=right）——**三方一致：0=居中(CENTER)、2=左(LEFT)、4=右(RIGHT)**。
- 结论：本技能包「0=左、2=居中」大概率写反，**建议按三方一致口径改为 0=中/2=左/4=右**。

**冲突 2：列宽/行高单位换算。**
- 本技能包：EMU，`914400=1 英寸`、`2743200=3 英寸`。
- 项目 B：`1 pt = 12700 EMU`（72pt=914400 EMU，与本包一致）；默认列宽 2743200=216pt。
- 项目 A：实测 `34290 单位 = 1px`（2743200/34290=80px，默认行高 723900/34290≈21px）。
- 说明：EMU/pt 换算三方自洽；项目 A 的「34290=px」是设计器网格像素标定（默认列≈80 网格 px、默认行≈21px），与 pt 换算并存不矛盾，但**「2743200=3 英寸」与「=80px」并存会让人困惑**，建议文档同时给两种标定。

**冲突 3：WorkBook 版本号。**
- 本技能包 demo 采样 `xmlVersion="20170720" releaseVersion="11.0.0"`；两个项目生成/采样均为 `20211223/11.5.0`。非对错，是版本新旧——新模板应写 11.5。

**冲突 4：日期控件值。**
- 本技能包 §4.3：`<widgetValue><O t="Date"><![CDATA[1264953600000]]></O>`（epoch 毫秒）。
- 项目 A：默认 `returnDate=false` 时回传格式化字符串，默认值用公式 `=MONTHDELTA(TODAY(),-1)`。
- 两者是不同序列化模式（控件存值 vs 回传值），不算硬冲突，但文档应说明「存值可 epoch ms，回传默认字符串」。

**冲突 5：样式是否带 style_name。**
- 本技能包/项目 A：自定义样式一律匿名。
- 项目 B 真实模板：自定义样式带 `style_name`（`表头左列` 等），仅内置「默认」带 `full="true"`。
- 结论：项目 A 的「不要自己加 full=true」仍成立；真实模板的 style_name 是设计器产物、不带 full，可接受。本技能包应区分「内置默认样式带 full=true」与「自派生样式必须匿名」。

---

## 11. 可直接吸收的改进建议（按优先级）

**P0（正确性硬伤，优先改）**
1. **修正 `horizontal_alignment` 映射为 0=居中/2=左/4=右**（三方证据，本包现写反）。
2. 给 `validate_cpt.py` 移植 §4 的 ★ 断言：XML 可解析、连接非 FRDemo、逐数据集参数集合一致、控件必包 BoundsWidget、allowBlank 是独立节点、样式下标不越界、`<Format>` 在 Style 首位、无 textStyle、表头样式加粗居中（ha=0）。
3. 文档补 **`<EMSG>`+`<allowBlank>` 独立子节点且在 DateAttr 前** 的正确写法片段。
4. 文档补 **`full="true"` 陷阱** 与 **`hor/ver=-1` 主题色陷阱** 两节。

**P1（生成能力补全）**
5. 补 DateAttr `start/end` vs `startdatefm/enddatefm`、returnDate 默认 false 行为。
6. 补 RecursionTableData 五节点 + TreeComboBoxEditor ReturnTypeAttr + 字典 kiName/viName 指认规则。
7. 补 ComboBox databinding `{Name:ds,Key:col}`。
8. 数据行 DSColumn 骨架补全（空 Condition、RG/Attr divideMode、Result $$$、cellSortAttr）。
9. WorkBook 新模板尾部节点补 DesensitizationList/StrongestControlAttr/StrategyConfigsAttr/ForkIdAttrMark，版本号写 20211223/11.5.0。

**P2（高级能力与文档）**
10. 移植多级表头 `_`/`~` 与表头底色规格、顶部标题行/单位行的连带改动规则。
11. 补 ClassTableData（Java 类数据集）与 NameTableData 引用知识。
12. 引入 JSON 中间层配置（filter_controls/data_sources/cells/styles）作为「自然语言需求→cpt」的结构化桥梁。
13. 补 ColWidthHighlightAction 动态列隐藏技术。
14. 补 sync_sql（只换 Query+参数、幂等）与 fix（只改指定项、保留用户调整）的改造工作流文档。
15. 单位换算同时给 EMU/pt 与项目 A 的 34290/px 网格标定，消除「3 英寸 vs 80px」困惑。
