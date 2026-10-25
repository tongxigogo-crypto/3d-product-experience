# 物理状态机与渲染层解耦架构

本规范用于指导开发“科学现象随参数连续真实变化”的 Web3D 交互场景，坚决杜绝使用死板的预制动画代替物理规律。

---

## 1. 架构总览

```
[ 用户交互 (UI / 鼠标拖拽 / 滑块) ]
                │ (变更参数)
                ▼
┌──────────────────────────────────────────────┐
│       科学状态引擎 (State Engine)             │
│  - 纯数学计算与科学定律公式                     │
│  - 独立运行，不依赖 Three.js / WebGL          │
│  - 可脱离界面直接进行 Node.js 自动化单元测试     │
└──────────────────────┬───────────────────────┘
                       │ (只读状态快照)
                       ▼
┌──────────────────────────────────────────────┐
│       渲染同步层 (Render Synchronizer)        │
│  - 每一帧从 State Engine 读取当前状态           │
│  - 更新 Mesh 顶点位置、粒子速度、刻度与光路     │
└──────────────────────────────────────────────┘
```

---

## 2. 状态机设计示例（以实验为例）

```javascript
export class SimulationStateEngine {
  constructor() {
    this.voltage = 0.0;            // 施加电压 (V)
    this.resistance = 5.0;         // 等效电阻
    this.timeElapsed = 0.0;        // 运行时间 (s)
    
    // 产物累计状态
    this.h2Volume = 0.0;           // 氢气体积 (mL)
    this.o2Volume = 0.0;           // 氧气体积 (mL)
    this.bubbleRate = 0;           // 气泡产生速率
  }

  setVoltage(v) {
    this.voltage = Math.max(0, Number(v));
    // 当电压小于水的分解临界电压 (1.23V) 时不发生反应
    if (this.voltage < 1.23) {
      this.bubbleRate = 0;
    } else {
      // 速率与超额电压成正比
      this.bubbleRate = Math.floor((this.voltage - 1.23) * 12);
    }
  }

  tick(deltaSeconds) {
    if (this.bubbleRate <= 0) return;
    
    this.timeElapsed += deltaSeconds;
    // 严格遵循法拉第电解定律与 2:1 化学计量比
    const producedO2 = 0.05 * (this.voltage - 1.23) * deltaSeconds;
    const producedH2 = producedO2 * 2.0;

    this.o2Volume += producedO2;
    this.h2Volume += producedH2;
  }

  getSnapshot() {
    return {
      voltage: this.voltage,
      h2Volume: this.h2Volume,
      o2Volume: this.o2Volume,
      ratio: this.o2Volume > 0 ? (this.h2Volume / this.o2Volume).toFixed(2) : '2.00',
      bubbleRate: this.bubbleRate
    };
  }
}
```

---

## 3. 屏幕投影距离吸附（Screen Distance Snapping）

当用户在 3D 空间拖拽器材、移动电极或滑动透镜时，纯 3D 距离吸附受相机透视畸变影响容易失控。

**标准做法**：
1. 将 3D 锚点位置通过 `vector.project(camera)` 转换为屏幕像素坐标 $(x_{screen}, y_{screen})$；
2. 计算鼠标指针到屏幕锚点的 Euclidean 像素距离；
3. 当屏幕距离 $< 25\text{px}$ 时，触发吸附锁死，播放微小声效并高亮提示线，极大提升非专业用户的交互成功率。
