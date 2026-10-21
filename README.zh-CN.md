# 3D 产品经验契约（3d-product-experience）

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
| 校验器 | `src/`（零依赖） | `p3d validate --file manifest.json --strict --strict-privacy` |
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

## 许可

MIT。
