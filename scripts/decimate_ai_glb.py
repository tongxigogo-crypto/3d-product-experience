#!/usr/bin/env python3
"""
decimate_ai_glb.py (v1.4.0)
===========================
AI 图生 3D 底模四步法重构 & 同品类“一模多款”极速批量生成器

支持两大工作模式：
--------------------------------------------------------------------------------
【模式 A：同品类“一模多款”极速换图与批量生成（无需启动 Blender，约 0.8 秒/件）】
只要拥有 1 个已处理好的同版型母版 GLB（如 `shirt-final.glb`），即可直接替换正反面实拍图
（自动对齐尺寸、合成 2048×2048 纯棉底色与法线贴图），秒级输出新款 `.glb` 与独立离线 `-3D.html`！

1) 单款极速生成：
   python3 decimate_ai_glb.py --mode swap \
     --base_glb /path/to/shirt-final.glb \
     --base_html /path/to/狗狗T恤-3D.html \
     --front /path/to/new_front.jpg \
     --back /path/to/new_back.jpg \
     --title "新款猫咪拉链短袖T恤 · 3D 预览" \
     --out_glb /path/to/cat-shirt.glb \
     --out_html /path/to/猫咪T恤-3D.html

2) 多款批量生成（传入 JSON 清单）：
   python3 decimate_ai_glb.py --mode batch \
     --base_glb /path/to/shirt-final.glb \
     --base_html /path/to/狗狗T恤-3D.html \
     --batch_json /path/to/sku_list.json

   其中 `sku_list.json` 格式示例：
   [
     {
       "title": "款式1-柯基短袖T恤",
       "front": "./sku1_front.jpg",
       "back": "./sku1_back.jpg",
       "out_glb": "./dist/sku1.glb",
       "out_html": "./dist/sku1-3D.html"
     }
   ]

--------------------------------------------------------------------------------
【模式 B：新产品版型首件母版重构（Blender 无头四步法，约 15 秒）】
当遇到全新版型（如连帽卫衣、新领型）且只有 AI 原始百万面高模 GLB 时，在 Blender 中运行：
   blender -b --python decimate_ai_glb.py -- --mode rebuild \
     --in_glb /path/to/raw_ai_150w.glb \
     --front /path/to/front.jpg \
     --back /path/to/back.jpg \
     --out_glb /path/to/shirt-final.glb \
     --faces 52500
"""

import sys
import os
import io
import re
import json
import struct
import base64
import argparse


# ==============================================================================
# 模式 A：基于 1 个母版 GLB 的极速换图与批量打包（纯 Python + PIL + NumPy，0 Blender 依赖）
# ==============================================================================
def build_cotton_diffuse_and_normal(img_path, canvas_size=2048):
    """将输入正/背面商品图合成为 2048×2048 标准纯棉漫反射贴图与微观针织法线贴图"""
    from PIL import Image, ImageFilter
    import numpy as np

    # 1. 创建 #F6F5F1 纯棉本白画布
    bg_color = (246, 245, 241)
    canvas = Image.new("RGB", (canvas_size, canvas_size), bg_color)

    if img_path and os.path.exists(img_path):
        src = Image.open(img_path).convert("RGB")
        # 按母版标准比例缩放并居中贴合 (宽占 75.6%, 高占 84.3%)
        target_w = int(canvas_size * 0.756)
        target_h = int(canvas_size * 0.843)
        src_resized = src.resize((target_w, target_h), Image.Resampling.LANCZOS)
        ox = (canvas_size - target_w) // 2
        oy = int(canvas_size * 0.108)
        canvas.paste(src_resized, (ox, oy))

    # 编码漫反射 JPEG
    diff_buf = io.BytesIO()
    canvas.save(diff_buf, format="JPEG", quality=92, optimize=True)
    diffuse_bytes = diff_buf.getvalue()

    # 2. 由灰度梯度生成针织凹凸法线贴图 (2048×2048 RGB)
    gray = np.asarray(canvas.convert("L").filter(ImageFilter.GaussianBlur(radius=1.2)), dtype=np.float32) / 255.0
    gx = np.zeros_like(gray)
    gy = np.zeros_like(gray)
    gx[:, 1:-1] = (gray[:, 2:] - gray[:, :-2]) * 1.8
    gy[1:-1, :] = (gray[2:, :] - gray[:-2, :]) * 1.8

    nz = np.ones_like(gray)
    length = np.sqrt(gx * gx + gy * gy + nz * nz)
    nx = (-gx / length * 0.5 + 0.5) * 255.0
    ny = (gy / length * 0.5 + 0.5) * 255.0
    nz_c = (nz / length * 0.5 + 0.5) * 255.0

    norm_arr = np.stack([nx, ny, nz_c], axis=-1).clip(0, 255).astype(np.uint8)
    norm_img = Image.fromarray(norm_arr, mode="RGB")
    norm_buf = io.BytesIO()
    norm_img.save(norm_buf, format="JPEG", quality=85, optimize=True)
    normal_bytes = norm_buf.getvalue()

    return diffuse_bytes, normal_bytes


def swap_glb_textures(base_glb_path, front_jpg, back_jpg, out_glb_path):
    """直接替换母版 GLB 内的正背面漫反射与法线贴图二进制块，保持 3D 网格与 UV 100% 不变"""
    with open(base_glb_path, "rb") as f:
        data = f.read()

    magic, version, _ = struct.unpack("<III", data[:12])
    if magic != 0x46546C67:
        raise ValueError(f"Invalid GLB file: {base_glb_path}")

    json_len, json_type = struct.unpack("<II", data[12:20])
    gltf = json.loads(data[20:20 + json_len].decode("utf-8"))
    bin_offset = 20 + json_len + 8
    old_bin = data[bin_offset:]

    front_diff, front_norm = build_cotton_diffuse_and_normal(front_jpg)
    back_diff, back_norm = build_cotton_diffuse_and_normal(back_jpg)

    replacement_map = {
        "front_normal": front_norm,
        "front_diffuse": front_diff,
        "back_normal": back_norm,
        "back_diffuse": back_diff,
    }

    # 将 이미지 bufferView 映射到名称
    bv_override = {}
    for idx, img_info in enumerate(gltf.get("images", [])):
        name = img_info.get("name", "")
        bv_idx = img_info.get("bufferView")
        if name in replacement_map and bv_idx is not None:
            bv_override[bv_idx] = replacement_map[name]
        elif bv_idx is not None:
            # 若母版未按名称命名，按槽位顺序回退 (0: front_norm, 1: front_diff, 2: back_norm, 3: back_diff)
            fallback_order = [front_norm, front_diff, back_norm, back_diff]
            if idx < len(fallback_order):
                bv_override[bv_idx] = fallback_order[idx]

    # 重新组装 BIN chunk 并更新所有 bufferViews 的 byteOffset / byteLength
    new_bin_parts = []
    curr_offset = 0
    for bv_idx, bv in enumerate(gltf.get("bufferViews", [])):
        if bv_idx in bv_override:
            chunk_bytes = bv_override[bv_idx]
        else:
            old_off = bv.get("byteOffset", 0)
            old_len = bv["byteLength"]
            chunk_bytes = old_bin[old_off:old_off + old_len]

        bv["byteOffset"] = curr_offset
        bv["byteLength"] = len(chunk_bytes)
        new_bin_parts.append(chunk_bytes)
        curr_offset += len(chunk_bytes)
        # 4 字节对齐填充
        pad = (4 - (curr_offset % 4)) % 4
        if pad:
            new_bin_parts.append(b"\x00" * pad)
            curr_offset += pad

    new_bin = b"".join(new_bin_parts)
    if gltf.get("buffers"):
        gltf["buffers"][0]["byteLength"] = len(new_bin)

    new_json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    json_pad = (4 - (len(new_json_bytes) % 4)) % 4
    if json_pad:
        new_json_bytes += b" " * json_pad

    total_len = 12 + 8 + len(new_json_bytes) + 8 + len(new_bin)
    os.makedirs(os.path.dirname(os.path.abspath(out_glb_path)), exist_ok=True)
    with open(out_glb_path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, version, total_len))
        f.write(struct.pack("<II", len(new_json_bytes), 0x4E4F534A))
        f.write(new_json_bytes)
        f.write(struct.pack("<II", len(new_bin), 0x004E4942))
        f.write(new_bin)

    print(f"✓ [Swap GLB] 已生成新款 GLB: {out_glb_path} ({os.path.getsize(out_glb_path):,} 字节)")
    return out_glb_path


def bundle_standalone_html(base_html_path, glb_path, out_html_path, title=None, subtitle=None):
    """将新款 GLB Base64 注入母版离线 HTML 查看器，生成零网络依赖的单文件网页"""
    with open(base_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    with open(glb_path, "rb") as f:
        b64_str = base64.b64encode(f.read()).decode("ascii")

    # 替换 <script id="b64-glb" type="text/plain">...</script>
    html = re.sub(
        r'(<script\s+id="b64-glb"\s+type="text/plain">).*?(</script>)',
        lambda m: m.group(1) + b64_str + m.group(2),
        html,
        flags=re.DOTALL,
    )

    if title:
        html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, flags=re.DOTALL)
        html = re.sub(r"(<div class=\"title\">.*?<h1>).*?(</h1>)", lambda m: m.group(1) + title + m.group(2), html, flags=re.DOTALL)
    if subtitle:
        html = re.sub(r"(<div class=\"title\">.*?<p>).*?(</p>)", lambda m: m.group(1) + subtitle + m.group(2), html, flags=re.DOTALL)

    os.makedirs(os.path.dirname(os.path.abspath(out_html_path)), exist_ok=True)
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ [Bundle HTML] 已生成单文件离线 3D 网页: {out_html_path} ({os.path.getsize(out_html_path):,} 字节)")


# ==============================================================================
# 模式 B：Blender 无头四步法重构（从 AI 原始百万面高模 GLB -> 标准双材质母版 GLB）
# ==============================================================================
def rebuild_ai_base_glb_in_blender(in_glb, front_jpg, back_jpg, out_glb, target_faces=52500):
    import bpy
    import bmesh
    from mathutils import Vector

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=in_glb)

    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise RuntimeError(f"No mesh found in {in_glb}")

    bpy.ops.object.select_all(action='DESELECT')
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active

    # Step 1: 拓扑减面 (Decimation)
    curr_faces = len(obj.data.polygons)
    print(f"[Step 1] 原始面数: {curr_faces}")
    if curr_faces > target_faces:
        dec = obj.modifiers.new("Decimate", 'DECIMATE')
        dec.ratio = float(target_faces) / float(curr_faces)
        bpy.ops.object.modifier_apply(modifier="Decimate")
        print(f"[Step 1] 减面完成: {len(obj.data.polygons)} 面")

    # Step 2: 变换矩阵归一化 (Normalize Transform)
    bpy.ops.object.shade_smooth()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Step 3 & 4: 正反面双材质物理隔离 + 正交 UV 重投影 + PBR 材质绑定
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv_lay = bm.loops.layers.uv.verify()

    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)
    span_x = max(1e-5, max_x - min_x)
    span_z = max(1e-5, max_z - min_z)

    for f in bm.faces:
        # Blender 中 -Y 为正面，+Y 为背面
        is_front = f.normal.y <= 0.0
        f.material_index = 0 if is_front else 1
        for l in f.loops:
            nx = (l.vert.co.x - min_x) / span_x
            nz = (l.vert.co.z - min_z) / span_z
            u = (0.031 + nx * 0.938) if is_front else (0.969 - nx * 0.938)
            v = 0.064 + nz * 0.886
            l[uv_lay].uv = (u, v)

    bm.to_mesh(obj.data)
    bm.free()

    # 构建 Mat_Front 与 Mat_Back
    obj.data.materials.clear()
    for mat_name, tex_path in [("Mat_Front", front_jpg), ("Mat_Back", back_jpg)]:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.80
        if "Sheen Weight" in bsdf.inputs:
            bsdf.inputs["Sheen Weight"].default_value = 0.65
        if tex_path and os.path.exists(tex_path):
            tex = nodes.new("ShaderNodeTexImage")
            tex.image = bpy.data.images.load(tex_path)
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        obj.data.materials.append(mat)

    os.makedirs(os.path.dirname(os.path.abspath(out_glb)), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_normals=True,
        export_texcoords=True,
    )
    print(f"✓ [Rebuild Base GLB] 母版 GLB 导出完成: {out_glb}")


def main():
    argv = sys.argv
    if "--" in argv and ("blender" in argv[0].lower() or "Blender" in argv[0]):
        argv = argv[argv.index("--") + 1:]
    else:
        argv = argv[1:]

    # 兼容旧版位置参数: <input.glb> <output.glb> [target_faces]
    if argv and not argv[0].startswith("--"):
        in_glb = argv[0]
        out_glb = argv[1]
        faces = int(argv[2]) if len(argv) > 2 else 50000
        rebuild_ai_base_glb_in_blender(in_glb, "", "", out_glb, faces)
        return

    parser = argparse.ArgumentParser(description="AI GLB 4-Step Rebuild & 1-Base-GLB Batch SKU Generator")
    parser.add_argument("--mode", choices=["swap", "batch", "rebuild"], default="swap")
    parser.add_argument("--base_glb", type=str, help="Canonical base GLB path (e.g. shirt-final.glb)")
    parser.add_argument("--base_html", type=str, default="", help="Template standalone HTML viewer path")
    parser.add_argument("--in_glb", type=str, help="Raw AI GLB path for rebuild mode")
    parser.add_argument("--front", type=str, default="", help="Front product photo path")
    parser.add_argument("--back", type=str, default="", help="Back product photo path")
    parser.add_argument("--out_glb", type=str, help="Output GLB path")
    parser.add_argument("--out_html", type=str, default="", help="Output standalone HTML path")
    parser.add_argument("--title", type=str, default="", help="Custom HTML viewer title")
    parser.add_argument("--subtitle", type=str, default="", help="Custom HTML viewer subtitle")
    parser.add_argument("--batch_json", type=str, default="", help="JSON manifest path for batch SKU generation")
    parser.add_argument("--faces", type=int, default=52500, help="Target face count for rebuild mode")

    args = parser.parse_args(argv)

    if args.mode == "rebuild":
        rebuild_ai_base_glb_in_blender(args.in_glb, args.front, args.back, args.out_glb, args.faces)
        if args.base_html and args.out_html:
            bundle_standalone_html(args.base_html, args.out_glb, args.out_html, args.title, args.subtitle)
    elif args.mode == "swap":
        swap_glb_textures(args.base_glb, args.front, args.back, args.out_glb)
        if args.base_html and args.out_html:
            bundle_standalone_html(args.base_html, args.out_glb, args.out_html, args.title, args.subtitle)
    elif args.mode == "batch":
        with open(args.batch_json, "r", encoding="utf-8") as f:
            sku_list = json.load(f)
        for idx, item in enumerate(sku_list, 1):
            print(f"[{idx}/{len(sku_list)}] 正在生成: {item.get('title', item.get('out_glb'))} ...")
            swap_glb_textures(args.base_glb, item["front"], item["back"], item["out_glb"])
            if args.base_html and item.get("out_html"):
                bundle_standalone_html(
                    args.base_html,
                    item["out_glb"],
                    item["out_html"],
                    item.get("title"),
                    item.get("subtitle"),
                )


if __name__ == "__main__":
    main()
