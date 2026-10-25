# AI 图生 3D（Image-to-3D）四步法重构与同品类“一模多款”批量生成规范

> 规范版本：v1.4.0 · 适用范围：T恤、卫衣、衬衫、软包、鞋帽等软质有机产品

本指南包含两大完整生产标准：
1. **阶段一（首件母版构建，约 15 秒）**：当遇到**全新版型**（如新款式卫衣、新领型）时，利用 AI 图生 3D（腾讯混元 3D / Tripo3D）生成初始底模，再通过 Blender 四步法重构出 **1 个标准母版 `.glb`（如 `shirt-final.glb`）**；
2. **阶段二（同品类“一模多款”极速批量生成，约 1 秒/件，零 Blender 依赖）**：**同类型产品只需要保留这 1 个母版 `.glb` 文件**，后续所有新花色、新图案款式（仅需提供新的 `front.jpg` 与 `back.jpg`），直接通过脚本替换母版内部纹理缓冲并注入离线网页模板，秒级批量产出新款 `.glb` 与单文件 `-3D.html`！

---

## 一、核心架构：为什么同品类只需 1 个母版 GLB？

```text
【阶段一：每个版型仅需做 1 次（首件母版定型）】
AI 原始高模 (T恤.glb, 150万面) 
   ──► Step 1: Decimate 减面至 52,500 面
   ──► Step 2: Apply Transform 坐标与米制尺寸归一化 (72×55 cm)
   ──► Step 3: 按法线拆分 Mat_Front / Mat_Back 双材质槽 + 烘焙正交投影 UV
   ──► Step 4: 注入 2048×2048 漫反射与针织法线贴图槽位
   ══► 产出唯一【同版型标准母版 GLB】(shirt-final.glb) + 【母版离线网页】(狗狗T恤-3D.html)

──────────────────────────────────────────────────────────────────────────────

【阶段二：同类型产品无限复用（一模多款秒级批量生产，无需再跑 AI 建模或 Blender）】
标准母版 (shirt-final.glb) + 款式 N 的正反图 (skuN_front.jpg + skuN_back.jpg)
   ──► 自动居中合成 2048×2048 纯棉本白画布 (#F6F5F1) + 自动计算梯度针织法线图
   ──► 直接二进制替换 GLB 内置纹理块 (front_diffuse / front_normal / back_diffuse / back_normal)
   ──► Base64 注入单文件 HTML 模板并替换标题
   ══► 1 秒/件 批量产出：skuN.glb + skuN-3D.html（网格、UV、光影、60fps 交互 100% 一致！）
```

---

## 二、阶段一详细步骤：全新版型首件母版构建（四步法）

当且仅当产品**几何轮廓改变**（例如从圆领短袖变为连帽卫衣）时执行一次：

### Step 1：拓扑减面与流形平滑（Decimation）
- **痛点**：混元 3D / Tripo 直接导出的 `.glb` 通常高达 80 万~150 万面，浏览器直接加载必掉帧。
- **操作**：在 Blender 中加载高模，添加 `Decimate (Collapse)` 修改器，按比例收缩至 **50,000 ~ 55,000 面**，执行 `shade_smooth()`。

### Step 2：尺度校准与变换矩阵归一化（Normalize Transform）
- **痛点**：AI 模型的原点偏移且带旋转四元数。
- **操作**：将模型居中对齐世界原点，按真实物理尺寸（如衣长 `0.72m`、胸宽 `0.55m`）缩放，执行 `bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)`。

### Step 3：正反双材质物理槽隔离与正交 UV 重投影（Zero-Bleed Orthographic UV）
- **痛点**：AI 自带贴图仅 512/1024 分辨率且前后串色。
- **操作**：
  1. 彻底丢弃 AI 原生 UV 与模糊贴图；
  2. 遍历网格多边形：法线朝前（Blender 中 $n_y \le 0$）分配至槽位 0（`Mat_Front`），法线朝后（$n_y > 0$）分配至槽位 1（`Mat_Back`）；
  3. 按包围盒归一化坐标 $(n_x, n_z) \in [0, 1]$ 写入正交投影 UV：
     - 正面：$u = 0.031 + 0.938 n_x,\quad v = 0.064 + 0.886 n_z$
     - 背面：$u = 0.969 - 0.938 n_x,\quad v = 0.064 + 0.886 n_z$

### Step 4：PBR 纯棉微绒毛材质（Sheen）与母版导出
- **操作**：绑定 2048×2048 的 `front_diffuse` / `front_normal` 与 `back_diffuse` / `back_normal`，Three.js 端配置 `MeshPhysicalMaterial`（`roughness: 0.80, metalness: 0.0, sheen: 0.65, sheenRoughness: 0.35`），导出为标准母版 `shirt-final.glb`。

#### 首件母版一键构建命令（模式 B：`--mode rebuild`）
```bash
blender -b --python scripts/decimate_ai_glb.py -- \
  --mode rebuild \
  --in_glb ./raw_ai_150w.glb \
  --front ./front.jpg \
  --back ./back.jpg \
  --out_glb ./shirt-final.glb \
  --faces 52500
```

---

## 三、阶段二详细步骤：同品类“一模多款”极速批量生成（日常主力）

一旦有了同品类的 `shirt-final.glb` 与 `product-3D.html` 母版，**后续同版型的所有新品完全不需要启动 Blender 或重新生成 3D 模型**，只需准备每款的正反面图片（`front.jpg` + `back.jpg`）。

### 方式 1：单款新品极速生成（1 秒出 `.glb` + `.html`）

```bash
python3 scripts/decimate_ai_glb.py \
  --mode swap \
  --base_glb "./shirt-final.glb" \
  --base_html "./template-3D.html" \
  --front "./新款正面.jpg" \
  --back "./新款背面.jpg" \
  --title "新款趣味短袖T恤 · 3D 可视化预览" \
  --subtitle "衣长 72 cm · 胸宽 55 cm · 纯棉重磅落肩版型" \
  --out_glb "./dist/new-shirt.glb" \
  --out_html "./dist/新款T恤-3D.html"
```

### 方式 2：多款商品一键批量生成（JSON 清单批处理）

1. 新建批量清单 `sku_batch.json`：
```json
[
  {
    "title": "款式01 · 柯基拉链短袖T恤",
    "subtitle": "260g 精梳棉 · 落肩宽松版型",
    "front": "./photos/sku01_front.jpg",
    "back": "./photos/sku01_back.jpg",
    "out_glb": "./dist/sku01.glb",
    "out_html": "./dist/款式01_柯基T恤-3D.html"
  },
  {
    "title": "款式02 · 橘猫口袋短袖T恤",
    "subtitle": "260g 精梳棉 · 落肩宽松版型",
    "front": "./photos/sku02_front.jpg",
    "back": "./photos/sku02_back.jpg",
    "out_glb": "./dist/sku02.glb",
    "out_html": "./dist/款式02_橘猫T恤-3D.html"
  }
]
```

2. 执行一行命令完成全部款式的 `.glb` 与离线 `.html` 批量生产：
```bash
python3 scripts/decimate_ai_glb.py \
  --mode batch \
  --base_glb "./shirt-final.glb" \
  --base_html "./template-3D.html" \
  --batch_json "./sku_batch.json"
```

### 内部自动化细节说明
脚本在 `--mode swap` 和 `--mode batch` 下会自动完成以下 4 件事：
1. **自动画布对齐与纯棉底色融合**：读取任意尺寸的 `front.jpg` / `back.jpg`，按母版黄金比例（宽 `75.6%`、高 `84.3%`、顶距 `10.8%`）缩放并居中贴合至 `2048×2048` 的 `#F6F5F1` 纯棉本白画布；
2. **自动生成微观法线贴图**：基于高斯平滑梯度自动计算对应的 `2048×2048` 凹凸法线图（`front_normal` / `back_normal`），使印花边缘与布料具备立体起伏受光；
3. **无损二进制热替换**：直接重写 GLB 的 `BIN` chunk 对应 `bufferView` 偏移量，**100% 保留母版原有的 52,500 面自然垂坠网格、顶点法线与正交 UV**；
4. **单文件离线 HTML 注入**：将新生成的 `.glb` 转为 Base64 替换进母版 HTML 的 `<script id="b64-glb">`，输出双击即开、60fps 运行的独立网页。
