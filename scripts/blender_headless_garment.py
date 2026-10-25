#!/usr/bin/env python3
"""
blender_headless_garment.py (v1.4.0)
====================================
Web3D 物理级真实感仿真与交互展示规范 · 软质服装与纺织产品无头几何生成流水线（零外部 3D 模型依赖保底基线）

路由与适用边界（Route Priority Verdict）：
- 面对软质服装、自然垂坠褶皱与穿戴形态，商用首选【AI 图生 3D（Hunyuan3D/Tripo）底模 + 减面重投影四步法】（`decimate_ai_glb.py`）；
- 本纯代码参数化脚本（用户视觉验收 60 分及格基线）仅在【明确禁止使用外部 3D 底模】时作为保底方案调用。

核心几何与材质特性：
1. J 型立体袖窿裁剪（肩端点宽于腋下）+ 24 顶点连续袖孔环（Continuous Armscye Loop）
2. 袖口内折边向每圈参考外环局部圆心（Local Ring Centroid）内缩，彻底根除腋下短袖内衬穿模
3. 极角参数化标准圆润圆领（平贴 20° 溜肩斜率）+ 解析椭圆领口内唇
4. Subsurf + CorrectiveSmooth 曲率平滑后置雕刻 1.1mm 极细双针车线微凹槽（领圈/肩线/袖笼/袖口/下摆）
5. 260g 哑光精梳棉 PBR（Roughness 0.89, Sheen 0.42）+ 深色印花区 Sheen 自动遮罩 + BOX 投射微针织法线

使用方式：
blender -b --python blender_headless_garment.py -- \
  --front /path/to/front.jpg \
  --back /path/to/back.jpg \
  --out /path/to/shirt.glb \
  [--normal /path/to/seamless_cotton_normal.png] \
  [--renders /path/to/renders_dir]
"""

import sys
import os
import math
import argparse
import bpy
import bmesh
from mathutils import Vector


def smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / max(1e-6, (edge1 - edge0))))
    return t * t * (3.0 - 2.0 * t)


def gauss(x, mu, sigma):
    return math.exp(-0.5 * ((x - mu) / max(1e-6, sigma)) ** 2)


def create_cotton_materials(front_tex="", back_tex="", normal_tex=""):
    """
    创建 6 个物理隔离的材质槽位：
    0: Mat_Front   (前胸精梳棉 + 正面印花贴图，深色图案区自动屏蔽 Sheen)
    1: Mat_Back    (后背精梳棉 + 背面印花贴图，深色图案区自动屏蔽 Sheen)
    2: Mat_Fabric  (袖子/领圈/边缘 260g 本白精梳棉)
    3: Mat_Inner   (领口后背内衬 #A0A4AC 浅冷灰)
    4: Mat_Seam    (1.1mm 极细双针车线微凹槽材质，亮度仅比白布略深 6%)
    5: Mat_Cavity  (袖口内壁与深腔 #787C84 中性冷灰，告别死黑空洞)
    """
    norm_img = bpy.data.images.load(normal_tex) if (normal_tex and os.path.exists(normal_tex)) else None
    if norm_img:
        norm_img.colorspace_settings.name = 'Non-Color'

    def build_mat(name, base_color, tex_path=None, roughness=0.89, sheen=0.42, bump_str=0.16, mask_sheen_on_dark=False):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        mat.use_backface_culling = False
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = 0.0
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = 1.32
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.06 if sheen > 0 else 0.02

        if "Sheen Weight" in bsdf.inputs:
            bsdf.inputs["Sheen Weight"].default_value = sheen
            bsdf.inputs["Sheen Roughness"].default_value = 0.58
            bsdf.inputs["Sheen Tint"].default_value = (1.0, 1.0, 1.0, 1.0)
        elif "Sheen" in bsdf.inputs:
            bsdf.inputs["Sheen"].default_value = sheen

        if tex_path and os.path.exists(tex_path):
            img = bpy.data.images.load(tex_path)
            tex = nodes.new("ShaderNodeTexImage")
            tex.image = img
            tex.extension = 'EXTEND'
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

            if mask_sheen_on_dark and "Sheen Weight" in bsdf.inputs:
                bw = nodes.new("ShaderNodeRGBToBW")
                ramp = nodes.new("ShaderNodeValToRGB")
                ramp.color_ramp.elements[0].position = 0.72
                ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
                ramp.color_ramp.elements[1].position = 0.90
                ramp.color_ramp.elements[1].color = (sheen, sheen, sheen, 1.0)
                links.new(tex.outputs["Color"], bw.inputs["Color"])
                links.new(bw.outputs["Val"], ramp.inputs["Fac"])
                links.new(ramp.outputs["Color"], bsdf.inputs["Sheen Weight"])
        else:
            bsdf.inputs["Base Color"].default_value = base_color

        if norm_img and bump_str > 0:
            uv_node = nodes.new("ShaderNodeTexCoord")
            mapping = nodes.new("ShaderNodeMapping")
            mapping.inputs["Scale"].default_value = (24.0, 24.0, 24.0)
            ntex = nodes.new("ShaderNodeTexImage")
            ntex.image = norm_img
            ntex.projection = 'BOX'
            ntex.projection_blend = 0.25
            nmap = nodes.new("ShaderNodeNormalMap")
            nmap.inputs["Strength"].default_value = bump_str
            links.new(uv_node.outputs["Generated"], mapping.inputs["Vector"])
            links.new(mapping.outputs["Vector"], ntex.inputs["Vector"])
            links.new(ntex.outputs["Color"], nmap.inputs["Color"])
            links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])

        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        return mat

    crisp_cotton = (0.945, 0.948, 0.954, 1.0)   # 纯净精梳棉本白
    inner_facing = (0.450, 0.460, 0.482, 1.0)   # 领口后背内衬浅冷灰 (#A0A4AC)
    seam_cotton  = (0.835, 0.845, 0.862, 1.0)   # 极细 1.1mm 缝合槽微阴影色（仅比白布暗 6%，绝非灰条带！）
    cuff_cavity  = (0.215, 0.225, 0.242, 1.0)   # 袖口内腔中性冷灰 (#787C84，告别纯黑空洞)

    mat_front  = build_mat("Mat_Front",  crisp_cotton, front_tex, roughness=0.89, sheen=0.42, bump_str=0.16, mask_sheen_on_dark=True)
    mat_back   = build_mat("Mat_Back",   crisp_cotton, back_tex,  roughness=0.89, sheen=0.42, bump_str=0.16, mask_sheen_on_dark=True)
    mat_fabric = build_mat("Mat_Fabric", crisp_cotton, None,      roughness=0.89, sheen=0.44, bump_str=0.18)
    mat_inner  = build_mat("Mat_Inner",  inner_facing, None,      roughness=0.93, sheen=0.12, bump_str=0.12)
    mat_seam   = build_mat("Mat_Seam",   seam_cotton,  None,      roughness=0.94, sheen=0.20, bump_str=0.24)
    mat_cavity = build_mat("Mat_Cavity", cuff_cavity,  None,      roughness=0.95, sheen=0.05, bump_str=0.10)

    return [mat_front, mat_back, mat_fabric, mat_inner, mat_seam, mat_cavity]


def build_garment_object(scene, materials):
    mesh = bpy.data.meshes.new("RouteA_TShirt_Mesh")
    obj = bpy.data.objects.new("RouteA_TShirt", mesh)
    scene.collection.objects.link(obj)
    for m in materials:
        obj.data.materials.append(m)

    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    # =========================================================================
    # 1. 构建躯干网格：采用非均匀精细行分布 (z_rows)，在下摆双针车线与肩缝处直接提供 1.0mm 微环！
    #    领口列采用极角 alpha 参数化，彻底消除 V 领与领角多边形折点！
    # =========================================================================
    NX = 57
    C_MID = NX // 2          # 28
    C_NECK_HALF = 14         # 领口占左右各 14 列
    C_NECK_L = C_MID - C_NECK_HALF  # 14
    C_NECK_R = C_MID + C_NECK_HALF  # 42
    XI_NECK = 0.500

    # 精心构造下躯干 t_low 序列 (0.0 -> 1.0)：
    # 在 t_low = 0.052 与 0.062 (对应距底摆 2.1cm 与 2.5cm) 处插入宽度仅 0.0028 (约 1.1mm) 的双针平行车线微环！
    t_low_list = [
        0.000, 0.018, 0.036,
        0.050, 0.0528,         # <- 下摆双针车线第 1 针 (宽 1.1mm)
        0.059,
        0.0618, 0.0646,        # <- 下摆双针车线第 2 针 (宽 1.1mm)
    ]
    for k in range(1, 31):
        t_low_list.append(0.0646 + (1.0 - 0.0646) * (k / 30.0))

    R_PIT = len(t_low_list) - 1  # 37

    # 构造上胸过肩 t_up 序列 (0.0 -> 1.0)：
    # 在肩顶 t_up = 0.992 -> 1.000 处插入宽 1.2mm 的肩缝微环！
    t_up_list = []
    for k in range(1, 26):
        t_up_list.append(0.992 * (k / 25.0))
    t_up_list.append(1.000)

    NZ = len(t_low_list) + len(t_up_list)
    hem_stitch_rows = {3, 6}          # 对应 (0.050->0.0528) 与 (0.0618->0.0646) 两条 1.1mm 双针微环！
    shoulder_seam_row = NZ - 2        # 对应 (0.992->1.000) 1.2mm 肩缝微环！

    front_grid = [[None for _ in range(NX)] for _ in range(NZ)]
    back_grid = [[None for _ in range(NX)] for _ in range(NZ)]

    Z_BOT = -0.350
    Z_PIT = 0.064
    Z_TOP = 0.276

    W_PIT = 0.155
    W_SHOULDER = 0.178
    R_Y_SCYE = 0.044
    Y_MID_TOP = 0.000

    # 极角参数化映射：使 c in [C_NECK_L, C_NECK_R] 按正弦极角平滑分布，消除领角多边形折点
    def get_xi_and_neck_angles(c):
        dc = c - C_MID
        if abs(dc) <= C_NECK_HALF:
            alpha = (dc / C_NECK_HALF) * (math.pi * 0.5)
            tau = math.sin(alpha)
            cos_a = math.cos(alpha)
            xi = XI_NECK * tau
            return xi, tau, cos_a, True
        else:
            sign_c = 1.0 if dc > 0 else -1.0
            s_out = (abs(dc) - C_NECK_HALF) / (C_MID - C_NECK_HALF)
            xi = sign_c * (XI_NECK + (1.0 - XI_NECK) * s_out)
            return xi, sign_c, 0.0, False

    def get_torso_pos(c, r, is_front):
        xi, tau, cos_a, in_neck = get_xi_and_neck_angles(c)
        abs_xi = abs(xi)
        sign_xi = 1.0 if xi >= 0.0 else -1.0

        phi = xi * (math.pi * 0.5)
        sin_p = math.sin(phi)
        cos_p = max(0.0, math.cos(phi))

        if r <= R_PIT:
            t_low = t_low_list[r]
            v = t_low * 0.60
        else:
            t_up = t_up_list[r - R_PIT - 1]
            v = 0.60 + t_up * 0.40

        df = 0.088 + 0.006 * math.sin(math.pi * min(1.0, v / 0.80))
        db = 0.084 + 0.005 * math.sin(math.pi * min(1.0, v / 0.80))

        x_base_norm = 0.510 * sin_p + 0.490 * (sin_p ** 3)

        # 19° 挺括溜肩斜率：从外领角 (z = 0.276m) 斜降至肩尖 (z = 0.236m, Δz = -0.040m)
        t_sh_only = max(0.0, (abs_xi - XI_NECK) / (1.0 - XI_NECK))
        z_sh_dome = Z_TOP - 0.040 * (t_sh_only ** 0.96)

        # 标准圆润圆领 (Crew Neck) 参数化：
        # 因为 tau = sin(alpha), cos_a = cos(alpha) = sqrt(1 - tau^2)：
        #   1) 正视平面 (x, z) 上：dz_collar = -0.056 * (cos_a ** 1.22) = -0.056 * (1 - (x/R)^2)^0.61
        #      这是真正的椭圆/圆弧 U 领！在 x=0 处平坦圆润，绝无 V 领尖角！
        #   2) 侧视平面 (y, z) 上：dy_collar = -0.042 * (cos_a ** 0.95)，故 dz ~ |y|^1.28，在 y=0 处 dz/dy = 0，侧视领顶圆润无尖角！
        if in_neck:
            if is_front:
                dy_collar = -0.042 * (cos_a ** 0.95)
                dz_collar = -0.056 * (cos_a ** 1.22)
            else:
                dy_collar = +0.036 * (cos_a ** 0.95)
                dz_collar = -0.005 * (cos_a ** 1.22)
        else:
            dy_collar = 0.0
            dz_collar = 0.0

        if r <= R_PIT:
            t_low = t_low_list[r]
            # 方案2修身立体剪影：胸线 0.155m -> 腰部 (t_low=0.45) 收至 0.1435m -> 下摆微放至 0.148m
            waist_scoop = -0.0086 * math.sin(math.pi * (t_low ** 0.80))
            w_low = 0.148 * (1.0 - t_low) + W_PIT * t_low + waist_scoop
            x = w_low * x_base_norm

            # 侧腰与腋下下方柔和自然的立体垂坠曲面起伏（捕光形成方案2中的自然侧边明暗过渡）
            drape_flute = 0.0022 * math.sin(math.pi * t_low) * (sin_p ** 2) * math.cos(2.5 * phi)
            if is_front:
                y = Y_MID_TOP - (df + drape_flute) * cos_p
            else:
                y = Y_MID_TOP + (db + drape_flute) * cos_p

            z = Z_BOT + t_low * (Z_PIT - Z_BOT)

            hem_env = 1.0 - smoothstep(0.0, 0.18, t_low)
            if is_front:
                z += (0.0015 * cos_p) * hem_env
            else:
                z += (-0.0025 * cos_p) * hem_env

        else:
            t_up = t_up_list[r - R_PIT - 1]
            h_up = 0.5 * (1.0 - math.cos(math.pi * t_up))
            sin_arch = math.sin(t_up * math.pi * 0.5)
            cos_arch = math.cos(t_up * math.pi * 0.5)
            sin_scye = 0.28 * (1.0 - t_up) + 0.72 * math.sin(math.pi * t_up)

            collar_env = smoothstep(0.45, 1.0, t_up) ** 1.15

            x_pit = W_PIT * x_base_norm
            x_top_eff = W_SHOULDER * x_base_norm
            scye_inward = -sign_xi * 0.0035 * math.sin(math.pi * t_up) * (sin_p ** 4)
            x = x_pit * (1.0 - h_up) + x_top_eff * h_up + scye_inward

            y_sign = -1.0 if is_front else +1.0
            d_body = df if is_front else db
            y_dome = Y_MID_TOP + y_sign * (
                d_body * cos_arch * cos_p
                + R_Y_SCYE * sin_scye * (1.0 - cos_p)
            )
            y = y_dome + dy_collar * collar_env

            f_z = 0.55 * sin_arch + 0.45 * h_up
            z_dome = Z_PIT + (z_sh_dome - Z_PIT) * f_z
            z = z_dome + dz_collar * collar_env

        return Vector((x, y, z))

    for r in range(NZ):
        for c in range(NX):
            pf = get_torso_pos(c, r, is_front=True)
            v_front = bm.verts.new(pf)
            front_grid[r][c] = v_front

            is_side_weld = (r <= R_PIT) and (c == 0 or c == NX - 1)
            is_shoulder_weld = (r == NZ - 1) and (c <= C_NECK_L or c >= C_NECK_R)
            if is_side_weld or is_shoulder_weld:
                back_grid[r][c] = v_front
            else:
                pb = get_torso_pos(c, r, is_front=False)
                back_grid[r][c] = bm.verts.new(pb)

    def get_torso_uv(co, is_front):
        if is_front:
            u = 0.496094 + (co.x / 0.244) * 0.514648
            v = 0.473633 + ((co.z - 0.046) / 0.124) * 0.262207
        else:
            u = 0.508545 - (co.x / 0.268) * 0.529785
            v = 0.437012 + ((co.z - (-0.022)) / 0.202) * 0.363281
        return (max(0.01, min(0.99, u)), max(0.01, min(0.99, v)))

    for r in range(NZ - 1):
        for c in range(NX - 1):
            is_hem_stitch = (r in hem_stitch_rows)
            is_shoulder_seam = (r == shoulder_seam_row) and (c < C_NECK_L or c >= C_NECK_R)

            f_mat = 4 if (is_hem_stitch or is_shoulder_seam) else 0
            b_mat = 4 if (is_hem_stitch or is_shoulder_seam) else 1

            vf1, vf2, vf3, vf4 = front_grid[r][c], front_grid[r][c+1], front_grid[r+1][c+1], front_grid[r+1][c]
            if len({vf1, vf2, vf3, vf4}) >= 3:
                ff = bm.faces.new((vf1, vf2, vf3, vf4))
                ff.material_index = f_mat
                for l in ff.loops:
                    l[uv_lay].uv = get_torso_uv(l.vert.co, is_front=True)

            vb1, vb2, vb3, vb4 = back_grid[r][c], back_grid[r][c+1], back_grid[r+1][c+1], back_grid[r+1][c]
            if len({vb1, vb2, vb3, vb4}) >= 3:
                fb = bm.faces.new((vb1, vb4, vb3, vb2))
                fb.material_index = b_mat
                for l in fb.loops:
                    l[uv_lay].uv = get_torso_uv(l.vert.co, is_front=False)

    # =========================================================================
    # 2. 构建平贴肩胸的标准圆润 2.0cm 罗纹圆领（彻底消除漏斗状凸起与 V 领！）
    # =========================================================================
    neck_loop = (
        [front_grid[NZ - 1][c] for c in range(C_NECK_L, C_NECK_R + 1)] +
        [back_grid[NZ - 1][c] for c in range(C_NECK_R - 1, C_NECK_L, -1)]
    )
    N_NECK = len(neck_loop)
    base_coords = [v.co.copy() for v in neck_loop]
    neck_center_xy = Vector((0.0, -0.002, 0.0))

    inner_targets = []
    for co in base_coords:
        # 直接使用严格解析椭圆构造内领圈目标点 co1 = (Rx_in * sin(alpha), +-Ry_in * cos(alpha), Z_in - dZ_in * cos(alpha))
        # 使外领圈与内领圈在正视图 (x, z) 上同为 100% 标准数学椭圆/圆弧，彻底消除任何多边形折角或平底！
        sin_a = max(-1.0, min(1.0, co.x / 0.089))
        cos_a = math.sqrt(max(0.0, 1.0 - sin_a * sin_a))
        is_front_half = (co.y < 0.0)

        x_in = 0.068 * sin_a
        y_in = (-0.030 * cos_a) if is_front_half else (+0.025 * cos_a)
        z_in = (0.283 - 0.046 * (cos_a ** 0.95)) if is_front_half else (0.283 - 0.003 * cos_a)

        target_in = Vector((x_in, y_in, z_in))
        rad_xy = Vector((co.x - x_in, co.y - y_in, 0.0))
        rad_dir = rad_xy.normalized() if rad_xy.length > 1e-5 else Vector((0.0, -1.0, 0.0))
        inner_targets.append((rad_dir, target_in))

    # Step 0 宽度仅 t_ac = 0.05 (约 1.0mm)，形成极细领圈外缝压线！
    # Step 7 宽度仅 2.0mm，形成后领水平汗带细压线！
    collar_steps = [
        (0.05, -0.0006, -0.0002, 4, False),  # 0: 1.0mm 极细领圈外缝压线 (Mat_Seam)
        (0.32,  0.0005,  0.0001, 2, True),   # 1: 平贴罗纹带下段
        (0.65,  0.0006,  0.0002, 2, True),   # 2: 平贴罗纹带中段
        (0.92,  0.0005,  0.0002, 2, True),   # 3: 平贴罗纹带上段
        (1.00,  0.0001,  0.0001, 2, True),   # 4: 领口顶沿平顺外唇
        (1.04, -0.0008, -0.0008, 2, True),   # 5: 领口顶沿内唇
        (1.03, -0.0014, -0.0135, 3, True),   # 6: 领圈内壁罗纹带 (Mat_Inner #A0A4AC)
        (1.02, -0.0018, -0.0152, 4, False),  # 7: 1.5mm 极细后领织带水平压线 (Mat_Seam)
        (1.02, -0.0016, -0.0520, 3, False),  # 8: 领口内部可见后背浅灰内衬 (Mat_Inner #A0A4AC)
        (1.00, -0.0024, -0.0950, 5, False),  # 9: 领口深处内腔封底
    ]

    curr_ring = neck_loop
    for t_ac, n_bulge, z_ext, mat_idx, is_rib in collar_steps:
        next_ring = []
        for i, co0 in enumerate(base_coords):
            rad_dir, co1 = inner_targets[i]
            theta = 2.0 * math.pi * i / N_NECK
            rib_wave = 0.00032 * math.sin(theta * 88.0) if is_rib else 0.0
            out_norm = (rad_dir * 0.50 + Vector((0.0, 0.0, 0.86))).normalized()
            pos = co0.lerp(co1, t_ac) + out_norm * (n_bulge + rib_wave) + Vector((0.0, 0.0, z_ext))
            next_ring.append(bm.verts.new(pos))

        for i in range(N_NECK):
            inext = (i + 1) % N_NECK
            f = bm.faces.new((curr_ring[i], curr_ring[inext], next_ring[inext], next_ring[i]))
            f.material_index = mat_idx
            for l in f.loops:
                l[uv_lay].uv = (0.5, 0.5)
        curr_ring = next_ring

    cap_center = bm.verts.new(sum((v.co for v in curr_ring), Vector((0, 0, 0))) / N_NECK)
    for i in range(N_NECK):
        inext = (i + 1) % N_NECK
        fc = bm.faces.new((curr_ring[i], curr_ring[inext], cap_center))
        fc.material_index = 5
        for l in fc.loops:
            l[uv_lay].uv = (0.5, 0.5)

    # =========================================================================
    # 3. 构建带 1.1mm 极细袖窿缝与双针袖口车线的圆筒短袖 (build_cylindrical_sleeve)
    # =========================================================================
    def build_cylindrical_sleeve(armscye_verts, side_sign):
        N_SCYE = len(armscye_verts)
        scye_coords = [v.co.copy() for v in armscye_verts]

        sleeve_axis = Vector((side_sign * 0.279, 0.0, -0.960)).normalized()
        v_vec = Vector((side_sign * 0.960, 0.0, 0.279)).normalized()
        u_vec = Vector((0.0, 1.0, 0.0))

        cuff_center = Vector((side_sign * 0.204, Y_MID_TOP, 0.033))
        R_CUFF_U = 0.0490
        R_CUFF_V = 0.0500

        cuff_ring_targets = []
        for i in range(N_SCYE):
            ang = math.pi - (2.0 * math.pi * i / N_SCYE)
            target_pt = (
                cuff_center
                + v_vec * (R_CUFF_V * math.cos(ang))
                - u_vec * (R_CUFF_U * math.sin(ang))
            )
            cuff_ring_targets.append((ang, target_pt))

        # 精心构造袖长 t 序列 (0.0 -> 1.0)：
        # 1) t = 0.000 -> 0.0065 (宽 1.2mm)：袖窿极细缝合槽 (step 1)
        # 2) t = 0.875 -> 0.8805 (宽 1.0mm) 与 0.893 -> 0.8985 (宽 1.0mm)：袖口双针平行极细车线！
        t_sleeve_list = [0.0065]
        for k in range(1, 23):
            t_sleeve_list.append(0.0065 + (0.8750 - 0.0065) * (k / 22.0))
        t_sleeve_list.extend([
            0.8805,   # <- 袖口双针车线第 1 针 (宽 1.0mm)
            0.8930,
            0.8985,   # <- 袖口双针车线第 2 针 (宽 1.0mm)
            0.9320,
            0.9660,
            1.0000,
        ])
        seam_step_indices = {0, 23, 25}  # 对应 (0->0.0065) 袖窿缝, (0.875->0.8805) 第1针, (0.893->0.8985) 第2针

        curr_s_ring = armscye_verts
        sleeve_rings_coords = [scye_coords]

        for s_idx, t in enumerate(t_sleeve_list):
            next_s_ring = []
            ring_coords = []

            deltoid_arch = math.sin(math.pi * (t ** 0.78))

            for i in range(N_SCYE):
                co0 = scye_coords[i]
                ang, co1 = cuff_ring_targets[i]

                pos = co0.lerp(co1, t)
                upper_weight = 0.5 * (1.0 + math.cos(ang))
                cap_lift = (0.0020 + 0.0065 * (upper_weight ** 1.3)) * deltoid_arch
                pos = pos + v_vec * cap_lift
                ring_coords.append(pos)
                next_s_ring.append(bm.verts.new(pos))

            sleeve_rings_coords.append(ring_coords)

            s_mat = 4 if (s_idx in seam_step_indices) else 2

            for i in range(N_SCYE):
                inext = (i + 1) % N_SCYE
                if side_sign < 0:
                    f = bm.faces.new((curr_s_ring[i], next_s_ring[i], next_s_ring[inext], curr_s_ring[inext]))
                else:
                    f = bm.faces.new((curr_s_ring[i], curr_s_ring[inext], next_s_ring[inext], next_s_ring[i]))
                f.material_index = s_mat
                for l in f.loops:
                    l[uv_lay].uv = (0.5, 0.5)

            curr_s_ring = next_s_ring

        # 袖口双层折边与中性冷灰内腔 (#787C84，防穿模 + 告别死黑)
        N_TOTAL_S = len(sleeve_rings_coords) - 1
        cuff_return_specs = [
            (N_TOTAL_S,     0.965, 2),   # 0: 袖口圆润折边内缘 (Mat_Fabric)
            (N_TOTAL_S - 2, 0.935, 5),   # 1: 袖口内部折边回退 (Mat_Cavity #787C84 中性冷灰)
            (N_TOTAL_S - 5, 0.900, 5),   # 2: 袖管内腔中段 (Mat_Cavity #787C84)
            (N_TOTAL_S - 8, 0.855, 5),   # 3: 袖管内腔封底环 (Mat_Cavity #787C84)
        ]
        for ref_step_idx, rad_scale, m_idx in cuff_return_specs:
            ref_ring = sleeve_rings_coords[ref_step_idx]
            ring_center = sum(ref_ring, Vector((0.0, 0.0, 0.0))) / N_SCYE
            inner_ring = []
            for co_ref in ref_ring:
                pos = ring_center + (co_ref - ring_center) * rad_scale
                inner_ring.append(bm.verts.new(pos))
            for i in range(N_SCYE):
                inext = (i + 1) % N_SCYE
                if side_sign < 0:
                    f = bm.faces.new((curr_s_ring[i], inner_ring[i], inner_ring[inext], curr_s_ring[inext]))
                else:
                    f = bm.faces.new((curr_s_ring[i], curr_s_ring[inext], inner_ring[inext], inner_ring[i]))
                f.material_index = m_idx
                for l in f.loops:
                    l[uv_lay].uv = (0.5, 0.5)
            curr_s_ring = inner_ring

        cuff_cap = bm.verts.new(sum((v.co for v in curr_s_ring), Vector((0, 0, 0))) / N_SCYE)
        for i in range(N_SCYE):
            inext = (i + 1) % N_SCYE
            if side_sign < 0:
                fc = bm.faces.new((curr_s_ring[i], cuff_cap, curr_s_ring[inext]))
            else:
                fc = bm.faces.new((curr_s_ring[i], curr_s_ring[inext], cuff_cap))
            fc.material_index = 5
            for l in fc.loops:
                l[uv_lay].uv = (0.5, 0.5)

    left_scye_loop = (
        [front_grid[r][0] for r in range(R_PIT, NZ)] +
        [back_grid[r][0] for r in range(NZ - 2, R_PIT, -1)]
    )
    build_cylindrical_sleeve(left_scye_loop, side_sign=-1.0)

    right_scye_loop = (
        [front_grid[r][NX - 1] for r in range(R_PIT, NZ)] +
        [back_grid[r][NX - 1] for r in range(NZ - 2, R_PIT, -1)]
    )
    build_cylindrical_sleeve(right_scye_loop, side_sign=+1.0)

    # =========================================================================
    # 4. 构建下摆折边厚度与内腔
    # =========================================================================
    hem_loop = (
        [front_grid[0][c] for c in range(0, NX)] +
        [back_grid[0][c] for c in range(NX - 2, 0, -1)]
    )
    N_HEM = len(hem_loop)
    hem_coords = [v.co.copy() for v in hem_loop]

    hem_inner_steps = [
        (-0.0016, 0.988, 2),
        ( 0.0020, 0.968, 3),
        ( 0.0350, 0.945, 5),
        ( 0.0750, 0.920, 5),
    ]
    curr_h_ring = hem_loop
    for dz_shift, r_scale, m_idx in hem_inner_steps:
        next_h_ring = []
        for co_h in hem_coords:
            pos = Vector((co_h.x * r_scale, co_h.y * r_scale, co_h.z + dz_shift))
            next_h_ring.append(bm.verts.new(pos))
        for i in range(N_HEM):
            inext = (i + 1) % N_HEM
            f = bm.faces.new((curr_h_ring[i], next_h_ring[i], next_h_ring[inext], curr_h_ring[inext]))
            f.material_index = m_idx
            for l in f.loops:
                l[uv_lay].uv = (0.5, 0.5)
        curr_h_ring = next_h_ring

    hem_cap = bm.verts.new(sum((v.co for v in curr_h_ring), Vector((0, 0, 0))) / N_HEM)
    for i in range(N_HEM):
        inext = (i + 1) % N_HEM
        fc = bm.faces.new((curr_h_ring[i], hem_cap, curr_h_ring[inext]))
        fc.material_index = 5
        for l in fc.loops:
            l[uv_lay].uv = (0.5, 0.5)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    # =========================================================================
    # 5. 第一阶段：Catmull-Clark 曲面细分 + 物理张力平滑定型
    # =========================================================================
    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    smooth_mod = obj.modifiers.new("CorrectiveSmooth", 'CORRECTIVE_SMOOTH')
    smooth_mod.factor = 0.40
    smooth_mod.iterations = 6
    smooth_mod.use_pin_boundary = True

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.modifier_apply(modifier="CorrectiveSmooth")

    # =========================================================================
    # 6. 第二阶段：仅对 1.1mm 宽的 Mat_Seam 车线微环中心线顶点做 0.95mm 法线内凹雕刻！
    #    只移动完全被 Mat_Seam 面包围的中心顶点（使 1.1mm 微环形成 V 型真实针迹凹槽，边缘不产生台阶）
    # =========================================================================
    bm_post = bmesh.new()
    bm_post.from_mesh(obj.data)
    bm_post.verts.ensure_lookup_table()
    bm_post.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm_post, faces=bm_post.faces)

    seam_center_verts = []
    seam_edge_verts = []
    for v in bm_post.verts:
        f_mats = [f.material_index for f in v.link_faces]
        if not f_mats:
            continue
        seam_count = sum(1 for m in f_mats if m == 4)
        if seam_count == len(f_mats):
            seam_center_verts.append(v)
        elif seam_count > 0:
            seam_edge_verts.append(v)

    for v in seam_center_verts:
        v.co -= v.normal * 0.00105
    for v in seam_edge_verts:
        v.co -= v.normal * 0.00030

    bmesh.ops.recalc_face_normals(bm_post, faces=bm_post.faces)
    non_manifold = [e for e in bm_post.edges if not e.is_manifold]
    boundary = [e for e in bm_post.edges if e.is_boundary]
    print("=== [Topology Audit] ===")
    print(f"Vertices: {len(bm_post.verts)}, Faces: {len(bm_post.faces)}, Seam Center Verts: {len(seam_center_verts)}")
    print(f"Non-manifold edges: {len(non_manifold)}, Boundary edges: {len(boundary)}")

    bm_post.to_mesh(obj.data)
    bm_post.free()
    obj.data.update()

    return obj


def render_three_views(scene, obj, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'METAL'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = 'GPU'
    except Exception as e:
        print("Cycles GPU setup note:", e)

    scene.render.film_transparent = True
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = 0.38

    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.52, 0.54, 0.58, 1.0)
        bg.inputs["Strength"].default_value = 0.18

    # 左前 36° 定向主光 + 低右侧辅光，塑造方案2的立体圆柱明暗过渡 (#F4F5F8 -> #CFD3DA)
    key_data = bpy.data.lights.new("KeyLight", 'AREA')
    key_data.energy = 74.0
    key_data.color = (1.0, 0.996, 0.992)
    key_data.shape = 'RECTANGLE'
    key_data.size = 1.25
    key_data.size_y = 1.75
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    scene.collection.objects.link(key_obj)

    fill_data = bpy.data.lights.new("FillLight", 'AREA')
    fill_data.energy = 8.5
    fill_data.color = (0.90, 0.93, 1.0)
    fill_data.shape = 'RECTANGLE'
    fill_data.size = 1.9
    fill_data.size_y = 2.2
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    scene.collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new("RimLight", 'AREA')
    rim_data.energy = 20.0
    rim_data.color = (0.98, 0.99, 1.0)
    rim_data.size = 1.5
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    scene.collection.objects.link(rim_obj)

    cam_data = bpy.data.cameras.new("InspectCam")
    cam_data.lens = 85.0
    cam_obj = bpy.data.objects.new("InspectCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    def look_at(obj_cam, target_pt):
        direction = target_pt - obj_cam.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        obj_cam.rotation_euler = rot_quat.to_euler()

    target = Vector((0.0, 0.0, -0.030))
    dist = 2.45
    views = [
        ("front", 0.0,   -1.0,  dist, target),
        ("side",  85.0,  -1.0,  dist, target),
        ("q45",   30.0,  -2.0,  dist, target),
        ("back",  180.0, -1.0,  dist, target),
        ("shoulder_closeup", 118.0, 4.0, 0.68, Vector((0.15, 0.00, 0.16))),
    ]

    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1300

    for vname, yaw_deg, pitch_deg, v_dist, v_target in views:
        yaw = math.radians(yaw_deg)
        pitch = math.radians(pitch_deg)
        cx = v_target.x + math.sin(yaw) * math.cos(pitch) * v_dist
        cy = v_target.y - math.cos(yaw) * math.cos(pitch) * v_dist
        cz = v_target.z + math.sin(pitch) * v_dist
        cam_obj.location = Vector((cx, cy, cz))
        look_at(cam_obj, v_target)

        def place_light(l_obj, rel_yaw_deg, rel_z, r_dist):
            lyaw = yaw + math.radians(rel_yaw_deg)
            lx = math.sin(lyaw) * r_dist
            ly = -math.cos(lyaw) * r_dist
            l_obj.location = Vector((lx, ly, rel_z))
            look_at(l_obj, target)

        place_light(key_obj,  36.0,  1.25, 2.05)
        place_light(fill_obj, -65.0, 0.20, 2.50)
        place_light(rim_obj,  145.0, 1.35, 2.05)

        out_path = os.path.join(out_dir, f"view_{vname}.png")
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"✓ 固定视角 Cycles 光追渲染完成: {out_path}")


def run_garment_pipeline(front_img="", back_img="", glb_out="", renders_dir=None, normal_img=""):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'

    materials = create_cotton_materials(front_tex=front_img, back_tex=back_img, normal_tex=normal_img)
    obj = build_garment_object(scene, materials)

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    os.makedirs(os.path.dirname(os.path.abspath(glb_out)), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=glb_out,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_image_format='JPEG',
        export_jpeg_quality=94,
    )
    print(f"✓ 已导出独立模型文件: {glb_out} ({os.path.getsize(glb_out):,} 字节)")

    if renders_dir:
        render_three_views(scene, obj, renders_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blender Headless Garment Pipeline v1.4.0")
    parser.add_argument("--front", type=str, default="", help="Front reference photo path")
    parser.add_argument("--back", type=str, default="", help="Back reference photo path")
    parser.add_argument("--normal", type=str, default="", help="Seamless micro-knit normal map path")
    parser.add_argument("--out", type=str, required=True, help="Output GLB path")
    parser.add_argument("--renders", type=str, default="", help="Directory for verification renders")

    if "--" in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    else:
        args = parser.parse_args()

    run_garment_pipeline(
        front_img=args.front,
        back_img=args.back,
        glb_out=args.out,
        renders_dir=args.renders if args.renders else None,
        normal_img=args.normal,
    )
