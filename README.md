# 中大信号研习室

中山大学信号与系统备考学习工具，独立仓库。包括2008—2026年所供真题的243个可见题组、逐题推导、90余幅图解、32道原创迁移与模拟训练、40道奥本海姆第二版精选索引，以及逐章考点统计。

## 使用

- 网页：[中大信号研习室](https://nishino0525nanase.github.io/sysu-signals-study/)，由 Pages 工作流发布 `dist/`。
- Android：下载 [Releases](https://github.com/Nishino0525Nanase/sysu-signals-study/releases/latest) 或网页“资料与安装”中的 `sysu-signals-study-v1.0.1.apk`。最低 Android 7.0，可覆盖升级1.0.0并保留本机学习记录。
- APK内置全部学习内容、公式字体和配图，核心阅读无需联网，不申请网络、定位、摄像头或账号权限。
- 学习进度、收藏、错题、笔记保存在本机，支持导出和导入JSON备份。

## 内容来源与边界

真题来自用户提供的PDF，页面附原题页以便核对；讲解是独立推导，并非中大官方答案。2025资料缺四、五题，2021整理版编号跳八，未补造。2013二2(1)已知响应扫描损坏，保留严格的符号组合解并说明。其他题面歧义均在题中列出条件和相应解释。

奥本海姆精选仅给题号、小问、原书英文第二版页码与方法路线，完整题干需对照教材。32道完整训练为独立编写。统计中的70类标签是本项目人工归类，综合题跨章重复记次，不能解释为分值占比或命题概率。

本轮逐题核对订正了旧摘要中的2012初态、2016“非时变”、2019无储能、2021有限回波等，网页和统计表使用校订标注。

## 源码与构建

```
content/2008.json … 2026.json  # 各年讲解与精确图引用
content/assets/               # 原创SVG图解
content/catalog.json          # 原创训练、原书精选与资料目录
content/statistics.json       # 章节计数与逐题标注
dist/                         # 可直接托管的完整离线网页
android/                      # 原生WebView封装，HTTPS本地资源、备份与文件选择
tools/build.mjs               # 零npm依赖内容构建
```

修改内容后运行 `node tools/build.mjs`。`dist/sources/`为原题页静态资源，`dist/vendor/`为本地KaTeX与marked（各自保留许可证），`dist/downloads/`为配套文档与APK。

Android使用JDK17、SDK platform35/build-tools35编译：设置`ANDROID_JAR`、`ANDROID_BUILD_TOOLS`、私有`SIGNING_KEYSTORE`和`SIGNING_PASSWORD_FILE`后运行`android/build-apk.sh`。签名密钥不放入公开源码。代码构建和签名已通过，未在实体Android设备上验收。

## 校订

请附年份、题号、原题截图与具体推导。保留题面疑误与条件区别，不用猜测补齐缺失题。
