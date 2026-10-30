# 授权与使用边界声明 / Notice on License, Attribution and Commercial Use

本文件是对 [LICENSE](LICENSE) 的**通俗解释与执行说明**，不替代 LICENSE 正文。
如果本文件与 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 法律文本冲突，**以法律文本为准**。

This file explains how the license in [LICENSE](LICENSE) is meant to be applied. It does not replace the license text. Where this file and the [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) legal code disagree, **the legal code governs**.

---

## 一、你可以做什么 / What you may do

1. **读、学、跑、改。** 个人学习、技术研究、内部评估、非商业项目，全部免费，不需要事先申请。
2. **在自己的项目里使用。** 把清单契约、校验器、参考文档用在你自己的**非商业**产品里，可以，不必告知我。
3. **引用和讨论。** 写文章、做视频、开分享会讲到本项目，可以，只要按下面第二节署名。
4. **分发。** 非商业地转发、镜像、打包本仓库，可以，只要按下面第二节署名。

## 二、署名怎么做才算合规 / Attribution is not optional

CC BY-NC 4.0 对「分享」和「改编」规定了三项**同时**成立的义务。缺任何一项，就不算合规使用：

| 义务 | 具体做法 |
|---|---|
| **署名** | 写明来源为 `tongxigogo-crypto`，并给出仓库地址 `https://github.com/tongxigogo-crypto/3d-product-experience` |
| **标明许可** | 给出许可链接 `https://creativecommons.org/licenses/by-nc/4.0/`，并说明本文受其约束 |
| **标明修改** | 如果你改过、翻译过、删减过、重新排版过，明确写出来 |

**以下这些做法，全部属于「未履行署名义务」：**

- 只写「整理自网络」「来源：GitHub」而不给账号和链接；
- 把内容机翻成中文后发布，不标注译者、来源和许可；
- 把 `SKILL.md` 的内容改写成一篇「XX 工具介绍」然后当原创发；
- 只在 `<meta keywords>` 或 SEO 字段里塞上作者名，正文里不署名、不给链接；
- 复制时顺手删掉文末的许可声明和禁止商用条款。

> **翻译、摘要、改写、重新配图，在法律上都是「改编（Adapt）」**，不因为「我没照抄原文」而免除署名义务。

## 三、你不可以做什么 / Prohibited

1. **商业使用。** 包括但不限于：付费课程、付费社群、付费专栏、商业咨询交付物、企业内部商业项目、以本项目为核心能力出售的产品或服务。
2. **平台打包转售。** 未经书面授权，禁止把本项目（全部或部分）打包、封装、改名后上架到任何第三方智能体平台、应用集市、付费知识社区。包括但不限于腾讯 WorkBuddy、Coze、Dify、GPT Store、各类「AI 技能商店」。
3. **去署名分发。** 见第二节。
4. **声称作者身份。** 禁止以任何方式暗示你对本项目拥有著作权，或暗示原作者为你的使用背书。

**需要商业授权**的，看第四节，或直接开 Issue 说明用途。

## 四、申请授权 / Requesting permission

- 商业使用、平台分发、企业内训、二次销售：请在本仓库开 Issue，标题前缀 `[License]`，说明使用方、用途、范围、期限。
- 我保留**拒绝**和**附加条件**的权利，也保留**免费批准**的权利——但批准必须是**书面的**。口头同意、默认、沉默都不构成授权。

## 五、已记录的违规使用 / Recorded non-compliant use

本仓库维护者会记录已核实的去署名搬运与违规转售。记录标准：**能固定证据、能复现、能指名到具体 URL 与时间**。不做推测性指控。

### 2026-10-25 · `alixixi.com`

| 项 | 内容 |
|---|---|
| URL | `https://www.alixixi.com/wz/663874.html` |
| 页面标题 | 《3d-product-experience：AI Agent 工具与自动化开发指南》 |
| 搬运范围 | `SKILL.md` 全文的机器翻译版本 |
| 违规事实 | 无署名、正文零外链、许可声明与禁止商用条款被完整删除 |
| 证据 | 渲染后 DOM、纯文本、截图，均带 SHA-256，由维护者留档 |

核对方法（任何人可复现）：该页面出现了 `SceneProductAnchor`、`ViewerSession`、`poc-decision-record`、`validate-product-manifest.mjs` 等本仓库自造标识符共 21 项，章节顺序与本仓库 `SKILL.md` 完全一致；同时页面内 `非商业`、`商用`、`CC BY-NC` 三个关键词命中数均为 **0**。

**如果上述记录有误，欢迎在本仓库开 Issue 提供反证，核实后我会更正或删除。**

## 六、发现侵权怎么报 / Reporting

开 Issue，标题前缀 `[Report]`，附上 URL、搬运页面截图、以及与本仓库对应文件的比对说明。

我不接受「帮我去骂」这类请求，也不做公开挂人以外的私刑式处理。我能做的是：核实、记录、要求下架、必要时走平台投诉。

## 七、这份声明本身的边界 / Limits of this notice

- 本声明**只管本仓库的内容**。你在自己项目里独立写出的 Three.js / glTF 契约，与本文无关，不受约束。
- 引用本仓库提到的第三方库、标准、论文，不受本许可约束，请遵守它们各自的许可。
- 本声明不构成法律意见。真要打官司，请咨询律师。

---

最后更新：2026-10-29
