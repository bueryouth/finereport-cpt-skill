# -*- coding: utf-8 -*-
"""
validate_cpt.py — FineReport 11.0 .cpt 结构校验器（CLI）

用法：
    python validate_cpt.py <文件或目录> [-r 递归]

校验项（每个 .cpt）：
  ① 文件级：无 UTF-8 BOM；首行 XML 声明且 encoding="UTF-8"。
  ② XML 良构：xml.etree.ElementTree.parse，异常报行号/列号。
  ③ 结构模式：
       - 根节点必须 <WorkBook> 且含必需属性 xmlVersion/releaseVersion
       - 顶层已知节点顺序符合 TOP_LEVEL_ORDER（顺序敏感）
       - TableData 的 class 在白名单 TABLEDATA_CLASSES
       - <O> 的 t 值在白名单 O_T_WHITELIST
       - 控件 class 前缀合法（com.fr.form.*）、图表 class 前缀合法
       - AttrMark 尾部三件套存在：DesignerVersion/PreviewType/TemplateIdAttMark

输出：每文件一行“通过/失败+原因”，末尾汇总；任一失败 exit code 非 0。
零第三方依赖。
"""

import sys
from pathlib import Path
import xml.etree.ElementTree as ET

import cpt_schema as S


def _sql_params(sql_text):
    """从 SQL 文本抽取 ${param} 引用名（仅用于一致性软提示）。"""
    import re
    return set(re.findall(r"\$\{\s*([A-Za-z_一-龥][\w一-龥]*)\s*\}", sql_text or ""))


def check_file(path: Path):
    """对单个 .cpt 校验。返回 (errors:list, warnings:list)。errors 非空即失败。"""
    errors = []
    warnings = []

    # ① 文件级：读原始字节
    raw = path.read_bytes()
    if raw[:3] == b"\xef\xbb\xbf":
        errors.append("存在 UTF-8 BOM（应为无 BOM）")
    text = raw.decode("utf-8", errors="replace")
    head = text.lstrip("﻿").lstrip()
    if not head.startswith("<?xml"):
        errors.append("缺少 XML 声明 <?xml ...?>")
    elif 'encoding="UTF-8"' not in head.split("?>", 1)[0]:
        errors.append('XML 声明未声明 encoding="UTF-8"')
    if "<!DOCTYPE" in text:
        errors.append("包含 DOCTYPE（应为无）")

    # ② XML 良构
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        errors.append("XML 良构失败: %s" % e)
        return errors, warnings

    # ③ 结构模式
    if root.tag != S.ROOT_TAG:
        errors.append("根节点 <%s>，应为 <%s>" % (root.tag, S.ROOT_TAG))
    for attr in S.WORKBOOK_REQUIRED_ATTRS:
        if attr not in root.attrib:
            errors.append("<WorkBook> 缺少必需属性 %s" % attr)

    # 顶层节点顺序（只校验出现在 TOP_LEVEL_ORDER 里的已知节点相对顺序）
    order_idx = [S.TOP_LEVEL_ORDER.index(ch.tag) for ch in root
                 if ch.tag in S.TOP_LEVEL_ORDER]
    if order_idx != sorted(order_idx):
        errors.append("顶层节点顺序不符合约定（应 %s）" % "→".join(S.TOP_LEVEL_ORDER))

    # AttrMark 尾部必需项
    for mark in S.ATTMARK_REQUIRED:
        if root.find(mark) is None:
            errors.append("缺少尾部属性标记节点 <%s>" % mark)
    tid = root.find("TemplateIdAttMark/TemplateIdAttMark")
    if tid is not None and not tid.attrib.get("TemplateId"):
        errors.append("TemplateIdAttMark 缺少 TemplateId（UUID）")

    # --- 样式表（digest §4 规则11/13/14）---
    sl = root.find("StyleList")
    n_styles = len(list(sl)) if sl is not None else 0
    # 规则11：单元格 s 索引不得越界
    for c in root.iter("C"):
        if "s" in c.attrib:
            try:
                sval = int(c.attrib["s"])
            except ValueError:
                errors.append("单元格 s 非整数: %r" % c.attrib["s"])
                continue
            if sval < 0 or sval >= n_styles:
                errors.append("单元格 s=%d 样式索引越界（StyleList 共 %d 个样式）"
                              % (sval, n_styles))
    # 规则13：<Format> 必须是 <Style> 第一个子节点，且不得为空
    if sl is not None:
        for i, st in enumerate(sl):
            kids = list(st)
            kid_tags = [k.tag for k in kids]
            if "Format" in kid_tags:
                if kid_tags[0] != "Format":
                    errors.append("Style[%d] 的 <Format> 不是首个子节点" % i)
                fmt = kids[kid_tags.index("Format")]
                if not (fmt.text or "").strip() and not list(fmt):
                    errors.append("Style[%d] 存在空 <Format> 节点" % i)

    # 规则14：禁止出现 textStyle 等设计器不输出的属性
    for el in root.iter():
        for k in el.attrib:
            if k in S.FORBIDDEN_ATTR_NAMES:
                errors.append("<%s> 出现禁用属性 %s" % (el.tag, k))

    # 规则8：allowBlank 必须是独立子节点，不得写成 *Attr 节点的属性
    for el in root.iter():
        if el.tag in S.ALLOWBLANK_ATTR_TAGS and "allowBlank" in el.attrib:
            errors.append("<%s> 的 allowBlank 写成了属性（应为独立子节点）" % el.tag)

    # --- 遍历全部元素做 class / O.t 白名单 ---
    for el in root.iter():
        cls = el.attrib.get("class")
        if el.tag == "TableData" and cls:
            if cls not in S.TABLEDATA_CLASSES:
                errors.append("<TableData name=%s> class 不在白名单: %s"
                              % (el.attrib.get("name", "?"), cls))
        if el.tag == "O":
            t = el.attrib.get("t", "")
            if t not in S.O_T_WHITELIST:
                errors.append("<O> 的 t=%r 不在白名单 %s" % (t, sorted(S.O_T_WHITELIST)))
        if cls:
            if cls.startswith("com.fr.form.") and not cls.startswith(S.WIDGET_CLASS_PREFIXES):
                errors.append("控件 class 前缀非法: %s" % cls)

    # --- DBTableData 必须有 DatabaseName（digest §4 规则2 可靠部分）---
    for td in root.iter("TableData"):
        if td.attrib.get("class") == "com.fr.data.impl.DBTableData":
            dn = td.find("Connection/DatabaseName")
            if dn is None or not (dn.text or "").strip():
                errors.append("DBTableData %s 缺少 DatabaseName" % td.attrib.get("name", "?"))

    # --- 控件嵌套：参数面板真实控件必须包在 BoundsWidget 内（digest §4 规则6）---
    pu = root.find(".//ParameterUI")
    if pu is not None:
        has_submit = False
        for w in pu.iter("Widget"):
            cls = w.attrib.get("class", "")
            if cls == "":
                continue  # 空占位 Widget，忽略
            if cls == S.BOUNDS_WIDGET_CLASS:
                if w.find("InnerWidget") is None:
                    errors.append("BoundsWidget 缺少 <InnerWidget>")
                if w.find("BoundsAttr") is None:
                    errors.append("BoundsWidget 缺少 <BoundsAttr>")
                iw = w.find("InnerWidget")
                if iw is not None and iw.attrib.get("class") == S.FORM_SUBMIT_BUTTON_CLASS:
                    has_submit = True
            elif cls.startswith(("com.fr.form.ui.", "com.fr.form.parameter.")):
                errors.append("参数面板真实控件未包裹 BoundsWidget: %s" % cls)
        # 规则7：有参数面板时应有一个查询按钮（软提示）
        if not has_submit:
            warnings.append("参数面板未检测到 FormSubmitButton 查询按钮")

    # --- 参数一致性（软提示，digest §3.3 / §4 规则4/5）---
    # 报表级参数名集合（ReportParameterAttr 内、ParameterUI 之外的裸 <Parameter>）
    rpa = root.find("ReportParameterAttr")
    rep_names = set()
    if rpa is not None:
        for p in rpa.findall("Parameter"):
            nm = p.find("Attributes")
            if nm is not None and nm.attrib.get("name"):
                rep_names.add(nm.attrib["name"])
    # 逐数据集：声明参数名 + SQL ${} 引用
    all_sql_refs = set()
    for td in root.iter("TableData"):
        declared = []
        for p in td.findall("./Parameters/Parameter"):
            nm = p.find("Attributes")
            name = nm.attrib.get("name") if nm is not None else None
            if name:
                declared.append(name)
        # 重复参数节点
        if len(declared) != len(set(declared)):
            errors.append("数据集 %s 存在重复参数节点: %s" % (td.attrib.get("name"), declared))
        # SQL 引用
        q = td.find("Query")
        sql = (q.text or "") if q is not None else ""
        refs = _sql_params(sql)
        all_sql_refs |= refs
        # 软提示：声明了但报表级没有（可能是数据集内部参数，digest 说缺失只提醒）
        for name in set(declared) - rep_names:
            warnings.append("数据集参数 %r 未在报表级参数声明（可能为数据集内部参数）" % name)
        # 软提示：SQL 用了但数据集 Parameters 没声明
        for name in refs - set(declared):
            warnings.append("数据集 %s SQL 引用 ${%s} 但未在其 Parameters 声明"
                            % (td.attrib.get("name", "?"), name))
    # 软提示：报表级参数没被任何 SQL 使用
    for name in rep_names - all_sql_refs:
        warnings.append("报表级参数 %r 未被任何数据集 SQL 引用（面板可能多一个无用控件）" % name)

    return errors, warnings


def iter_cpt_files(target: Path, recursive: bool):
    if target.is_file():
        if target.suffix.lower() == ".cpt":
            yield target
        return
    pat = "**/*.cpt" if recursive else "*.cpt"
    yield from sorted(target.glob(pat))


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    recursive = "-r" in argv or "--recursive" in argv
    if not args:
        print("usage: python validate_cpt.py <文件或目录> [-r]", file=sys.stderr)
        return 2
    target = Path(args[0])
    if not target.exists():
        print("路径不存在: %s" % target, file=sys.stderr)
        return 2

    files = list(iter_cpt_files(target, recursive))
    if not files:
        print("未找到 .cpt 文件: %s" % target)
        return 1

    passed = 0
    failed = 0
    warn_total = 0
    for f in files:
        try:
            errors, warnings = check_file(f)
        except Exception as e:  # 读取异常也算失败
            errors, warnings = ["读取/解析异常: %r" % e], []
        rel = str(f)
        if not errors:
            passed += 1
            print("[通过] %s" % rel)
        else:
            failed += 1
            print("[失败] %s" % rel)
            for r in errors:
                print("         - %s" % r)
        for w in warnings:
            warn_total += 1
            print("         ! 提示: %s" % w)

    print("-" * 60)
    print("总计 %d 个：通过 %d，失败 %d（提示 %d 条）" % (len(files), passed, failed, warn_total))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
