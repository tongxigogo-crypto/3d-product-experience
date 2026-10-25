# 物理玻璃、液体、光路与明暗室材质配方

本参考手册总结了在 Three.js (r160+) 中实现物理级真实感透明器皿与光学实验的确定性参数。

---

## 1. 物理玻璃材质配方（Glass Material）

在 WebGL 中模拟真实玻璃，切勿使用传统的 `transparent: true` 与 `opacity`，必须使用物理透射（Transmission）：

```javascript
import * as THREE from 'three';

export function createPhysicalGlassMaterial() {
  return new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0xffffff),
    metalness: 0.0,
    roughness: 0.04,                // 极低粗糙度产生清澈的高光锐利感
    transmission: 0.98,             // 物理透射率（光线穿透）
    ior: 1.52,                      // 冕牌光学玻璃折射率 (Crown Glass)
    thickness: 0.015,               // 虚拟厚度，影响内部折射深度与吸收
    specularIntensity: 1.0,
    specularColor: new THREE.Color(0xffffff),
    envMapIntensity: 1.2,           // 环境反射强度，确保反射出真实的 HDR 倒影
    transparent: false,             // 物理透射材质不要设为普通透明
    depthWrite: true,
  });
}
```

---

## 2. 液体着色与防穿模配方（Liquid Material）

透明液体在玻璃容器内部时，如果表面几何完全重叠会导致深度冲突（Z-Fighting）出现黑色斑纹。

**规避策略**：
- 液体模型的半径缩放比例设为玻璃内壁的 `0.998`；
- 使用体积吸收色（`attenuationColor`）表现液体纵深浓度。

```javascript
export function createLiquidMaterial(options = {}) {
  const {
    color = 0x88ccff,
    ior = 1.333,                    // 水的折射率
    attenuationDistance = 0.05,     // 衰减距离：越小颜色越浓厚
    transmission = 0.95
  } = options;

  return new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(color),
    metalness: 0.0,
    roughness: 0.02,
    transmission: transmission,
    ior: ior,
    thickness: 0.03,
    attenuationColor: new THREE.Color(color),
    attenuationDistance: attenuationDistance,
    transparent: false,
    depthWrite: true,
  });
}
```

---

## 3. 光学光束与折射渲染（Ray & Refraction Optics）

在暗室光学实验中，光线表现为实体光束与聚焦点：

- **入射光束**：采用带细微透明渐变与发光强度的线段或圆柱体（`MeshBasicMaterial` 或 自定义 Shader，开启加法混合 `blending: THREE.AdditiveBlending`）；
- **动态折射几何体计算**：
  在主光轴上实时根据斯涅尔定律（Snell's Law）计算折射点：
  $$n_1 \cdot \sin(\theta_1) = n_2 \cdot \sin(\theta_2)$$
  当光线从密介质射向疏介质且入射角超过临界角 $\theta_c = \arcsin(n_2 / n_1)$ 时，触发全反射模式，折射光线强度瞬间清零，反射光线强度升为 100%。

---

## 4. 布光分室矩阵参数

```javascript
// 明室（化学/通用产品展示）
export function setupBrightStudio(scene) {
  const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 1.2);
  hemiLight.position.set(0, 20, 0);
  scene.add(hemiLight);

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.5);
  keyLight.position.set(5, 10, 7);
  keyLight.castShadow = true;
  scene.add(keyLight);
}

// 暗室（物理光学/激光/发光场）
export function setupDarkOpticsStudio(scene) {
  scene.background = new THREE.Color(0x05070a); // 深青黑色，保留微弱科技纵深感
  
  const weakAmbient = new THREE.AmbientLight(0x223344, 0.4); // 仅微微照亮刻度尺与光学导轨
  scene.add(weakAmbient);
}
```
