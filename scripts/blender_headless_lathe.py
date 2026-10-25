#!/usr/bin/env python3
"""
Blender Headless Lathe Tool (闭合双层壁厚旋转体程序化建模脚本)
用于无头模式下通过纯代码生成符合物理折射要求的透明玻璃器皿、透镜或圆柱容器。

运行方式:
  blender -b --python blender_headless_lathe.py -- ./output/apparatus.glb [preset]
"""

import sys
import os
import math

def build_apparatus(output_path, preset="flask"):
    try:
        import bpy
        import bmesh
    except ImportError:
        print("错误: 本脚本必须在 Blender 环境中以无头模式运行 (--python)")
        sys.exit(1)

    # 1. 清空默认场景对象
    bpy.ops.wm.read_factory_settings(use_empty=True)

    mesh = bpy.data.meshes.new("ApparatusMesh")
    obj = bpy.data.objects.new("ApparatusObject", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    # 2. 定义截面轮廓点（米制单位，带真实双层壁厚）
    # 轮廓按顺时针/逆时针形成封闭线段：外壁顶点 -> 底部厚度 -> 内壁顶点 -> 封口
    wall_thickness = 0.0015  # 1.5 mm 壁厚

    if preset == "lens":
        # 凸透镜剖面 (中央厚度 8mm, 边缘厚度 1.5mm, 直径 50mm)
        profile_points = [
            (0.0, 0.004),           # 前表面中心
            (0.015, 0.0035),
            (0.025, 0.00075),       # 边缘上点
            (0.025, -0.00075),      # 边缘下点
            (0.015, -0.0035),
            (0.0, -0.004)           # 后表面中心
        ]
    else:
        # 默认标准烧杯/反应柱剖面 (直径 60mm, 高度 120mm, 底部加厚)
        radius = 0.030
        height = 0.120
        profile_points = [
            (0.0, 0.0),                                       # 外底中心
            (radius - 0.004, 0.0),                            # 外底倒角
            (radius, 0.004),                                  # 外侧壁底部
            (radius, height),                                 # 外侧壁顶口
            (radius + 0.002, height),                         # 翻边外沿
            (radius - wall_thickness, height),                # 翻边内沿
            (radius - wall_thickness, 0.003 + wall_thickness),# 内侧壁底部
            (0.0, 0.003 + wall_thickness)                     # 内底中心
        ]

    # 创建截面顶点
    verts = [bm.verts.new((p[0], 0, p[1])) for p in profile_points]
    for i in range(len(verts) - 1):
        bm.edges.new((verts[i], verts[i + 1]))

    # 3. 绕 Z 轴执行 360 度旋转拉伸 (Spin)
    bmesh.ops.spin(
        bm,
        geom=bm.edges[:] + bm.verts[:],
        angle=math.radians(360.0),
        steps=48,
        axis=(0, 0, 1),
        cent=(0, 0, 0)
    )

    # 4. 移除重叠重复点并重算物理法线
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()

    # 5. 设置平滑着色
    for poly in mesh.polygons:
        poly.use_smooth = True

    # 6. 导出干净的 glTF/GLB 模型
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_extras=True
    )
    print(f"成功导出程序化 3D 几何体 (真实双层壁厚): {output_path}")

if __name__ == "__main__":
    args = sys.argv
    if "--" in args:
        user_args = args[args.index("--") + 1:]
    else:
        user_args = []

    out = user_args[0] if len(user_args) > 0 else "./output/apparatus.glb"
    pre = user_args[1] if len(user_args) > 1 else "flask"
    build_apparatus(out, pre)
