# -*- coding: utf-8 -*-
"""生成 plan.json —— 84天大纲全部基于已检索验证的真实教材目录编排。
每个 res 的 u 均为实测 HTTP 200 的链接，t 为教材章节名（来源可查）。
用法: python build_plan.py  ->  输出 plan.json
"""
import json, datetime

START = datetime.date(2026, 9, 26)

LXF = "廖雪峰的官方网站"
PYDOC = "Python官方中文文档"
LXFG = "廖雪峰Git教程"
LXFS = "廖雪峰SQL教程"
RUNOOB = "菜鸟教程"
OIWIKI = "OI-Wiki(开源算法wiki)"
LC = "LeetCode中文站"
CSG = "计算机考研杂货铺(csgraduates.com)"
XIAOLIN = "小林coding图解系列"
MDN = "Mozilla开发者网络MDN中文"
PANDAS = "pandas官方文档"
MPL = "matplotlib中文站"
GITS = "Git官方中文书Pro Git"
REQ = "requests官方文档"
MS = "ModelScope魔搭文档"
CHROMA = "ChromaDB官方文档"
FAM408 = "408全家桶"
C3 = "菜鸟C语言教程"

D = []
def day(d, stage, title, tasks, kp, res, hw):
    D.append(dict(day=d, stage=stage, title=title, tasks=tasks, kp=kp,
                  res=[{"t": t, "u": u, "src": s} for t, u, s in res], hw=hw))

# ===== 阶段1 Python入门 (D1-7) =====
day(1, 1, "Python初体验：环境、变量与数据类型", [
    "打开VS Code，运行第一个Python程序(print Hello)",
    "跟着教程在交互式解释器里练10个表达式(算术/字符串/变量)",
    "写并运行你的第一个完整脚本：自我介绍生成器(input+print)"],
    ["print()/input()", "变量与赋值", "int/float/str类型", "注释 #"],
    [("5.1 数据类型和变量", "https://liaoxuefeng.com/books/python/basic/data-types/index.html", LXF),
     ("官方教程 3.1 Python用作计算器(数字/文本)", "https://docs.python.org/zh-cn/3/tutorial/introduction.html", PYDOC),
     ("菜鸟 Python3 基础语法", "https://www.runoob.com/python3/python3-basic-syntax.html", RUNOOB)],
    {"t": "自我介绍生成器", "d": "写一个程序：input()依次问姓名、专业、今天心情，最后用一条print()输出一句话自我介绍。要求：至少用到2个变量和1次f-string格式化。", "e": "示例输出：大家好，我是社会学专业的邹小雨，今天心情不错！"})

day(2, 1, "条件判断：让程序学会做选择", [
    "精读条件判断章节，抄写3个例子后合上书自己重写",
    "在解释器里测试 and/or/not 的组合真值",
    "写BMI计算器：输入身高体重，输出BMI值和体型判断(至少3个分支)"],
    ["if/elif/else", "比较运算符", "布尔值True/False", "逻辑运算and/or/not"],
    [("5.4 条件判断", "https://liaoxuefeng.com/books/python/basic/if/index.html", LXF),
     ("官方教程 4.1 更多控制流工具", "https://docs.python.org/zh-cn/3/tutorial/controlflow.html", PYDOC)],
    {"t": "BMI计算器+体测评级", "d": "input输入身高(m)和体重(kg)，计算BMI=kg/m^2，按中国标准分：偏瘦/正常/超重/肥胖四档输出。再加防错：输入非数字时用isdigit()判断并友好提示。", "e": "输入1.70 65 -> 输出：BMI=22.5，体型正常"})

day(3, 1, "循环：批量干活的效率武器", [
    "精读循环章节，理解while与for的区别",
    "手写九九乘法表(嵌套for)",
    "写猜数字游戏：程序随机1-100，玩家猜，提示大/小，直到猜中"],
    ["for/while", "range()", "break/continue", "循环嵌套"],
    [("5.6 循环", "https://liaoxuefeng.com/books/python/basic/loop/index.html", LXF),
     ("官方教程 4.2/4.3 循环", "https://docs.python.org/zh-cn/3/tutorial/controlflow.html", PYDOC)],
    {"t": "猜数字游戏", "d": "用random.randint(1,100)出题，while循环接收猜测，print提示大了/小了，猜中打印用了几次。选做：限8次机会判负。", "e": "输入50 -> 大了！ -> ... -> 恭喜，第6次猜中！"})

day(4, 1, "容器数据结构：list/tuple/dict/字符串", [
    "精读list与tuple章节，重点理解可变与不可变",
    "把通讯录练习改成dict存储：增删查各写一个函数",
    "字符串方法练习：split/join/strip/replace/format 各用一次"],
    ["list增删改查", "dict键值对", "tuple不可变", "字符串索引与切片"],
    [("5.2 字符串和编码", "https://liaoxuefeng.com/books/python/basic/string-encoding/index.html", LXF),
     ("5.3 使用list和tuple", "https://liaoxuefeng.com/books/python/basic/list-tuple/index.html", LXF),
     ("5.7 使用dict和set", "https://liaoxuefeng.com/books/python/basic/dict-set/index.html", LXF),
     ("官方教程 3.1.3 列表", "https://docs.python.org/zh-cn/3/tutorial/introduction.html", PYDOC)],
    {"t": "通讯录管理器(dict版)", "d": "用dict存联系人(名字->电话)，循环菜单：1添加 2查找 3删除 4列出全部 5退出。所有操作在一个while True里完成。", "e": "菜单循环运转，输入4列出全部联系人"})

day(5, 1, "函数：把重复代码打包复用", [
    "精读函数三章(调用/定义/参数)，做参数传递示意",
    "把前4天的散代码重构成至少5个函数",
    "理解默认参数/可变参数，各写一个例子"],
    ["def/return", "参数与返回值", "默认参数", "作用域初步"],
    [("6.1 调用函数", "https://liaoxuefeng.com/books/python/function/call-function/index.html", LXF),
     ("6.2 定义函数", "https://liaoxuefeng.com/books/python/function/define-function/index.html", LXF),
     ("6.3 函数的参数", "https://liaoxuefeng.com/books/python/function/parameter/index.html", LXF),
     ("官方教程 4.8 用户自定义函数", "https://docs.python.org/zh-cn/3/tutorial/controlflow.html", PYDOC)],
    {"t": "重构：工具函数库", "d": "新建utils.py，把通讯录/BMI/猜数字的公共逻辑抽成函数(如safe_int(s)安全转数字)，主程序import utils调用。每个函数写docstring。", "e": "主程序变短一半以上，功能不变"})

day(6, 1, "文件读写与异常处理：程序也要有记忆", [
    "精读文件读写章节，理解open/with/编码",
    "把通讯录数据存成JSON，重启程序自动加载",
    "精读错误处理章节，给程序加try/except"],
    ["open()/with", "JSON序列化", "try/except/finally", "常见异常类型"],
    [("13.1 文件读写", "https://liaoxuefeng.com/books/python/io/file/index.html", LXF),
     ("12.1 错误处理", "https://liaoxuefeng.com/books/python/error-debug-test/error/index.html", LXF),
     ("官方教程 4.9 错误和异常", "https://docs.python.org/zh-cn/3/tutorial/controlflow.html", PYDOC)],
    {"t": "存档版通讯录", "d": "每次增删后json.dump写入contacts.json；启动时若文件存在则json.load加载。所有input()包异常处理(输入空值/非数字不崩溃)。", "e": "关掉程序重开，联系人还在"})

day(7, 1, "阶段项目：命令行Todo工具(毕业作品1)", [
    "独立设计数据结构(列表存任务字典)，先写设计再写代码",
    "实现：添加/完成/删除/列出/保存 五个功能",
    "写README.md，git init提交，push到GitHub"],
    ["综合运用本周知识", "数据与展示分离", "README写作", "git基本提交"],
    [("4 创建版本库", "https://liaoxuefeng.com/books/git/create-repo/index.html", LXFG),
     ("官方教程 4.9.1 定义函数", "https://docs.python.org/zh-cn/3/tutorial/controlflow.html", PYDOC)],
    {"t": "Todo命令行工具", "d": "完整实现：todo.py 支持 add/done/del/list/自动存档，目标80行以上。自己敲，卡住先想10分钟再问AI。完成后传GitHub(D15正式教git，今天先用AI给的三条命令)。", "e": "python todo.py add 学Python 后 list 显示 [ ] 1. 学Python"})

# ===== 阶段2 Python进阶 (D8-14) =====
day(8, 2, "列表推导式与常用内建函数", [
    "精读切片/迭代/列表生成式三节",
    "用推导式重写第4天的过滤代码(一行顶五行)",
    "sorted/map/filter实战：成绩列表处理"],
    ["切片语法", "列表推导式", "sorted(key=)", "map/filter"],
    [("7.1 切片", "https://liaoxuefeng.com/books/python/advanced/slice/index.html", LXF),
     ("7.3 列表生成式", "https://liaoxuefeng.com/books/python/advanced/list-comprehension/index.html", LXF),
     ("8.1.3 sorted", "https://liaoxuefeng.com/books/python/functional/higher-order-function/sorted/index.html", LXF)],
    {"t": "成绩单处理器", "d": "scores=[(张三,87),(李四,92)...]自编8人。sorted按分数降序、按名字各排一遍；推导式筛90分以上；format对齐输出表格。", "e": "输出对齐的成绩排名表"})

day(9, 2, "模块、pip与虚拟环境", [
    "理解模块机制：import/from",
    "学会pip install与pip list",
    "创建独立venv，理解环境隔离"],
    ["模块导入", "pip使用", "venv虚拟环境", "__name__=='__main__'"],
    [("9.1 使用模块", "https://liaoxuefeng.com/books/python/module/use-module/index.html", LXF),
     ("9.2 安装第三方模块", "https://liaoxuefeng.com/books/python/module/install/index.html", LXF),
     ("16.13 venv", "https://liaoxuefeng.com/books/python/built-in-modules/venv/index.html", LXF)],
    {"t": "包结构改造", "d": "把Todo拆成todo_pkg/包：__main__.py入口+storage.py存档+cli.py界面，在新建venv里跑通。", "e": "python -m todo_pkg 正常运行"})

day(10, 2, "面向对象(一)：类与对象", [
    "精读类和实例章节，理解__init__/self",
    "把Todo任务重构为TodoItem类",
    "理解实例属性与类属性的区别"],
    ["class/__init__/self", "方法与属性", "类属性vs实例属性", "封装初识"],
    [("10.1 类和实例", "https://liaoxuefeng.com/books/python/oop/class/index.html", LXF),
     ("10.5 实例属性和类属性", "https://liaoxuefeng.com/books/python/oop/props/index.html", LXF)],
    {"t": "TodoItem类重构", "d": "定义class TodoItem(title, done=False)含mark_done()和__str__。Todo列表存对象，list功能遍历打印。", "e": "print(item)输出 [ ] 学Python 或 [x] 学Python"})

day(11, 2, "面向对象(二)：继承与多态", [
    "精读继承和多态章节",
    "写基类Shape，派生Circle/Rect求面积(多态调用)",
    "理解isinstance与type判断"],
    ["继承", "方法重写", "多态", "super()"],
    [("10.3 继承和多态", "https://liaoxuefeng.com/books/python/oop/extend/index.html", LXF),
     ("10.4 获取对象信息", "https://liaoxuefeng.com/books/python/oop/attr/index.html", LXF)],
    {"t": "图形面积计算器", "d": "Shape基类定义area()占位，Circle/Rect/Triangle各自实现。写total_area(shapes)统一调用，不判断类型直接算。", "e": "total_area([Circle(1),Rect(2,3)])返回面积和"})

day(12, 2, "标准库精粹：os/json/datetime/re", [
    "四模块各抄一个官方例子",
    "用os+re写批量文件重命名",
    "用datetime写日记文件名生成器"],
    ["os路径操作", "json读写", "datetime格式化", "正则表达式基础"],
    [("15 正则表达式", "https://liaoxuefeng.com/books/python/reg-exp/index.html", LXF),
     ("16.1 datetime", "https://liaoxuefeng.com/books/python/built-in-modules/datetime/index.html", LXF),
     ("官方re模块howto中文", "https://docs.python.org/zh-cn/3/howto/regex.html", PYDOC)],
    {"t": "批量重命名工具", "d": "指定测试文件夹，把文件名空格转下划线、统一小写(os.listdir+os.rename)。只动自己建的测试文件夹，勿碰系统文件！", "e": "'我的 文档.txt' -> '我的_文档.txt'"})

day(13, 2, "调试技术：像侦探一样找Bug", [
    "学习print调试与VS Code断点调试(F5)",
    "故意在旧代码埋5个bug并修复",
    "学会读Traceback：从最后一行往上定位"],
    ["断点调试", "读Traceback", "常见bug模式", "pdb初步"],
    [("12.2 调试", "https://liaoxuefeng.com/books/python/error-debug-test/debug/index.html", LXF),
     ("官方教程 4.9 错误和异常", "https://docs.python.org/zh-cn/3/tutorial/controlflow.html", PYDOC)],
    {"t": "找Bug练习", "d": "打开你的旧项目，故意插入5种典型bug(类型错/缩进错/索引越界/死循环/拼写错)，用VS Code断点逐个抓出修复，调试过程记入笔记。", "e": "5个bug全部被断点定位并修复"})

day(14, 2, "阶段项目：批量文件整理器(毕业作品2)", [
    "综合os/json/re/datetime写文件整理工具",
    "按扩展名分类移动文件到子文件夹",
    "测试文件夹验证，README+GitHub"],
    ["综合项目实战", "shutil用法", "防呆设计dry-run", "项目文档"],
    [("13.3 操作文件和目录", "https://liaoxuefeng.com/books/python/io/dir/index.html", LXF),
     ("菜鸟 Python3 文件I/O", "https://www.runoob.com/python3/python3-errors-execptions.html", RUNOOB)],
    {"t": "文件智能整理器", "d": "file_tidy.py 目标路径：默认--dry-run打印计划(不执行)，加--go才真移动。按扩展名分到docs/imgs/code/others。目标路径不存在时报错退出。", "e": "dry-run显示计划，--go执行后文件夹变整齐"})

# ===== 阶段3 Git与SQL (D15-21) =====
day(15, 3, "Git版本控制(一)：仓库、提交与时光机", [
    "精读Git简介，在测试文件夹git init跑通第一个仓库",
    "练习add/commit/status/log，理解工作区与暂存区",
    "给Todo项目补3条以上有意义的提交历史"],
    ["git init/add/commit/log", "工作区与暂存区", ".gitignore", "git status"],
    [("Git简介", "https://liaoxuefeng.com/books/git/introduction/index.html", LXFG),
     ("Git是什么/集中式vs分布式", "https://liaoxuefeng.com/books/git/what-is-git/svn-vs-git/index.html", LXFG),
     ("创建版本库", "https://liaoxuefeng.com/books/git/create-repo/index.html", LXFG),
     ("菜鸟Git教程", "https://www.runoob.com/git/git-tutorial.html", RUNOOB),
     ("Pro Git 起步-命令行", "https://git-scm.com/book/zh/v2/%e8%b5%b7%e6%ad%a5-%e5%91%bd%e4%bb%a4%e8%a1%8c", GITS)],
    {"t": "给Todo项目补历史", "d": "在todo项目里git init，分3次提交：初版框架/功能完成/修bug，每次commit写清楚改了什么。再写.gitignore排除__pycache__。", "e": "git log显示3条清晰的中文提交信息"})

day(16, 3, "Git分支与撤销操作", [
    "练习reset三模式，理解版本回退的边界",
    "创建feature分支开发小功能并合并回master",
    "制造一次合并冲突并亲手解决"],
    ["branch/merge", "reset --soft/--hard", "merge冲突解决", "stash"],
    [("使用分支", "https://liaoxuefeng.com/books/git/branch/create/index.html", LXFG),
     ("分支管理与合并", "https://liaoxuefeng.com/books/git/branch/merge/index.html", LXFG),
     ("时光机:工作区与暂存区", "https://liaoxuefeng.com/books/git/time-travel/working-stage/index.html", LXFG),
     ("时光机:版本回退", "https://liaoxuefeng.com/books/git/time-travel/reset/index.html", LXFG),
     ("Pro Git 查看提交历史", "https://git-scm.com/book/zh/v2/Git-%e5%9f%ba%e7%a1%80-%e6%9f%a5%e7%9c%8b%e6%8f%90%e4%ba%a4%e5%8e%86%e5%8f%b2", GITS)],
    {"t": "分支实战", "d": "在测试仓库：master上写v1，开feature分支加一个函数，回到master改同一行制造冲突，手动解决后merge。整个过程截图/记录到notes.md。", "e": "git log --graph显示合并记录，无冲突残留"})

day(17, 3, "Git远程协作与GitHub上传", [
    "把Todo项目推送到GitHub(用已有账号chenzhongyu331166-hub)",
    "练习clone/pull/push，理解远程与本地关系",
    "配置.gitignore保护venv和数据库文件"],
    ["remote add/push/pull", "clone", "HTTPS与凭据", "协作flow初步"],
    [("添加远程库", "https://liaoxuefeng.com/books/git/remote/add-remote/index.html", LXFG),
     ("克隆远程仓库", "https://liaoxuefeng.com/books/git/remote/clone/index.html", LXFG),
     ("使用GitHub", "https://liaoxuefeng.com/books/git/github/index.html", LXFG),
     ("忽略特殊文件", "https://liaoxuefeng.com/books/git/customize/ignore/index.html", LXFG),
     ("Pro Git 账户创建和配置", "https://git-scm.com/book/zh/v2/GitHub-%e8%b4%a6%e6%88%b7%e7%9a%84%e5%88%9b%e5%bb%ba%e5%92%8c%e9%85%8d%e7%bd%ae", GITS)],
    {"t": "首次推送", "d": "新建GitHub仓库study-todo(公开)，把D7的Todo项目推上去。.gitignore必须排除venv/、data/、*.db。推完在网页上确认文件齐全。", "e": "GitHub仓库里能看到完整项目且无venv"})

day(18, 3, "SQL入门：认识数据库与查询", [
    "精读SQL教程前两章，理解关系型数据库模型",
    "用Python sqlite3建库建表并插入10条数据",
    "写5条不同条件的SELECT查询"],
    ["关系型数据库概念", "CREATE TABLE/INSERT", "SELECT/FROM", "Python sqlite3连接"],
    [("SQL简介", "https://liaoxuefeng.com/books/sql/introduction/index.html", LXFS),
     ("基本查询", "https://liaoxuefeng.com/books/sql/query/basic/index.html", LXFS),
     ("菜鸟SQL教程", "https://www.runoob.com/sql/sql-intro.html", RUNOOB),
     ("SQL SELECT语句", "https://www.runoob.com/sql/sql-select.html", RUNOOB),
     ("Python sqlite3模块", "https://docs.python.org/zh-cn/3/library/sqlite3.html", PYDOC)],
    {"t": "成绩库初始化", "d": "Python脚本：sqlite3创建students.db(字段:学号/姓名/班级/分数/城市)，插入你自己编的10条数据，写5条查询(全部/按分数排/查某班/查某城市/分数段)。", "e": "每条查询打印对齐的结果表"})

day(19, 3, "SQL查询进阶：过滤、排序与列计算", [
    "WHERE/LIKE/IN/BETWEEN实战各3例",
    "ORDER BY多列排序与别名",
    "聚合函数COUNT/SUM/AVG/MIN/MAX跟敲"],
    ["WHERE与运算符", "LIKE/IN/BETWEEN", "ORDER BY", "聚合函数"],
    [("条件查询WHERE", "https://liaoxuefeng.com/books/sql/query/where/index.html", LXFS),
     ("查询列与别名", "https://liaoxuefeng.com/books/sql/query/projection/index.html", LXFS),
     ("排序ORDER BY", "https://liaoxuefeng.com/books/sql/query/order-by/index.html", LXFS),
     ("SQL WHERE子句", "https://www.runoob.com/sql/sql-where.html", RUNOOB),
     ("SQL ORDER BY", "https://www.runoob.com/sql/sql-orderby.html", RUNOOB)],
    {"t": "查询挑战10题", "d": "基于students.db写10个Python查询函数(如:及格人数、各城市平均分、姓李的学生、分数在60-80之间...每个函数一条SQL+参数化查询)。", "e": "10个函数全部返回正确结果"})

day(20, 3, "SQL核心：分组聚合与多表连接", [
    "GROUP BY+HAVING统计练习",
    "理解INNER/LEFT JOIN的区别并画图示意",
    "三表连接查询：学生-课程-成绩"],
    ["GROUP BY/HAVING", "JOIN原理", "多表查询", "NULL与连接"],
    [("聚合查询", "https://liaoxuefeng.com/books/sql/query/aggregation/index.html", LXFS),
     ("连接查询", "https://liaoxuefeng.com/books/sql/query/join/index.html", LXFS),
     ("多表查询", "https://liaoxuefeng.com/books/sql/query/multi-tables/index.html", LXFS),
     ("SQL GROUP BY", "https://www.runoob.com/sql/sql-groupby.html", RUNOOB),
     ("SQL HAVING", "https://www.runoob.com/sql/sql-having.html", RUNOOB),
     ("SQL JOIN", "https://www.runoob.com/sql/sql-join.html", RUNOOB)],
    {"t": "三表查询器", "d": "建courses/scores两表与students关联，脚本输出：每门课平均分、成绩前10的学生(带课程名)、左连接找出没选课的学生。", "e": "三个问题各一条SQL全部答对"})

day(21, 3, "SQL增删改、索引与阶段项目", [
    "INSERT/UPDATE/DELETE三类DML练习",
    "理解索引与事务的意义(读对应章节)",
    "完成SQL练习器项目"],
    ["INSERT/UPDATE/DELETE", "事务ACID初步", "索引原理", "参数化防注入"],
    [("增删改语句", "https://liaoxuefeng.com/books/sql/manipulation/insert/index.html", LXFS),
     ("索引", "https://liaoxuefeng.com/books/sql/relational/index/index.html", LXFS),
     ("事务", "https://liaoxuefeng.com/books/sql/transaction/index.html", LXFS),
     ("SQL CREATE TABLE", "https://www.runoob.com/sql/sql-create-table.html", RUNOOB),
     ("SQL CREATE INDEX", "https://www.runoob.com/sql/sql-create-index.html", RUNOOB)],
    {"t": "SQL练习器", "d": "命令行循环：输入SQL则执行并打印结果，输入q退出；统计语句自动带fetchone返回；所有用户输入一律参数化。加分项：历史命令存txt。", "e": "能对students.db完成整套增删改查"})

# ===== 阶段4 pandas数据分析 (D22-28) =====
day(22, 4, "pandas初识：DataFrame上手", [
    "精读官方10 Minutes to pandas并跟敲",
    "读取成绩CSV为DataFrame，head/info/describe三连",
    "理解Series与DataFrame的关系"],
    ["Series/DataFrame", "read_csv/read_excel", "head/info/describe", "列选择"],
    [("10 Minutes to pandas", "https://pandas.pydata.org/docs/user_guide/10min.html", PANDAS),
     ("菜鸟pandas教程", "https://www.runoob.com/pandas/pandas-tutorial.html", RUNOOB)],
    {"t": "成绩数据载入", "d": "把你之前的Kaggle成绩CSV(或D18生成的)用pd.read_csv读入，输出：前5行、各列dtype、describe统计摘要到result.txt。要求处理好编码(utf-8/gbk报错时都要能读)。", "e": "result.txt含完整统计摘要"})

day(23, 4, "pandas索引与选择：loc/iloc", [
    "精读10min的索引章节，区分label与position",
    "列运算：新增等级列、总分列",
    "布尔组合筛选(多条件)"],
    ["loc/iloc", "列运算与赋值", "布尔索引", "query方法"],
    [("10 Minutes to pandas 索引", "https://pandas.pydata.org/docs/user_guide/10min.html", PANDAS),
     ("菜鸟pandas教程", "https://www.runoob.com/pandas/pandas-tutorial.html", RUNOOB)],
    {"t": "成绩筛选器", "d": "脚本：筛选数学>90且英语>85的学生；按分数从高到低取前20；把90+标为A、80+标为B(新增level列)。全部用loc/iloc实现，不许用for循环遍历行。", "e": "输出三段结果且未用iterrows"})

day(24, 4, "pandas数据清洗：缺失、重复与类型", [
    "精读Missing Data文档，掌握isna/dropna/fillna",
    "构造脏数据CSV(空值/重复/类型混杂)并清洗",
    "类型转换astype与to_datetime"],
    ["缺失值处理", "重复行drop_duplicates", "astype类型转换", "清洗流水线"],
    [("Working with Missing Data", "https://pandas.pydata.org/docs/user_guide/missing_data.html", PANDAS),
     ("10 Minutes to pandas", "https://pandas.pydata.org/docs/user_guide/10min.html", PANDAS)],
    {"t": "脏数据清洗挑战", "d": "手工造dirty.csv(含空分数、重复学号、分数列混入'缺考'字符串)，写clean.py：清洗后存clean.csv，同时打印清洗日志(删了几行/填了几格/改了几处)。", "e": "clean.csv可用且日志数字与手工核对一致"})

day(25, 4, "pandas分组聚合groupby", [
    "精读Groupby文档，理解split-apply-combine",
    "多键分组：班级×性别统计均值方差",
    "pivot_table透视表入门"],
    ["groupby/agg", "多级分组", "agg多函数", "pivot_table"],
    [("Grouping", "https://pandas.pydata.org/docs/user_guide/groupby.html", PANDAS),
     ("菜鸟pandas教程", "https://www.runoob.com/pandas/pandas-tutorial.html", RUNOOB)],
    {"t": "班级成绩报告", "d": "对clean.csv：按班级统计各科均分/最高分/人数；按班级×性别统计数学均分；用pivot_table输出班级排名透视表。三张表写入report_data.xlsx或csv。", "e": "三个统计口径数字全部正确"})

day(26, 4, "pandas合并与重塑", [
    "精读Merging文档：concat/merge/join区别",
    "成绩表与花名册按学号merge",
    "reshape：宽表转长表melt"],
    ["concat/merge", "连接键与how", "melt/pivot", "列重命名"],
    [("Merge, join, concatenate", "https://pandas.pydata.org/docs/user_guide/merging.html", PANDAS),
     ("Reshaping and pivot tables", "https://pandas.pydata.org/docs/user_guide/reshaping.html", PANDAS)],
    {"t": "数据整合", "d": "造roster.csv(学号/姓名/性别/班级)与scores.csv，inner/left各合并一次对比行数差异，再melt成长表：每行=一次(学生,科目,分数)。", "e": "left连接能找出无成绩学生，melt结果可读"})

day(27, 4, "数据可视化：matplotlib出图", [
    "matplotlib中文站快速上手，跑通第一个图",
    "直方图/柱状图/折线图/散点图各画一张",
    "解决中文乱码与xlabel/ylabel/title"],
    ["plot/bar/hist/scatter", "子图subplot", "中文与标签", "保存PNG"],
    [("matplotlib中文站", "https://matplotlib.org.cn/", MPL),
     ("菜鸟matplotlib教程", "https://www.runoob.com/matplotlib/matplotlib-tutorial.html", RUNOOB)],
    {"t": "成绩四联图", "d": "2×2子图：分数直方图、各班均分柱状图、按学号的分数折线、数学vs英语散点(标相关性)。中文正常显示，每图有标题和轴标签，保存fig.png。", "e": "fig.png四张图无乱码"})

day(28, 4, "阶段项目：成绩数据分析报告(毕业作品3)", [
    "整合D22-27写完整分析脚本analyze.py",
    "输出4张图与关键统计表",
    "写report.md：5条数据驱动的结论并push GitHub"],
    ["分析流水线", "可复现性", "数据可视化叙事", "报告写作"],
    [("10 Minutes to pandas", "https://pandas.pydata.org/docs/user_guide/10min.html", PANDAS),
     ("Grouping", "https://pandas.pydata.org/docs/user_guide/groupby.html", PANDAS),
     ("matplotlib中文站", "https://matplotlib.org.cn/", MPL)],
    {"t": "完整分析报告", "d": "analyze.py一键跑完：读取→清洗→分组统计→4图→存results/。report.md含5条结论(如:哪班均分最高、性别差异、分数分布形态)。传GitHub新仓库或子目录。", "e": "他人clone后运行analyze.py可复现全部结果"})

# ===== 阶段5 Flask Web开发 (D29-35) =====
FLASK = "Flask官方文档"
AGENT = "小林《图解Agent》"

day(29, 5, "HTTP基础与Flask首秀", [
    "读MDN HTTP概述，手绘一次请求-响应流程图",
    "跑通Flask hello world，用浏览器和curl各测一次",
    "列出常用状态码与GET/POST区别"],
    ["HTTP请求/响应结构", "状态码", "URL路由", "app.run调试模式"],
    [("HTTP概述(MDN中文)", "https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Overview", MDN),
     ("Flask Quickstart", "https://flask.palletsprojects.com/en/stable/quickstart/", FLASK)],
    {"t": "学习台雏形1", "d": "app.py两个路由：/显示'今天是X月X日，我在学D29'；/info显示你的名字和当前计划进度(硬编码百分比即可)。要求用curl测出200状态码并记录。", "e": "浏览器与curl都正常返回"})

day(30, 5, "路由参数与Jinja2模板", [
    "掌握路径变量<类型:名>与查询参数request.args",
    "精读Quickstart模板章节，练if/for/过滤器",
    "渲染多页面代替字符串拼接"],
    ["路径参数", "render_template", "Jinja if/for", "过滤器"],
    [("Flask Quickstart 模板", "https://flask.palletsprojects.com/en/stable/quickstart/", FLASK),
     ("Flask Tutorial", "https://flask.palletsprojects.com/en/stable/tutorial/", FLASK)],
    {"t": "分数评级页", "d": "/score/<int:score>：模板里用Jinja if输出 90+优秀/80+良好/60+及格/不及格；/list 用for循环渲染5个人的姓名+分数表格。", "e": "/score/95 显示优秀，/list 显示表格"})

day(31, 5, "表单处理与静态资源", [
    "掌握request.form与GET/POST语义",
    "实现表单提交→服务器处理→页面回显",
    "加style.css统一页面样式"],
    ["request.method/form", "POST防重复提交概念", "static目录", "模板继承初步"],
    [("Flask Tutorial", "https://flask.palletsprojects.com/en/stable/tutorial/", FLASK),
     ("Flask Quickstart", "https://flask.palletsprojects.com/en/stable/quickstart/", FLASK)],
    {"t": "记分板表单", "d": "/输入页表单(姓名+分数)POST到/add，存入内存列表，/board展示全部记录并算平均分。样式放static/style.css。", "e": "提交3条后board显示3条与平均分"})

day(32, 5, "数据库集成：把数据存下来", [
    "精读SQLAlchemy模式章节(理解即可)，主用sqlite3",
    "实现增删改查三个路由",
    "数据库文件放data/目录并加入.gitignore"],
    ["SQLite文件库", "CRUD路由", "参数化SQL", "连接管理"],
    [("Flask SQLAlchemy模式", "https://flask.palletsprojects.com/en/stable/patterns/sqlalchemy/", FLASK),
     ("Python sqlite3", "https://docs.python.org/zh-cn/3/library/sqlite3.html", PYDOC)],
    {"t": "TodoWeb v1", "d": "把D7的Todo搬上Web：sqlite存data/todos.db，/add(form提交) /list(展示) /done/<id>(标记完成)。数据库路径用相对项目根，确保git不会提交.db文件。", "e": "刷新页面数据还在(已持久化)"})

day(33, 5, "REST API与requests调用", [
    "设计JSON接口：GET列表/POST新增",
    "用requests写客户端调用自己的API",
    "理解无状态与幂等概念(读一遍即可)"],
    ["JSON响应", "@app.route methods", "requests.post(json=)", "接口约定"],
    [("Flask Quickstart", "https://flask.palletsprojects.com/en/stable/quickstart/", FLASK),
     ("Requests Quickstart", "https://requests.readthedocs.io/en/latest/user/quickstart/", REQ),
     ("Requests Advanced", "https://requests.readthedocs.io/en/latest/user/advanced/", REQ)],
    {"t": "API+客户端", "d": "/api/todos返回JSON列表，POST /api/todos接收json新增；写client.py用requests调用两个接口并打印格式化结果(含状态码与耗时)。", "e": "client.py一键跑通增+查"})

day(34, 5, "错误处理与代码模块化", [
    "注册errorhandler，统一JSON错误格式",
    "把项目拆成Blueprint模块",
    "制造404/400验证错误处理生效"],
    ["errorhandler", "Blueprint", "统一错误协议", "项目结构"],
    [("Flask Error Handling", "https://flask.palletsprojects.com/en/stable/errorhandling/", FLASK),
     ("Flask Blueprints", "https://flask.palletsprojects.com/en/stable/blueprints/", FLASK)],
    {"t": "重构+防呆", "d": "把D33项目拆成app.py+bp_todos.py；所有错误返回{\"error\": ...}；POST缺字段返回400并给出中文提示。用curl分别触发404和400各一次留记录。", "e": "curl -i看到正确状态码与错误JSON"})

day(35, 5, "阶段项目：TodoWeb完整版(毕业作品4)", [
    "完成统计接口/api/stats(总数/完成率)",
    "补README：启动方式、接口文档、截图",
    "push GitHub并打tag v1.0"],
    ["项目收尾", "接口文档", "统计查询SQL", "打tag发布"],
    [("Flask Tutorial", "https://flask.palletsprojects.com/en/stable/tutorial/", FLASK),
     ("Flask Quickstart", "https://flask.palletsprojects.com/en/stable/quickstart/", FLASK)],
    {"t": "TodoWeb v1.0发布", "d": "补齐统计接口与错误处理，README含：安装/运行/接口表(方法/路径/参数/返回示例)。git tag v1.0并push。运行自测：增删改查+统计全部通过。", "e": "GitHub上v1.0标签可见，README完整"})

# ===== 阶段6 AI应用开发 (D36-42) =====
day(36, 6, "调通大模型API：魔搭首秀", [
    "读ModelScope推理服务文档，理解OpenAI兼容协议",
    "用requests向魔搭发第一条对话(读本地配置拿key)",
    "封装ask(prompt)函数，key绝不明文进仓库"],
    ["OpenAI兼容/messages接口", "API Key安全", "requests.post(json=)", "model与usage字段"],
    [("ModelScope API推理服务", "https://modelscope.cn/docs/model-service/API-Inference/intro", MS),
     ("ModelScope文档首页", "https://modelscope.cn/docs", MS),
     ("Requests Quickstart", "https://requests.readthedocs.io/en/latest/user/quickstart/", REQ)],
    {"t": "我的第一个AI函数", "d": "chat.py：key从环境变量或本地config.py读(该文件进.gitignore)；ask(prompt)->str；测试3个问题并把模型返回的usage(token数)打印出来。", "e": "ask('用一句话介绍Python')返回中文回答"})

day(37, 6, "提示词工程：让模型听懂指令", [
    "对比system/user两种角色的效果差异",
    "练习few-shot：给2个示例再提要求",
    "让模型输出JSON并可靠解析"],
    ["system提示词", "few-shot示例", "JSON输出与json.loads", "重试与容错"],
    [("ModelScope API推理服务", "https://modelscope.cn/docs/model-service/API-Inference/intro", MS),
     ("Python json模块", "https://docs.python.org/zh-cn/3/library/json.html", PYDOC)],
    {"t": "概念卡片生成器", "d": "输入知识点名→prompt要求只输出JSON{标题,要点[3],一句话总结}；json.loads解析后格式化打印卡片；解析失败自动重试1次并在prompt里追加'只输出JSON'。", "e": "输入'三次握手'得到排版整齐的卡片"})

day(38, 6, "多轮对话与流式输出", [
    "维护messages历史实现真正的聊天",
    "理解上下文长度与截断策略",
    "stream=True流式逐字打印"],
    ["messages历史", "上下文管理", "SSE流式", "角色一致性"],
    [("Requests Advanced 流式", "https://requests.readthedocs.io/en/latest/user/advanced/", REQ),
     ("ModelScope API推理服务", "https://modelscope.cn/docs/model-service/API-Inference/intro", MS)],
    {"t": "终端聊天室", "d": "chatroom.py：循环输入，history列表存所有消息，输入clear清空历史，quit退出；尝试stream=True逐块打印(提示: iter_lines)。", "e": "模型记得你三轮前提过的名字"})

day(39, 6, "向量与Embedding：语义搜索原理", [
    "理解embedding与余弦相似度(读概念+公式)",
    "手写TF-IDF向量化与cos函数",
    "用10条自己的笔记做最相似检索"],
    ["embedding概念", "TF-IDF实现", "余弦相似度", "top-k检索"],
    [("ChromaDB文档", "https://docs.trychroma.com/docs/overview/introduction", CHROMA),
     ("ModelScope文档", "https://modelscope.cn/docs", MS)],
    {"t": "语义搜索mini版", "d": "纯Python实现：notes.py存10条学习笔记→分词(按字符2-gram即可)→TF-IDF向量→输入查询返回top3相似笔记及相似度分数。不许用任何向量库。", "e": "查'TCP握手'能排到TCP相关笔记"})

day(40, 6, "RAG检索增强生成实战", [
    "把D39检索器接上D36的ask()：检索→拼提示词→回答",
    "prompt要求引用[来源]并只依据检索内容回答",
    "测试有/无RAG的答案差异"],
    ["chunk分块", "检索拼装", "引用来源", "幻觉抑制"],
    [("ChromaDB文档", "https://docs.trychroma.com/docs/overview/introduction", CHROMA),
     ("Requests Quickstart", "https://requests.readthedocs.io/en/latest/user/quickstart/", REQ),
     ("ModelScope API推理服务", "https://modelscope.cn/docs/model-service/API-Inference/intro", MS)],
    {"t": "迷你RAG问答", "d": "rag.py：语料=你D1-39的notes笔记(或课程大纲md)；输入问题→top3片段→prompt'仅依据资料回答并标注[来源]'→打印答案+来源列表。", "e": "问大纲内容能答对并给出来源，无关问题会拒答"})

day(41, 6, "Agent最小实现：工具调用循环", [
    "读小林《图解Agent》理解规划-行动-观察循环",
    "实现JSON协议：模型输出{tool, args}决定调用",
    "本地执行工具后把结果喂回模型"],
    ["ReAct循环", "工具注册", "JSON协议", "循环上限防失控"],
    [("小林图解Agent", "https://xiaolinnote.com/agent/", AGENT),
     ("ModelScope API推理服务", "https://modelscope.cn/docs/model-service/API-Inference/intro", MS)],
    {"t": "两个工具的Agent", "d": "agent.py注册get_time()和calc(表达式，仅允许数字和+-*/)；模型回答'需要工具'则执行并回传observation，否则输出最终答案；max_round=5防死循环。", "e": "问'现在几点+3等于几'能正确走完工具链"})

day(42, 6, "阶段项目：AI助教(毕业作品5)", [
    "把AI老师做成命令行三问流程",
    "自测：生成3道问答题(非选择题)→作答→AI评分点评",
    "总结阶段6，push代码"],
    ["会话流程编排", "评分prompt设计", "结果落盘", "项目复盘"],
    [("ModelScope API推理服务", "https://modelscope.cn/docs/model-service/API-Inference/intro", MS),
     ("Flask Blueprints", "https://flask.palletsprojects.com/en/stable/blueprints/", FLASK)],
    {"t": "AI助教 teach.py", "d": "输入知识点→AI出3道必须动手写/答的问答题→逐题作答→AI按要点打分(0-2分)并给改进建议→总分与薄弱点总结存ai_session.json。", "e": "完整跑一轮并生成可回看的成绩记录"})

# ===== 阶段7 408计算机网络 (D43-49) =====
day(43, 7, "网络体系结构：分层与一次网页请求", [
    "精读小林TCP/IP模型，手绘五层/四层对照图",
    "跟敲'键入网址到显示'全流程，能口头复述",
    "对照MDN HTTP概述补协议细节"],
    ["OSI与TCP/IP分层", "封装与解封装", "键入网址全过程", "客户端/服务端"],
    [("TCP/IP网络模型有哪几层？", "https://xiaolincoding.com/network/1_base/tcp_ip_model.html", XIAOLIN),
     ("键入网址到网页显示，期间发生了什么？", "https://xiaolincoding.com/network/1_base/what_happen_url.html", XIAOLIN),
     ("HTTP概述(MDN中文)", "https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Overview", MDN),
     ("408计算机网络", "https://csgraduates.com/computer_network/", CSG)],
    {"t": "全流程复述+绘图", "d": "不看资料白纸写出从DNS解析到浏览器渲染的10步；再画分层图标注每层的PDU名称与对应协议。拍照/文字存notes。", "e": "10步无明显遗漏，图含关键协议"})

day(44, 7, "应用层：HTTP协议精讲", [
    "精读小林HTTP常见面试题(长文，分两批读完)",
    "整理方法/状态码/头部三张速查表",
    "用requests实测GET/POST/自定义头/重定向"],
    ["HTTP方法与语义", "状态码分类", "常用头部", "重定向"],
    [("HTTP常见面试题", "https://xiaolincoding.com/network/2_http/http_interview.html", XIAOLIN),
     ("HTTP状态码404示例", "https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/404", MDN),
     ("Requests Quickstart", "https://requests.readthedocs.io/en/latest/user/quickstart/", REQ)],
    {"t": "HTTP实验报告", "d": "写probe.py：对3个已验证URL分别发GET，打印状态码/Content-Type/编码/耗时；再请求一个404页面记录异常处理；用一次POST(可对httpbin?没有则本机Flask)验证方法语义。报告存notes。", "e": "probe.py输出完整对照表"})

day(45, 7, "HTTPS与HTTP演进", [
    "精读HTTPS RSA握手，画握手时序图",
    "了解HTTP/2多路复用与HTTP/3 QUIC要点",
    "理解对称/非对称加密的分工"],
    ["TLS握手", "证书与CA", "HTTP/2特性", "HTTP/3与QUIC"],
    [("HTTPS RSA握手解析", "https://xiaolincoding.com/network/2_http/https_rsa.html", XIAOLIN),
     ("HTTP/2牛逼在哪？", "https://xiaolincoding.com/network/2_http/http2.html", XIAOLIN),
     ("HTTP/3强势来袭", "https://xiaolincoding.com/network/2_http/http3.html", XIAOLIN)],
    {"t": "握手时序图+自问自答", "d": "默画RSA握手8步(从ClientHello到Finished)；写出5组高频问答(为何要HTTPS/证书怎么来的/HTTP2解决了什么...)并口述一遍录音或文字稿。", "e": "能脱稿讲清楚为什么需要非对称加密"})

day(46, 7, "TCP：连接管理与可靠传输", [
    "精读三次握手四次挥手面试题(长文，务必啃完)",
    "精读重传/滑动窗口/流量/拥塞控制",
    "整理状态机：11种状态与转移条件"],
    ["三次握手", "四次挥手与TIME_WAIT", "可靠传输机制", "滑动窗口/拥塞控制"],
    [("TCP三次握手与四次挥手面试题", "https://xiaolincoding.com/network/3_tcp/tcp_interview.html", XIAOLIN),
     ("TCP重传、滑动窗口、流量控制、拥塞控制", "https://xiaolincoding.com/network/3_tcp/tcp_feature.html", XIAOLIN)],
    {"t": "状态机默写", "d": "白纸画出TCP状态转移图(CLOSED到ESTABLISHED再到TIME_WAIT)；回答：为什么挥手是四次而握手是三次？TIME_WAIT为何是2MSL？写成notes。", "e": "状态图完整，两个为什么能自圆其说"})

day(47, 7, "TCP细节与socket编程实战", [
    "读小林半连接队列/字节流/端口复用三篇",
    "用socket写echo服务端+客户端",
    "理解accept/listen与并发处理雏形"],
    ["socket API", "listen/accept", "字节流与粘包概念", "本地回环测试"],
    [("TCP半连接队列和全连接队列", "https://xiaolincoding.com/network/3_tcp/tcp_queue.html", XIAOLIN),
     ("如何理解TCP面向字节流协议？", "https://xiaolincoding.com/network/3_tcp/tcp_stream.html", XIAOLIN),
     ("TCP和UDP可以使用同一个端口吗？", "https://xiaolincoding.com/network/3_tcp/port.html", XIAOLIN)],
    {"t": "echo服务器", "d": "server.py监听127.0.0.1:9999，client.py连接后发消息回显，Ctrl+C优雅退出；再写一个版本：服务端同时给消息加长度前缀，体会字节流边界问题。", "e": "两进程本机跑通，记录抓到的端口号与流程"})

day(48, 7, "网络层：IP地址与路由", [
    "精读IP基础知识全家桶与ping原理",
    "掌握子网划分与私有地址(能算题)",
    "用Python ipaddress模块做地址计算"],
    ["IP地址分类", "子网掩码与网段", "ping/ICMP", "路由转发概念"],
    [("IP基础知识全家桶", "https://xiaolincoding.com/network/4_ip/ip_base.html", XIAOLIN),
     ("ping的工作原理", "https://xiaolincoding.com/network/4_ip/ping.html", XIAOLIN),
     ("断网了，还能ping通127.0.0.1吗？", "https://xiaolincoding.com/network/4_ip/ping_lo.html", XIAOLIN)],
    {"t": "子网计算器", "d": "subnet.py：输入IP和掩码位数，输出网络地址/广播地址/可用主机数/是否同网段(两个IP+掩码比较)；用ipaddress模块验证你的手算结果。", "e": "手算与模块输出一致(测5组)"})

day(49, 7, "阶段项目：网络探测工具(毕业作品6)", [
    "综合socket+requests+ipaddress写探测工具",
    "端口扫描(仅限127.0.0.1)与HTTP探测两模块",
    "整理网络八股速查卡，push代码"],
    ["综合项目", "端口扫描", "超时与并发", "八股速查卡"],
    [("计算机网络怎么学？", "https://xiaolincoding.com/network/5_learn/learn_network.html", XIAOLIN),
     ("408计算机网络", "https://csgraduates.com/computer_network/", CSG)],
    {"t": "netprobe.py", "d": "两功能：①scan(host=仅允许127.0.0.1, ports=常用20个)用socket+超时并行度不限但总耗时要短；②http(url)打印状态/类型/耗时。附netcard.md：网络阶段所有高频问答。", "e": "扫描出本机真实开放端口，http探测3个URL成功"})

# ===== 阶段8 408数据结构与算法 (D50-56) =====
day(50, 8, "复杂度分析与线性表", [
    "精读复杂度章节，能手算常见代码O(n²)",
    "跟读线性表总览，理解顺序存储vs链式",
    "用timeit实测不同规模的时间增长"],
    ["大O记号", "时间/空间复杂度", "顺序存储", "timeit基准测试"],
    [("数据结构复杂度", "https://oi-wiki.org/basic/complexity/", OIWIKI),
     ("数据结构概述", "https://www.runoob.com/data-structures/dsa-intro.html", RUNOOB),
     ("线性数据结构", "https://www.runoob.com/data-structures/dsa-linear-data-structures.html", RUNOOB)],
    {"t": "复杂度实验", "d": "写counter.py：同一任务三种写法(如双重循环找重对/排序后双指针/哈希)，用timeit测n=1000/5000/10000耗时表，验证O记号预测；附手算的5段代码复杂度。", "e": "耗时比值随n增大符合理论趋势"})

day(51, 8, "栈与队列", [
    "精读OI-Wiki栈与队列，理解LIFO/FIFO",
    "手写数组栈与链式队列",
    "用栈解决括号匹配(LeetCode 20)"],
    ["栈push/pop", "队列入队出队", "括号匹配", "单调栈初识"],
    [("栈", "https://oi-wiki.org/ds/stack/", OIWIKI),
     ("队列", "https://oi-wiki.org/ds/queue/", OIWIKI),
     ("有效的括号", "https://leetcode.cn/problems/valid-parentheses/", LC)],
    {"t": "手写+刷题", "d": "mystack.py用list实现栈(禁止用pop直接偷懒要自己写边界)；用两个栈实现队列并自测；LeetCode 20自己AC一次(不许看题解，卡住超20分钟可看后重写)。", "e": "LC提交通过+队列实现自测5例"})

day(52, 8, "链表：指针操作三板斧", [
    "精读单链表与双链表，默画头插/尾插/删除时序",
    "手写单链表类：增删查反转",
    "LeetCode 206反转 + 141环形链表"],
    ["节点与指针", "头插/尾插", "快慢指针", "反转链表"],
    [("链表", "https://oi-wiki.org/ds/linked-list/", OIWIKI),
     ("反转链表", "https://leetcode.cn/problems/reverse-linked-list/", LC),
     ("环形链表", "https://leetcode.cn/problems/linked-list-cycle/", LC)],
    {"t": "手写链表库", "d": "LinkedList类含append/prepend/delete/search/reverse，每方法自测；然后LC 206与141各AC一次。reverse必须自己写出三指针迭代版。", "e": "5个方法自测通过+2题AC"})

day(53, 8, "树与二叉树", [
    "精读树与二叉搜索树，理解递归定义",
    "手写二叉树节点+前中后序遍历(递归版)",
    "层序遍历用队列实现(非递归)"],
    ["树的递归结构", "三种深度优先遍历", "层序遍历", "BST性质"],
    [("树", "https://www.runoob.com/data-structures/dsa-tree.html", RUNOOB),
     ("二叉搜索树", "https://www.runoob.com/data-structures/binary-search-tree.html", RUNOOB),
     ("高级树结构", "https://www.runoob.com/data-structures/dsa-advanced-tree.html", RUNOOB)],
    {"t": "遍历手写+验证", "d": "TreeNode类，手写preorder/inorder/postorder(递归)与levelorder(队列)，自己构造10节点树，用三种遍历结果互相验证(中序+后序重建也试一下)。", "e": "遍历序列正确且能解释递归栈过程"})

day(54, 8, "排序算法：三大排序手写", [
    "精读排序总览，整理各算法复杂度/稳定性表",
    "手写插入排序、归并排序、快速排序",
    "用随机大数组对比sorted验证正确性"],
    ["插入排序", "归并分治", "快划分", "稳定性"],
    [("排序算法", "https://www.runoob.com/data-structures/dsa-sorting.html", RUNOOB),
     ("插入排序", "https://www.runoob.com/data-structures/insertion-sort.html", RUNOOB),
     ("归并排序", "https://www.runoob.com/data-structures/merge-sort.html", RUNOOB),
     ("快速排序", "https://www.runoob.com/data-structures/random-quick-sort.html", RUNOOB),
     ("堆排序", "https://www.runoob.com/data-structures/heap-sort.html", RUNOOB)],
    {"t": "sorts.py三合一", "d": "实现insertion_sort/merge_sort/quick_sort三个函数；对10组随机数组(含全等/已排序/逆序边界)与sorted结果比对；用timeit输出三者耗时对比表。", "e": "全部用例通过且有耗时表"})

day(55, 8, "查找与哈希表", [
    "精读哈希表与冲突解决(链地址法)",
    "手写链地址法哈希表put/get/delete",
    "LeetCode 1两数之和 + 242有效字母异位词 + 34查找"],
    ["哈希函数", "链地址法", "二分查找", "哈希O(1)查询"],
    [("哈希表", "https://oi-wiki.org/ds/hash/", OIWIKI),
     ("哈希表(菜鸟)", "https://www.runoob.com/data-structures/dsa-hash-table.html", RUNOOB),
     ("两数之和", "https://leetcode.cn/problems/two-sum/", LC),
     ("有效的字母异位词", "https://leetcode.cn/problems/valid-anagram/", LC),
     ("在排序数组中查找元素的第一个和最后一个位置", "https://leetcode.cn/problems/binary-search/", LC)],
    {"t": "手写哈希+三题", "d": "MyHashTable：桶数组+链表，支持put/get/delete/扩容(负载因子0.75)，自测10例；LC 1、242各AC一次。", "e": "哈希自测通过+2题AC"})

day(56, 8, "图论入门与阶段综合刷题", [
    "精读图的存储与遍历(邻接表/矩阵)",
    "手写邻接表+BFS求迷宫最短步数",
    "LeetCode 200岛屿数量(DFS)"],
    ["邻接表/矩阵", "BFS/DFS", "最短步数", "岛屿问题"],
    [("图", "https://www.runoob.com/data-structures/dsa-graph.html", RUNOOB),
     ("图论", "https://www.runoob.com/data-structures/graph-theory.html", RUNOOB),
     ("图论(基础)", "https://oi-wiki.org/graph/", OIWIKI),
     ("岛屿数量", "https://leetcode.cn/problems/number-of-islands/", LC)],
    {"t": "迷宫BFS+LC200", "d": "maze.py：5×5字符迷宫，邻接表存边，BFS从S到E输出最短步数与路径；再把D50-56所有做过的LeetCode题号与状态整理成刷题清单push。", "e": "迷宫有解且步数正确，刷题清单完整"})

# ===== 阶段9 操作系统+C语言启蒙 (D57-63) =====
day(57, 9, "操作系统概述与CPU如何执行程序", [
    "精读小林'CPU是如何执行程序的'",
    "理解冯诺依曼结构与指令周期",
    "整理OS四大管理功能思维导图"],
    ["冯诺依曼结构", "取指-译码-执行", "OS四大管理", "内核态/用户态"],
    [("CPU是如何执行程序的？", "https://xiaolincoding.com/os/1_hardware/how_cpu_run.html", XIAOLIN),
     ("408操作系统", "https://csgraduates.com/operating_system/", CSG),
     ("什么是软中断？", "https://xiaolincoding.com/os/1_hardware/soft_interrupt.html", XIAOLIN)],
    {"t": "指令周期模拟器", "d": "cpu_sim.py：定义3条玩具指令(LOAD/ADD/STORE)，用Python模拟取指→译码→执行循环，内存用list表示，跑完计算1+2并打印每步的PC/寄存器状态。", "e": "状态表逐步显示且结果=3"})

day(58, 9, "内存管理：从地址到虚拟内存", [
    "精读虚拟内存与malloc两篇",
    "理解分页/页表/TLB基本机制",
    "手算逻辑地址→物理地址(几道题)"],
    ["逻辑/物理地址", "分页与页表", "TLB", "malloc原理"],
    [("为什么要有虚拟内存？", "https://xiaolincoding.com/os/3_memory/vmem.html", XIAOLIN),
     ("malloc是如何分配内存的？", "https://xiaolincoding.com/os/3_memory/malloc.html", XIAOLIN),
     ("内存满了，会发生什么？", "https://xiaolincoding.com/os/3_memory/mem_reclaim.html", XIAOLIN)],
    {"t": "分区分配模拟", "d": "allocator.py：实现首次适应与最佳适应两种分区分配，输入一串作业(大小/到达/结束)，输出每次分配的分区与内部碎片，统计两算法总碎片对比。", "e": "两算法结果表可对比，最佳适应碎片更多(边界情况)"})

day(59, 9, "进程与线程：并发的最小单元", [
    "精读进程线程基础知识+IPC方式",
    "Python实现多线程生产者-消费者",
    "对比threading与multiprocessing耗时"],
    ["进程/线程区别", "上下文切换", "IPC", "GIL概念"],
    [("进程、线程基础知识", "https://xiaolincoding.com/os/4_process/process_base.html", XIAOLIN),
     ("进程间有哪些通信方式？", "https://xiaolincoding.com/os/4_process/process_commu.html", XIAOLIN)],
    {"t": "并发对比实验", "d": "producer_consumer.py用Queue实现(线程版+进程版)；再写CPU密集任务(算1e7次)分别跑单线程/多线程/多进程，记录耗时解释GIL现象。", "e": "三组耗时数据+你的解释"})

day(60, 9, "同步互斥与死锁", [
    "精读多线程冲突与死锁两篇",
    "用Lock解决线程竞态(写坏例子再修好)",
    "手写银行家算法并自测安全序列"],
    ["竞态条件", "Lock/信号量", "死锁四条件", "银行家算法"],
    [("多线程冲突了怎么办？", "https://xiaolincoding.com/os/4_process/multithread_sync.html", XIAOLIN),
     ("怎么避免死锁？", "https://xiaolincoding.com/os/4_process/deadlock.html", XIAOLIN),
     ("悲观锁与乐观锁", "https://xiaolincoding.com/os/4_process/pessim_and_optimi_lock.html", XIAOLIN)],
    {"t": "银行家算法", "d": "banker.py：输入资源总量/各进程已分配/最大需求，判断给定序列是否安全(输出安全序列)，再提供request接口判断能否分配。自测教材经典例题2组。", "e": "教材例题结果与答案一致"})

day(61, 9, "调度算法与文件系统", [
    "精读进程调度/页面置换/磁盘调度一篇通",
    "手写LRU/FIFO/OPT页面置换模拟",
    "理解inode与目录结构"],
    ["调度算法分类", "页面置换LRU/FIFO/OPT", "磁盘调度", "文件系统与inode"],
    [("进程调度/页面置换/磁盘调度算法", "https://xiaolincoding.com/os/5_schedule/schedule.html", XIAOLIN),
     ("文件系统全家桶", "https://xiaolincoding.com/os/6_file_system/file_system.html", XIAOLIN)],
    {"t": "页面置换模拟器", "d": "paging.py：输入物理块数与访问串，分别跑LRU/FIFO/OPT，输出每步驻留集合与缺页次数对比表；扩展：加Belady异常的验证用例。", "e": "三算法缺页数与手算一致"})

day(62, 9, "C语言启蒙(看懂为主)：变量与类型", [
    "读菜鸟C教程前三章，重点理解与Python的差异",
    "对照注释：同一程序的Python与C双版本",
    "手写C版自我介绍+交换两数(暂不运行)"],
    ["C的静态类型", "int/float/char", "printf/scanf", "&取地址"],
    [("C语言教程", "https://www.runoob.com/cprogramming/c-tutorial.html", C3),
     ("C变量", "https://www.runoob.com/cprogramming/c-variables.html", C3),
     ("C数据类型", "https://www.runoob.com/cprogramming/c-data-types.html", C3),
     ("C输入输出", "https://www.runoob.com/cprogramming/c-input-output.html", C3)],
    {"t": "双语对照笔记", "d": "写3段C代码(自我介绍/交换两数/温度转换)，每行上方注释对应Python怎么写；标记与Python最大的5个不同点。无编译器没关系，写完让AI助教逐行讲解纠错。", "e": "三段代码语法自查无误且差异清单完整"})

day(63, 9, "C语言(看懂为主)：控制流与函数", [
    "读if-else/循环/函数三章",
    "把D2的BMI计算器翻译成C",
    "理解值传递与指针传递的区别(为指针铺垫)"],
    ["if/else与switch", "for/while", "函数定义与返回", "值传递"],
    [("C if...else", "https://www.runoob.com/cprogramming/c-if-else.html", C3),
     ("C循环", "https://www.runoob.com/cprogramming/c-loops.html", C3),
     ("C函数", "https://www.runoob.com/cprogramming/c-functions.html", C3),
     ("C作用域规则", "https://www.runoob.com/cprogramming/c-scope-rules.html", C3)],
    {"t": "C版BMI+九九乘法表", "d": "两段C代码手写：BMI计算器(含scanf防错讨论)与九九乘法表；写清楚每行意图，AI助教批改语法，错误记录到mistakes。", "e": "AI助教评审语法通过率90%+"})

# ===== 阶段10 408计组+综合强化 (D64-70) =====
day(64, 10, "计组(一)：数据表示与运算器", [
    "读408计组数据表示章节，手算补码溢出题",
    "理解IEEE754浮点数格式(能手工解码一个数)",
    "整理原码/反码/补码/移码对照表"],
    ["进制转换", "补码运算与溢出", "IEEE754", "定点数"],
    [("408计算机组成原理", "https://csgraduates.com/constitution_principle/", CSG),
     ("408全家桶-计组", "https://408-family.netlify.app/ccp", FAM408)],
    {"t": "补码与浮点工具", "d": "binary_tool.py：①输入十进制输出8位原码/补码/反码并做补码加法检测溢出；②输入IEEE754十六进制串解析出符号/阶码/真值。全部与手算对照。", "e": "5组手算用例全对"})

day(65, 10, "计组(二)：存储系统与Cache", [
    "读存储系统章节，理解层次化存储",
    "掌握组相联映射的块号/组号/标记计算",
    "理解写策略与替换算法"],
    ["Cache映射", "主存Cache计算", "写回/全写", "替换算法"],
    [("408计算机组成原理", "https://csgraduates.com/constitution_principle/", CSG),
     ("磁盘比内存慢几万倍？", "https://xiaolincoding.com/os/1_hardware/storage.html", XIAOLIN)],
    {"t": "Cache计算器", "d": "cache_calc.py：输入主存大小/Cache大小/块大小/相联度，输出组号位数、标记位数、给定地址的(块号,组号,标记)；内置教材3道例题自动核对。", "e": "例题全部自动判定正确"})

day(66, 10, "计组(三)：指令系统", [
    "读指令系统章节，整理指令格式与寻址方式表",
    "理解定长/变长指令与操作码扩展",
    "手算指令字各字段位数"],
    ["指令格式", "寻址方式", "操作码扩展", "CISC/RISC"],
    [("408计算机组成原理", "https://csgraduates.com/constitution_principle/", CSG),
     ("408全家桶-计组", "https://408-family.netlify.app/ccp", FAM408)],
    {"t": "玩具汇编解释器", "d": "asm.py：支持MOV/ADD/SUB/JMP与3种寻址(立即/直接/寄存器)，输入几条指令逐步执行并打印寄存器与内存快照；能算出循环求1到10的和。", "e": "累加结果=55且每步状态可追踪"})

day(67, 10, "计组(四)：CPU与流水线", [
    "读CPU章节，理解单总线数据通路",
    "掌握五段流水线的时序与三种冒险",
    "手算流水线加速比与效率"],
    ["数据通路", "流水线时序", "结构/数据/控制冒险", "加速比计算"],
    [("CPU是如何执行任务的？", "https://xiaolincoding.com/os/1_hardware/how_cpu_deal_task.html", XIAOLIN),
     ("CPU缓存一致性", "https://xiaolincoding.com/os/1_hardware/cpu_mesi.html", XIAOLIN),
     ("408计算机组成原理", "https://csgraduates.com/constitution_principle/", CSG)],
    {"t": "流水线甘特图生成器", "d": "pipeline.py：输入n条指令与各段耗时(可含冲突停顿)，输出甘特图ASCII画与总周期/加速比/效率；内置2道教材例题核对。", "e": "例题数值全对且图清晰"})

day(68, 10, "计组(五)：总线、输入输出与磁盘", [
    "读总线与IO章节，理解程序查询/中断/DMA三方式",
    "掌握磁盘调度四种算法",
    "整理三种IO方式对比表"],
    ["IO三方式", "中断过程", "DMA", "磁盘调度"],
    [("408计算机组成原理", "https://csgraduates.com/constitution_principle/", CSG),
     ("408全家桶-计组", "https://408-family.netlify.app/ccp", FAM408)],
    {"t": "磁盘调度模拟器", "d": "disk_sched.py：输入磁道序列与当前头位置，输出FCFS/SSTF/SCAN/C-SCAN四种算法的移动顺序与总寻道距离，自动找最优。", "e": "教材例题数据一致且最优算法正确"})

day(69, 10, "C进阶(看懂为主)：指针与数组", [
    "读指针/数组/字符串/结构体四章",
    "对照Python理解地址与引用的差异",
    "手写C版单链表节点操作(不运行，AI批改)"],
    ["指针与地址", "数组与指针等价", "字符串与\\0", "struct"],
    [("C指针", "https://www.runoob.com/cprogramming/c-pointers.html", C3),
     ("C数组", "https://www.runoob.com/cprogramming/c-array.html", C3),
     ("C字符串", "https://www.runoob.com/cprogramming/c-strings.html", C3),
     ("C结构体", "https://www.runoob.com/cprogramming/c-struct.html", C3)],
    {"t": "C链表头插法", "d": "写C代码：struct Node、头插法建表、遍历打印、释放内存(free)；每行注释说明指针在做什么；AI助教重点批内存管理部分。", "e": "语法与内存释放逻辑评审通过"})

day(70, 10, "408综合强化与错题本", [
    "四门各做一套AI生成的自测问答(用teach.py)",
    "把错题与薄弱点结构化存入mistakes",
    "制定最后两周408复习侧重"],
    ["综合自测", "错题结构化", "薄弱点定位", "复习规划"],
    [("408计算机网络", "https://csgraduates.com/computer_network/", CSG),
     ("408操作系统", "https://csgraduates.com/operating_system/", CSG),
     ("408计算机组成原理", "https://csgraduates.com/constitution_principle/", CSG),
     ("408全家桶-数据结构", "https://408-family.netlify.app/ds", FAM408)],
    {"t": "408错题本v1", "d": "用teach.py对四门各出5道问答题作答，AI评分后把错题(题干/我的答案/正确要点/薄弱标签)写入data/mistakes.json；输出各科薄弱点Top3。", "e": "mistakes.json结构化且四门全覆盖"})

# ===== 阶段11 毕业项目冲刺 (D71-77) =====
day(71, 11, "毕业项目启动：规划与分支协作", [
    "写spec.md：毕业项目功能清单与三个里程碑",
    "开dev分支，学习分支协作流程",
    "确定项目：学习台增强 或 独立RAG助手"],
    ["需求spec", "分支开发流", "里程碑拆解", "自研边界"],
    [("分支与协作", "https://liaoxuefeng.com/books/git/branch/collaboration/index.html", LXFG),
     ("Pro Git 维护项目", "https://git-scm.com/book/zh/v2/GitHub-%e7%bb%b4%e6%8a%a4%e9%a1%b9%e7%9b%ae", GITS)],
    {"t": "spec.md+dev分支", "d": "spec含：目标用户/3个核心功能/验收标准/三天各做什么；git checkout -b dev并push。先写文档再写码，文档进仓库。", "e": "spec可执行(每条能验收)，dev分支在GitHub可见"})

day(72, 11, "开发日1：资源抓取模块", [
    "实现fetch.py：输入URL列表抓取正文",
    "简易HTML→文本提取并保留标题层级",
    "抓取结果存resources/日期.md并附来源"],
    ["requests抓取", "HTML文本提取", "编码处理", "来源标注"],
    [("Requests Advanced", "https://requests.readthedocs.io/en/latest/user/advanced/", REQ),
     ("Requests Quickstart", "https://requests.readthedocs.io/en/latest/user/quickstart/", REQ)],
    {"t": "fetch.py", "d": "对3个已验证教材URL抓取：超时10s、gzip处理、乱码兜底(utf-8→gbk)，提取正文文本，文件头写清[来源](URL)[抓取时间]，存resources/。这就是'每天学完确认明天资源'的引擎。", "e": "3个页面正文落盘且来源可点"})

day(73, 11, "开发日2：测试与容错", [
    "学unittest，给fetch.py写3个单元测试",
    "处理失败路径：404/超时/非HTML",
    "全绿后合并dev回main"],
    ["unittest用例", "mock/跳过网络", "异常路径", "合并分支"],
    [("Python unittest", "https://docs.python.org/zh-cn/3/library/unittest.html", PYDOC),
     ("Requests Quickstart", "https://requests.readthedocs.io/en/latest/user/quickstart/", REQ)],
    {"t": "test_fetch.py", "d": "3用例：正常抓取(用本机Flask测试页或已验证URL)、404抛错、超时重试1次；python -m unittest全绿；git merge dev并push。", "e": "测试输出OK，main已更新"})

day(74, 11, "数据副线：真实数据分析迭代", [
    "选一份新数据(课程相关或E盘已有表格)提出问题",
    "复用D22-27技能完成清洗-统计-绘图",
    "输出结论并对比你之前的Kaggle分析进步点"],
    ["问题驱动分析", "技能复用", "图表叙事", "结论质量"],
    [("Grouping", "https://pandas.pydata.org/docs/user_guide/groupby.html", PANDAS),
     ("Merge, join, concatenate", "https://pandas.pydata.org/docs/user_guide/merging.html", PANDAS),
     ("matplotlib中文站", "https://matplotlib.org.cn/", MPL)],
    {"t": "新数据EDA报告", "d": "3个问题→分析→3张图→结论，写进eda_second.md；明确标注这次比D28报告多做了什么(更严的清洗/更细的分组/更清楚的图)。", "e": "报告含问题-方法-证据-结论完整链路"})

day(75, 11, "AI助教Web化：接入服务", [
    "给学习台(或独立Flask服务)加/api/ask接口",
    "把D42 teach.py的出题-评分流程暴露成API",
    "前端/客户端调通完整一轮"],
    ["API封装AI", "超时与错误返回", "会话暂存", "接口测试"],
    [("Flask Blueprints", "https://flask.palletsprojects.com/en/stable/blueprints/", FLASK),
     ("ModelScope API推理服务", "https://modelscope.cn/docs/model-service/API-Inference/intro", MS)],
    {"t": "ai_teach API", "d": "/api/teach/quiz(生成题)与/api/teach/score(评分)两个接口，带JSON错误协议；用requests客户端跑通一轮出题-作答-评分；记录token消耗。", "e": "客户端一键完成一轮AI自测"})

day(76, 11, "作品集与简历素材", [
    "给三个毕业作品各写：一句话价值+技术栈+链接",
    "更新个人README首页(自我介绍+项目导航)",
    "参考小林简历页面优化项目描述动词"],
    ["项目叙事", "README排版", "STAR式描述", "作品导航"],
    [("小林简历", "https://www.xiaolincoding.com/project/xiaolinnote/", AGENT),
     ("Markdown语法", "https://www.runoob.com/markdown/md-tutorial.html", RUNOOB),
     ("使用GitHub", "https://liaoxuefeng.com/books/git/github/index.html", LXFG)],
    {"t": "portfolio.md", "d": "每个项目写3行：解决什么问题(动词开头)/用了什么技术/量化结果(多少题AC、多少功能)；README加上全部项目链接并push。", "e": "portfolio可直接粘进简历项目栏"})

day(77, 11, "代码质量：重构与复盘", [
    "选一个旧项目做重构：函数拆分+docstring+类型注解",
    "写复盘blog.md：84天里最有效的3个学习方法",
    "全项目push并打v1.5标签"],
    ["重构手法", "类型注解", "docstring", "阶段复盘"],
    [("Python数据结构", "https://docs.python.org/zh-cn/3/tutorial/datastructures.html", PYDOC),
     ("Python控制流", "https://docs.python.org/zh-cn/3/tutorial/controlflow.html", PYDOC)],
    {"t": "重构+复盘", "d": "重构D14或D35项目：main逻辑≤50行、每函数有类型注解和docstring、消除重复代码；blog.md写3条方法论+1条最大教训。tag v1.5。", "e": "重构后功能不变(自测通过)+复盘已提交"})

# ===== 阶段12 模拟面试与毕业 (D78-84) =====
day(78, 12, "错题自测器与Python八股", [
    "写quiz.py：从mistakes.json抽题、AI评分、更新状态",
    "复习Python易错点，错题入本",
    "LeetCode 146 LRU + 3无重复字符(自己写)"],
    ["错题循环工具", "Python异常与迭代器", "LRU设计", "滑动窗口"],
    [("Python错误和异常", "https://www.runoob.com/python3/python3-errors-execptions.html", RUNOOB),
     ("Python控制流", "https://docs.python.org/zh-cn/3/tutorial/controlflow.html", PYDOC),
     ("LRU缓存", "https://leetcode.cn/problems/lru-cache/", LC),
     ("无重复字符的最长子串", "https://leetcode.cn/problems/longest-substring-without-repeating-characters/", LC)],
    {"t": "quiz.py", "d": "抽10道错题→用户作答→AI按要点评分→答对标记done/答错留ready；输出本次正确率与剩余待复习数。此后每天收尾都跑一次。", "e": "工具跑通且两道LC AC"})

day(79, 12, "数据结构八股+算法题日", [
    "复习复杂度/树/哈希/图的高频问答",
    "LeetCode 322零钱兑换 + 347前K高频(自己写)",
    "错题入本，quiz收尾"],
    ["DP入门", "哈希计数", "堆/桶排序思想", "口述复杂度"],
    [("动态规划", "https://www.runoob.com/data-structures/dsa-dynamic-programming.html", RUNOOB),
     ("动态规划(OI-Wiki)", "https://oi-wiki.org/dp/", OIWIKI),
     ("零钱兑换", "https://leetcode.cn/problems/coin-change/", LC),
     ("前K个高频元素", "https://leetcode.cn/problems/top-k-frequent-elements/", LC)],
    {"t": "两题+口述卡", "d": "LC 322与347各AC(卡住20分钟看题解后必须合上重写)；每题写一张口述卡：思路/复杂度/易错点。quiz.py收尾自测。", "e": "2题AC+2张口述卡"})

day(80, 12, "网络八股突击", [
    "重读HTTP与TCP两篇长文，只看自己错过的点",
    "口述30道网络高频题(录音或文字)",
    "薄弱题入mistakes，quiz收尾"],
    ["HTTP高频题", "TCP状态机", "HTTPS握手", "口述表达"],
    [("HTTP常见面试题", "https://xiaolincoding.com/network/2_http/http_interview.html", XIAOLIN),
     ("TCP三次握手四次挥手", "https://xiaolincoding.com/network/3_tcp/tcp_interview.html", XIAOLIN),
     ("408计算机网络", "https://csgraduates.com/computer_network/", CSG)],
    {"t": "网络口述30题", "d": "teach.py对'计算机网络'出10题+从mistakes抽20题，全部口述作答，AI评分低于1分的重学并记录页码链接。", "e": "正确率较D70提升且网络题ready≤5"})

day(81, 12, "操作系统八股突击", [
    "重读进程线程与死锁两篇的面试题部分",
    "口述OS高频题并复跑D60-61的代码题",
    "quiz收尾"],
    ["进程线程高频题", "同步与死锁", "内存与置换", "代码题复跑"],
    [("进程线程基础知识", "https://xiaolincoding.com/os/4_process/process_base.html", XIAOLIN),
     ("怎么避免死锁？", "https://xiaolincoding.com/os/4_process/deadlock.html", XIAOLIN),
     ("408操作系统", "https://csgraduates.com/operating_system/", CSG)],
    {"t": "OS口述+代码复跑", "d": "不看代码重写banker.py核心判断函数(限时20分钟)；teach.py出10道OS题口述；对比D70正确率。", "e": "banker.py盲写通过+OS题正确率提升"})

day(82, 12, "计组+数据结构综合刷题", [
    "复习计组：Cache/流水线/磁盘三个计算器重跑",
    "LeetCode 215数组中第K大(自己写)",
    "四门综合quiz收尾"],
    ["计算题手感", "快速选择/堆", "综合自测", "时间分配"],
    [("408计算机组成原理", "https://csgraduates.com/constitution_principle/", CSG),
     ("408全家桶-数据结构", "https://408-family.netlify.app/ds", FAM408),
     ("数组中的第K个最大元素", "https://leetcode.cn/problems/kth-largest-element-in-an-array/", LC)],
    {"t": "三计算器重跑+LC215", "d": "cache_calc/pipeline/disk_sched各跑一遍内置例题确保全对；LC 215手写堆版AC；quiz.py综合抽20题。", "e": "例题全绿+LC AC+综合正确率≥80%"})

day(83, 12, "项目深问与架构文档", [
    "给毕业项目写arch.md：架构图+数据流+API表",
    "预演深挖问题：为什么这么设计/瓶颈/改进",
    "准备一个你踩过的最深的坑的完整故事"],
    ["架构图", "设计取舍", "性能瓶颈", "故事化表达"],
    [("Flask Blueprints", "https://flask.palletsprojects.com/en/stable/blueprints/", FLASK),
     ("ChromaDB文档", "https://docs.trychroma.com/docs/overview/introduction", CHROMA)],
    {"t": "arch.md+深挖题库", "d": "画架构图(文字版即可)：前端/Flask/SQLite/AI接口/资源库五块+数据流；列出5个必被问的设计问题并写好答案(每个含取舍)。", "e": "arch.md完整且5问答有具体数字/例子"})

day(84, 12, "毕业日：模拟面试与84天总结", [
    "完整模拟面试：自我介绍2min+项目深挖+手撕1题+八股5题",
    "AI助教评分并生成最终能力雷达",
    "写毕业总结与下一个84天计划，tag v2.0"],
    ["模拟面试全流程", "时间控制", "能力盘点", "下一阶段规划"],
    [     ("小林简历", "https://www.xiaolincoding.com/project/xiaolinnote/", AGENT),
     ("LeetCode题目列表", "https://leetcode.cn/problemset/algorithms/", LC),
     ("LeetCode两数之和", "https://leetcode.cn/problems/two-sum/", LC)],
    {"t": "毕业答辩", "d": "用teach.py+quiz.py组合完成：模拟面试评分≥80；写graduation.md(84天数据：完成天数/AC题数/项目数/最大变化)+下一个84天路线；全部push打tag v2.0。", "e": "v2.0标签+graduation.md入库"})

# ===== 元数据与输出 =====
STAGES = [
    {"stage": 1, "name": "Python入门", "range": "D1-7", "goal": "语法/函数/文件打底，产出命令行Todo(毕业作品1)"},
    {"stage": 2, "name": "Python进阶", "range": "D8-14", "goal": "推导式/模块/OOP/调试，产出文件整理器(毕业作品2)"},
    {"stage": 3, "name": "Git与SQL", "range": "D15-21", "goal": "版本控制+关系型查询，产出SQL练习器"},
    {"stage": 4, "name": "pandas数据分析", "range": "D22-28", "goal": "清洗/聚合/可视化，产出成绩分析报告(毕业作品3)"},
    {"stage": 5, "name": "Flask Web开发", "range": "D29-35", "goal": "HTTP/模板/数据库/API，产出TodoWeb(毕业作品4)"},
    {"stage": 6, "name": "AI应用开发", "range": "D36-42", "goal": "魔搭API/提示词/RAG/Agent，产出AI助教(毕业作品5)"},
    {"stage": 7, "name": "408计算机网络", "range": "D43-49", "goal": "分层/HTTP/TCP/IP+socket实战，产出netprobe(毕业作品6)"},
    {"stage": 8, "name": "408数据结构", "range": "D50-56", "goal": "复杂度/线性结构/排序哈希图+LeetCode约15题"},
    {"stage": 9, "name": "408操作系统+C启蒙", "range": "D57-63", "goal": "内存/进程/调度代码题，C语言看懂为主"},
    {"stage": 10, "name": "408计组+综合", "range": "D64-70", "goal": "四个计算器工具+408错题本"},
    {"stage": 11, "name": "毕业项目冲刺", "range": "D71-77", "goal": "spec/抓取模块/测试/AI助教Web化/作品集"},
    {"stage": 12, "name": "模拟面试与毕业", "range": "D78-84", "goal": "错题循环/四门八股/架构文档/模拟面试/毕业v2.0"},
]

def main():
    days = sorted(D, key=lambda x: x["day"])
    assert len(days) == 84, f"应有84天，实际{len(days)}"
    for i, d in enumerate(days, start=1):
        assert d["day"] == i, f"天数断档: 期望{i} 实际{d['day']}"
        assert d["tasks"] and d["kp"] and d["res"] and d["hw"], f"D{i} 内容不完整"
        for r in d["res"]:
            assert r["u"].startswith("https://"), f"D{i} 非https: {r['u']}"
        d["date"] = (START + datetime.timedelta(days=i - 1)).isoformat()
    plan = {
        "meta": {
            "start": START.isoformat(),
            "total_days": 84,
            "generated": datetime.datetime.now().isoformat(timespec="seconds"),
            "note": "所有资源链接均为2026-09-26实测HTTP 200的真实教材章节；"
                    "每天学完点'确认明天学这个'才会抓取明天资源正文存resources/供核对；"
                    "课后作业一律为动手写代码，不会可求助AI但要理解。",
        },
        "stages": STAGES,
        "days": days,
    }
    out = r"D:\VibeBuddy\study-buddy\plan.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    total_res = sum(len(d["res"]) for d in days)
    print(f"OK plan.json 84天 / {len(STAGES)}阶段 / {total_res}条资源 / D1={days[0]['date']} D84={days[-1]['date']}")

if __name__ == "__main__":
    main()
