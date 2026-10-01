# FineReport 11 · CPT 技能包独立验收报告（终版 · 整合后复验）

> **本报告为两轮整合后的复验终版**，覆盖首次验收。首验曾有 1 项失败（04_图表报表.cpt 缺 TemplateIdAttMark），本轮已修复并复跑全部检查。

- 验收对象：`C:\Users\Administrator\skills\finereport-cpt-skill\`
- 验收方式：只读校验 + 独立运行（未修改技能包内任何文件）
- 验收环境：Windows / Python 3.14.7 / pyyaml 6.0.3
- 复验时间：2026-10-01（整合后）

本轮整合点（据验收方实际核对）：①04 补尾部三件套；②validate_cpt.py/cpt_schema.py 升级（新增样式索引越界、Format 首位、textStyle 禁用、allowBlank 子节点、BoundsWidget 嵌套、DBTableData 需 DatabaseName、数据集参数不重名等规则，白名单扩 ClassTableData/RecursionTableData）；③生成器修复并重生成 4 个 out_*.cpt；④references 新增 related-projects.md，cpt-structure.md 修正对齐值等 5 处，SKILL.md 新增"关联项目参考"节与 3 条坑。

---

## ① 文件清单核对

| 期望位置 | 文件 | 存在 | 备注 |
|---|---|:--:|---|
| 根目录 | SKILL.md | 是 | 11774 B（新增关联项目节+3 坑） |
| scripts\ | cpt_schema.py | 是 | 12396 B（升级） |
| scripts\ | generate_cpt.py | 是 | 27783 B（修复 InnerWidget 等） |
| scripts\ | validate_cpt.py | 是 | 10759 B（新增大半规则） |
| references\ | cpt-structure.md | 是 | 40927 B（修正对齐值等 5 处） |
| references\ | feature-catalog.md | 是 | 15873 B |
| references\ | features.md | 是 | 14574 B |
| references\ | generator-guide.md | 是 | 12378 B |
| references\ | related-projects.md | 是 | **新增** 8455 B |
| assets\templates\ | 01~08 共 8 个 .cpt | 是 | 04 增至 19994 B（尾部修复） |
| assets\templates\ | 模板说明.md | 是 | 12319 B |
| assets\examples\ | spec_01~04 json（4 个） | 是 | |
| assets\examples\ | out_01~04 cpt（4 个） | 是 | out_02/out_04 已重生成 |

**结论：清单全部齐全。** references 由 4 份增至 5 份；共 12 个 .cpt（模板 8 + 样例产物 4）。

---

## ② 全量 cpt 校验（validate_cpt.py -r 递归）

命令：`python scripts\validate_cpt.py <技能包根> -r`（exit code = 0）

| # | 文件 | 结果 | 备注 |
|---|---|:--:|---|
| 1 | assets\examples\out_01_基础查询.cpt | 通过 | 提示：报表级参数'地区'未被数据集 SQL 引用 |
| 2 | assets\examples\out_02_参数联动.cpt | 通过 | 提示：'城市'/'渠道'参数未被 SQL 引用 |
| 3 | assets\examples\out_03_填报入库.cpt | 通过 | — |
| 4 | assets\examples\out_04_图表.cpt | 通过 | — |
| 5 | assets\templates\01_基础查询报表.cpt | 通过 | 提示：'地区'参数未被 SQL 引用 |
| 6 | assets\templates\02_参数联动报表.cpt | 通过 | 提示：数据集参数 layer1/layer2 未在报表级声明；'运输方式'未被 SQL 引用 |
| 7 | assets\templates\03_填报入库报表.cpt | 通过 | — |
| 8 | assets\templates\04_图表报表.cpt | 通过 | **首验失败项已修复**：尾部现含 TemplateIdAttMark |
| 9 | assets\templates\05_按钮JS事件报表.cpt | 通过 | — |
| 10 | assets\templates\06_样式定制报表.cpt | 通过 | — |
| 11 | assets\templates\07_脚本报表.cpt | 通过 | 提示：'p' 参数未被 SQL 引用 |
| 12 | assets\templates\08_Java自定义函数报表.cpt | 通过 | 提示：'地区'参数未被 SQL 引用 |

**汇总：总计 12 个，通过 12，失败 0（提示 10 条，均为非阻断性软提示——参数使用情况提醒，文件仍判 [通过]）。** 升级后的新规则（参数引用/重名检查）已实际生效并产出上述提示。

---

## ③ 独立抽查（自写 stdlib 代码，4 文件 × 5 项）

| 文件 | ①ET.parse | ②根=WorkBook 且含 xmlVersion/releaseVersion | ③无 BOM + encoding=UTF-8 | ④纯 LF 无 CRLF | ⑤关键能力标记 |
|---|:--:|:--:|:--:|:--:|---|
| 03_填报入库报表.cpt | 通过 | 通过 | 通过（首字节 3c3f78） | 通过 | BuiltInSQLSubmiter：存在 |
| 04_图表报表.cpt | 通过 | 通过 | 通过（首字节 3c3f78） | 通过 | VanChart：存在；Plot：存在 |
| 05_按钮JS事件报表.cpt | 通过 | 通过 | 通过（首字节 3c3f78） | 通过 | afterload：存在（含 JavaScriptImpl 事件） |
| out_01_基础查询.cpt | 通过 | 通过 | 通过（首字节 3c3f78） | 通过 | StyleList：存在；公式单元格：存在（com.fr.base.Formula，=B3/SUM(B3)、=SUM(B3)） |

**结论：20 项全部通过。**

---

## ④ SKILL.md quick_validate 合规校验

命令：`python "...\skill-creator-for-work\scripts\quick_validate.py" "...\finereport-cpt-skill"`

输出：`Skill is valid!`（exit code = 0）

**结论：通过。**

---

## ⑤ 引用完整性

### SKILL.md 正文引用（含本轮新增）

| 引用路径 | 存在 |
|---|:--:|
| references/generator-guide.md | 是 |
| scripts/generate_cpt.py / scripts/validate_cpt.py | 是 |
| assets/templates/、assets/templates/01_基础查询报表.cpt | 是 |
| references/cpt-structure.md / feature-catalog.md / features.md | 是 |
| references/related-projects.md（新增） | 是 |
| E:\mis-workspace\08-fanruan\report-cpt-skill\finereport-cpt-skill-main\（关联项目 A） | 是（目录存在） |
| E:\mis-workspace\08-fanruan\report-cpt-skill\fineReport-builder-main\（关联项目 B） | 是（目录存在） |

### features.md 九专题「模板引用」（复点）

脚本→07、JS→05、Java→08、入库→03、工具栏→03/05、按钮→05/02、事件→05、样式→06、公式→01/07，全部指向 assets\templates\ 下真实文件。

**结论：通过。** 两个外部关联项目目录经实测均存在（isdir=True）。

---

## ⑥ 覆盖矩阵核对（同前）

8 模板关键标记 grep：01 SummaryGrouper/Sum/Count/StyleList/DBTableData 全有；02 FormParameterUI/ComboBox/${layer1}/FormSubmitButton 全有（树形控件真实类名 TreeComboBoxEditor）；03 BuiltInSQLSubmiter/IntelliDMLConfig/ReportWriteAttr/Submit/Verify/DeleteRowButton/AppendRowButton 全有；04 VanChart/PiePlot/VanChartColumnPlot/ChartDefinition 全有；05 FreeButton/afterinit/click/statechange/afterload/WebHyperlink 全有；06 StyleList/FormulaCondition/两类 Highlight/yyyy-MM-dd/#0.00 全有；07 afterload/=NOW()/statechange/JavaScriptImpl 全有；08 MySum(=MySum(C2))/com.fr.base.Formula 全有。

**结论：与模板说明.md 覆盖矩阵一致。** 03 确含 BuiltInSQLSubmiter、08 确含 MySum 公式，均属实。

---

## ⑦ 编码抽查（cpt-structure.md / SKILL.md / related-projects.md）

| 文件 | UTF-8 严格解码 | BOM | U+FFFD |
|---|---|:--:|:--:|
| references\cpt-structure.md | OK | 无 | 0 |
| SKILL.md | OK | 无 | 0 |
| references\related-projects.md | OK | 无 | 0 |

**对齐修正已生效**：cpt-structure.md 中 `0=居中` 出现 3 处、`2=左` 2 处、`4=右` 3 处，`horizontal_alignment` 出现 5 处——原误写（0=左/2=居中/4=右）已更正为 0=居中/2=左/4=右。

---

## 总体结论（终版）

**全部通过，0 项失败。**

| 验收项 | 结果 |
|---|---|
| ① 文件清单 | 通过（含新增 related-projects.md，共 25 文件） |
| ② 全量 cpt 校验 | 通过：12/12（首验失败的 04 已修复；10 条为非阻断软提示） |
| ③ 独立抽查 | 通过：20/20 |
| ④ quick_validate | 通过：Skill is valid! |
| ⑤ 引用完整性 | 通过（含 related-projects.md 与两个关联项目目录，均存在） |
| ⑥ 覆盖矩阵 | 通过 |
| ⑦ 编码 + 对齐修正 | 通过（三文档无 BOM/无乱码；0=居中/2=左/4=右 已生效） |

> 首验唯一失败项 `04_图表报表.cpt` 缺 `<TemplateIdAttMark>` 已由模板方修复：其尾部现止于 `…PreviewType, TemplateThemeAttrMark, StrategyConfigsAttr, TemplateIdAttMark`，与其余 11 个模板一致。升级后的 7 条硬校验规则 + 扩充白名单运行正常，12 个 cpt 零错误通过。
