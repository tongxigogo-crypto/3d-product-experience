# 软质服装与纺织面料物理仿真配方指南 (Fabric & Apparel Recipe)

> 规范版本：v1.4.0 · 适用产品：T恤、卫衣、衬衫、抱枕、纺织品与双面印花服饰

---

## 0. 路线优先级与实证对比裁决（Route Priority Verdict）

在“狗狗趣味拉链短袖 T 恤”双路线实测与用户终审验收中，明确得出以下跨项目选型定论：
1. **首选主路线（AI 图生 3D + 减面重投影四步法，商用推荐）**：
   - 采用腾讯混元 3D（Hunyuan3D）或 Tripo3D 生成初始底模 GLB $\to$ 无头减面至 50,000 面 $\to$ 坐标系归一化 $\to$ 高清原图正交 UV 重投影 $\to$ PBR Sheen 材质注入；
   - **核心优势**：天然具备真实织物的有机立体饱满度、自然垂坠褶皱与人体工学轮廓，视觉还原度显著优于纯代码参数化放样。
2. **备选保底路线（纯代码参数化四边形放样，用户视觉验收 60 分及格基线）**：
   - 仅在**明确禁止导入外部 3D 模型**或需零外部依赖验证时启用；
   - **局限与边界**：即便引入 J 型立体袖窿、`CorrectiveSmooth` 曲率平滑与后置微米级车线雕刻，并在独立挑刺子智能体（Adversarial Critic）取得 `9.32/10` 诊断分，其**宏观 3D 有机形态仍偏几何规整，对比上不如直接图生 GLB 自然**。子智能体评分仅作工程几何/材质诊断，绝不替代用户最终视觉验收。

---

## 1. 核心挑战与失败教训总结

在过去服装类产品 3D 转换测试中，模型常陷入以下灾难性误区：
1. **工具错配**：将回转体工具（Lathe 车削）套用至非轴对称服装，生成粗暴圆筒；
2. **布尔切孔反模式（严禁重试）**：试图用布尔差集在圆柱曲面上切开领口和袖口，导致顶点撕裂、非流形边缘（Non-manifold edges）、法线错乱与飞面；
3. **机械结构空耗**：针对平面印花（如拉链、口袋图样）过度设计动态布尔开缝与三维滑块，导致几何极其脆弱；
4. **贴图串色与拉伸**：前后单图使用单一材质混贴，在侧缝处严重拉扯畸变；
5. **离线跨端白屏**：在 `file://` 协议下直接使用动态 `import(blobUrl)` 导致跨源沙箱拦截，页面卡死在加载状态。

---

## 2. 几何拓扑法则：四边形控制笼与连续袖孔环

### 2.1 四边形网格（Quad Cage）
- 躯干采用 $11 \times 11$ 规则四边形网格（10 列 $\times$ 10 行）；
- 前幅面朝 $-Y$（与相机默认视角对齐），后幅面朝 $+Y$；
- 领口通过顶行中心两列顶点向后/向下平滑下凹形成，不使用切割操作。

### 2.2 自然溜肩弧度（Shoulder Slope）
- 肩线最高点必须位于颈根处（$|x| \approx 0.08$ 米）；
- 从颈根向外侧袖孔延伸，高度单调向下平滑倾斜：
  $$Z_{\text{drop}} = \max(0, |x| - 0.06) \times 0.26 \times \left(\frac{r}{N_z - 1}\right)^{1.5}$$
- 杜绝在锁骨处出现突起峰值（耳朵状驼峰）。

### 2.3 J 型立体袖窿与连续袖孔环（Tailored J-Curve Armscye & Local-Centroid Cuff）
- **J 型立体袖窿裁剪**：肩端点半宽（$W_{\text{shoulder}} \approx 0.178\text{ m}$）必须宽于腋下半宽（$W_{\text{pit}} \approx 0.155\text{ m}$），从而让三角肌到袖山形成连续的 C1/C2 凸弧，消除方盒躯干向内凹陷的折角；
- **袖管下垂与防穿模内缩**：短袖沿自然垂挂轴（离垂线约 $20.8^\circ$）放样；在构建袖口内折边（Inner Cuff Lining）时，必须向**每圈参考外环自身的局部圆心（Local Ring Centroid）**按比例内缩：
  $$\mathbf{p}_{\text{inner}} = \mathbf{c}_{\text{ring}} + (\mathbf{p}_{\text{ref}} - \mathbf{c}_{\text{ring}}) \cdot s_{\text{rad}} \quad (s_{\text{rad}} < 1.0)$$
  严禁沿全局固定方向平移内壁，否则会导致袖口深色内衬刺穿较短的腋下内袖外壁（形成暗灰月牙穿模伪影）。

### 2.4 曲面平滑与后置微米级双针车线雕刻（Post-Smoothing Hairline Seams）
- 先施加 2 阶 Catmull-Clark 曲面细分（`Subsurf` level 2）与曲率平滑（`CorrectiveSmooth` iterations 24），消除肩袖接缝折痕；
- **关键顺序铁律**：`CorrectiveSmooth` 会抹平细微几何凹槽，因此领圈外沿、肩线、袖笼、袖口双针车线（距袖口 2.0 cm）与下摆双针车线（距底边 2.2 cm）的 **`1.1 mm` 极细缝线凹槽必须在平滑修改器应用之后（Post-Smoothing）沿顶点法线向内微雕 `1.05 mm`**，杜绝整排粗网格涂灰造成的“塑料条纹感”。

---

## 3. 面料 PBR 材质、深色印花 Sheen 遮罩与 BOX 法线投射

1. **纯棉与针织面料微绒毛高光（Sheen）**：
   - 纯棉由于微纤维漫反射，边缘具有柔和微光（`roughness: 0.88~0.92`, `metalness: 0.0`, `sheen: 0.42~0.45`）；
2. **深色印花区 Sheen 遮罩（Dark-Graphic Sheen Masking）**：
   - 白色 `Sheen` 叠加在黑色/深色印花（如黑狗毛发、深色图案）上会导致暗部泛白发灰（如 `#101216` 被抬升至 `#35383E`）；
   - 在 Blender / Shader 中必须通过亮度阈值（`RGBToBW -> ColorRamp [0.72, 0.90]`）遮罩 `Sheen Weight`，使浅色棉布保留 `0.42` 绒毛泛光，而深色印花区域 `Sheen = 0`；
3. **微针织法线贴图 BOX 投射**：
   - 当躯干正面/背面使用局部钳制 UV 映射胸前印花时，无缝针织法线贴图（Micro-Knit Normal Map）应使用 `Generated` 坐标配合 `BOX` 投影，避免下腹部因 UV 钳制（`v=0.01`）产生纵向拉伸条纹。

```javascript
const cottonMaterial = new THREE.MeshPhysicalMaterial({
  color: 0xfafafa,
  roughness: 0.89,
  metalness: 0.0,
  side: THREE.DoubleSide,
  sheen: 0.42,             // 纺织品微绒毛高光权重（深色印花区须遮罩）
  sheenRoughness: 0.55,    // 绒毛散射漫度
  sheenColor: new THREE.Color(0xffffff),
  transparent: false,      // 纯棉服装严禁开启 transparent
  alphaTest: 0             // 杜绝非透明面料的像素镂空伪影
});
```

---

## 4. 双面无串色贴图隔离（Multi-Material Slots）

在 Blender 中分配 3 个独立材质槽位，glTF 导出为独立的 Primitive 分组：
- 槽位 0 (`Mat_Front`)：正面照片投影（带印花主角）；
- 槽位 1 (`Mat_Back`)：背面照片投影（带背面揭晓元素，如尾巴、背影）；
- 槽位 2 (`Mat_Trim`)：领圈、袖口与侧缝纯白面料，采样高光与织物底色。

### UV 映射归一化公式
$$v = \frac{z - z_{\min}}{z_{\max} - z_{\min}} \cdot S_v + V_{\text{offset}}$$
$$u_{\text{front}} = 0.50 + \frac{x}{W_{\text{body}}}, \quad u_{\text{back}} = 0.50 - \frac{x}{W_{\text{body}}}$$
保证正反两面图案中心与比例完全一致，旋转 180° 时视角无缝对齐。

---

## 5. 单文件离线交付与跨端安全

1. **避免 `file://` 下的 Blob ES 模块导入**：使用 `esbuild` 打包为标准 IIFE 脚本（`window.THREE` 全局对象），彻底根除浏览器沙箱 `blob:null` 跨源拦截；
2. **内联 GLB Base64**：将经过压缩的 GLB 文件转为 Base64 内嵌在 HTML 的 `<script id="b64-glb" type="text/plain">` 中；
3. **触控与惯性平滑阻尼**：加入阻尼衰减系数 $k = 1 - 0.0016^{\Delta t}$，确保拖拽、缩放及一键切换（正面/背面/特写）体验丝滑，达到 60fps 稳定帧率。
