# 中大信号研习室

中山大学信号与系统备考学习工具，独立仓库。包括2008—2026年所供真题的243个可见题组、逐题推导、100幅中文SVG图解与4幅训练配图、32道原创迁移与模拟训练、40组奥本海姆第二版所选课后题逐小问答案，以及逐章考点统计。

## 使用

- 网页：[中大信号研习室](https://nishino0525nanase.github.io/sysu-signals-study/)，由 Pages 工作流发布 `dist/`。
- Android：下载 [Releases](https://github.com/Nishino0525Nanase/sysu-signals-study/releases/latest) 或网页“资料与安装”中的 `sysu-signals-study-v1.3.0.apk`。最低 Android 7.0，可覆盖升级旧版并保留本机学习记录。
- APK内置全部学习内容、公式字体和配图，核心阅读无需联网，不申请网络、定位、摄像头或账号权限。
- 学习进度、收藏、错题、笔记保存在本机，支持导出和导入JSON备份。

## 内容来源与边界

真题来自用户提供的PDF，页面附原题页以便核对；讲解是独立推导，并非中大官方答案。2025资料缺四、五题，2021整理版编号跳八，未补造。2013二2(1)已知响应扫描损坏，保留严格的符号组合解并说明。其他题面歧义均在题中列出条件和相应解释。

奥本海姆课后详解按题号、所选小问和英文第二版页码组织，包含必要题意简述、逐小问推导与结果检查；原始图形和完整上下文需对照教材。32道完整训练为独立编写。网页、PDF与APK共用详细答案。统计中的70类标签是本项目人工归类，综合题跨章重复记次，不能解释为分值占比或命题概率。

本轮逐题核对订正了旧摘要中的2012初态、2016“非时变”、2019无储能、2021有限回波等，网页和统计表使用校订标注。

## 源码与构建

```
content/2008.json … 2026.json  # 各年讲解与精确图引用
content/assets/               # 原创SVG图解
content/catalog.json          # 原创训练、原书课后逐步答案与资料目录
content/resources.json        # 来源证据、题号映射和独立演算的其他解法
content/statistics.json       # 章节计数与逐题标注
dist/                         # 可直接托管的完整离线网页
android/                      # 原生WebView封装，HTTPS本地资源、备份与文件选择
tools/build.mjs               # 零npm依赖内容构建
```

修改内容后运行 `node tools/build.mjs && node tools/check.mjs`。课后答案PDF由 `python3 tools/export-workbook.py` 从同一份JSON生成（需Pandoc、XeLaTeX、Inkscape及Noto CJK字体）。`dist/sources/`为原题页静态资源，`dist/vendor/`为本地KaTeX与marked（各自保留许可证），`dist/downloads/`为配套文档与APK。

Android使用JDK17、SDK platform35/build-tools35编译：设置`ANDROID_JAR`、`ANDROID_BUILD_TOOLS`、私有`SIGNING_KEYSTORE`和`SIGNING_PASSWORD_FILE`后运行`android/build-apk.sh`。签名密钥不放入公开源码。代码构建和签名已通过，未在实体Android设备上验收。

## 校订

请附年份、题号、原题截图与具体推导。保留题面疑误与条件区别，不用猜测补齐缺失题。

## 1.1.0 答案与公式修订

- 重写题目卡片预览，保留完整LaTeX片段并渲染，不删除命令或从公式中间截断。
- 40组奥本海姆所选课后题增加逐小问答案入口，32道训练补齐具体最终结果。
- 真题答案补充卷积支撑交集、系数积分、变换尺度、部分分式与初值等计算过程。
- 阅读页默认展开详细答案；打印时保留答案正文；原有学习记录ID保持不变。

## 1.2.0 中文图解、课程与其他解法

- 图中英文语义注解、坐标说明、图例和单位全部改为中文，保留数学变量及标准运算符。
- 课程资料按实际读取范围区分：已读官方讲义/字幕、已核对课程介绍、仅可检索的视频目录。B站未取得字幕的条目只作为观看导航。
- 新增24条方法补充，覆盖30道对应题目；38条课程/资料入口包含12个B站、5个慕课、17个MIT课程/讲义及4个GitHub来源。
- 其他解法按确切题号关联，参考一手课程的思路后独立推导，并写明适用条件和核验方法。外部资料的原文定位和作者信息保存在 `content/resources.json`。
- 引用课程和仓库均保留原作者链接。数学演算与中文解说由本项目独立整理，不转载课程视频或原仓库的整份教材/答案。

## 1.3.0 直接阅读的中文课程精讲

- 网页标识、浏览器/PWA图标和Android桌面图标统一为中山大学绿色校徽。原矢量来源、版权及尺寸转换说明见 `content/brand/README.md`；项目仍为个人备考整理。
- “课程精讲”默认展示12篇自成体系的中文整理，覆盖第1至11章及正交投影/匹配滤波。每篇包含结论、第一步的理由、完整例题、条件辨析、易错点、自检答案及可点开的配套题号。
- 实际读取MIT官方课程文字稿/讲义等正文后重新组织方法；未取得正文的视频保留在独立“资料出处”页，不作为已读课堂内容。24条逐题多解保留。
- 同一份 `content/study-guides.json` 同时用于网页、APK及38页中文精讲PDF。网页学习页为 `#resources`；可用 `#resources?guide=G07` 等固定链接直接进入章节。
- 公式与题号/来源映射由 `npm run check` 检查。PDF可运行 `python tools/export-course-digest.py` 生成，需要Pandoc、XeLaTeX、Inkscape及Noto CJK字体。

重绘中文图可分别运行 `tools/localize-early-figures.py`、`tools/localize-middle-figures.py`、`tools/localize-late-figures.py`；需要Matplotlib、NumPy/SciPy及Noto CJK字体。
