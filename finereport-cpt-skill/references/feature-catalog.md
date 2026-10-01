# cpt 功能特征目录

> 适用场景：需要确认某个 class 名/事件名/按钮类是否真实存在、想了解某特征在官方 demo 中的出现频次、按类别检索示例文件时。
> 一句话摘要：本文是 240 个官方 demo cpt 的全量 grep 统计手册，按特征类别给出"特征值 | 出现次数 | 文件数 | 示例文件路径"，用于查证类名与选型。
>
> 数据来源：`D:\FineReport_11.0\webapps\webroot\WEB-INF\reportlets\demo`，240 个 .cpt（纯 XML）+ 144 个 .fvs（ZIP，不可 grep）。统计时间 2026-10-01。

---

## 目录

1. [数据集类型](#1-数据集类型)
2. [控件 / Widget 类型](#2-控件--widget-类型)
3. [图表类型](#3-图表类型)
4. [JS 事件 / 监听器](#4-js-事件--监听器)
5. [超链接类型](#5-超链接类型)
6. [工具栏与按钮](#6-工具栏与按钮)
7. [填报 / 入库](#7-填报--入库)
8. [公式函数](#8-公式函数)
9. [样式与条件属性](#9-样式与条件属性)
10. [条件类与高亮动作](#10-条件类与高亮动作)
11. [权限目录特征](#11-权限目录特征)
12. [其他辨识度特征](#12-其他辨识度特征)
13. [决策报表 fvs 说明](#13-决策报表-fvs-说明)

---

## 1. 数据集类型

**检索模式**：`class="com\.fr\.data\.impl\.[^"]+"`

| 特征值（类名） | 出现次数 | 文件数 | 示例文件路径 |
|---|---|---|---|
| com.fr.data.impl.NameDatabaseConnection | 287 | 131 | DataReport\销售财务报销表.cpt |
| com.fr.data.impl.EmbeddedTableData | 244 | 78 | Phone\basic\档案式报表-phone.cpt |
| com.fr.data.impl.DBTableData | 221 | 131 | DataReport\销售财务报销表.cpt |
| com.fr.data.impl.NameTableData | 209 | 90 | analytics\financial\现金流量分析.cpt |
| com.fr.data.impl.CustomDictionary | 86 | 25 | authority\联合填报.cpt |
| com.fr.data.impl.DatabaseDictionary | 60 | 40 | parameter\多选下拉树实现多值查询.cpt |
| com.fr.data.impl.TableDataDictionary | 54 | 25 | parameter\多选下拉树实现多值查询.cpt |
| com.fr.data.impl.FormulaDictionary | 8 | 7 | form\固定资产(增删改).cpt |
| com.fr.data.impl.DynamicSQLDict | 6 | 4 | form\填报可暂存.cpt |
| com.fr.data.impl.ExcelTableData | 2 | 2 | Phone\industry\银行存贷汇总-phone.cpt |
| com.fr.data.impl.RecursionTableData | 2 | 2 | Phone\form\scheduling\工作内容录入-phone.cpt |

要点：DBTableData 与 NameDatabaseConnection 是主流（各 131 文件）；EmbeddedTableData 也常见（78 文件）。

## 2. 控件 / Widget 类型

**检索模式**：`class="com\.fr\.form\.ui\.[^"]+"`

| 特征值（类名） | 含义 | 出现次数 | 文件数 | 示例文件路径 |
|---|---|---|---|---|
| com.fr.form.ui.NumberEditor | 数字控件 | 1814 | 20 | parameter\库存查询每页显示固定行.cpt |
| com.fr.form.ui.TextEditor | 文本控件 | 252 | 28 | NewbieGuide\行式填报报表.cpt |
| com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget | 绝对布局容器 | 243 | 36 | parameter\库存查询每页显示固定行.cpt |
| com.fr.form.ui.reg.NoneReg | 无数据校验 | 153 | 25 | NewbieGuide\行式填报报表.cpt |
| com.fr.form.ui.Label | 标签 | 103 | 34 | parameter\库存查询每页显示固定行.cpt |
| com.fr.form.ui.ComboBox | 下拉框 | 57 | 27 | DataReport\销售财务报销表.cpt |
| com.fr.form.ui.DateEditor | 日期控件 | 56 | 25 | Phone\parameter\下拉树与动态显示查询按钮-phone.cpt |
| com.fr.form.ui.container.WParameterLayout | 参数布局容器 | 36 | 36 | parameter\库存查询每页显示固定行.cpt |
| com.fr.form.ui.FreeButton | 自由按钮 | 24 | 12 | chart\basic\轮播气泡图.cpt |
| com.fr.form.ui.ComboCheckBox | 复选下拉框 | 17 | 12 | authority\产品销售情况查询.cpt |
| com.fr.form.ui.RadioGroup | 单选按钮组 | 16 | 10 | authority\联合填报.cpt |
| com.fr.form.ui.TreeComboBoxEditor | 树形下拉框 | 11 | 8 | parameter\多选下拉树实现多值查询.cpt |
| com.fr.form.ui.TextArea | 文本域 | 9 | 8 | DataReport\销售财务报销表.cpt |
| com.fr.form.ui.CheckBoxGroup | 复选按钮组 | 7 | 5 | parameter\动态列查询.cpt |
| com.fr.form.ui.MultiFileEditor | 多文件上传 | 5 | 5 | NewbieGuide\自由填报报表.cpt |
| com.fr.form.ui.IframeEditor | 内嵌网页 | 5 | 4 | chart\basic\轮播气泡图.cpt |
| com.fr.form.ui.CheckBox | 复选框 | 2 | 2 | form\批量删除.cpt |

校验规则类（reg 包）：MobileReg（4 文件）、PhoneReg（4）、CustomReg（4）、PostCardReg（3）、IDCardReg（2）。

## 3. 图表类型

**检索模式**：`chartClass="com\.fr\.plugin\.chart\.[^"]+"`

| 特征值（类名） | 图表类型 | 出现次数 | 文件数 | 示例文件路径 |
|---|---|---|---|---|
| com.fr.plugin.chart.vanchart.VanChart | 通用图表引擎 | 155 | 58 | chart\basic\曲线折线图.cpt |
| com.fr.plugin.chart.map.MapMainTypeChart | 地图 | 6 | 6 | chart\extend\三维柱形地球.cpt |
| com.fr.plugin.chart.kpi.KPIMainTypeChart | KPI 指标卡 | 5 | 4 | chart\extend\粒子计数器.cpt |
| com.fr.plugin.chart.catalog.CatalogMainTypeChart | 智慧树图 | 4 | 4 | chart\extend\智慧树图-模型.cpt |
| com.fr.plugin.chart.meter.MeterMainTypeChart | 仪表盘 | 4 | 4 | chart\extend\轮播像素点图.cpt |
| com.fr.plugin.chart.column.ColumnMainTypeChart | 柱形图 | 3 | 3 | chart\extend\轮播条形图.cpt |
| com.fr.plugin.chart.pie.PieMainTypeChart | 饼图 | 1 | 1 | chart\extend\轮播饼图.cpt |
| com.fr.plugin.chart.time.TimeMainTypeChart | 时间轴 | 1 | 1 | chart\extend\时间齿轮.cpt |

VanChart 内部子类型（按 Plot 类区分）：饼/环/玫瑰（PiePlot4VanChart）、柱形（VanChartColumnPlot）、折线（VanChartLinePlot）、面积（VanChartAreaPlot）、仪表盘（VanChartGaugePlot）、散点（VanChartScatterPlot）、气泡（VanChartBubblePlot）、地图（VanChartMapPlot）、热力（VanChartHeatMapPlot）。地图类合计 52 次匹配、跨 13 文件。

## 4. JS 事件 / 监听器

**检索模式**：`event="[^"]+"`（即 Listener 节点）

| 事件名 | 含义 | 出现次数 | 典型示例文件 |
|---|---|---|---|
| stopedit | 停止编辑 | 19+ | authority\联合填报.cpt、analytics\financial\在线切换统计维度.cpt |
| click | 点击 | 18+ | form\批量删除.cpt、chart\basic\轮播气泡图.cpt |
| statechange | 状态改变 | 8+ | form\批量删除.cpt、analytics\financial\应收应付账款图表联动.cpt |
| afterload | 加载后 | 6 | chart\basic\轮播气泡图.cpt、chart\DataVisualization\数据可视化.cpt |
| afteredit | 编辑结束 | 5+ | Phone\form\移动端连续扫码-phone.cpt、parameter\参数联动与自动查询.cpt |
| afterinit | 初始化后 | 3 | parameter\批量处理数据.cpt |
| writesuccess | 写入成功 | 3 | Phone\form\移动端连续扫码-phone.cpt |
| startload | 开始加载 | 3 | chart\basic\轮播气泡图.cpt |
| beforeimportexcel | 导入 Excel 前 | 1 | form\导入Excel前清空表.cpt |

总计 66 条 Listener 记录。

## 5. 超链接类型

**检索模式**：`Hyperlink`

| 特征值（类名） | 含义 | 出现次数 | 文件数 | 示例文件路径 |
|---|---|---|---|---|
| com.fr.js.WebHyperlink | 网络超链接 | ~60 | ~15 | authority\订单情况查看.cpt |
| com.fr.js.ReportletHyperlink | 报表超链接 | ~80 | ~20 | cloud\demonew.cpt、analytics\financial2\资金分析.cpt |
| com.fr.js.ReportletHyperlinkDialogAttr | 报表超链接对话框 | ~25 | ~10 | cloud\demo.cpt |
| com.fr.report.cell.cellattr.highlight.HyperlinkHighlightAction | 超链接高亮动作 | 7 | 3 | Phone\analytics\operations\签约情况分析-phone.cpt |

JS API 跳转方式：FR.doHyperlinkByGet（GET）、FR.doHyperlinkByPost（POST，第二参 'REPORT'），见 chart\basic\轮播气泡图.cpt。

## 6. 工具栏与按钮

### 6.1 工具栏结构

| 形态 | 文件数 | 说明 |
|---|---|---|
| ToolBarManager 完整工具栏 | 91 | 含分页/打印/导出等按钮 |
| ToolBars 空自闭合（禁用） | 75 | 无自定义按钮 |

### 6.2 工具栏按钮类型

**检索模式**：`Widget class="com\.fr\.report\.web\.button\.[^"]+"`

| 按钮类 | 含义 | 出现次数 | 文件数 | 示例文件 |
|---|---|---|---|---|
| com.fr.report.web.button.Export | 导出 | 95 | 82 | basic\同比环比等财务统计表.cpt |
| com.fr.report.web.button.Email | 邮件发送 | 82 | 77 | basic\同比环比等财务统计表.cpt |
| com.fr.report.web.button.Print | 打印 | 78 | 69 | basic\同比环比等财务统计表.cpt |
| com.fr.report.web.button.FlashPrint | Flash 打印 | 60 | 56 | basic\同比环比等财务统计表.cpt |
| com.fr.report.web.button.page.First | 首页 | 54 | 54 | 同上 |
| com.fr.report.web.button.page.Previous | 上一页 | 54 | 54 | 同上 |
| com.fr.report.web.button.page.PageNavi | 页码导航 | 54 | 54 | 同上 |
| com.fr.report.web.button.page.Next | 下一页 | 54 | 54 | 同上 |
| com.fr.report.web.button.page.Last | 末页 | 54 | 54 | 同上 |
| com.fr.report.web.button.write.Submit | 提交入库 | 26 | 26 | NewbieGuide\自由填报报表.cpt |
| com.fr.report.web.button.write.Verify | 数据校验 | 25 | 24 | NewbieGuide\自由填报报表.cpt |
| com.fr.report.web.button.write.AppendColumnRow | 添加行列 | 18 | 18 | Phone\form\scheduling\工作内容录入-phone.cpt |
| com.fr.report.web.button.write.ShowCellValue | 显示单元格值 | 16 | 16 | parameter\动态列查询.cpt |
| com.fr.report.web.button.NewPrint | 新打印 | 16 | 12 | cloud\business.cpt |
| com.fr.report.web.button.write.DeleteRowButton | 删除行 | 11 | 6 | form\土地出让（非行式增加删除行）.cpt |
| com.fr.report.web.button.write.AppendRowButton | 添加行 | 9 | 5 | form\土地出让（非行式增加删除行）.cpt |
| com.fr.report.web.button.write.ImportExcelData | 导入 Excel | 5 | 5 | analytics\横向扩展后某列数据占比.cpt |
| com.fr.report.web.button.PageSetup | 页面设置 | 5 | 5 | cloud\demopeople.cpt |
| com.fr.report.web.button.PrintPreview | 打印预览 | 5 | 5 | cloud\demopeople.cpt |

## 7. 填报 / 入库

| 特征 | 说明 | 文件数 | 示例文件 |
|---|---|---|---|
| Submit 提交按钮（IconName=submit） | 提交入库 | 27 | NewbieGuide\行式填报报表.cpt |
| 行式填报 | 行式增删行 | ~10 | form\土地出让（非行式增加删除行）.cpt |
| 自由填报 | 自由布局填报 | ~8 | form\简单自由填报.cpt |
| 主从表填报 | 多源填报 | 1 | form\主从表多源填报.cpt |
| Excel 导入 | 在线导入/自匹配 | 4 | form\在线导入Excel.cpt |
| 填报暂存 | 暂存+清除暂存 | 2 | form\填报可暂存.cpt |
| 联合填报 | 权限+填报结合 | 1 | authority\联合填报.cpt |
| 批量删除 | 批量操作 | 1 | form\批量删除.cpt |

填报事件：writesuccess、afteredit、beforeimportexcel。提交配置结构（ReportWriteAttr + BuiltInSQLSubmiter + IntelliDMLConfig）详见 cpt-structure.md 第 11 节。

## 8. 公式函数

**检索模式**：`value="=`（单元格公式）

| 统计项 | 数值 |
|---|---|
| value="=" 匹配次数 | 270 |
| 涉及文件数 | 50 |
| 公式最密集文件 | chart\DataVisualization\数据可视化.cpt（22 处）、IOS平台年度数据报告.cpt（20 处） |

说明：公式嵌入在 O 节点的 CDATA 文本中，以等号开头；具体函数清单见 cpt-structure.md 第 7 节。

## 9. 样式与条件属性

### 9.1 样式

- StyleList 节点几乎所有带样式模板都有。
- horizontal_alignment：0=左、2=居中、4=右。
- 数字格式 `com.fr.base.CoreDecimalFormat`；日期格式 `com.fr.base.SimpleDateFormatThreadSafe`。

### 9.2 条件类

**检索模式**：`Condition class="com\.fr\.data\.condition\.[^"]+"`

| 条件类型 | 类名 | 出现次数 | 文件数 | 示例文件 |
|---|---|---|---|---|
| 公式条件 | com.fr.data.condition.FormulaCondition | 1097 | 68 | basic\同比环比等财务统计表.cpt |
| 列表条件 | com.fr.data.condition.ListCondition | 504 | 96 | basic\同比环比等财务统计表.cpt |
| 对象条件 | com.fr.data.condition.ObjectCondition | 506 | 22 | analytics\marketing\销售等级分析.cpt |
| 通用条件 | com.fr.data.condition.CommonCondition | 430 | 59 | basic\同比环比等财务统计表.cpt |

## 10. 条件类与高亮动作

**检索模式**：`HighlightAction class="com\.fr\.report\.cell\.cellattr\.highlight\.[^"]+"`

| 高亮动作类型 | 类名 | 出现次数 | 文件数 | 示例文件 |
|---|---|---|---|---|
| ValueHighlightAction | 值高亮 | 717 | 21 | cloud\demoinformation.cpt |
| BackgroundHighlightAction | 背景高亮 | 328 | 53 | Phone\industry\银行头寸表-phone.cpt |
| FRFontHighlightAction | 字体高亮 | 209 | 18 | Phone\industry\银行存贷汇总.cpt |
| ForegroundHighlightAction | 前景色高亮 | 164 | 11 | analytics\financial2\净利润_3.cpt |
| RowHeightHighlightAction | 行高高亮 | 127 | 20 | analytics\financial\在线切换统计维度.cpt |
| BorderHighlightAction | 边框高亮 | 19 | 5 | Phone\industry\银行存贷汇总.cpt |
| PageHighlightAction | 分页高亮 | 11 | 11 | parameter\下拉树与动态显示查询按钮.cpt |
| HyperlinkHighlightAction | 超链接高亮 | 7 | 3 | Phone\analytics\operations\签约情况分析-phone.cpt |
| ColWidthHighlightAction | 列宽高亮 | 7 | 2 | Phone\analytics\financial\公司回款额-phone.cpt |
| WidgetHighlightAction | 控件高亮 | 1 | 1 | DataReport\产品月销量情况录入表.cpt |

## 11. 权限目录特征

目录：demo\authority\（4 个 cpt）

| 文件 | 特征说明 |
|---|---|
| 订单情况查看.cpt | 多 Sheet 权限报表，全套工具栏按钮，DictPresent 字典展示 |
| 各部门人员信息查看.cpt | 部门数据权限，ListCondition + CommonCondition + GETUSERDEPARTMENTS() |
| 联合填报.cpt | 权限+填报结合，7 处 stopedit 事件 |
| 多级权限配置使用说明.cpt | WebHyperlink 跳转说明 |

## 12. 其他辨识度特征

- 打印：ServerPrinter 节点 138 文件；FlashPrint 按钮 56 文件；Print 69 文件。
- 分组器：`com.fr.report.cell.cellattr.core.group.FunctionGrouper` 广泛用于分组报表；汇总用 SummaryGrouper。
- 移动端：Phone\ 目录约 40+ 个 cpt，特征为 -phone 后缀、DefaultMobileBookMarkStyle、MobileReg/PhoneReg 校验。
- 数据集条件参数：ConditionFuncCheck check="true"；参数联动示例 parameter\参数联动与自动查询.cpt。
- 15 个顶级目录全覆盖：analytics / authority / basic / chart / cloud / DataReport / form / fvs / homepage / Industrial template / NewbieGuide / Newtheme / other / parameter / Phone。

## 13. 决策报表 fvs 说明

- **全部 144 个 .fvs 文件首字节均为 PK（50 4B 03 04），是 ZIP 压缩包，不是纯 XML**，因此 grep 无法直接检索其内部。
- 解压后内部结构（来源：chart/map/巡展地图.fvs）：

```
editor.tpl                       主模板 XML
<uuid>.chart                     图表定义 XML
<uuid>.ec                        内嵌数据 XML
<uuid>.png                       图片资源
info.json                        资源登记（title/type/alias）
timestamp_folder/                时间戳目录
```

- editor.tpl 根节点是 **Duchamp**（不是 cpt 的 WorkBook）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Duchamp xmlVersion="20211223" releaseVersion="11.0.0">
<TableDataMap>
<TableData name="File1" class="com.fr.data.impl.EmbeddedTableData">
<Desensitizations desensitizeOpen="false"/>
```

- 资源文件用 UUID 命名，靠 info.json 登记。
- **本技能包只生成普通报表 .cpt，不生成 .fvs**；遇到 .fvs 需求应引导用户使用设计器的决策报表设计器，或只把其中的数据集/数据定义部分迁移到 cpt。

---

*统计基于 2026-10-01 对官方 demo 目录的全量 grep；次数为全目录匹配数，文件数为去重后命中文件数。*
