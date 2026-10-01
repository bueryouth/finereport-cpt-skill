# -*- coding: utf-8 -*-
"""
cpt_schema.py — FineReport 11.0 .cpt 结构常量（纯数据模块）

本模块只放从 `E:\\mis-workspace\\08-fanruan\\finereport-build\\scratch\\demo-structure.md`
（以下简称“结构权威”）逐字提炼的白名单常量，供 generate_cpt.py（生成）与
validate_cpt.py（校验）共同引用，保证生成端与校验端口径一致。

所有取值均来自真实 demo（D:\\FineReport_11.0\\...\\reportlets\\demo，240 个 .cpt），
不是凭空设计。每条常量注释里标注了结构权威文档中的出处小节。

禁止依赖任何第三方库，仅用标准库。
"""

# ---------------------------------------------------------------------------
# 1. 文件级硬性约定（结构权威 §0 / §1.1 / §16）
# ---------------------------------------------------------------------------

# XML 声明行：240 个 demo 文件全部一致（§0 表格）。
XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'

# 文件编码事实（§0）：无 BOM、LF 换行、无 DOCTYPE、标签顶格零缩进。
FILE_HAS_BOM = False          # 全部 240 个 .cpt 均无 UTF-8 BOM
FILE_LINE_ENDING = "\n"       # 全部为 LF（0A），无 CRLF
FILE_HAS_DOCTYPE = False      # 0 个含 <!DOCTYPE
FILE_ZERO_INDENT = True       # 每个标签顶格写，无前导空格缩进

# ---------------------------------------------------------------------------
# 2. 根节点 <WorkBook> 与必需属性（§1.1 / §2.1 / §14）
# ---------------------------------------------------------------------------

ROOT_TAG = "WorkBook"         # 根节点是 <WorkBook>，不是 <Report>（§16 差异#1）

# xmlVersion = 模板格式版本号（字符串日期）；releaseVersion = 产品版本。
# 取值直接抄 §1.1 真实文件头 NewbieGuide/分组报表.cpt。
WB_XML_VERSION = "20170720"
WB_RELEASE_VERSION = "11.0.0"

# <WorkBook> 必须具备的属性（§1.1）。
WORKBOOK_REQUIRED_ATTRS = ("xmlVersion", "releaseVersion")

# Report（sheet）节点的 class 与默认 name（§2.1 / §14）。
REPORT_CLASS = "com.fr.report.worksheet.WorkSheet"
REPORT_DEFAULT_NAME = "sheet1"

# ---------------------------------------------------------------------------
# 3. WorkBook 下一级子节点顺序（结构权威 §2.1 / §14 骨架 / utools §3.3 规则③）
#    节点顺序敏感：TableDataMap → Report → ReportParameterAttr → StyleList → AttrMark
# ---------------------------------------------------------------------------
TOP_LEVEL_ORDER = (
    "TableDataMap",           # 数据集注册表（§2.1 / §14）
    "Report",                 # sheet 主体（唯一）
    "ReportParameterAttr",    # 报表参数 + 参数面板
    "StyleList",              # 命名样式表
    "DesignerVersion",        # 尾部属性标记开始
    "PreviewType",
    "TemplateThemeAttrMark",
    "StrategyConfigsAttr",
    "TemplateIdAttMark",      # 模板 UUID
    "TemplateCloudInfoAttrMark",  # 可选，§2.1 骨架中出现
)

# AttrMark 尾部必需项（§2.1 / §14 最小骨架第 8 项）。
# DesignerVersion / PreviewType / TemplateIdAttMark 必须存在；
# TemplateIdAttMark 的 TemplateId 需为随机 UUID。
ATTMARK_REQUIRED = ("DesignerVersion", "PreviewType", "TemplateIdAttMark")

# DesignerVersion 取值（§2.1）：与 releaseVersion 对应的设计器混淆编码。
# 11.0.0 对应 "LAA"（§14 真实取值）。
DESIGNER_VERSION = "LAA"

# PreviewType（§2.1 / utools dict）：0=普通/分页预览，1=填报预览，2=数据分析。
PREVIEW_TYPE_NORMAL = "0"
PREVIEW_TYPE_WRITE = "1"

# ---------------------------------------------------------------------------
# 4. 数据集 TableData class 白名单（§3.3 / §16 差异#6 + digest §3.5/§8）
#    demo 中只出现两种；EmbeddedTableData 的 RowData 是压缩二进制（§3.2），
#    手工造不出真实行数据，只能产出空壳。
#    digest §8/§3.5 补充 ClassTableData(Java类) 与 RecursionTableData(递归树)。
# ---------------------------------------------------------------------------
TABLEDATA_CLASSES = frozenset({
    "com.fr.data.impl.DBTableData",           # SQL 查询数据集（§3.1）
    "com.fr.data.impl.EmbeddedTableData",     # 内嵌数据集（§3.2）
    "com.fr.data.impl.NameTableData",         # 服务器数据集引用（utools dict 3.2）
    "com.fr.data.impl.ClassTableData",        # Java 类数据集（digest §8）
    "com.fr.data.impl.RecursionTableData",    # 递归树数据集（digest §3.5）
})

# DBTableData 的连接 class（§3.1 真实写法）。
CONNECTION_CLASS = "com.fr.data.impl.NameDatabaseConnection"

# ---------------------------------------------------------------------------
# 5. 单元格值 <O> 的 t 属性白名单（§5.2）
#    空字符串表示“无 t”= 纯文本 CDATA。
# ---------------------------------------------------------------------------
O_T_WHITELIST = frozenset({
    "",                       # 纯文本 CDATA（§5.2）
    "DSColumn",               # 数据集列绑定（§5.1/§5.3）
    "Formula",                # 公式老写法 class="Formula"（§7.4 / §16#15）
    "XMLable",                # 公式新写法 class="com.fr.base.Formula"（§7.1）
    "BiasTextPainter",        # 斜线表头（§5.5）
    "B",                      # 布尔值（§4.3.5）
    "Date",                   # 日期 epoch 毫秒（§4.3.3）
    "CC",                     # 图表单元格（§12.1 / §16#8）
    "I",                      # 整数（utools §2.5/§2.11 解析到 t="I"）
})

# <O t="XMLable"> 公式节点必须配的 class（§7.1 新写法）。
FORMULA_CLASS = "com.fr.base.Formula"

# DSColumn 的分组器 class（§5.3）。
GROUPER_FUNCTION = "com.fr.report.cell.cellattr.core.group.FunctionGrouper"   # 普通分组
GROUPER_SUMMARY = "com.fr.report.cell.cellattr.core.group.SummaryGrouper"      # 汇总分组

# 汇总函数全限定名（§5.3 FN）。
SUMMARY_FUNCTIONS = {
    "sum": "com.fr.data.util.function.SumFunction",
    "avg": "com.fr.data.util.function.AverageFunction",
    "count": "com.fr.data.util.function.CountFunction",
    "max": "com.fr.data.util.function.MaxFunction",
    "min": "com.fr.data.util.function.MinFunction",
}

# Expand 扩展方向（§5.4）：dir=0 纵向向下，dir=1 横向向右，不写=不扩展。
EXPAND_DIR_NONE = None
EXPAND_DIR_DOWN = "0"
EXPAND_DIR_RIGHT = "1"

# ---------------------------------------------------------------------------
# 6. 控件 widget class 前缀白名单（§4.3 真实控件清单）
# ---------------------------------------------------------------------------
WIDGET_CLASS_PREFIXES = (
    "com.fr.form.ui.",             # 绝大多数单元格/面板控件
    "com.fr.form.parameter.",      # 参数面板提交按钮 FormSubmitButton
    "com.fr.form.main.parameter.", # 参数面板容器 FormParameterUI（§4.2）
    "com.fr.form.ui.container.",   # WParameterLayout / WAbsoluteLayout$BoundsWidget（§4.2）
)

# 常见控件 class 全名映射（§4.3 表格），供生成器把规格里的短类型名映射成全限定名。
WIDGET_CLASSES = {
    "button": "com.fr.form.ui.FreeButton",            # 单元格按钮
    "checkbox": "com.fr.form.ui.CheckBox",           # 复选框
    "text": "com.fr.form.ui.TextEditor",             # 文本框
    "number": "com.fr.form.ui.NumberEditor",          # 数字框
    "combo": "com.fr.form.ui.ComboBox",              # 下拉框
    "radio": "com.fr.form.ui.RadioGroup",             # 单选组
    "combocheck": "com.fr.form.ui.ComboCheckBox",     # 下拉复选
    "date": "com.fr.form.ui.DateEditor",             # 日期
    "treedown": "com.fr.form.ui.TreeComboBoxEditor", # 下拉树
    "label": "com.fr.form.ui.Label",                  # 标签
    "iframe": "com.fr.form.ui.IframeEditor",         # 网页框
    "submit": "com.fr.form.parameter.FormSubmitButton",  # 参数面板查询按钮
}

# JS 事件名（§8.2 grep 全量）。
JS_EVENTS = frozenset({
    "afterinit", "click", "statechange", "afteredit",
    "beforeimportexcel", "startload", "afterload", "beforeload",
})

# ---------------------------------------------------------------------------
# 7. 图表 class 前缀与 Plot 映射（§12）
# ---------------------------------------------------------------------------
CHART_CLASS_PREFIXES = (
    "com.fr.chart.",               # 旧版普通图表
    "com.fr.plugin.chart.",        # VanChart 插件化图表（§12.2）
)

CHART_ROOT_CLASS = "com.fr.plugin.chart.vanchart.VanChart"   # §12.1

# 规格里的图表类型 → (Plot class, wrapperName)（§12.2 表格）。
CHART_PLOT_MAP = {
    "pie":  ("com.fr.plugin.chart.PiePlot4VanChart", "RosePieChart"),
    "bar":  ("com.fr.plugin.chart.column.VanChartColumnPlot", "ColumnChart"),
    "line": ("com.fr.plugin.chart.line.VanChartLinePlot", "LineChart"),
    "area": ("com.fr.plugin.chart.area.VanChartAreaPlot", "AreaChart"),
}

# ---------------------------------------------------------------------------
# 8. 填报提交（§11.1 / utools §2.9）
# ---------------------------------------------------------------------------
SUBMIT_BUILTIN = "com.fr.report.write.BuiltInSQLSubmiter"   # 内置 SQL 提交（§11.1）
SUBMIT_WCLASS = "com.fr.report.write.WClassSubmiter"        # 自定义 Java 类提交（utools §2.9）
DML_INTELLI = "com.fr.write.config.IntelliDMLConfig"        # 智能提交（按主键增改）
DML_CUSTOM = "com.fr.write.config.CustomDMLConfig"          # 自定义 DML

# ---------------------------------------------------------------------------
# 9. 工具栏内置按钮映射（§10.1 真实片段 / utools §4 BTN_MAP）
# ---------------------------------------------------------------------------
TOOLBAR_BUTTONS = {
    # 短名: (class, iconName, text)
    "submit": ("com.fr.report.web.button.write.Submit", "submit",
               "${i18n('Fine-Engine_Report_Utils_Submit')}"),
    "verify": ("com.fr.report.web.button.write.Verify", "verify",
               "${i18n('Fine-Engine_Report_Verify_Data')}"),
    "append": ("com.fr.report.web.button.write.AppendColumnRow", "append",
               "${i18n('Fine-Engine_Add_Record')}"),
    "delete": ("com.fr.report.web.button.write.DeleteRowButton", "delete",
               "${i18n('Fine-Engine_Delete_Record')}"),
}

# ---------------------------------------------------------------------------
# 10. 样式默认值（§6.1 / §2.2 EMU）
# ---------------------------------------------------------------------------
# 行高默认 EMU（§2.2：723900 ≈ 0.8cm）。
DEFAULT_ROW_HEIGHT = "723900"
# 列宽默认 EMU（§2.2：2743200 ≈ 3.2cm / 3 英寸）。
DEFAULT_COL_WIDTH = "2743200"

# 水平对齐（§6.1）：0=左、2=居中、4=右。
HALIGN_LEFT = "0"
HALIGN_CENTER = "2"
HALIGN_RIGHT = "4"

# FRFont style（§6.1）：0=常规、1=加粗；size 单位半磅（size=120 → 15pt）。
FONT_STYLE_NORMAL = "0"
FONT_STYLE_BOLD = "1"

# 颜色 int 编码（§6.1 / §16#14）：白=-1，黑=-16777216。
COLOR_WHITE = "-1"
COLOR_BLACK = "-16777216"

# ---------------------------------------------------------------------------
# 11. 移植自相关项目 A（check_cpt.py）的可靠静态校验规则常量
#     来源：related-projects-digest.md 第 4 节
# ---------------------------------------------------------------------------

# 参数面板布局容器：真实控件必须包在它里面（digest §3.2 / §4 规则6）。
BOUNDS_WIDGET_CLASS = "com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget"
# 查询按钮 class（digest §4 规则7：有 SQL 参数时面板必须有一个）。
FORM_SUBMIT_BUTTON_CLASS = "com.fr.form.parameter.FormSubmitButton"

# 校验：allowBlank 必须是独立子节点，写成这些 *Attr 节点上的属性即失效（digest §4 规则8）。
ALLOWBLANK_ATTR_TAGS = frozenset({
    "DateAttr", "TextAttr", "NumberAttr", "TreeAttr",
})

# 不允许出现的属性：textStyle 设计器不输出，写了靠不住（digest §4 规则14）。
FORBIDDEN_ATTR_NAMES = frozenset({"textStyle"})

# DBTableData 必须具备 DatabaseName 子节点（digest §4 规则2 的可靠部分）。
# 注：项目 A 的“不得残留 FRDemo”是其生产环境规则，本技能包开发库就是 FRDemo，
# 故只校验 DatabaseName 存在，不校验具体连接名。
REQUIRED_DB_CHILD = "DatabaseName"

