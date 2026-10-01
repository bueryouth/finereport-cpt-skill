# cpt 结构与语法规则知识文档

> 适用场景：编写新 cpt、手工修改 cpt XML、报错定位节点含义、查证某个 class 名/属性名是否真实存在。
> 一句话摘要：本文是 FineReport 11 普通报表（.cpt）的完整结构语法手册，每一条结论都附官方 demo 中的真实 XML 片段与来源路径；与旧标签字典不一致处已标注【修正】，一切以 demo 实测为准。
>
> 采样口径：`D:\FineReport_11.0\webapps\webroot\WEB-INF\reportlets\demo`，240 个 .cpt 全部字节级扫描。下文"来源"路径均相对该 demo 目录。

---

## 目录

1. 文件级约定
2. 根节点与报表属性
3. 数据集
4. 参数与控件
5. 单元格体系
6. 样式体系
7. 公式
8. JS 事件
9. 超链接
10. 按钮与工具栏
11. 填报入库
12. 图表
13. 权限
14. 打印 / 分页
15. AttrMark 尾部节点
16. 最小可用报表完整骨架
17. 与常见认知的差异
18. 常用 XPath 定位表

---

## 1. 文件级约定

对全部 240 个 .cpt 首 2KB 字节扫描结果：

| 检查项 | 结果 |
|---|---|
| 文件总数 | 240 |
| 带 UTF-8 BOM（EF BB BF） | 0 |
| 行尾为 CRLF | 0（全部 LF `0A`） |
| 含 `<!DOCTYPE` | 0 |
| 含前导空格缩进 | 0（每个标签顶格写） |
| XML 声明 | 全部为 `<?xml version="1.0" encoding="UTF-8"?>` |

真实文件头（来源：`NewbieGuide/分组报表.cpt`）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<WorkBook xmlVersion="20170720" releaseVersion="11.0.0">
<TableDataMap>
<TableData name="ds1" class="com.fr.data.impl.DBTableData">
```

硬性约定：

- **编码**：UTF-8 无 BOM，声明固定为 `<?xml version="1.0" encoding="UTF-8"?>`。
- **CDATA**：所有用户可见文本（SQL、表头、参数默认值、样式名）一律放 CDATA，防止 `<`、`&` 破坏 XML。
- **class 属性 = Java 类全限定名**：引擎按 class 值反射实例化对象，是 cpt 与 lib 下 jar 的依赖指针。写错类名=模板打不开。
- **EMU 单位**：行高/列宽用 EMU，914400=1 英寸=72pt（1pt=12700 EMU）、360000=1 厘米；默认列宽 2743200=3 英寸=216pt≈设计器 80 网格 px（34290 EMU≈1 网格 px）。【修正】原文档只写"3 英寸"，补充 pt 与网格 px 两种标定，避免与设计器像素认知混淆。
- **节点顺序敏感**：WorkBook 下固定顺序为 TableDataMap → Report → ReportParameterAttr → StyleList → 各 AttrMark。程序生成必须保持。
- **无 DOCTYPE**：纯序列化 XML，无 DTD/XSD。
- **零缩进、LF 换行**：不要用 XML 美化工具格式化后写回。

老版本文件头差异（来源：`DataReport/财务报销审核表.cpt`）：

```xml
<WorkBook xmlVersion="20140501" releaseVersion="7.1.0">
```

## 2. 根节点与报表属性

### 2.1 WorkBook 下一级子节点顺序

来源：`NewbieGuide/分组报表.cpt`

```xml
<WorkBook xmlVersion="20170720" releaseVersion="11.0.0">
<TableDataMap> ... </TableDataMap>
<Report class="com.fr.report.worksheet.WorkSheet" name="sheet1"> ... </Report>
<ReportParameterAttr> ... </ReportParameterAttr>
<StyleList> ... </StyleList>
<DesignerVersion DesignerVersion="LAA"/>
<PreviewType PreviewType="0"/>
<TemplateThemeAttrMark .../>
<StrategyConfigsAttr .../>
<TemplateIdAttMark .../>
<TemplateCloudInfoAttrMark .../>
</WorkBook>
```

要点：

- 根节点是 **WorkBook**，不是教程里常见的 Report。Report 只是 WorkBook 下的一个子节点。
- 一个 cpt = 一个 WorkBook = 一个 sheet（`com.fr.report.worksheet.WorkSheet`）。demo 240 个文件中未出现多 sheet。
- 【修正】旧标签字典称"多 sheet 时出现多个 Report"——demo 实测未覆盖，不要主动生成多 sheet。
- DesignerVersion 是设计器混淆版本码（LAA/KAA/JAA...），只读。
- PreviewType：`0`=普通（分页）预览，`1`=填报预览。
- 【补充】版本号：本技能包 demo 采样为 xmlVersion="20170720" releaseVersion="11.0.0"；关联两个项目的真实/新生成模板均为 xmlVersion="20211223" releaseVersion="11.5.0"。新旧皆可被 11.0 设计器读取；新模板建议写 20211223/11.5.0，并在 StyleList 后补 DesensitizationList、StrongestControlAttr、ForkIdAttrMark 等尾部节点。

### 2.2 页面属性 ReportPageAttr / ReportAttrSet

来源：`NewbieGuide/分组报表.cpt` + `chart/basic/饼图.cpt`

```xml
<Report class="com.fr.report.worksheet.WorkSheet" name="sheet1">
<ReportPageAttr>
<HR/>
<FR/>
<HC/>
<FC/>
</ReportPageAttr>
<ColumnPrivilegeControl/>
<RowPrivilegeControl/>
<RowHeight defaultValue="723900">
<![CDATA[914400,990600,723900,...]]></RowHeight>
<ColumnWidth defaultValue="2743200">
<![CDATA[2995748,3413760,3553097,...]]></ColumnWidth>
```

- 【修正】旧字典把 HR/FR/HC/FC 解释为"页眉行/页脚行/页眉列/页脚列"，实测语义是**分页重复**：HR=水平重复行、FR=垂直重复行、HC=水平重复标题列、FC=垂直重复标题列。可带 from/to：`<HR F="0" T="1"/>`（来源：`parameter/批量处理数据.cpt`）。
- RowHeight/ColumnWidth 的 CDATA 是逗号分隔的 EMU 数值串，个数对应实际行数/列数；defaultValue 是超出列表后的默认值。
- 冻结：`<FrozenColumnRow columnrow="A3"/>`（来源：`parameter/批量处理数据.cpt`）。

纸张与边距（来源：`chart/basic/饼图.cpt`）：

```xml
<ReportAttrSet>
<ReportSettings headerHeight="0" footerHeight="0">
<PaperSetting>
<PaperSize width="32400000" height="18000000"/>
<Margin top="986400" left="2743200" bottom="986400" right="2743200"/>
</PaperSetting>
</ReportSettings>
<Header reportPageType="0">
<Background name="NullBackground"/>
<LeftList/><CenterList/><RightList/>
</Header>
<Footer reportPageType="0">
<Background name="NullBackground"/>
<LeftList/><CenterList/><RightList/>
</Footer>
</ReportAttrSet>
```

横向纸张：`<PaperSetting orientation="1">`（来源：`authority/各部门人员信息查看.cpt`）。

## 3. 数据集

### 3.1 SQL 数据集 DBTableData（最常见）

来源：`NewbieGuide/分组报表.cpt`

```xml
<TableData name="ds1" class="com.fr.data.impl.DBTableData">
<Parameters/>
<Attributes maxMemRowCount="-1"/>
<Connection class="com.fr.data.impl.NameDatabaseConnection">
<DatabaseName>
<![CDATA[FRDemo]]></DatabaseName>
</Connection>
<Query>
<![CDATA[select * from 销量]]></Query>
<PageQuery>
<![CDATA[]]></PageQuery>
</TableData>
```

【修正】utools 插件 sample 中出现过 `<Connection><DataModel class="com.fr.data.impl.Connection"/>` 与 `<Content>` 两种旧写法；demo 实测 FR11 精简格式是 Connection 带 `class="com.fr.data.impl.NameDatabaseConnection"`、SQL 写在 `<Query>` 里。生成器一律采用实测写法。

带参数与动态拼 SQL（来源：`parameter/多选下拉树实现多值查询.cpt`）：

```xml
<TableData name="ds1" class="com.fr.data.impl.DBTableData">
<Parameters>
<Parameter>
<Attributes name="地区"/>
<O><![CDATA[]]></O>
</Parameter>
</Parameters>
<Attributes maxMemRowCount="-1"/>
<Connection class="com.fr.data.impl.NameDatabaseConnection">
<DatabaseName><![CDATA[FRDemo]]></DatabaseName>
</Connection>
<Query><![CDATA[SELECT * FROM S订单 as 订单
where 货主地区 is not null
${if(len(地区)=0,"","and 货主城市 in ('"+SUBSTITUTE(地区,",","','")+"')")} ]]></Query>
</TableData>
```

要点：

- `${...}` 是数据集内公式，动态拼 SQL 片段。
- PageQuery 是分页 SQL，demo 里几乎都为空。
- 跨数据集传参：`<Parameter><Attributes name="layer1"/><O><![CDATA[]]></O></Parameter>`，SQL 里用 `'${layer1}'`。

### 3.2 内嵌数据集 EmbeddedTableData

来源：`cloud/retention_up.cpt`

```xml
<TableData name="留存上升" class="com.fr.data.impl.EmbeddedTableData">
<Parameters/>
<DSName><![CDATA[]]></DSName>
<ColumnNames><![CDATA[yearMonth,,.,,tName,,.,,tPV,,.,,tUV,,.,,lPV,,.,,lUV,,.,,retention]]></ColumnNames>
<ColumnTypes><![CDATA[java.sql.Timestamp,java.lang.String,java.lang.Integer,java.lang.Integer,java.lang.Long,java.lang.Long,java.math.BigDecimal]]></ColumnTypes>
<RowData ColumnTypes="java.sql.Timestamp,java.lang.String,...">
<![CDATA[NKhU]A_E\rlfAfg)!]ADj`cEq`WUF>Co'B;FR)PTYs.e0g-i$BLP0ueH(%55V`neV5R!Ngp@;A...]]></RowData>
</TableData>
```

- 列名之间用 `,,.,,` 分隔，不是逗号。
- RowData 是压缩/编码后的二进制（FineReport 专有编码），不是明文 CSV。**手工构造内嵌数据集不现实**，必须由设计器写出；生成器只产 DBTableData。

### 3.3 服务器数据集引用 NameTableData

图表/字典里引用已注册数据集时出现（实测 90 个文件）：

```xml
<TableData class="com.fr.data.impl.NameTableData"><Name><![CDATA[ds1]]></Name></TableData>
```

### 3.4 数据集类型边界

- demo 实测确认的 TableData class 只有两种：DBTableData（221 次/131 文件）与 EmbeddedTableData（244 次/78 文件）。
- **未发现**存储过程（Procedure/StoredProcedure）类数据集——不要生成。
- 另有 ExcelTableData（2 文件）、RecursionTableData（2 文件）属边缘类型，默认不使用。

## 4. 参数与控件

### 4.1 报表参数定义（无控件）

来源：`NewbieGuide/交叉报表.cpt`

```xml
<ReportParameterAttr>
<Attributes showWindow="true" delayPlaying="true" windowPosition="1" align="0" useParamsTemplate="true" currentIndex="0"/>
<PWTitle><![CDATA[参数]]></PWTitle>
<Parameter>
<Attributes name="地区"/>
<O><![CDATA[华东]]></O>
</Parameter>
</ReportParameterAttr>
```

【修正】ReportParameterAttr 实测挂在 **WorkBook 下**（与 StyleList 同级），不是 Report 内部。utools sample 里嵌在 Report/ReportAttrSet 内属旧写法。

### 4.2 参数面板控件容器 ParameterUI

来源：`parameter/多选下拉树实现多值查询.cpt`

```xml
<ReportParameterAttr>
<Attributes showWindow="true" delayPlaying="false" windowPosition="1" align="0" useParamsTemplate="false"/>
<PWTitle><![CDATA[参数]]></PWTitle>
<ParameterUI class="com.fr.form.main.parameter.FormParameterUI">
<Parameters/>
<Layout class="com.fr.form.ui.container.WParameterLayout">
<WidgetName name="para"/>
<WidgetAttr description=""><PrivilegeControl/></WidgetAttr>
<Margin top="1" left="1" bottom="1" right="1"/>
<Border>...</Border>
<Background name="ColorBackground" color="-1118482"/>
<LCAttr vgap="0" hgap="0" compInterval="0"/>
<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">
<InnerWidget class="com.fr.form.parameter.FormSubmitButton">
<WidgetName name="Search"/>
<Text><![CDATA[查询]]></Text>
<Hotkeys><![CDATA[enter]]></Hotkeys>
</InnerWidget>
<BoundsAttr x="455" y="52" width="129" height="21"/>
</Widget>
...
<DesignAttr width="960" height="103"/>
</Layout>
</ParameterUI>
</ReportParameterAttr>
```

- 每个控件包一层 BoundsWidget + BoundsAttr（绝对定位像素坐标）。
- 查询按钮 class 固定为 `com.fr.form.parameter.FormSubmitButton`。

### 4.3 真实控件类型清单

| 控件 | class 全名 | 来源文件 |
|---|---|---|
| 按钮（单元格） | `com.fr.form.ui.FreeButton` | `parameter/批量处理数据.cpt` |
| 复选框（单元格） | `com.fr.form.ui.CheckBox` | `parameter/批量处理数据.cpt` |
| 文本框 | `com.fr.form.ui.TextEditor` | `DataReport/产品月销量情况录入表.cpt` |
| 数字框 | `com.fr.form.ui.NumberEditor` | `DataReport/销售财务报销表.cpt` |
| 下拉框（参数面板） | `com.fr.form.ui.ComboBox` | `Phone/parameter/参数查询-phone.cpt` |
| 单选组 | `com.fr.form.ui.RadioGroup` | `Phone/parameter/参数查询-phone.cpt` |
| 下拉复选 | `com.fr.form.ui.ComboCheckBox` | `Phone/parameter/参数查询-phone.cpt` |
| 日期 | `com.fr.form.ui.DateEditor` | `Phone/parameter/复选框多值查询.cpt` |
| 下拉树 | `com.fr.form.ui.TreeComboBoxEditor` | `parameter/多选下拉树实现多值查询.cpt` |
| 标签 | `com.fr.form.ui.Label` | 同上 |
| 网页框 | `com.fr.form.ui.IframeEditor` | `other/网页框控件.cpt` |

ComboBox + CustomDictionary（来源：`Phone/parameter/参数查询-phone.cpt`）：

```xml
<InnerWidget class="com.fr.form.ui.ComboBox">
<WidgetName name="area"/>
<WidgetAttr description=""><PrivilegeControl/></WidgetAttr>
<Dictionary class="com.fr.data.impl.CustomDictionary">
<CustomDictAttr>
<Dict key="北京" value="北京"/>
<Dict key="江苏" value="江苏"/>
<Dict key="重庆" value="重庆"/>
</CustomDictAttr>
</Dictionary>
<widgetValue><O><![CDATA[北京]]></O></widgetValue>
</InnerWidget>
```

DateEditor（存值是 epoch 毫秒，来源：`Phone/parameter/复选框多值查询.cpt`）：

```xml
<InnerWidget class="com.fr.form.ui.DateEditor">
<WidgetName name="starttime"/>
<DateAttr/>
<widgetValue><O t="Date"><![CDATA[1264953600000]]></O></widgetValue>
</InnerWidget>
```

- 【修正/补充】日期序列化两种模式：控件存值（widgetValue/O t="Date"）是 epoch 毫秒字符串；但 returnDate 默认 false 时，控件回传给 SQL 的是格式化字符串（yyyyMM 等），SQL 里 '${param}' 加引号当字符串用即可。上下限：字面量写 start/end，公式写 startdatefm/enddatefm（字面量优先）。
- 【新增】必填校验是独立子节点 EMSG + allowBlank，且必须排在 DateAttr/TextAttr 之前；写成 DateAttr allowBlank="false" 属性不报错但完全不生效。

```xml
<EMSG><![CDATA[数据月份不允许为空]]></EMSG>
<allowBlank><![CDATA[false]]></allowBlank>
<DateAttr format="yyyyMM" enddatefm="=TODAY()"/>
```

TreeComboBoxEditor（多级下拉树，来源：`parameter/多选下拉树实现多值查询.cpt`）：

```xml
<InnerWidget class="com.fr.form.ui.TreeComboBoxEditor">
<WidgetName name="地区"/>
<LabelName name="地区:"/>
<TreeAttr mutiSelect="true" selectLeafOnly="true"/>
<TreeNodeAttr>
<Dictionary class="com.fr.data.impl.TableDataDictionary">
<FormulaDictAttr kiName="货主地区" viName="货主地区"/>
<TableDataDictAttr>
<TableData class="com.fr.data.impl.NameTableData"><Name><![CDATA[ds2]]></Name></TableData>
</TableDataDictAttr>
</Dictionary>
</TreeNodeAttr>
<TreeNodeAttr> ... ds3 ... </TreeNodeAttr>
<TreeNodeAttr> ... ds4 ... </TreeNodeAttr>
<widgetValue><O><![CDATA[]]></O></widgetValue>
</InnerWidget>
```

## 5. 单元格体系

### 5.1 CellElementList / C 节点

来源：`NewbieGuide/分组报表.cpt`

```xml
<CellElementList>
<C c="0" r="0" s="0">
<O><![CDATA[地区]]></O>
<PrivilegeControl/>
<Expand/>
</C>
<C c="0" r="1" s="1">
<O t="DSColumn">
<Attributes dsName="ds1" columnName="地区"/>
<Complex/>
<RG class="com.fr.report.cell.cellattr.core.group.FunctionGrouper"/>
<Parameters/>
</O>
<PrivilegeControl/>
<Expand dir="0"/>
</C>
</CellElementList>
```

- C 属性：c=列号、r=行号（均 0 基）、s=样式索引、cs=跨列合并、rs=跨行合并。
- 【修正】旧标签字典把 `s` 解释为"水平扩展后列数"——实测 `s="0"` 对应 StyleList 第 0 个 Style，**s 是样式表索引**。
- O 是单元格值（Object），t 属性是值类型。

### 5.2 O 的内容类型 t 属性

| t 值 | 含义 | 来源 |
|---|---|---|
| 无 t | 纯文本 CDATA | `NewbieGuide/分组报表.cpt` |
| t="DSColumn" | 数据集列 | `NewbieGuide/分组报表.cpt` |
| t="Formula" class="Formula" | 公式（老写法） | `DataReport/财务报销审核表.cpt` |
| t="XMLable" class="com.fr.base.Formula" | 公式（新写法） | `NewbieGuide/交叉报表.cpt` |
| t="BiasTextPainter" | 斜线表头 | `NewbieGuide/交叉报表.cpt` |
| t="B" | 布尔值 | `parameter/批量处理数据.cpt` |
| t="Date" | 日期（epoch 毫秒） | `Phone/parameter/复选框多值查询.cpt` |
| t="CC" | 图表单元格 | `chart/basic/饼图.cpt` |

### 5.3 数据集列 + 分组/汇总

来源：`NewbieGuide/分组报表.cpt`

```xml
<O t="DSColumn">
<Attributes dsName="ds1" columnName="销量"/>
<Complex/>
<RG class="com.fr.report.cell.cellattr.core.group.SummaryGrouper">
<FN><![CDATA[com.fr.data.util.function.SumFunction]]></FN>
</RG>
<Parameters/>
</O>
```

- FunctionGrouper = 普通分组；SummaryGrouper = 汇总。
- FN 指定聚合函数全名，如 SumFunction。

### 5.4 扩展节点 Expand

来源：`parameter/批量处理数据.cpt` + `DataReport/产品月销量情况录入表.cpt`

```xml
<Expand dir="0"/>
<Expand dir="1"/>
<Expand leftParentDefault="false" left="B4"/>
<Expand dir="0" leftParentDefault="false" left="C5" upParentDefault="false" up="D4"/>
```

- dir="0" = 纵向扩展（向下），dir="1" = 横向扩展（向右），不写 = 不扩展。
- left="C5" / up="D4" = 设置左父格/上父格（A1 风格引用）。

### 5.5 斜线表头

来源：`NewbieGuide/交叉报表.cpt`

```xml
<C c="0" r="2" cs="2" s="1">
<O t="BiasTextPainter">
<IsBackSlash value="false"/>
<![CDATA[产品|销售员|地区]]></O>
<PrivilegeControl/>
<Expand/>
</C>
```

### 5.6 单元格过滤条件（多 Join）

来源：`DataReport/产品月销量情况录入表.cpt`

```xml
<Condition class="com.fr.data.condition.ListCondition">
<JoinCondition join="0">
<Condition class="com.fr.data.condition.CommonCondition">
<CNUMBER><![CDATA[0]]></CNUMBER>
<CNAME><![CDATA[月份]]></CNAME>
<Compare op="0"><ColumnRow column="2" row="4"/></Compare>
</Condition>
</JoinCondition>
<JoinCondition join="0">
<Condition class="com.fr.data.condition.CommonCondition">
<CNUMBER><![CDATA[0]]></CNUMBER>
<CNAME><![CDATA[销售员]]></CNAME>
<Compare op="0">
<O t="XMLable" class="com.fr.base.Formula"><Attributes><![CDATA[=$fine_username]]></Attributes></O>
</Compare>
</Condition>
</JoinCondition>
</Condition>
```

- join="0" 表示 AND；Compare op="0" 表示等于。
- ColumnRow column/row 是 0 基单元格坐标。

### 5.7 HTML 渲染单元格

来源：`form/以html实现横向跑马灯特效.cpt`

```xml
<CellGUIAttr showAsHTML="true"/>
```

## 6. 样式体系

### 6.1 StyleList / Style 基本结构

来源：`NewbieGuide/交叉报表.cpt`

```xml
<StyleList>
<Style horizontal_alignment="0" imageLayout="1">
<FRFont name="微软雅黑" style="1" size="120"/>
<Background name="NullBackground"/>
<Border>
<Top style="1"/>
<Bottom style="1"/>
<Left style="1"/>
<Right style="1"/>
</Border>
</Style>
</StyleList>
```

- 【修正】horizontal_alignment：**0=居中、2=左、4=右**。此前误写为"0=左、2=居中、4=右"。经三方坐实：关联项目 A 反编译 Constants 常量、关联项目 B 真实模板脚本统计（表头/数据样式均 ha="2" 左对齐、金额样式 ha="4" 右对齐）、以及本节 demo 样式 ha="0" 配加粗表头（居中表头惯例）——均指向 0=居中。表头默认居中用 0，文本数据用 2，金额用 4。
- FRFont style：0=常规、1=加粗。
- size 单位是半磅：size="72"=9pt，size="120"=15pt。
- Background color 是 int 反色编码：-1=白色，-16777216=黑色；RRGGBB 转有符号 32 位（0xFF000000|RGB 超 2^31 折负），如 #FFFF00→-256。
- 【新增】FineColor 的 hor/ver 必须写 "-1"。hor/ver 是主题配色盘行列索引，任一非负时帆软按索引取主题色、忽略 color 字面值（文件里颜色正确、预览却是主题灰）。
- 【新增】Format 必须是 Style 的第一个子节点（在 FRFont 之前），写在后面帆软读不到数字格式。
- 【新增】自定义样式一律匿名：不要加 style_name / full="true" / border_source。full="true" 会让帆软拿样式库/主题整块覆盖 XML 属性，表现为"一部分表头居中、另一部分没居中"；自编名字样式库里查不到则回落主题默认。真实模板里仅内置"默认"样式带 full="true" border_source="-1"，自派生样式不带 full。
- 【新增】样式表按索引引用、只追加：单元格 C 的 s 是 StyleList 中 Style 的 0 基下标（匿名样式也占下标）；增删样式一律 append 到 StyleList 末尾，插在中间会让已有引用全部错位。

### 6.2 带颜色和数字格式的 Style

来源：`DataReport/产品月销量情况录入表.cpt`

```xml
<Style horizontal_alignment="2" imageLayout="1">
<Format class="com.fr.base.CoreDecimalFormat"><![CDATA[#0.00%]]></Format>
<FRFont name="微软雅黑" style="0" size="72"/>
<Background name="ColorBackground" color="-855310"/>
<Border><Top style="1" color="-2631721"/></Border>
</Style>
<Style horizontal_alignment="4" imageLayout="1">
<Format class="com.fr.base.SimpleDateFormatThreadSafe"><![CDATA[yyyy-MM-dd]]></Format>
<FRFont name="微软雅黑" style="0" size="72" foreground="-16750951"/>
<Background name="NullBackground"/>
<Border/>
</Style>
```

- 数字格式：`com.fr.base.CoreDecimalFormat`；日期格式：`com.fr.base.SimpleDateFormatThreadSafe`。
- foreground 是字体颜色，color 是背景色。

### 6.3 条件属性 HighlightList

来源：`parameter/多选下拉树实现多值查询.cpt`

```xml
<HighlightList>
<Highlight class="com.fr.report.cell.cellattr.highlight.DefaultHighlight">
<Name><![CDATA[条件属性2]]></Name>
<Condition class="com.fr.data.condition.FormulaCondition">
<Formula><![CDATA[row() % 2! = 0]]></Formula>
</Condition>
<HighlightAction class="com.fr.report.cell.cellattr.highlight.BackgroundHighlightAction">
<Scope val="1"/>
<Background name="ColorBackground" color="-657158"/>
</HighlightAction>
</Highlight>
</HighlightList>
```

其他 Action（统计见 feature-catalog.md）：ValueHighlightAction（717 次）、FRFontHighlightAction（209 次）、ForegroundHighlightAction、RowHeightHighlightAction（127 次）、PageHighlightAction（强制分页，11 次）、WidgetHighlightAction（动态换控件，仅 1 次）。

## 7. 公式

公式统一写在 O 的 Attributes 里，以等号开头。

聚合公式（来源：`NewbieGuide/交叉报表.cpt`）：

```xml
<O t="XMLable" class="com.fr.base.Formula">
<Attributes><![CDATA[=SUM(C4)]]></Attributes>
</O>
```

算术 + SQL 函数（来源：`DataReport/产品月销量情况录入表.cpt`）：

```xml
<O t="XMLable" class="com.fr.base.Formula">
<Attributes><![CDATA[=sql("FRDemo", "select name from user where user='" + $fr_username + "'", 1) + "-各产品月销量情况录入"]]></Attributes>
</O>
```

日期函数（来源：`DataReport/产品月销量情况录入表.cpt`）：

```xml
<O t="XMLable" class="com.fr.base.Formula">
<Attributes><![CDATA[=year(monthdelta(today(),-1)) + "-" + month(monthdelta(today(),-1))]]></Attributes>
</O>
```

权限函数（来源：`authority/各部门人员信息查看.cpt`）：

```xml
<O t="Formula" class="Formula">
<Attributes><![CDATA[=if(len($fr_authority) > 0 && $fr_authority = "SUPERROLE", "  各", GETUSERDEPARTMENTS()) + "部门员工信息查看"]]></Attributes>
</O>
```

demo 中已出现的系统变量/函数：$fr_username、$fine_username、$fr_authority、$fr_task_id、$$$（当前单元格值）、A1/B5 单元格引用、nofilter、row()、len()、sum()、today()、year()、month()、monthdelta()、sql()、GETUSERDEPARTMENTS()、GETUSERJOBTITLES()、REPLACE()、SUBSTITUTE()。

## 8. JS 事件

来源：`parameter/批量处理数据.cpt`

```xml
<Widget class="com.fr.form.ui.FreeButton">
<Listener event="afterinit">
<JavaScript class="com.fr.js.JavaScriptImpl">
<Parameters/>
<Content><![CDATA[window.ceshi=[]A;]]></Content>
</JavaScript>
</Listener>
<Listener event="click">
<JavaScript class="com.fr.js.JavaScriptImpl">
<Parameters/>
<Content><![CDATA[window.parent.form.getWidgetByName("公司名称").setValue(ceshi);
window.parent.FR.closeDialog();
window.parent.FR.destroyDialog();]]></Content>
</JavaScript>
</Listener>
</Widget>
```

带公式参数的 Listener：

```xml
<Listener event="statechange">
<JavaScript class="com.fr.js.JavaScriptImpl">
<Parameters>
<Parameter>
<Attributes name="a"/>
<O t="XMLable" class="com.fr.base.Formula"><Attributes><![CDATA[=B4]]></Attributes></O>
</Parameter>
</Parameters>
<Content><![CDATA[var value = this.getValue(); ...]]></Content>
</JavaScript>
</Listener>
```

demo 全量 grep 到的 event 名（共 66 条 Listener）：stopedit（19+）、click（18+）、statechange（8+）、afteredit（5+）、afterload（6）、afterinit（3）、writesuccess（3）、startload（3）、beforeimportexcel（1）。

## 9. 超链接

报表钻取超链接（来源：`NewbieGuide/订单信息表.cpt`）：

```xml
<NameJavaScriptGroup>
<NameJavaScript name="订单明细">
<JavaScript class="com.fr.js.ReportletHyperlink">
<JavaScript class="com.fr.js.ReportletHyperlink">
<Parameters>
<Parameter>
<Attributes name="订单号"/>
<O t="XMLable" class="com.fr.base.Formula"><Attributes><![CDATA[=$$$]]></Attributes></O>
</Parameter>
</Parameters>
<TargetFrame><![CDATA[_blank]]></TargetFrame>
<Features width="600" height="400"/>
<ReportletName showPI="true"><![CDATA[/订单明细表.cpt]]></ReportletName>
<Attr>
<DialogAttr class="com.fr.js.ReportletHyperlinkDialogAttr">
<O><![CDATA[]]></O>
<Location center="true"/>
</DialogAttr>
</Attr>
</JavaScript>
</JavaScript>
</NameJavaScript>
</NameJavaScriptGroup>
```

Web 超链接（来源：`authority/各部门人员信息查看.cpt`）：

```xml
<NameJavaScriptGroup>
<NameJavaScript name="网页链接1">
<JavaScript class="com.fr.js.WebHyperlink">
<JavaScript class="com.fr.js.WebHyperlink">
<Parameters/>
<TargetFrame><![CDATA[_blank]]></TargetFrame>
<Features width="600" height="400"/>
<URL><![CDATA[http://help.finereport.com/doc-view-865.html]]></URL>
</JavaScript>
</JavaScript>
</NameJavaScript>
</NameJavaScriptGroup>
```

- 超链接挂在 C 单元格内，与 O 同级。
- class 名嵌套出现两次（外层+内层同名），是历史序列化风格，照抄即可。

## 10. 按钮与工具栏

填报工具栏（来源：`NewbieGuide/行式填报报表.cpt`）：

```xml
<ReportWebAttr>
<ServerPrinter/>
<WebWriteContent>
<ToolBars>
<ToolBarManager>
<Location><Embed position="1"/></Location>
<ToolBar>
<Widget class="com.fr.report.web.button.write.Submit">
<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="0.0" description="">
<MobileBookMark useBookMark="false" bookMarkName="" frozen="false"/>
<PrivilegeControl/>
</WidgetAttr>
<Text><![CDATA[${i18n('Fine-Engine_Report_Utils_Submit')}]]></Text>
<Hotkeys><![CDATA[]]></Hotkeys>
<IconName><![CDATA[submit]]></IconName>
<Verify failVerifySubmit="false" value="true"/>
<Sheet onlySubmitSelect="false"/>
</Widget>
<Widget class="com.fr.report.web.button.write.Verify">
<Text><![CDATA[${i18n('Fine-Engine_Report_Verify_Data')}]]></Text>
<IconName><![CDATA[verify]]</IconName>
</Widget>
<Widget class="com.fr.report.web.button.write.AppendColumnRow">
<Text><![CDATA[${i18n('Fine-Engine_Add_Record')}]]></Text>
<IconName><![CDATA[append]]</IconName>
</Widget>
</ToolBar>
</ToolBarManager>
</ToolBars>
</WebWriteContent>
</ReportWebAttr>
```

- 填报预览工具栏在 ReportWebAttr > WebWriteContent > ToolBars 下；普通预览工具栏在 WebViewContent > ToolBars 下（demo 多为空自闭合）。
- 按钮文案 i18n 用 `${i18n('key')}`。
- 内置按钮 class 全清单（出现频次）见 references/feature-catalog.md 第 6 节：Export（95 次/82 文件）、Email（82）、Print（78）、FlashPrint（60）、分页五件套 First/Previous/PageNavi/Next/Last（各 54）、write.Submit（26）、write.Verify（25）等。
- 单元格内自由按钮见 §4.3.5 的 FreeButton。

## 11. 填报入库

智能提交 IntelliDMLConfig（来源：`DataReport/产品月销量情况录入表.cpt`）：

```xml
<ReportWriteAttr>
<SubmitVisitor class="com.fr.report.write.BuiltInSQLSubmiter">
<Name><![CDATA[内置SQL1]]></Name>
<Attributes dsName="FRDemo"/>
<DMLConfig class="com.fr.write.config.IntelliDMLConfig">
<Table schema="" name="up"/>
<ColumnConfig name="月份" isKey="true" skipUnmodified="false">
<ColumnRowGroup>
<ColumnRow column="2" row="4"/>
<ColumnRow column="2" row="5"/>
</ColumnRowGroup>
</ColumnConfig>
<ColumnConfig name="产品名称" isKey="true" skipUnmodified="false">
<ColumnRow column="3" row="3"/>
</ColumnConfig>
<ColumnConfig name="销售员" isKey="true" skipUnmodified="false">
<ColumnRow column="4" row="7"/>
</ColumnConfig>
<ColumnConfig name="销量" isKey="false" skipUnmodified="false">
<ColumnRowGroup>
<ColumnRow column="3" row="4"/>
<ColumnRow column="3" row="5"/>
</ColumnRowGroup>
</ColumnConfig>
<Condition class="com.fr.data.condition.FormulaCondition">
<Formula><![CDATA[len(D6)!=0]]></Formula>
</Condition>
</DMLConfig>
</SubmitVisitor>
</ReportWriteAttr>
```

要点：

- 【修正】填报配置挂在 Report 下（ReportAttrSet 同级、Report 结束前）；FR11 实测**没有** ReportWriteData 外壳节点（utools 旧 sample 里有，属旧格式）。
- ColumnConfig isKey="true" 是主键列，智能提交按主键自动判断 insert/update。
- ColumnRow column/row 是 0 基单元格坐标；ColumnRowGroup 表示该列绑定一组扩展行。
- demo 统一是 BuiltInSQLSubmiter + IntelliDMLConfig，未出现其他写回节点。
- 自定义 Java 类提交（utools 沉淀）：SubmitVisitor class="com.fr.report.write.WClassSubmiter"，内有 SubmitTask class="com.fr.data.ClassSubmitJob" + ClassAttr className + Property 绑定单元格。

## 12. 图表

图表单元格骨架（来源：`chart/basic/饼图.cpt`）：

```xml
<C c="0" r="0" cs="7" rs="17">
<O t="CC">
<LayoutAttr selectedIndex="0"/>
<Chart name="默认" chartClass="com.fr.plugin.chart.vanchart.VanChart">
<Chart class="com.fr.plugin.chart.vanchart.VanChart"
       wrapperName="RosePieChart"
       requiredJS="/com/fr/web/core/js/d3.js,/com/fr/web/core/js/vancharts-all.js,/com/fr/web/core/js/RosePieChart.js,"
       chartImagePath="">
<GI>...</GI>
<ChartAttr isJSDraw="true" isStyleGlobal="false"/>
<Title4VanChart>...</Title4VanChart>
<Plot class="com.fr.plugin.chart.PiePlot4VanChart">...</Plot>
<ChartDefinition>
<OneValueCDDefinition seriesName="货主地区" valueName="应付金额"
                      function="com.fr.data.util.function.SumFunction">
<Top topCate="-1" topValue="-1" isDiscardOtherCate="false" .../>
<TableData class="com.fr.data.impl.NameTableData"><Name><![CDATA[ds1]]></Name></TableData>
<CategoryName value=""/>
</OneValueCDDefinition>
</ChartDefinition>
</Chart>
<tools hidden="true" sort="true" export="true" fullScreen="true"/>
</Chart>
</O>
<PrivilegeControl/>
<Expand/>
</C>
```

【修正】旧标签字典写的 Plot class 是 VanChartColumnPlotAttr/PieAttr——demo 实测是带 "4VanChart" 后缀的类：

| Plot class | 图表类型 |
|---|---|
| com.fr.plugin.chart.PiePlot4VanChart | 饼图/环图/玫瑰图 |
| com.fr.plugin.chart.column.VanChartColumnPlot | 柱形图 |
| com.fr.plugin.chart.line.VanChartLinePlot | 折线图 |
| com.fr.plugin.chart.area.VanChartAreaPlot | 面积图 |
| com.fr.plugin.chart.gauge.VanChartGaugePlot | 仪表盘 |
| com.fr.plugin.chart.scatter.VanChartScatterPlot | 散点图 |
| com.fr.plugin.chart.bubble.VanChartBubblePlot | 气泡图 |
| com.fr.plugin.chart.map.VanChartMapPlot | 地图 |
| com.fr.plugin.chart.heatmap.VanChartHeatMapPlot | 热力图 |

- 图表根是 O t="CC"，不是 t="Chart"。
- 数据定义统一在 ChartDefinition 下；单值图用 OneValueCDDefinition。
- VanChart 引擎共 155 次出现/58 文件，是绝对主流。

## 13. 权限

模板内容权限（公式控制行过滤，来源：`authority/各部门人员信息查看.cpt`）：

```xml
<O t="DSColumn">
<Attributes dsName="staff" columnName="name"/>
<Condition class="com.fr.data.condition.ListCondition">
<JoinCondition join="0">
<Condition class="com.fr.data.condition.CommonCondition">
<CNUMBER><![CDATA[0]]></CNUMBER>
<CNAME><![CDATA[department]]></CNAME>
<Compare op="0">
<O t="Formula" class="Formula">
<Attributes><![CDATA[=if(len($fr_authority) > 0 && $fr_authority = "SUPERROLE", nofilter, GETUSERDEPARTMENTS())]]></Attributes>
</O>
</Compare>
</Condition>
</JoinCondition>
</Condition>
...
</O>
```

- cpt 里每个 C 下都有一个空的 PrivilegeControl 占位。
- 系统变量：$fr_authority、$fr_username、$fine_username、$fr_task_id。
- 权限函数：GETUSERDEPARTMENTS()、GETUSERJOBTITLES()、nofilter。
- **权限不写在 cpt XML 里**：真正的行/列权限靠数据决策系统配置 + 模板内公式过滤。demo 中未出现独立的 TemplatePrivilege 节点。

## 14. 打印 / 分页

- ServerPrinter 节点出现在 138 个文件中（几乎每个报表都有），位置在 ReportWebAttr 下。
- 打印按钮类：Print（78 次/69 文件）、FlashPrint（60/56）、NewPrint（16/12）、PrintPreview（5）、PageSetup（5）。
- 重复行/列见 §2.2 的 HR/FR/HC/FC。
- 强制分页通过条件属性 PageHighlightAction 实现（11 个文件）。

## 15. AttrMark 尾部节点

WorkBook 尾部固定一组标记节点（来源：`NewbieGuide/订单明细表.cpt`）：

```xml
<DesignerVersion DesignerVersion="LAA"/>
<PreviewType PreviewType="0"/>
<TemplateThemeAttrMark class="com.fr.base.iofile.attr.TemplateThemeAttrMark">
<TemplateThemeAttrMark name="兼容" dark="false"/>
</TemplateThemeAttrMark>
<StrategyConfigsAttr class="com.fr.esd.core.strategy.persistence.StrategyConfigsAttr">
<StrategyConfigs/>
</StrategyConfigsAttr>
<TemplateIdAttMark class="com.fr.base.iofile.attr.TemplateIdAttrMark">
<TemplateIdAttMark TemplateId="ce8c9899-5693-4927-ab4b-bb0e0769399c"/>
</TemplateIdAttMark>
```

- TemplateIdAttMark 的 TemplateId 是模板唯一 UUID，新生成时由生成器随机生成一个即可。
- TemplateCloudInfoAttrMark 仅被云分析功能处理过的模板才有，普通模板不写。

## 16. 最小可用报表完整骨架

基准：`NewbieGuide/订单明细表.cpt`（5905 字节，SQL 数据集+参数+表头+数据列+公式+汇总）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<WorkBook xmlVersion="20170720" releaseVersion="11.0.0">
<TableDataMap>
<TableData name="ds1" class="com.fr.data.impl.DBTableData">
<Parameters>
<Parameter>
<Attributes name="订单号"/>
<O><![CDATA[10248]]></O>
</Parameter>
</Parameters>
<Attributes maxMemRowCount="-1"/>
<Connection class="com.fr.data.impl.NameDatabaseConnection">
<DatabaseName><![CDATA[FRDemo]]></DatabaseName>
</Connection>
<Query><![CDATA[SELECT * FROM 订单明细 WHERE 订单ID=${订单号}]]></Query>
<PageQuery><![CDATA[]]></PageQuery>
</TableData>
</TableDataMap>
<Report class="com.fr.report.worksheet.WorkSheet" name="sheet1">
<ReportPageAttr><HR/><FR/><HC/><FC/></ReportPageAttr>
<ColumnPrivilegeControl/>
<RowPrivilegeControl/>
<RowHeight defaultValue="723900">
<![CDATA[723900,723900,876300,952500,838200,723900,723900,723900,723900,723900,723900]]></RowHeight>
<ColumnWidth defaultValue="2743200">
<![CDATA[3505200,2743200,2743200,2743200,2743200,3467100,2743200,2743200,2743200,2743200,2743200]]></ColumnWidth>
<CellElementList>
<C c="0" r="2" s="1"><O><![CDATA[订单号]]></O><PrivilegeControl/><Expand/></C>
<C c="1" r="2" s="1"><O><![CDATA[产品ID]]></O><PrivilegeControl/><Expand/></C>
<C c="2" r="2" s="1"><O><![CDATA[单价]]></O><PrivilegeControl/><Expand/></C>
<C c="3" r="2" s="1"><O><![CDATA[数量]]></O><PrivilegeControl/><Expand/></C>
<C c="4" r="2" s="1"><O><![CDATA[折扣]]></O><PrivilegeControl/><Expand/></C>
<C c="5" r="2" s="1"><O><![CDATA[总金额]]></O><PrivilegeControl/><Expand/></C>
<C c="0" r="3" s="2">
<O t="DSColumn">
<Attributes dsName="ds1" columnName="订单ID"/>
<Complex/>
<RG class="com.fr.report.cell.cellattr.core.group.FunctionGrouper"/>
<Parameters/>
</O>
<PrivilegeControl/><Expand dir="0"/>
</C>
<C c="5" r="3" s="2">
<O t="XMLable" class="com.fr.base.Formula">
<Attributes><![CDATA[=C4*D4*(1-E4)]]></Attributes>
</O>
<PrivilegeControl/><Expand/>
</C>
<C c="0" r="4" cs="5" s="3"><O><![CDATA[合计：]]></O><PrivilegeControl/><Expand/></C>
<C c="5" r="4" s="4">
<O t="XMLable" class="com.fr.base.Formula">
<Attributes><![CDATA[=SUM(F4)]]></Attributes>
</O>
<PrivilegeControl/><Expand/>
</C>
</CellElementList>
<ReportAttrSet>
<ReportSettings headerHeight="0" footerHeight="0">
<PaperSetting/>
<FollowingTheme background="false"/>
<Background name="ColorBackground">
<color><FineColor color="-1" hor="-1" ver="-1"/></color>
</Background>
</ReportSettings>
</ReportAttrSet>
<PrivilegeControl/>
</Report>
<ReportParameterAttr>
<Attributes showWindow="true" delayPlaying="true" windowPosition="1" align="0" useParamsTemplate="true" currentIndex="0"/>
<PWTitle><![CDATA[参数]]></PWTitle>
</ReportParameterAttr>
<StyleList>
<!-- 若干 Style：标题粗体、表头带边框、数据浅蓝底、右对齐、合计黄底 -->
</StyleList>
<DesignerVersion DesignerVersion="LAA"/>
<PreviewType PreviewType="0"/>
<TemplateThemeAttrMark class="com.fr.base.iofile.attr.TemplateThemeAttrMark">
<TemplateThemeAttrMark name="兼容" dark="false"/>
</TemplateThemeAttrMark>
<StrategyConfigsAttr class="com.fr.esd.core.strategy.persistence.StrategyConfigsAttr">
<StrategyConfigs/>
</StrategyConfigsAttr>
<TemplateIdAttMark class="com.fr.base.iofile.attr.TemplateIdAttrMark">
<TemplateIdAttMark TemplateId="ce8c9899-5693-4927-ab4b-bb0e0769399c"/>
</TemplateIdAttMark>
</WorkBook>
```

生成器最小必填节点清单：

1. XML 声明 + WorkBook
2. TableDataMap 至少一个 TableData
3. Report + ReportPageAttr + RowHeight + ColumnWidth + CellElementList
4. 至少一个 C 含 O + PrivilegeControl + Expand
5. ReportAttrSet + ReportSettings
6. ReportParameterAttr
7. StyleList
8. DesignerVersion + PreviewType + TemplateIdAttMark

## 17. 与常见认知的差异

继承 demo 实测结论并补充核对：

1. **根节点不是 Report 而是 WorkBook**。Report（WorkSheet）只是其子节点，每个 cpt 只有一个 sheet。
2. **.fvs 不是 XML，是 ZIP**（PK 头）。里面主模板叫 editor.tpl，根节点是 Duchamp。
3. **文件无 BOM、无缩进、LF 换行**。不要美化后写回。
4. **没有 DOCTYPE**。
5. **单元格不是 Cell/CellElement，而是 C + O**。C 是坐标容器，O 才是值；s 是样式索引（【修正】不是"水平扩展后列数"）。
6. **数据集 class 实测只有 DBTableData 与 EmbeddedTableData**；无存储过程数据集。
7. **内嵌数据集 RowData 是压缩二进制**，手工构造不现实。
8. **图表单元格类型是 O t="CC"**；Plot 类名带 4VanChart 后缀（【修正】旧字典的 PieAttr/VanChartColumnPlotAttr 写法有误）。
9. **填报入库统一走 ReportWriteAttr > SubmitVisitor(BuiltInSQLSubmiter) > IntelliDMLConfig**；FR11 无 ReportWriteData 外壳（【修正】utools 旧 sample 的旧格式）。
10. **权限不写在 cpt XML 里**，靠 $fr_authority 公式 + 决策系统配置。
11. **行高列宽单位是 EMU**，逗号分隔 CDATA 串；1pt=12700 EMU、34290 EMU≈设计器 1 网格 px（不是网页像素）。
12. **日期控件存值是 epoch 毫秒**；但 returnDate 默认 false 时回传 SQL 的是格式化字符串（不是日期类型）。
13. **超链接节点是 NameJavaScriptGroup > NameJavaScript > JavaScript，且 class 名嵌套重复两次**。
14. **颜色是 int 反色编码**（白色 -1、黑色 -16777216），不是 #RRGGBB；FineColor 的 hor/ver 必须 -1/-1，否则被主题色顶掉。
15. **公式有新旧两种写法**：老版 t="Formula" class="Formula"，新版 t="XMLable" class="com.fr.base.Formula"。
16. **【补充】HR/FR/HC/FC 是分页重复行列标记**，不是页眉页脚开关。
17. **【补充】ReportParameterAttr 挂 WorkBook 下**，不在 Report 内部。
18. **【补充】SQL 正文写在 Query 节点**（FR11 精简格式），不是 Content。
19. **【补充】字号 size 单位是半磅**（72=9pt），不是 pt 也不是 EMU。
20. **【修正】horizontal_alignment：0=居中、2=左、4=右**（此前误写反；三方坐实：关联项目反编译常量+真实模板统计+demo 表头 ha="0" 加粗惯例）。
21. **【新增】样式自定义一律匿名**：full="true" 会让主题覆盖 XML 属性，出现"一半表头居中、一半没居中"。
22. **【新增】必填校验是 EMSG+allowBlank 独立子节点且排在 DateAttr 前**，写成属性不生效。
23. **【新增】Format 必须是 Style 第一个子节点**；样式只追加末尾、不插中间。

## 18. 常用 XPath 定位表

| 目标 | XPath |
|---|---|
| 全部 SQL 数据集 | /WorkBook/TableDataMap/TableData[@class='com.fr.data.impl.DBTableData'] |
| 数据集名 | TableData/@name |
| 连接名 | TableData/Connection/DatabaseName |
| SQL 正文 | TableData/Query |
| 指定单元格内容 | /WorkBook/Report/CellElementList/C[@c='0'][@r='0']/O |
| 数据集参数 | /WorkBook/TableDataMap/TableData/Parameters/Parameter |
| 报表参数 | /WorkBook/ReportParameterAttr/Parameter |
| 填报配置 | /WorkBook/Report/ReportWriteAttr |
| 工具栏 | /WorkBook/Report/ReportWebAttr//ToolBar/Widget |
| 条件属性 | /WorkBook/Report/CellElementList/C//HighlightList |
| 图表单元格 | /WorkBook/Report/CellElementList/C/O[@t='CC'] |
| 模板 ID | /WorkBook/TemplateIdAttMark/TemplateIdAttMark/@TemplateId |
| JS 监听器 | /WorkBook/Report/CellElementList/C//Listener/@event |

---

*本文档基于 240 个官方 demo cpt 实测整理；凡与旧标签字典不一致处，以本文为准并已标注【修正】。*
