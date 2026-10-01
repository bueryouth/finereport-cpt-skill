# 九大能力专题

> 适用场景：动手做某个具体能力（脚本、JS、Java 自定义函数、入库、工具栏、按钮、事件、样式、公式）之前，按专题查阅原理、写法要点与对应模板。
> 一句话摘要：本文把 cpt 的九项高频能力拆成九个专题，每个专题给出"原理 + 写法要点 + 对应模板引用 + 注意事项"，是从需求到落地的操作手册。
>
> 模板引用均指向 `assets/templates/` 下文件；结构语法细节见 cpt-structure.md，类名频次见 feature-catalog.md。

---

## 专题 1：脚本（数据集脚本 / 公式变量 / JS 脚本）

### 知识说明

cpt 里"脚本"分三层，别混淆：

1. **数据集内公式脚本**：写在 SQL 正文的 `${...}` 里，是 FineReport 公式引擎在取数前动态拼接 SQL。典型用法是多值查询条件拼装：

```
${if(len(地区)=0,"","and 货主城市 in ('"+SUBSTITUTE(地区,",","','")+"')")}
```

原理：报表参数传入 → 公式引擎求值 → 拼出最终 SQL → 发给数据库。来源 demo：`parameter/多选下拉树实现多值查询.cpt`。

2. **单元格公式变量脚本**：写在单元格 O 节点的 Attributes 里，以等号开头，如 `=SUM(C4)`、`=sql("FRDemo","select ...",1)`。它在报表引擎计算时求值，可引用单元格坐标、参数（$名）、系统变量。

3. **前端 JS 脚本**：写在 Listener 的 Content CDATA 里，浏览器端执行，如 `window.parent.form.getWidgetByName("xxx").setValue(...)`。详见专题 2。

写法要点：

- 数据集脚本只能产出 SQL 片段（字符串拼接），不能返回结果集。
- 公式变量里引用参数用 `$参数名`，引用单元格用 A1 风格坐标。
- 脚本内容一律包 CDATA，含 `]]>` 时要改写避免截断。

### 模板引用

- `assets/templates/07_脚本报表.cpt`：演示数据集内 `${}` 拼参 + 单元格公式变量 + 前端 JS 脚本三层脚本的完整组合。

### 注意事项

- 数据集脚本拼字符串时注意 SQL 注入面：多值参数务必用 SUBSTITUTE 拆成 `'a','b','c'` 形式。
- 公式引擎报错不会让 cpt 打不开，只在预览时报错；生成后必须在设计器预览确认。
- 不要把业务逻辑全堆进数据集脚本，复杂逻辑优先在 Java 自定义函数里实现（专题 3）。

---

## 专题 2：JS（事件种类与写法）

### 知识说明

JS 事件挂在控件（Widget）或单元格按钮上，结构为 Listener > JavaScript(JavaScriptImpl) > Parameters + Content。demo 全量 grep 到的事件名与频次：

| 事件名 | 触发时机 | 次数 |
|---|---|---|
| stopedit | 停止编辑 | 19+ |
| click | 点击 | 18+ |
| statechange | 状态改变 | 8+ |
| afteredit | 编辑结束 | 5+ |
| afterload | 加载后 | 6 |
| afterinit | 初始化后 | 3 |
| writesuccess | 写入成功 | 3 |
| startload | 开始加载 | 3 |
| beforeimportexcel | 导入 Excel 前 | 1 |

写法骨架（来源 demo：`parameter/批量处理数据.cpt`）：Listener 带 event 属性，内层 JavaScript class 固定 `com.fr.js.JavaScriptImpl`，Content 放 CDATA 包裹的 JS 代码；需要把单元格值传进 JS 时，用 Parameters > Parameter > O(公式) 结构注入，JS 内用 this.getValue() 取控件值。

常用前端 API：`form.getWidgetByName("控件名")`、`FR.closeDialog()`、`FR.destroyDialog()`、`FR.doHyperlinkByGet/Post`。

### 模板引用

- `assets/templates/05_按钮JS事件报表.cpt`：FreeButton 上的 afterinit / click / statechange 三事件组合，含弹窗关闭与控件赋值。

### 注意事项

- 事件名必须小写连字符拼写（afterinit 不是 afterInit），写错不生效且不报错。
- 参数面板控件与单元格控件的 JS API 略有差异：单元格内用 this，参数面板跨控件用 window.parent.form。
- JS 代码里不要写 `]]>`，否则截断 CDATA。

---

## 专题 3：Java（自定义函数 / 类）

### 知识说明

cpt 公式引擎支持调用自定义 Java 函数。开发链路三步：

1. **写 Java 类**：继承 `com.fr.script.AbstractFunction`，实现 `run(Object[] args)`，args 即公式括号里的参数数组。帆软官方示例（report-example 项目 `src/main/java/com/fr/function/StringCat.java`）：

```java
package com.fr.function;

import com.fr.script.AbstractFunction;

public class StringCat extends AbstractFunction {
    public Object run(Object[] args) {
        StringBuilder stringBuilder = new StringBuilder();
        for (int i = 0; i < args.length; i++) {
            stringBuilder.append(args[i].toString());
        }
        return stringBuilder.toString();
    }
}
```

2. **编译部署**：编译需引入帆软 lib 下 jar（fine-core-11.0.jar、fine-report-engine-11.0.jar 等）；编译后的 class 放入插件目录或通过 plugin.xml 注册的插件包部署。plugin.xml 结构（report-example 实测）：

```xml
<plugin>
    <id>com.fr.plugin.doc.demo.v10</id>
    <name><![CDATA[文档demo代码集成]]></name>
    <active>yes</active>
    <version>1.1.1</version>
    <env-version>10.0~</env-version>
    <vendor>finereport</vendor>
    <extra-core></extra-core>
    <extra-designer></extra-designer>
</plugin>
```

3. **cpt 中引用**：部署后在公式里直接写函数名（类名），如 `=StringCat(A1,B1)`。函数名在公式中就是 Java 类名。

同类参考：report-example 的 function 目录下还有 CellSum（单元格求和）、DateDiff（日期差）、Lunar（农历）、IRR 等完整示例。

### 模板引用

- `assets/templates/08_Java自定义函数报表.cpt`：演示单元格公式调用自定义函数（如 `=StringCat(...)` 形态），并附插件部署说明注释。

### 注意事项

- cpt 文件本身不包含 Java 代码；**函数类必须先在服务器/设计器侧部署生效，cpt 里的公式才能算出值**，否则预览报"函数未定义"。
- 编译用 JDK 1.8，依赖从帆软安装目录 webapps\webroot\WEB-INF\lib 取。
- 函数名区分大小写，与 Java 类名一致。
- 本技能包只生成"调用函数"的 cpt 侧写法；Java 工程编写与打包不在 cpt 生成范围，需用户在帆软插件工程中完成。

---

## 专题 4：入库（智能提交 / 填报入库）

### 知识说明

填报入库的核心节点链：ReportWriteAttr > SubmitVisitor(class=BuiltInSQLSubmiter) > DMLConfig(class=IntelliDMLConfig) > Table + ColumnConfig。

原理：填报预览时用户在单元格控件里输入 → 点提交按钮 → 引擎按 ColumnConfig 的 isKey 配置比对主键：主键匹配走 UPDATE，不匹配走 INSERT，自动生成内置 SQL。

写法要点（结构细节见 cpt-structure.md 第 11 节）：

- Table 的 name 是目标表名，schema 可空。
- 每个 ColumnConfig：name=数据库列名，isKey=true 表示主键列，skipUnmodified=false 表示未修改也提交。
- 字段来源三种：单元格（ColumnRow column/row，0 基坐标）、公式（O t="XMLable"）、常量（裸 O）。
- Condition 节点（FormulaCondition）决定"哪些行参与提交"，如 `len(D6)!=0`。
- 自定义 Java 类提交：SubmitVisitor class 换成 WClassSubmiter，内接 SubmitTask(ClassSubmitJob) + ClassAttr className + Property 绑定。

### 模板引用

- `assets/templates/03_填报入库报表.cpt`：填报控件 + IntelliDMLConfig 智能提交 + 工具栏提交/校验按钮的完整范本（对标 demo `DataReport/产品月销量情况录入表.cpt`）。

### 注意事项

- 主键列（isKey=true）至少配一个，否则引擎无法判断 insert/update。
- ColumnRow 坐标必须与实际填报单元格一致；扩展行用 ColumnRowGroup 覆盖整组行。
- 提交配置挂在 Report 节点内（ReportAttrSet 同级），不是 WorkBook 下。
- 目标表与数据连接必须真实存在，且数据库账号有 insert/update 权限。

---

## 专题 5：工具栏（内置工具栏配置 / 自定义按钮）

### 知识说明

工具栏分两处：

- **填报预览工具栏**：ReportWebAttr > WebWriteContent > ToolBars > ToolBarManager > ToolBar > Widget 列表。
- **普通预览工具栏**：ReportWebAttr > WebViewContent > ToolBars（demo 多为空自闭合，表示用默认）。

内置按钮 class 清单（频次见 feature-catalog.md 第 6 节）：提交 write.Submit（26 文件）、校验 write.Verify（25）、添加行列 write.AppendColumnRow（18）、删除行 write.DeleteRowButton（11）、分页五件套 page.First/Previous/PageNavi/Next/Last（各 54）、打印 Print（78）、导出 Export（95）、邮件 Email（82）。

每个 Widget 的标准外壳：WidgetAttr（含 PrivilegeControl）+ Text（CDATA，常用 ${i18n('key')} 国际化）+ Hotkeys + IconName。

### 模板引用

- `assets/templates/03_填报入库报表.cpt`：填报工具栏 Submit / Verify / AppendColumnRow 三按钮配置范本。
- `assets/templates/05_按钮JS事件报表.cpt`：自定义 JS 按钮的事件写法。

### 注意事项

- 按钮文案建议用 ${i18n('...')} 国际化键，不要硬编码中文（demo 风格）。
- 普通预览与填报预览的工具栏是两套，按需分别配置。
- 空 ToolBars 自闭合表示"用系统默认工具栏"。

---

## 专题 6：按钮（自定义 / 提交 / 填报按钮）

### 知识说明

按钮分三类：

1. **工具栏提交按钮**：com.fr.report.web.button.write.Submit，见专题 5。
2. **单元格自由按钮**：com.fr.form.ui.FreeButton，直接放在单元格里，可挂 click/afterinit 事件。demo 出现 24 次/12 文件。
3. **参数面板查询按钮**：com.fr.form.parameter.FormSubmitButton，固定在参数面板 WParameterLayout 里，文本"查询"，快捷键 enter。

单元格按钮骨架（来源 demo：`parameter/批量处理数据.cpt`）：C 节点内嵌 Widget class=FreeButton，下挂 Listener、WidgetAttr、Text、Hotkeys、widgetValue。

### 模板引用

- `assets/templates/05_按钮JS事件报表.cpt`：单元格 FreeButton + 事件组合。
- `assets/templates/02_参数联动报表.cpt`：参数面板 FormSubmitButton 查询按钮。

### 注意事项

- FreeButton 与工具栏 Submit 是两套体系：前者是单元格内交互按钮，后者才触发入库提交。
- 按钮必须有 WidgetName，否则 JS 里 getWidgetByName 找不到。

---

## 专题 7：事件（初始化后 / 加载结束 / 点击等）

### 知识说明

"事件"与专题 2 的 JS 是一体两面：专题 2 讲 JS 代码怎么写，本专题讲事件时机怎么选。

常用时机选择：

| 需求 | 选事件 |
|---|---|
| 报表/控件加载完后初始化全局变量 | afterinit |
| 页面加载完成后联动取数 | afterload / startload |
| 用户点按钮 | click |
| 控件值被用户改变 | statechange |
| 用户编辑完一个单元格 | afteredit |
| 提交入库成功后提示 | writesuccess |
| 导入 Excel 前清空旧数据 | beforeimportexcel |

事件挂的位置：控件上（Widget 内 Listener）或报表整体上（ReportWebAttr 下全局 Listener）。

### 模板引用

- `assets/templates/05_按钮JS事件报表.cpt`：afterinit（初始化变量）+ click（弹窗交互）+ statechange（取值联动）三种时机对比。

### 注意事项

- 同一控件可挂多个 Listener，每个 event 一个。
- writesuccess 只在填报提交成功后触发，普通预览不触发。
- 事件名拼错不报错也不执行，交付前在设计器逐个点击验证。

---

## 专题 8：样式（字体 / 边框 / 背景 / 对齐 / 条件属性）

### 知识说明

样式集中在 StyleList，单元格通过 C 的 s 索引引用（s="0" = StyleList 第 0 个 Style）。

一个 Style 的四要素：

- **字体**：FRFont name（字体名，如微软雅黑）、size（半磅，72=9pt、120=15pt）、style（0 常规、1 加粗）、foreground（字体色，int 编码）。
- **背景**：Background name=NullBackground/ColorBackground/ImageBackground，color 是 int 反色编码（-1 白、-16777216 黑）。
- **边框**：Border 下 Top/Bottom/Left/Right 各自 style="1" 有线、color 可配。
- **对齐**：horizontal_alignment 0=左、2=居中、4=右。
- **格式**：数字 CoreDecimalFormat（如 #0.00%）、日期 SimpleDateFormatThreadSafe（如 yyyy-MM-dd）。

条件属性（HighlightList）：FormulaCondition 命中后执行 HighlightAction（背景色/字体色/行高/分页等十种，频次见 feature-catalog.md 第 10 节）。典型用法斑马纹：`row() % 2! = 0` 时换背景色。

### 模板引用

- `assets/templates/06_样式定制报表.cpt`：StyleList 多套样式（标题/表头/数据/合计）+ 条件属性斑马纹高亮。

### 注意事项

- 颜色是 int 反色编码，不要写成 #RRGGBB。常用值：-1 白、-16777216 黑、-657158 浅灰。
- 改样式不要新建节点，复用 StyleList 索引；单元格 s 属性指错索引会导致样式错乱。
- 条件属性挂在具体 C 节点内，不是全局。

---

## 专题 9：公式（常用函数与写法）

### 知识说明

公式写在 O t="XMLable" class="com.fr.base.Formula" 的 Attributes CDATA 里，以等号开头。三类高频写法：

1. **聚合**：=SUM(F4)、=AVERAGE(...)，配合扩展单元格自动区域聚合。
2. **算术与引用**：=C4*D4*(1-E4)，单元格坐标 A1 风格；$$$ 表示当前单元格值。
3. **函数族**：
   - 日期：today()、year()、month()、monthdelta()
   - 字符串：len()、REPLACE()、SUBSTITUTE()
   - SQL 取数：sql("连接名","select ...",列号)
   - 权限：$fr_username、$fine_username、$fr_authority、GETUSERDEPARTMENTS()、GETUSERJOBTITLES()、nofilter

写法要点：

- 字符串拼接用 + 号；多值参数拆分用 SUBSTITUTE。
- 旧写法 t="Formula" class="Formula" 仍兼容，新生成一律用 t="XMLable" class="com.fr.base.Formula"。
- 公式里引用参数用 $参数名（数据集 SQL 里用 ${参数名}，两者别混）。

### 模板引用

- `assets/templates/01_基础查询报表.cpt`：=SUM(...) 合计公式 + 扩展单元格聚合。
- `assets/templates/07_脚本报表.cpt`：日期函数、sql() 取数、权限函数组合。

### 注意事项

- 公式报错只在预览时体现，生成器校验不出；交付前必须预览。
- nofilter 用于权限场景"超级管理员不过滤"，普通报表不要乱用。
- sql() 函数每格执行一次，大数据量下性能差，优先用数据集。

---

*九专题完。结构语法细节查 cpt-structure.md，类名词频查 feature-catalog.md，动手顺序按 SKILL.md 工作流总览。*
