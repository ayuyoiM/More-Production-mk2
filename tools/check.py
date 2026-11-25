#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""More_Production_coal 静态校验。

用法： python tools/check.py
退出码 0 = 没问题，1 = 有错误。只读，不写盘。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors, warns = [], []


def err(m):
    errors.append(m)


def warn(m):
    warns.append(m)


def read(p):
    return p.read_text(encoding="utf-8-sig")


def norm(text):
    out = []
    for line in text.splitlines():
        i = line.find("#")
        if i >= 0:
            line = line[:i]
        out.append(line.replace("\t", "    "))
    return "\n".join(out)


def indent(s):
    return len(s) - len(s.lstrip(" "))


def block_ranges(text, base_depth=1):
    """按花括号层级取块，不看缩进——各文件缩进不统一，不能写死。"""
    lines = norm(text).splitlines()
    out, depth, cur, start = {}, 0, None, 0
    for i, line in enumerate(lines):
        s = line.strip()
        o, c = s.count("{"), s.count("}")
        if cur is None and depth == base_depth and o > 0:
            m = re.match(r"([A-Za-z0-9_.\-]+)\s*=\s*\{", s)
            if m:
                cur, start = m.group(1), i
        depth += o - c
        if cur is not None and depth == base_depth:
            out[cur] = (start, i)
            cur = None
    return out


def body(text, rng):
    return "\n".join(norm(text).splitlines()[rng[0]:rng[1] + 1])


def field(b, name):
    """取块内某个标量字段，按整行匹配，避免 is_archetype 命中 archetype。"""
    for line in b.splitlines():
        m = re.match(r"\s*" + name + r"\s*=\s*([A-Za-z0-9_]+)\s*$", line)
        if m:
            return m.group(1)
    return None


def load(pattern):
    return sorted(ROOT.glob(pattern))


equip_files = load("common/units/equipment/*.txt")
tech_files = load("common/technologies/*.txt")
oa_files = load("common/on_actions/*.txt")
dec_files = load("common/decisions/*.txt")
cat_files = load("common/decisions/categories/*.txt")
dm_files = load("common/dynamic_modifiers/*.txt")
gfx_files = load("interface/*.gfx")
loc_files = load("localisation/*/*.yml")

equip, tech, categories, decisions = {}, {}, set(), {}
set_flags, init_vars, sprites = set(), set(), set()
dm_names, dm_vars = set(), {}

for p in equip_files:
    t = read(p)
    for eid, rng in block_ranges(t).items():
        if eid in equip:
            err("装备 id 重复：%s（%s 和 %s）" % (eid, equip[eid]["file"], p.name))
            continue
        b = body(t, rng)
        m = re.search(r"can_be_produced\s*=\s*\{\s*has_country_flag\s*=\s*([a-z0-9_]+)", b)
        equip[eid] = {
            "file": p.name,
            "archetype": field(b, "archetype"),
            "picture": field(b, "picture"),
            "is_archetype": field(b, "is_archetype") == "yes",
            "flag": m.group(1) if m else None,
        }

for p in cat_files:
    categories.update(block_ranges(read(p), 0))

for p in dec_files:
    t = read(p)
    for cat, rng in block_ranges(t, 0).items():
        if cat not in categories:
            err("%s 的外层块 %s 不是已定义的分类" % (p.name, cat))
        for did in block_ranges(body(t, rng), 1):
            if did in decisions:
                err("决策 id 重复：%s（%s 和 %s）" % (did, decisions[did], p.name))
            decisions[did] = p.name
    set_flags.update(re.findall(r"set_country_flag\s*=\s*([a-z0-9_]+)", t))

for p in tech_files:
    t = read(p)
    for tid, rng in block_ranges(t).items():
        if tid in tech:
            err("科技 id 重复：%s" % tid)
        m = re.search(r"enable_equipments\s*=\s*\{(.*?)\}", body(t, rng), re.S)
        tech[tid] = re.findall(r"([a-z0-9_]+)", m.group(1)) if m else []

for p in dm_files:
    t = read(p)
    for did, rng in block_ranges(t, 0).items():
        dm_names.add(did)
        for line in body(t, rng).splitlines():
            m = re.match(r"\s*([a-z0-9_]+)\s*=\s*([a-z][a-z0-9_]+)\s*$", line)
            if m and m.group(1) not in ("enable", "icon"):
                dm_vars.setdefault(m.group(2), []).append(did + "." + m.group(1))

for p in oa_files + dec_files + dm_files:
    init_vars.update(re.findall(r"set_variable\s*=\s*\{\s*var\s*=\s*([a-z0-9_]+)", read(p)))

sprite_home = {}
for p in gfx_files:
    for name in re.findall(r'name\s*=\s*"(GFX_[A-Za-z0-9_.\-]+)"', read(p)):
        if name in sprite_home:
            err("精灵名重复：%s（%s 和 %s）" % (name, sprite_home[name], p.name))
        sprite_home[name] = p.name
        sprites.add(name)

# ---------- 检查 ----------

for p in equip_files + tech_files + oa_files + dec_files + cat_files + dm_files + gfx_files:
    t = norm(read(p))
    o, c = t.count("{"), t.count("}")
    if o != c:
        err("%s 括号不平衡：{ %d  } %d" % (p.name, o, c))

for p in gfx_files:
    bad = sum(1 for ch in read(p) if ord(ch) > 127)
    if bad:
        err("%s 含非 ASCII 字符 %d 个" % (p.name, bad))

# HOI4 脚本不用逗号分隔，出现逗号会把后面整块解析歪
for p in equip_files + tech_files + oa_files + dec_files + cat_files + dm_files:
    for i, line in enumerate(read(p).splitlines(), 1):
        body_line = re.sub(r'"[^"]*"', "", line.split("#")[0])
        if "," in body_line:
            err("%s 第 %d 行有逗号：%s" % (p.name, i, line.strip()))

for eid, e in equip.items():
    if e["archetype"]:
        if e["archetype"] not in equip:
            err("装备 %s 的 archetype %s 不存在" % (eid, e["archetype"]))
        elif not equip[e["archetype"]]["is_archetype"]:
            err("装备 %s 的 archetype %s 没标 is_archetype = yes" % (eid, e["archetype"]))
    if e["picture"] and "GFX_" + e["picture"] not in sprites:
        warn("装备 %s 的 picture %s 没有对应精灵 GFX_%s" % (eid, e["picture"], e["picture"]))
    if e["flag"] and e["flag"] not in set_flags:
        err("装备 %s 要的 flag %s 没有任何决策设置" % (eid, e["flag"]))

families = {}
for eid, e in equip.items():
    if e["is_archetype"] or not e["archetype"]:
        continue
    families.setdefault(re.sub(r"_(2|3)$", "", eid), []).append(eid)
for base in sorted(families):
    need = [base, base + "_medium", base + "_2_medium", base + "_3_medium"]
    missing = [n for n in need if "GFX_" + n not in sprites]
    if missing:
        warn("装备 %s 缺精灵：%s" % (base, ", ".join("GFX_" + n for n in missing)))

for tid, lst in tech.items():
    for e in lst:
        if e not in equip:
            err("科技 %s 的 enable_equipments 指向不存在的装备 %s" % (tid, e))

for p in oa_files:
    for e in re.findall(r"num_equipment@([a-z0-9_]+)", read(p)):
        if e not in equip:
            err("%s 引用不存在的装备 %s" % (p.name, e))

for var, used in sorted(dm_vars.items()):
    if var not in init_vars:
        err("动态修饰符变量 %s 没有 set_variable 初始化（%s）" % (var, ", ".join(used)))

# 多帧贴图没写 noOfFrames 会被当成一整条横图显示
GAME = Path("D:/Program Files/Steam/steamapps/common/Hearts of Iron IV")
for p in gfx_files:
    text = read(p)
    for m in re.finditer(r"name\s*=\s*\"(GFX_[A-Za-z0-9_.\-]+)\"\s*texturefile\s*=\s*\"([^\"]+)\"([^}]*)", text):
        name, tex, rest = m.group(1), m.group(2), m.group(3)
        if "noOfFrames" in rest:
            continue
        path = ROOT / tex
        if not path.exists():
            path = GAME / tex
        if not path.exists():
            continue
        raw = path.read_bytes()[:20]
        if len(raw) < 20:
            continue
        width = int.from_bytes(raw[16:20], "little")
        height = int.from_bytes(raw[12:16], "little")
        if height and width % height == 0 and width // height > 1:
            warn("%s 的贴图 %s 是 %dx%d（%d 帧横图），但没写 noOfFrames" % (name, tex, width, height, width // height))

langs = {}
for p in loc_files:
    raw = p.read_bytes()
    if raw[:3] != b"\xef\xbb\xbf":
        err("%s 缺 UTF-8 BOM" % p.name)
    keys = set()
    for line in read(p).splitlines():
        m = re.match(r'\s*([A-Za-z0-9_.\-]+):\d*\s*"', line)
        if m:
            if m.group(1) in keys:
                warn("%s 里 key 重复：%s" % (p.name, m.group(1)))
            keys.add(m.group(1))
    langs[p.parent.name] = langs.get(p.parent.name, set()) | keys

products = {k for k, v in equip.items() if not v["is_archetype"]}
required = products | set(tech) | set(decisions) | categories | dm_names
optional = {k for k, v in equip.items() if v["is_archetype"]} | set_flags
for lang, keys in sorted(langs.items()):
    miss = sorted(k for k in required if k not in keys)
    if miss:
        err("%s 缺本地化键 %d 个：%s" % (lang, len(miss), ", ".join(miss[:12]) + (" ..." if len(miss) > 12 else "")))
    miss2 = sorted(k for k in optional if k not in keys)
    if miss2:
        warn("%s 缺可选本地化键 %d 个：%s" % (lang, len(miss2), ", ".join(miss2[:8]) + (" ..." if len(miss2) > 8 else "")))

print("装备 %d / 科技 %d / 决策 %d / 分类 %d / 精灵 %d / 语言 %d"
      % (len(equip), len(tech), len(decisions), len(categories), len(sprites), len(langs)))
for m in warns:
    print("[警告] " + m)
for m in errors:
    print("[错误] " + m)
print("---")
print("错误 %d，警告 %d" % (len(errors), len(warns)))
sys.exit(1 if errors else 0)
