# -*- coding: utf-8 -*-
"""
generate_cpt.py — FineReport 11.0 .cpt 报表生成器（CLI）

用法：
    python generate_cpt.py <spec.json> [输出.cpt路径]
    缺省输出路径时，按 spec.meta.name 生成到 spec 同目录。

设计要点（严格对齐结构权威 demo-structure.md）：
  * 字符串拼接 XML，不用 ElementTree 序列化（因为 ET 不产生 CDATA、缩进不可控）。
  * 输出：<?xml version="1.0" encoding="UTF-8"?> + 顶格零缩进 + LF + UTF-8 无 BOM。
  * 用户可见文本 / SQL / 公式 / JS 一律 CDATA 包裹。
  * class 属性一律 Java 全限定名。

零第三方依赖，仅标准库 json / uuid / pathlib / sys / os。
"""

import json
import re
import sys
import uuid
from pathlib import Path

import cpt_schema as S


# ===========================================================================
# 转义 helper（任务硬性要求）
# ===========================================================================
def esc_attr(v):
    """属性值转义：& < > " '  → 实体。"""
    if v is None:
        return ""
    s = str(v)
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", "&apos;")
    return s


def esc_text(v):
    """文本节点转义：& < >（属性里的引号不出现）。"""
    if v is None:
        return ""
    s = str(v)
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s


def cdata(v):
    """包 CDATA；正文若含 ]]> 必须拆段，否则会截断 CDATA。
    拆法：把 ]]> 切成  ]]]]><![CDATA[>]]>  还原后仍是 ]]>。
    """
    s = "" if v is None else str(v)
    parts = s.split("]]>")
    return "<![CDATA[" + "]]]]><![CDATA[>]]>".join(parts) + "]]>"


def a_equals(attr_dict):
    """把 {attr: value} 拼成 ' k="v" k2="v2"'，值已 esc_attr。None 值跳过。"""
    out = ""
    for k, v in attr_dict.items():
        if v is None or v == "":
            continue
        out += ' %s="%s"' % (k, esc_attr(v))
    return out


def a1(c, r):
    """0 基列/行 → A1 风格引用（列字母+1 基行号），用于 left/up 父格。"""
    col = ""
    n = int(c)
    while True:
        col = chr(65 + (n % 26)) + col
        n = n // 26 - 1
        if n < 0:
            break
    return "%s%d" % (col, int(r) + 1)


def _sql_param_refs(sql):
    """抽取 SQL 中 ${name} 引用的参数名（去重保序）。"""
    return re.findall(r"\$\{\s*([A-Za-z_一-龥][\w一-龥]*)\s*\}", sql or "")


# ===========================================================================
# 数据集
# ===========================================================================
def build_dataset_params(params):
    """数据集参数：<Parameters><Parameter><Attributes name=x/><O>CDATA</O></Parameter>..."""
    if not params:
        return "<Parameters/>"
    items = []
    for p in params:
        items.append(
            "<Parameter><Attributes name=\"%s\"/>%s</Parameter>"
            % (esc_attr(p["name"]), cdata(p.get("defaultValue", "")))
        )
    return "<Parameters>" + "".join(items) + "</Parameters>"


def build_dataset(ds):
    name = ds["name"]
    dtype = ds.get("type", "sql")
    if dtype == "sql":
        cls = "com.fr.data.impl.DBTableData"
        inner = [
            build_dataset_params(ds.get("params")),
            "<Attributes maxMemRowCount=\"-1\"/>",
            "<Connection class=\"%s\"><DatabaseName>%s</DatabaseName></Connection>"
            % (S.CONNECTION_CLASS, cdata(ds.get("connection", "FRDemo"))),
            "<Query>%s</Query>" % cdata(ds.get("sql", "")),
            "<PageQuery>%s</PageQuery>" % cdata(ds.get("pageQuery", "")),
        ]
        return '<TableData name="%s" class="%s">%s</TableData>' % (
            esc_attr(name), cls, "".join(inner))
    elif dtype == "builtin":
        # 内嵌数据集：RowData 是 FineReport 专有压缩二进制（结构权威 §3.2），
        # 手工无法构造真实行数据。这里产出合法空壳，真实数据请用设计器回填。
        cls = "com.fr.data.impl.EmbeddedTableData"
        col_names = ",,.,,".join(ds.get("columns", []))
        col_types = ",".join(ds.get("columnTypes",
                                    ["java.lang.String"] * len(ds.get("columns", []))))
        inner = [
            build_dataset_params(ds.get("params")),
            "<DSName>%s</DSName>" % cdata(""),
            "<ColumnNames>%s</ColumnNames>" % cdata(col_names),
            "<ColumnTypes>%s</ColumnTypes>" % cdata(col_types),
            "<RowData ColumnTypes=\"%s\">%s</RowData>" % (esc_attr(col_types), cdata("")),
        ]
        return '<TableData name="%s" class="%s">%s</TableData>' % (
            esc_attr(name), cls, "".join(inner))
    elif dtype == "server":
        # 服务器数据集引用 NameTableData
        return ('<TableData name="%s" class="com.fr.data.impl.NameTableData">'
                '<Name>%s</Name></TableData>'
                % (esc_attr(name), cdata(ds.get("ref", name))))
    raise ValueError("unknown dataset type: %r" % dtype)


# ===========================================================================
# 报表参数（默认值 O）
# ===========================================================================
def build_param_value_o(p):
    """参数默认值：text→裸O，int→O t=I，formula→O t=XMLable class=Formula（§7/§2.11）。"""
    t = p.get("defaultType", "text")
    v = p.get("defaultValue", "")
    if t == "int":
        return '<O t="I">%s</O>' % cdata(v)
    if t == "formula":
        return ('<O t="XMLable" class="%s"><Attributes>%s</Attributes></O>'
                % (S.FORMULA_CLASS, cdata(v)))
    return "<O>%s</O>" % cdata(v)


def build_parameter_ui(params_with_widget):
    """参数面板控件容器 ParameterUI + WParameterLayout + 绝对定位（§4.2）。
    params_with_widget: [{"name","label","type","options","defaultValue"}]
    控件沿水平方向依次摆放，末尾放 FormSubmitButton 查询按钮。
    """
    if not params_with_widget:
        return ""
    widgets = []
    x = 10
    for p in params_with_widget:
        wcls = S.WIDGET_CLASSES.get(p.get("type", "text"))
        inner = ['<InnerWidget class="%s">' % esc_attr(wcls)]
        inner.append("<WidgetName name=\"%s\"/>" % esc_attr(p["name"]))
        if p.get("label"):
            inner.append("<LabelName name=\"%s\"/>" % esc_attr(p["label"]))
        # 下拉框/单选组：CustomDictionary 选项（§4.3.1/§4.3.2）
        if p.get("options"):
            dic = ['<Dictionary class="com.fr.data.impl.CustomDictionary"><CustomDictAttr>']
            for opt in p["options"]:
                if isinstance(opt, dict):
                    k, v = opt.get("key"), opt.get("value", opt.get("key"))
                else:
                    k = v = opt
                dic.append('<Dict key="%s" value="%s"/>' % (esc_attr(k), esc_attr(v)))
            dic.append("</CustomDictAttr></Dictionary>")
            inner.append("".join(dic))
        # 默认值
        inner.append("<widgetValue>%s</widgetValue>" % build_param_value_o(p))
        inner.append("</InnerWidget>")
        w = (
            '<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">'
            '%s'
            '<BoundsAttr x="%d" y="8" width="130" height="21"/>'
            '</Widget>' % ("".join(inner), x)
        )
        widgets.append(w)
        x += 150
    # 查询按钮（§4.2：class 固定 FormSubmitButton，热键 enter）
    widgets.append(
        '<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">'
        '<InnerWidget class="com.fr.form.parameter.FormSubmitButton">'
        '<WidgetName name="Search"/><Text>%s</Text><Hotkeys>%s</Hotkeys>'
        '</InnerWidget>'
        '<BoundsAttr x="%d" y="8" width="90" height="21"/>'
        '</Widget>' % (cdata("查询"), cdata("enter"), x)
    )
    width = x + 110
    return (
        '<ParameterUI class="com.fr.form.main.parameter.FormParameterUI">'
        '<Parameters/>'
        '<Layout class="com.fr.form.ui.container.WParameterLayout">'
        + "".join(widgets) +
        '<DesignAttr width="%d" height="36"/>'
        '</Layout></ParameterUI>' % width
    )


# ===========================================================================
# 样式
# ===========================================================================
def build_style(st):
    """命名样式（§6.1/§6.2）。st: {name,font,fontStyle,size,halign,bg,foreground,border,format}"""
    align = st.get("halign", S.HALIGN_LEFT)
    parts = ['<Style horizontal_alignment="%s" imageLayout="1">' % align]
    if st.get("format"):
        fcls = st.get("formatClass", "com.fr.base.CoreDecimalFormat")
        parts.append('<Format class="%s">%s</Format>' % (esc_attr(fcls), cdata(st["format"])))
    fname = st.get("font", "微软雅黑")
    fstyle = st.get("fontStyle", S.FONT_STYLE_NORMAL)
    size = st.get("size", "72")
    fg = st.get("foreground")
    fg_attr = (' foreground="%s"' % esc_attr(fg)) if fg else ""
    parts.append('<FRFont name="%s" style="%s" size="%s"%s/>'
                 % (esc_attr(fname), esc_attr(fstyle), esc_attr(size), fg_attr))
    if st.get("bg"):
        parts.append('<Background name="ColorBackground" color="%s"/>' % esc_attr(st["bg"]))
    else:
        parts.append('<Background name="NullBackground"/>')
    if st.get("border"):
        parts.append("<Border><Top style=\"1\"/><Bottom style=\"1\"/>"
                     "<Left style=\"1\"/><Right style=\"1\"/></Border>")
    else:
        parts.append("<Border/>")
    parts.append("</Style>")
    return "".join(parts)


# ===========================================================================
# 单元格内部值
# ===========================================================================
def build_o(cell):
    """根据 cell 规格生成 <O>...</O> 节点串。"""
    if "text" in cell:
        return "<O>%s</O>" % cdata(cell["text"])
    if "formula" in cell:
        return ('<O t="XMLable" class="%s"><Attributes>%s</Attributes></O>'
                % (S.FORMULA_CLASS, cdata(cell["formula"])))
    if "ds" in cell:
        d = cell["ds"]
        s = ['<O t="DSColumn"><Attributes dsName="%s" columnName="%s"/>'
             % (esc_attr(d["dsName"]), esc_attr(d["column"]))]
        s.append("<Complex/>")
        if d.get("summary"):
            fn = S.SUMMARY_FUNCTIONS.get(d["summary"], d["summary"])
            s.append('<RG class="%s"><FN>%s</FN></RG>'
                     % (S.GROUPER_SUMMARY, cdata(fn)))
        else:
            s.append('<RG class="%s"/>' % S.GROUPER_FUNCTION)
        s.append("<Parameters/></O>")
        return "".join(s)
    if cell.get("t") == "b":
        return '<O t="B">%s</O>' % cdata(str(cell.get("value", "false")).lower())
    if cell.get("t") == "date":
        return '<O t="Date">%s</O>' % cdata(cell.get("value", ""))
    return "<O/>"


def build_widget(cell):
    """单元格控件（§4.3.5）。cell.widget = {type,name,listeners}"""
    w = cell["widget"]
    wcls = S.WIDGET_CLASSES.get(w.get("type", "text"))
    s = ['<Widget class="%s">' % esc_attr(wcls)]
    # JS 事件 Listener（§8.1）
    for ev in w.get("listeners", []):
        s.append(
            '<Listener event="%s"><JavaScript class="com.fr.js.JavaScriptImpl">'
            '<Parameters/><Content>%s</Content></JavaScript></Listener>'
            % (esc_attr(ev["event"]), cdata(ev["js"]))
        )
    s.append('<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="0.0" description="">'
             '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false"/>'
             '<PrivilegeControl/></WidgetAttr>')
    s.append("<WidgetName name=\"%s\"/>" % esc_attr(w.get("name", "widget")))
    if w.get("text") is not None:
        s.append("<Text>%s</Text>" % cdata(w.get("text", "")))
    if w.get("defaultValue") is not None:
        s.append("<widgetValue>%s</widgetValue>" % build_param_value_o(
            {"defaultValue": w["defaultValue"], "defaultType": w.get("defaultType", "text")}))
    s.append("</Widget>")
    return "".join(s)


def build_hyperlink(cell):
    """超链接（§9）。cell.hyperlink = {type:report|web, name, reportlet|url, params:[{name,formula}]}"""
    h = cell["hyperlink"]
    if h.get("type", "report") == "web":
        inner_cls = "com.fr.js.WebHyperlink"
        body = "<URL>%s</URL>" % cdata(h.get("url", ""))
    else:
        inner_cls = "com.fr.js.ReportletHyperlink"
        params = []
        for p in h.get("params", []):
            params.append(
                '<Parameter><Attributes name="%s"/>'
                '<O t="XMLable" class="%s"><Attributes>%s</Attributes></O></Parameter>'
                % (esc_attr(p["name"]), S.FORMULA_CLASS, cdata(p.get("formula", "=$$$")))
            )
        body = ('<Parameters>%s</Parameters>'
                '<ReportletName showPI="true">%s</ReportletName>'
                % ("".join(params), cdata(h.get("reportlet", ""))))
    return (
        '<NameJavaScriptGroup><NameJavaScript name="%s">'
        '<JavaScript class="%s"><JavaScript class="%s">'
        '<TargetFrame>%s</TargetFrame><Features width="600" height="400"/>%s'
        '</JavaScript></JavaScript></NameJavaScript></NameJavaScriptGroup>'
        % (esc_attr(h.get("name", "链接")), inner_cls, inner_cls,
           cdata(h.get("target", "_blank")), body)
    )


def build_expand(cell):
    """<Expand> 节点（§5.4）。dir:0下/1右；left/up 自动转 A1。"""
    attrs = {}
    if "dir" in cell and cell["dir"] is not None:
        attrs["dir"] = str(cell["dir"])
    if cell.get("leftParent"):
        attrs["leftParentDefault"] = "false"
        attrs["left"] = cell["leftParent"]
    if cell.get("upParent"):
        attrs["upParentDefault"] = "false"
        attrs["up"] = cell["upParent"]
    if not attrs:
        return "<Expand/>"
    return "<Expand%s/>" % a_equals(attrs)


def build_cell(cell, style_index):
    """生成一个 <C ...>...</C>。带 rawC 时整段透传。"""
    if cell.get("rawC"):
        return cell["rawC"]
    attrs = {"c": cell["c"], "r": cell["r"]}
    merge = cell.get("merge", {})
    if merge.get("cs"):
        attrs["cs"] = merge["cs"]
    if merge.get("rs"):
        attrs["rs"] = merge["rs"]
    attrs["s"] = style_index
    head = "<C%s>" % a_equals(attrs)

    if "chart" in cell:
        body = build_chart_o(cell["chart"]) + "<PrivilegeControl/>" + build_expand(cell)
    elif "widget" in cell:
        body = "<PrivilegeControl/>" + build_widget(cell)
        if cell.get("hyperlink"):
            body += build_hyperlink(cell)
        body += build_expand(cell)
    else:
        body = build_o(cell) + "<PrivilegeControl/>"
        if cell.get("hyperlink"):
            body += build_hyperlink(cell)
        body += build_expand(cell)
    return head + body + "</C>"


# ===========================================================================
# 图表（§12）
# ===========================================================================
def build_chart_o(ch):
    plot_cls, wrapper = S.CHART_PLOT_MAP.get(ch.get("type", "pie"),
                                             S.CHART_PLOT_MAP["pie"])
    title = ch.get("title", "")
    return (
        '<O t="CC"><LayoutAttr selectedIndex="0"/>'
        '<Chart name="默认" chartClass="%s">'
        '<Chart class="%s" wrapperName="%s" requiredJS="" chartImagePath="">'
        '<GI/><ChartAttr isJSDraw="true" isStyleGlobal="false"/>'
        '<Title4VanChart><Text>%s</Text></Title4VanChart>'
        '<Plot class="%s"/>'
        '<ChartDefinition>'
        '<OneValueCDDefinition seriesName="%s" valueName="%s" function="%s">'
        '<Top topCate="-1" topValue="-1" isDiscardOtherCate="false"/>'
        '<TableData class="com.fr.data.impl.NameTableData"><Name>%s</Name></TableData>'
        '<CategoryName value="%s"/>'
        '</OneValueCDDefinition>'
        '</ChartDefinition>'
        '</Chart>'
        '<tools hidden="true" sort="true" export="true" fullScreen="true"/>'
        '</Chart></O>'
        % (S.CHART_ROOT_CLASS, S.CHART_ROOT_CLASS, esc_attr(wrapper),
           cdata(title), esc_attr(plot_cls),
           esc_attr(ch.get("series", "")), esc_attr(ch.get("value", "")),
           esc_attr(S.SUMMARY_FUNCTIONS.get(ch.get("agg", "sum"), ch.get("agg", "sum"))),
           cdata(ch.get("dsName", "ds1")), esc_attr(ch.get("category", "")))
    )


# ===========================================================================
# 工具栏（§10.1）与自定义按钮
# ===========================================================================
def builtin_button_widget(key):
    cls, icon, text = S.TOOLBAR_BUTTONS[key]
    return (
        '<Widget class="%s">'
        '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="0.0" description="">'
        '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false"/>'
        '<PrivilegeControl/></WidgetAttr>'
        '<Text>%s</Text><Hotkeys>%s</Hotkeys><IconName>%s</IconName>'
        '</Widget>' % (esc_attr(cls), cdata(text), cdata(""), cdata(icon))
    )


def custom_button_widget(btn):
    return (
        '<Widget class="com.fr.form.ui.Button">'
        '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="0.0" description="">'
        '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false"/>'
        '<PrivilegeControl/></WidgetAttr>'
        '<WidgetName name="%s"/><Text>%s</Text>'
        '<JavaScript class="com.fr.js.JavaScriptImpl"><Parameters/><Content>%s</Content>'
        '</JavaScript></Widget>'
        % (esc_attr(btn.get("name", "btn")), cdata(btn.get("text", "按钮")),
           cdata(btn.get("js", "")))
    )


def build_report_web_attr(spec):
    """ReportWebAttr：工具栏 + 报表级 JS 事件。"""
    parts = ["<ReportWebAttr>"]
    # 报表级 JS 事件（afterload/beforeload）
    for ev_name, js in (spec.get("events") or {}).items():
        parts.append(
            '<JavaScript class="com.fr.js.JavaScriptImpl" event="%s">'
            '<Parameters/><Content>%s</Content></JavaScript>'
            % (esc_attr(ev_name), cdata(js))
        )
    toolbar = spec.get("toolbar") or {}
    buttons = list(toolbar.get("buttons") or [])
    if buttons or spec.get("buttons"):
        w = []
        for k in buttons:
            if k in S.TOOLBAR_BUTTONS:
                w.append(builtin_button_widget(k))
        for btn in spec.get("buttons", []):
            w.append(custom_button_widget(btn))
        content = "WebWriteContent" if spec.get("fill", {}).get("enabled") else "WebViewContent"
        parts.append(
            "<%s><ToolBars><ToolBarManager><Location><Embed position=\"1\"/></Location>"
            "<ToolBar>%s</ToolBar></ToolBarManager></ToolBars></%s>"
            % (content, "".join(w), content)
        )
    parts.append("</ReportWebAttr>")
    return "".join(parts)


# ===========================================================================
# 填报入库（§11.1 / utools §2.9）
# ===========================================================================
def column_source_xml(src):
    kind = src.get("kind", "cell")
    if kind == "cell":
        return '<ColumnRow column="%s" row="%s"/>' % (src["c"], src["r"])
    if kind == "formula":
        return ('<O t="XMLable" class="%s"><Attributes>%s</Attributes></O>'
                % (S.FORMULA_CLASS, cdata(src["value"])))
    if kind == "int":
        return '<O t="I">%s</O>' % cdata(src["value"])
    return "<O>%s</O>" % cdata(src.get("value", ""))   # text/常量


def build_report_write_attr(spec):
    fill = spec.get("fill") or {}
    if not fill.get("enabled"):
        return ""
    if fill.get("submitter") == "wclass":
        # 自定义 Java 类提交（utools §2.9）
        props = []
        for pr in fill.get("properties", []):
            props.append('<Property name="%s"><ColumnRow column="%s" row="%s"/></Property>'
                         % (esc_attr(pr["name"]), pr["c"], pr["r"]))
        return (
            '<ReportWriteAttr><SubmitVisitor class="%s">'
            '<Name>%s</Name>'
            '<SubmitTask class="com.fr.data.ClassSubmitJob">'
            '<ClassAttr className="%s"/>%s'
            '</SubmitTask></SubmitVisitor></ReportWriteAttr>'
            % (S.SUBMIT_WCLASS, cdata(fill.get("name", "自定义提交")),
               esc_attr(fill.get("customClass", "")), "".join(props))
        )
    # 内置 SQL 智能提交（§11.1）
    cols = []
    for c in fill.get("columns", []):
        cols.append(
            '<ColumnConfig name="%s" isKey="%s" skipUnmodified="false">%s</ColumnConfig>'
            % (esc_attr(c["name"]),
               "true" if c.get("isKey") else "false",
               column_source_xml(c.get("source", {"kind": "cell"})))
        )
    cond = ""
    if fill.get("conditionFormula"):
        cond = ('<Condition class="com.fr.data.condition.FormulaCondition">'
                '<Formula>%s</Formula></Condition>' % cdata(fill["conditionFormula"]))
    return (
        '<ReportWriteAttr><SubmitVisitor class="%s">'
        '<Name>%s</Name>'
        '<Attributes dsName="%s"/>'
        '<DMLConfig class="%s">'
        '<Table schema="%s" name="%s"/>'
        '%s%s'
        '</DMLConfig></SubmitVisitor></ReportWriteAttr>'
        % (S.SUBMIT_BUILTIN, cdata(fill.get("name", "内置SQL1")),
           esc_attr(fill.get("connection", "FRDemo")),
           S.DML_INTELLI, esc_attr(fill.get("schema", "")), esc_attr(fill.get("table", "")),
           "".join(cols), cond)
    )


# ===========================================================================
# 主拼装
# ===========================================================================
def build(spec):
    wb = spec.get("workbook", {})
    xml_version = wb.get("xmlVersion", S.WB_XML_VERSION)
    release = wb.get("releaseVersion", S.WB_RELEASE_VERSION)
    designer = wb.get("designerVersion", S.DESIGNER_VERSION)
    preview = wb.get("previewType", S.PREVIEW_TYPE_WRITE if spec.get("fill", {}).get("enabled")
                     else S.PREVIEW_TYPE_NORMAL)

    lines = [S.XML_DECLARATION]
    lines.append('<WorkBook xmlVersion="%s" releaseVersion="%s">'
                 % (esc_attr(xml_version), esc_attr(release)))

    # rawXml.workbookPrefix 逃生舱
    raw = spec.get("rawXml") or {}
    if raw.get("workbookPrefix"):
        lines.append(raw["workbookPrefix"])

    # --- TableDataMap ---
    # 参数一致性：让每个 SQL 数据集的 <Parameters> 自动覆盖其 SQL 里 ${name} 引用到、
    # 但未显式声明的报表级参数（默认值取自报表参数）。保证“数据集参数⊆报表级参数”。
    report_params = {p["name"]: p for p in spec.get("parameters", []) if "name" in p}
    for d in spec.get("datasets", []):
        if d.get("type", "sql") != "sql":
            continue
        declared = {pp.get("name") for pp in d.get("params", [])}
        for ref in _sql_param_refs(d.get("sql", "")):
            if ref not in declared and ref in report_params:
                rp = report_params[ref]
                d.setdefault("params", []).append({
                    "name": ref,
                    "defaultValue": rp.get("defaultValue", ""),
                })
    ds_xml = "".join(build_dataset(d) for d in spec.get("datasets", []))
    lines.append("<TableDataMap>" + ds_xml + "</TableDataMap>")

    # --- Report ---
    cells = spec.get("cells", [])
    styles = spec.get("styles", [])
    style_index = {st["name"]: i for i, st in enumerate(styles)}
    n_cols = max([int(c["c"]) for c in cells if "c" in c] + [0]) + 1
    n_rows = max([int(c["r"]) for c in cells if "r" in c] + [0]) + 1
    row_hds = ",".join([S.DEFAULT_ROW_HEIGHT] * n_rows)
    col_wds = ",".join([S.DEFAULT_COL_WIDTH] * n_cols)

    cell_xmls = []
    for c in cells:
        si = style_index.get(c.get("style", ""), 0)
        cell_xmls.append(build_cell(c, si))

    report = [
        '<Report class="%s" name="%s">' % (S.REPORT_CLASS, esc_attr(spec.get("sheetName", "sheet1"))),
        "<ReportPageAttr><HR/><FR/><HC/><FC/></ReportPageAttr>",
        "<ColumnPrivilegeControl/><RowPrivilegeControl/>",
        '<RowHeight defaultValue="%s">%s</RowHeight>' % (S.DEFAULT_ROW_HEIGHT, cdata(row_hds)),
        '<ColumnWidth defaultValue="%s">%s</ColumnWidth>' % (S.DEFAULT_COL_WIDTH, cdata(col_wds)),
        "<CellElementList>" + "".join(cell_xmls) + "</CellElementList>",
        "<ReportAttrSet><ReportSettings headerHeight=\"0\" footerHeight=\"0\">"
        "<PaperSetting/><FollowingTheme background=\"false\"/>"
        '<Background name="ColorBackground"><color><FineColor color="-1" hor="-1" ver="-1"/></color></Background>'
        "</ReportSettings></ReportAttrSet>",
    ]
    web_attr = build_report_web_attr(spec)
    if web_attr:
        report.append(web_attr)
    write_attr = build_report_write_attr(spec)
    if write_attr:
        report.append(write_attr)
    if raw.get("reportSuffix"):
        report.append(raw["reportSuffix"])
    report.append("<PrivilegeControl/></Report>")
    lines.append("".join(report))

    # --- ReportParameterAttr ---
    params = spec.get("parameters", [])
    pxml = ['<ReportParameterAttr>'
            '<Attributes showWindow="true" delayPlaying="true" windowPosition="1" '
            'align="0" useParamsTemplate="true" currentIndex="0"/>'
            '<PWTitle>%s</PWTitle>' % cdata("参数")]
    pxml.append(build_parameter_ui([p for p in params if p.get("widget")]))
    for p in params:
        pxml.append("<Parameter><Attributes name=\"%s\"/>%s</Parameter>"
                    % (esc_attr(p["name"]), build_param_value_o(p)))
    pxml.append("</ReportParameterAttr>")
    lines.append("".join(pxml))

    # --- StyleList ---
    # 始终保证至少一个默认样式：单元格 s="0" 必须能落到 StyleList 内（digest §4 规则11）。
    eff_styles = styles if styles else [{}]
    lines.append("<StyleList>" + "".join(build_style(st) for st in eff_styles) + "</StyleList>")

    # --- AttrMark 尾部 ---
    lines.append('<DesignerVersion DesignerVersion="%s"/>' % esc_attr(designer))
    lines.append('<PreviewType PreviewType="%s"/>' % esc_attr(preview))
    lines.append(
        '<TemplateThemeAttrMark class="com.fr.base.iofile.attr.TemplateThemeAttrMark">'
        '<TemplateThemeAttrMark name="兼容" dark="false"/></TemplateThemeAttrMark>')
    lines.append(
        '<StrategyConfigsAttr class="com.fr.esd.core.strategy.persistence.StrategyConfigsAttr">'
        '<StrategyConfigs/></StrategyConfigsAttr>')
    lines.append(
        '<TemplateIdAttMark class="com.fr.base.iofile.attr.TemplateIdAttrMark">'
        '<TemplateIdAttMark TemplateId="%s"/></TemplateIdAttMark>' % str(uuid.uuid4()))

    if raw.get("workbookSuffix"):
        lines.append(raw["workbookSuffix"])

    lines.append("</WorkBook>")
    return S.FILE_LINE_ENDING.join(lines) + S.FILE_LINE_ENDING


def main(argv):
    if len(argv) < 2:
        print("usage: python generate_cpt.py <spec.json> [out.cpt]", file=sys.stderr)
        return 2
    spec_path = Path(argv[1])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    xml = build(spec)

    if len(argv) >= 3:
        out_path = Path(argv[2])
    else:
        name = (spec.get("meta") or {}).get("name") or spec_path.stem
        out_path = spec_path.parent / ("%s.cpt" % name)
    # UTF-8 无 BOM，newline='' 避免 Windows 上被转成 \r\n
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(xml)
    print("generated: %s (%d bytes)" % (out_path, len(xml.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
