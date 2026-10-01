# FineReport 11 · CPT 生成器参考手册（generator-guide）

本手册说明如何用 `scripts/generate_cpt.py` 把一份 JSON 规格（spec）转换成
FineReport 11.0 的明文 `.cpt` 模板，并用 `scripts/validate_cpt.py` 校验。

> 结构权威：所有输出严格对齐 `demo-structure.md` 实测约定——
> 根节点 `<WorkBook>`、UTF-8 无 BOM、LF 换行、标签顶格零缩进、无 DOCTYPE、
> 用户文本/SQL/公式/JS 一律 CDATA、class 为 Java 全限定名、节点顺序敏感。

---

## 1. 快速上手

```bash
# 生成（缺省输出名 = spec.meta.name，落到 spec 同目录）
python scripts/generate_cpt.py assets/examples/spec_01_基础查询.json

# 指定输出路径
python scripts/generate_cpt.py my_spec.json out/my_report.cpt

# 校验单个文件 / 整个目录（-r 递归）
python scripts/validate_cpt.py assets/examples -r
```

标准配合流程：**写 spec → generate → validate → 通过后丢进 FineReport 设计器**。
validate 全部通过（exit 0）才说明模板结构合法。

---

## 2. JSON 规格顶层字段一览

| 字段 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `meta` | object | 否 | `{}` | `name`(输出文件名) / `title` / `description` |
| `workbook` | object | 否 | 见下 | xmlVersion / releaseVersion / designerVersion / previewType |
| `datasets` | array | 否 | `[]` | 数据集（sql / builtin / server） |
| `parameters` | array | 否 | `[]` | 报表参数 + 可选参数面板控件 |
| `styles` | array | 否 | `[]` | 命名样式（按下标索引，单元格 `style` 引用 name） |
| `cells` | array | 否 | `[]` | 单元格（坐标 + 值/绑定/控件/超链接/图表） |
| `events` | object | 否 | `{}` | 报表级 JS：`afterload` / `beforeload` |
| `toolbar` | object | 否 | `{}` | 内置工具栏按钮 |
| `buttons` | array | 否 | `[]` | 自定义 JS 工具栏按钮 |
| `fill` | object | 否 | `{enabled:false}` | 填报启用 + 智能提交入库 |
| `script` | — | 否 | — | 见 §10（预留，走 rawXml） |
| `java` | — | 否 | — | 见 §10（自定义函数，公式里直接引用） |
| `rawXml` | object | 否 | `{}` | 高级 XML 透传逃生舱 |

### 2.1 `workbook`

```json
"workbook": { "xmlVersion": "20170720", "releaseVersion": "11.0.0",
              "designerVersion": "LAA", "previewType": "0" }
```

- `previewType`：`0`=普通预览（默认），`1`=填报预览。开启 `fill.enabled` 时自动取 `1`。

---

## 3. 数据集 `datasets`

### 3.1 SQL 数据集（最常用）
```json
{ "name": "ds1", "type": "sql", "connection": "FRDemo",
  "sql": "SELECT * FROM 销量 WHERE 地区='${地区}'",
  "params": [ { "name": "地区", "defaultValue": "华东" } ] }
```
- SQL 里用 `${参数名}` 引用参数；`${if(...)}` 可动态拼 SQL。
- 连接名 = 平台数据连接名（CDATA）。

### 3.2 内嵌数据集 builtin
```json
{ "name": "ds2", "type": "builtin", "columns": ["月份","销量"],
  "columnTypes": ["java.lang.String","java.math.BigDecimal"] }
```
> 注意：内嵌数据集的 `RowData` 是 FineReport 专有压缩二进制，手工无法构造真实行。
> 生成器只产出合法空壳，**真实行数据请在设计器里打开后补录**。

### 3.3 服务器数据集 server
```json
{ "name": "ds3", "type": "server", "ref": "已注册的服务器数据集名" }
```

---

## 4. 报表参数 `parameters`

```json
{ "name": "地区", "defaultValue": "华东", "defaultType": "text",
  "widget": { "type": "combo", "label": "地区:", "options": ["华东","华北"] } }
```

| 子字段 | 说明 |
|---|---|
| `defaultType` | `text`(默认)/ `int`(整数) / `formula`(公式默认值，如 `=NOW()`) |
| `widget.type` | 给了它才会在参数面板自动摆控件：`combo` `radio` `text` `date` `number` `check` … |
| `widget.options` | 下拉框/单选组选项，字符串数组或 `{key,value}` 数组 |

带 `widget` 的参数会自动进入 `ParameterUI`（WParameterLayout 绝对布局），
末尾自动追加“查询”按钮（FormSubmitButton，回车触发）。

---

## 5. 命名样式 `styles`

按数组顺序生成 `<Style>`，下标即单元格 `s` 引用。

```json
{ "name": "header", "font": "微软雅黑", "fontStyle": 1, "size": 72,
  "halign": 2, "border": true, "bg": "-16764052",
  "format": "0.00%", "formatClass": "com.fr.base.CoreDecimalFormat" }
```

| 子字段 | 说明 |
|---|---|
| `fontStyle` | `0` 常规 / `1` 加粗 |
| `size` | 半磅（`72`=9pt，`120`=15pt） |
| `halign` | `0` 左 / `2` 居中 / `4` 右 |
| `bg` | 背景色 int 编码（白 `-1`、黑 `-16777216`）；不给=透明 |
| `foreground` | 字体颜色 int 编码 |
| `border` | `true` 四边细边框 |
| `format` | 数字/日期格式串；`formatClass` 默认 `CoreDecimalFormat`，日期用 `SimpleDateFormatThreadSafe` |

---

## 6. 单元格 `cells`（核心）

坐标 `c`(列) / `r`(行) **均从 0 开始**；公式里仍用 A1 风格 1 基引用（如 `B3`）。

一个 cell 三选一给值（`text` / `formula` / `ds`），或用 `widget` / `chart` / `rawC`。

```json
{ "c": 0, "r": 0, "merge": {"cs":3}, "text": "标题", "style": "title" }
{ "c": 0, "r": 1, "formula": "=SUM(B3)", "style": "total" }
{ "c": 0, "r": 2, "ds": {"dsName":"ds1","column":"地区"}, "dir": 0, "style":"data" }
{ "c": 1, "r": 2, "ds": {"dsName":"ds1","column":"销量","summary":"sum"}, "dir": 0 }
```

| 子字段 | 说明 |
|---|---|
| `merge.cs` / `merge.rs` | 跨列 / 跨行合并 |
| `style` | 引用 styles 里的 name（下标） |
| `text` | 静态文本（CDATA） |
| `formula` | 公式（`=` 开头，CDATA） |
| `ds.dsName` / `ds.column` | 绑定数据集列 |
| `ds.summary` | `sum`/`avg`/`count`/`max`/`min`（=汇总分组 SummaryGrouper）；不给=普通分组 |
| `dir` | `0` 纵向向下扩展 / `1` 横向向右扩展 / 不给=不扩展 |
| `leftParent` / `upParent` | 左/上父格（A1 引用，如 `"C5"`） |
| `widget` | 单元格控件，见 §6.1 |
| `hyperlink` | 超链接，见 §6.2 |
| `chart` | 图表，见 §8 |
| `rawC` | 整段 `<C>...</C>` 原样插入（逃生舱） |

### 6.1 单元格控件 `widget`
```json
"widget": { "type": "text", "name": "inp1",
            "defaultValue": "", "listeners": [ {"event":"afteredit","js":"..."} ] }
```
`type` 短名 → class：`text` `number` `checkbox` `date` `combo` `radio` `button` `label` …

### 6.2 超链接 `hyperlink`
```json
"hyperlink": { "type": "report", "name": "订单明细",
  "reportlet": "/订单明细表.cpt", "params": [ {"name":"订单号","formula":"=$$$"} ] }
```
网页链接：`"type":"web", "url":"http://..."`。

---

## 7. 工具栏 / 自定义按钮 / 事件

```json
"toolbar": { "buttons": ["submit","verify","append","delete"] },
"buttons": [ { "name":"btn_help","text":"说明","js":"FR.Msg.toast('hi')" } ],
"events": { "afterload": "console.log('template loaded');" }
```
内置按钮短名：`submit` `verify` `append` `delete`。

---

## 8. 图表 `charts`（用 cell.chart）

```json
{ "c":0, "r":0, "merge":{"cs":7,"rs":16},
  "chart": { "type":"pie", "title":"地区占比", "dsName":"ds1",
             "category":"货主地区", "series":"货主地区", "value":"应付金额", "agg":"sum" } }
```
- `type`：`pie`(饼/环/玫瑰) `bar`(柱) `line`(折线) `area`(面积)。
- 映射到 VanChart Plot：`PiePlot4VanChart` / `VanChartColumnPlot` / `VanChartLinePlot`。

---

## 9. 填报入库 `fill`

```json
"fill": {
  "enabled": true, "name": "内置SQL1",
  "connection": "FRDemo", "table": "月销量录入", "schema": "",
  "columns": [
    { "name":"月份",   "isKey": true,  "source": {"kind":"cell","c":0,"r":2} },
    { "name":"产品名称","isKey": true, "source": {"kind":"cell","c":1,"r":2} },
    { "name":"销量",   "isKey": false, "source": {"kind":"cell","c":2,"r":2} }
  ],
  "conditionFormula": "len(C3)!=0"
}
```
- `source.kind`：`cell`(单元格，给 c/r) / `formula`(给 value 公式) / `int`(整数) / `text`(常量)。
- `isKey:true` = 主键列（智能提交据此 INSERT/UPDATE）。
- 自定义 Java 类提交：`"submitter":"wclass", "customClass":"com.xxx.YourSubmiter", "properties":[{"name":"x","c":..,"r":..}]`。

---

## 10. script / java / rawXml

- **java 自定义函数**：在公式里直接写 `=MYFUNC(x)` 即可；该函数需在设计器/服务器注册，
  生成器不负责注册，仅做公式文本透传。
- **script（数据集脚本/公式变量）**：生成器不臆造未知节点，请用 `rawXml` 注入。

### rawXml 透传（复杂能力逃生舱）
```json
"rawXml": {
  "workbookPrefix": "<自定义WorkBook开头节点/>",
  "reportSuffix":   "<插到 </Report> 前的任意XML/>",
  "workbookSuffix": "<插到 </WorkBook> 前的任意XML/>"
}
```
凡生成器未覆盖但你确知写法的能力，一律用 rawXml 原样插入，保证不被破坏。

---

## 11. 三个完整示例

样例文件位于 `assets/examples/`：

| 文件 | 展示能力 |
|---|---|
| `spec_01_基础查询.json` | SQL 数据集 + 参数 + 汇总公式 + 命名样式 + 合并标题 |
| `spec_02_参数联动.json` | 多参数 + 参数面板 ComboBox/RadioGroup + 查询按钮 |
| `spec_03_填报入库.json` | 填报预览 + 可录入控件 + BuiltInSQLSubmiter 智能提交 + 工具栏/自定义按钮 |
| `spec_04_图表.json` | VanChart 饼图（O t=CC） |

对应输出 `out_0X_*.cpt` 已生成并通过校验，可直接对照学习。

---

## 12. validate_cpt.py 校验口径

对每个 `.cpt` 做两级判定：**错误（errors，导致失败、非 0 退出码）** 与
**提示（warnings，打印但不影响通过）**。

**文件级**：①无 BOM + UTF-8 声明；②XML 良构（报错带行号）。

**结构错误（硬失败）**：
- 根 `<WorkBook>` 且含 `xmlVersion/releaseVersion`；
- 顶层已知节点顺序（TableDataMap→Report→ReportParameterAttr→StyleList→AttrMark）；
- TableData class 白名单（DBTableData/Embedded/Name/Class/Recursion）；
- `<O>` 的 `t` 白名单；控件/图表 class 前缀合法；
- 尾部 AttrMark 三件套（DesignerVersion/PreviewType/TemplateIdAttMark 含 UUID）；
- **样式索引越界**：单元格 `s` 必须落在 StyleList 的 `<Style>` 下标范围内；
- **`<Format>` 必须是 `<Style>` 第一个子节点**，且不得为空；
- **禁用属性**：不允许出现 `textStyle`（设计器不输出）；
- **allowBlank 必须是独立子节点**：写在 DateAttr/TextAttr/NumberAttr/TreeAttr 上即失败；
- **控件嵌套**：参数面板里的真实控件（com.fr.form.ui.*）必须包在
  `WAbsoluteLayout$BoundsWidget` 内，且 BoundsWidget 带 `InnerWidget`+`BoundsAttr`；
- DBTableData 必须有 `DatabaseName`；同一数据集内参数节点不得重名。

**提示（软，不失败）**：数据集参数未在报表级声明、SQL `${}` 引用未在数据集 Parameters
声明、报表级参数未被任何 SQL 使用、缺查询按钮。这些多为跨数据集/内部参数的正常情况，
按项目 A 口径“缺失只提醒不失败”。

它同样可用来校验模板制作方在 `assets/templates/` 下手工产出的模板：
```bash
python scripts/validate_cpt.py assets/templates -r
```
任一文件失败 → 汇总失败数并以非 0 退出码结束。

---

## 13. 生成器的合规保证（输出天然通过校验）

为保证 `generate_cpt.py` 产物天然合规，它做了以下自动处理：

1. **参数自动双注册**：你在 `parameters` 里声明的报表级参数，若被某个 SQL 用 `${名}`
   引用，会自动补进该数据集的 `<Parameters>`（默认值取自报表参数），无需手写 dataset.params。
2. **控件自动包 BoundsWidget**：带 `widget` 的参数控件，生成器自动用
   `WAbsoluteLayout$BoundsWidget` 包裹，真实控件放在 `<InnerWidget>`，位置写 `<BoundsAttr>`，
   末尾自动追加 FormSubmitButton 查询按钮。
3. **样式表保底**：即使 `styles` 为空，也会输出一个默认 `<Style>`，保证单元格 `s="0"`
   不会越界。
4. **Format 顺序**：数字/日期格式 `<Format>` 总是生成在 `<FRFont>` 之前。

> 关于 `style_name`：cpt 单元格是按**数字下标 s** 引用样式，不按名字引用；`style_name`
> 只是设计器侧的备注元数据，故校验器按“下标不越界”这一真实机制判定，不做名字存在性校验。
