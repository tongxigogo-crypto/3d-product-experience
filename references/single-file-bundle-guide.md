# 单文件离线 HTML 打包工程指南

本指南阐述如何将 Three.js 运行时、二进制 3D 模型（GLB）、环境贴图（HDR/JPG）与业务逻辑一次性压入**单个独立 HTML 文件**，实现无需任何网络与服务端的双击运行。

---

## 1. 为什么坚持单文件交付？

1. **避免跨域报错**：用户直接双击 `index.html`（`file://` 协议）时，浏览器会禁止通过 `fetch` 读取外部 `.glb` 或 `.hdr` 文件。内联后完全规避此限制。
2. **零安装门槛**：不要求用户、教师或客户电脑安装 Node.js、Python 或搭建 Web 服务器。
3. **资产不可分割**：不会出现“拷走了 html 漏拷了 textures 文件夹导致材质全黑”的低级失误。

---

## 2. 基于 esbuild 的打包流程

通过 Node.js 构建脚本（见 `templates/build.mjs`）：

1. **资产转码**：
   - 将 glTF / GLB 模型读取为 Buffer，转为 Base64 Data URL 或通过 Uint8Array 嵌入；
   - 将环境图、音频转为 Base64 字符串；
2. **JS Bundle 打包**：
   - `esbuild.buildSync` 将 Three.js 库与状态机代码打包压缩（minify）；
3. **HTML 模板注入**：
   - 将 CSS 样式内嵌进 `<style>` 标签；
   - 将生成的 JS 代码注入进 `<script>` 标签；
   - 最终写盘为单独的 `.html` 文件，体积控制在 2MB~12MB 之间（视模型与贴图精度而定）。

---

## 3. 性能优化要点

- **模型轻量化**：使用 Draco 压缩或在 Blender 中精简多余面数，单个零件控制在 5000 面以内；
- **环境贴图尺寸**：环境漫反射建议使用 512×256 或 1024×512 尺寸的 EXR/HDR，转为低压缩比 JPG 替代以缩减内嵌体积；
- **垃圾回收**：场景切换或重置时，显式调用 `geometry.dispose()` 与 `material.dispose()`，确保长时间演示不发生内存泄漏。
