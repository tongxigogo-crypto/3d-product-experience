# 3D 产品经验契约（3d-product-experience）

> **许可：CC BY-NC 4.0，禁止商用。** 转载、翻译、摘要、改写都**必须署名并回链**，缺一项就不算合规。细则见 [NOTICE.md](NOTICE.md)。

给 Three.js / glTF 产品展示页用的一套**契约 + 校验器**。它不渲染画面，它做两件事：

1. 阻止产品展示页悄悄改掉已经验收过的产品外观；
2. 把「我看着还行」变成可核查的记录。

> 英文是主文档（[README.md](README.md)）。本页只做中文导读。

## 它防的三个真实事故

| 事故 | 现场长什么样 | 这里给什么 |
| --- | --- | --- |
| 资产漂移 | 有人重新导出 GLB，轮廓移了 4%，构建依然绿 | 清单必须携带冻结的 SHA-256，CI 可 diff |
| 演示冒充产品 | AI 生成的网格被当成 1:1 数字孪生，螺纹是编的，开合是猜的 | 强制标注 `demo`、记录 provenance、能力阶梯禁止装载产品没有的资产 |
| 测试绿、画面废 | lint/unit/build 全过，没人用手机打开过页面 | 视觉验收是独立硬门，任何自动化都替代不了 |

## 三件东西

| 层 | 位置 | 作用 |
| --- | --- | --- |
| 契约 | `references/product-capability-contract.md` | 渲染器无关的产品清单：语义节点、材质、热点、机位预设、分平台资产变体、兜底、来源、能力标记 |
| 几何与材质配方 | `references/fabric-apparel-recipe.md`<br>`references/image-to-3d-pipeline.md`<br>`references/glass-liquid-optics-recipe.md` | 服饰软质产品（`apparel-garment`）PBR 微绒毛 Sheen、J型袖窿、车线雕刻；AI 图生 3D 四步法重构与一模多款极速换图批量生成（1秒/款）；光学玻璃透明与液体折射配方 |
| 校验与批处理工具 | `src/` & `scripts/`（零外部 npm 依赖） | `p3d validate` 清单校验；`decimate_ai_glb.py`（AI 模型四步法重构与单母版多款批量生成器）；`blender_headless_garment.py` 与 `blender_headless_lathe.py` |
| Agent 技能 | `SKILL.md` | 给 AI 编码 Agent 的执行步骤：立基线 → 分能力 → 建契约 → 记来源 → 分层验证 → 收口 |

## 快速开始

```sh
git clone https://github.com/tongxigogo-crypto/3d-product-experience.git
cd 3d-product-experience
npm test                    # 18 个契约测试，无需安装依赖
npm run validate:examples   # 校验两个示例清单
npm run demo                # http://localhost:4173
```

## 能力阶梯

叠加式，产品只声明自己真正有的：

`static` → `interactive` → `assembly` → `spatial`

一条静态开合演示，不是编造螺纹的许可证；`spatial` 也不等于自由行走。

## 诚实范围（0.2.0）

- 校验器和测试已实现，Node 20 / 22 通过。
- 清单契约在一个商业产品展示（Web）和一个小程序构建上用过；这两个项目是私有的，所以本仓库不引用任何读者无法核验的数字。
- 色彩一致性（CIEDE2000）只作为契约文档提供，没有随仓库附代码。
- 隐私检查依赖系统 `exiftool`；缺失时退出码 `2` 并报告「未验证」，不会假装干净。

## 许可与商用限制（License）

本项目采用 **[CC BY-NC 4.0（署名-非商业性使用 4.0 国际许可）](LICENSE)**。

### ⚠️ 严正声明：禁止商业化与第三方平台打包转售

1. **仅限非商业用途**：仅供个人学习、技术研究与内部非商业性测试免费使用。
2. **严禁第三方平台收费转售**：未经原作者书面明确授权，**严禁**任何个人或机构将本项目的任何内容（包括但不限于 3D 产品经验规范、Skill 定义、Three.js/glTF 契约规范、校验脚本及技术文档）打包、二次封装、上架转售至任何第三方智能体平台或应用集市（包括但不限于腾讯 WorkBuddy、Coze、Dify、GPT Store 等）。
3. **保留追责权利**：如发现任何去署名搬运、违规转售或商业化变现行为，原作者将向相关平台提起侵权下架投诉并保留追究法律责任的权利。

### 转载必须署名（这一条以前没写清楚，现在写清楚）

CC BY-NC 4.0 对「分享」和「改编」规定了三项**同时**成立的义务。**缺一项就不算合规**：

| 义务 | 具体做法 |
|---|---|
| 署名 | 写明来源 `tongxigogo-crypto`，并给仓库地址 `https://github.com/tongxigogo-crypto/3d-product-experience` |
| 标明许可 | 给出许可链接 `https://creativecommons.org/licenses/by-nc/4.0/` |
| 标明修改 | 改过、翻译过、删减过、重新排版过，都要写出来 |

翻译、摘要、改写、重新配图——在法律上都算「改编」，**不会因为「我没照抄原文」就免除署名义务**。

只在 SEO 字段里塞作者名、正文里不给署名也不给链接；或者复制时顺手删掉许可声明和禁止商用条款——**这两种都不算署名**，都算违规。

完整的转载要求、已记录的违规案例、以及商业授权申请方式，见 **[NOTICE.md](NOTICE.md)**。
