#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从现有 txt / yml 反推生产线配置，输出 TOML 到 tools/lines_imported/。

只读仓库，写的是 tools/lines_imported/，人工核对后再挪进 tools/lines/。
用法： python tools/import_lines.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "tools" / "lines_imported"


def set_root(path):
    global ROOT
    ROOT = Path(path)

GROUPS = [
    "agency", "autonomy", "doctrine", "facility_breakthrough", "factory",
    "ideology", "intel_decryption", "manpower", "mio", "occupation",
    "political", "research_point", "resource", "world_tension", "xp_commandpp",
]

MANUAL_ACTIONS = {"autonomy", "facility_breakthrough", "occupation", "resource"}

LANGS = [("chinese", "simp_chinese"), ("english", "english"), ("russian", "russian")]
ROMAN = ["I", "II", "III"]

problems = []


def read(path):
    return path.read_text(encoding="utf-8-sig")


def norm(text):
    out = []
    for line in text.splitlines():
        i = line.find("#")
        if i >= 0:
            line = line[:i]
        out.append(line.replace("\t", "    "))
    return "\n".join(out)


def block_list(text, base_depth=1):
    """返回 [(名字, 起始行号, 结束行号)]，按花括号层级，不看缩进。"""
    lines = norm(text).splitlines()
    out = []
    depth = 0
    cur = None
    start = 0
    for i, line in enumerate(lines):
        s = line.strip()
        o, c = s.count("{"), s.count("}")
        if cur is None and depth == base_depth and o > 0:
            m = re.match(r"([A-Za-z0-9_.\-]+)\s*=\s*\{", s)
            if m:
                cur, start = m.group(1), i
        depth += o - c
        if cur is not None and depth == base_depth:
            out.append((cur, start, i))
            cur = None
    return out


def body(text, start, end):
    return "\n".join(norm(text).splitlines()[start:end + 1])


def parse_resources(text):
    m = re.search(r"resources\s*=\s*\{([^}]*)\}", text)
    if not m:
        return {}
    return {k: int(v) for k, v in re.findall(r"([a-z_]+)\s*=\s*(\d+)", m.group(1))}


def field(text, name):
    for line in text.splitlines():
        m = re.match(r"\s*" + name + r"\s*=\s*([A-Za-z0-9_.\-]+)\s*$", line)
        if m:
            return m.group(1)
    return None


def parse_loc():
    """返回 {语言: {key: 文本}}。"""
    data = {}
    for lang, suffix in LANGS:
        keys = {}
        for kind in ("equipment", "technology"):
            path = ROOT / "localisation" / lang / ("more_production_%s_l_%s.yml" % (kind, suffix))
            if not path.exists():
                continue
            for line in read(path).splitlines():
                m = re.match(r'\s*([A-Za-z0-9_.\-]+):\d*\s*"(.*)"\s*$', line)
                if m:
                    keys[m.group(1)] = m.group(2)
        data[lang] = keys
    return data


def parse_sprites():
    """返回 {精灵名: {"texture": 路径, "frames": 帧数}}。"""
    out = {}
    for path in (ROOT / "interface").glob("*.gfx"):
        text = read(path)
        for m in re.finditer(r'name\s*=\s*"(GFX_[A-Za-z0-9_.\-]+)"\s*texturefile\s*=\s*"([^"]+)"(\s*noOfFrames\s*=\s*(\d+))?', text):
            out[m.group(1)] = {"texture": m.group(2), "frames": int(m.group(4)) if m.group(4) else 1}
    return out


def strip_roman(name):
    for roman in reversed(ROMAN):
        if name.endswith(" " + roman):
            return name[: -(len(roman) + 1)]
    return name


def statements(region):
    """把一段 effect 拆成顶层语句 [(名字, 整段文本)]。"""
    lines = region.splitlines()
    out = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        m = re.match(r"([A-Za-z0-9_.\-]+)\s*=\s*(.*)$", s)
        if not m:
            problems.append("看不懂的行：%s" % s)
            i += 1
            continue
        name = m.group(1)
        depth = s.count("{") - s.count("}")
        chunk = [s]
        i += 1
        while depth > 0 and i < len(lines):
            t = lines[i].strip()
            depth += t.count("{") - t.count("}")
            chunk.append(t)
            i += 1
        out.append((name, "\n".join(chunk)))
    return out


def translate(region, temp):
    """把结算区翻译成配置里的 effect 列表。"""
    effects = []
    for name, chunk in statements(region):
        if name == "divide_variable":
            m = re.search(r"value\s*=\s*(\d+)", chunk)
            effects.append({"type": "divide_variable", "by": int(m.group(1)) if m else 1})
        elif name == "add_to_variable":
            target = re.search(r"var\s*=\s*([A-Za-z0-9_]+)", chunk)
            if not target:
                target = re.match(r"add_to_variable\s*=\s*\{\s*([A-Za-z0-9_]+)", chunk)
                target = target.group(1) if target else None
            else:
                target = target.group(1)
            if not target:
                problems.append("add_to_variable 认不出目标：" + chunk.replace("\n", " "))
            elif target == "doctrine_mastery_pool":
                effects.append({"type": "add_mastery"})
            else:
                effects.append({"type": "add_to_variable", "target": target})
        elif name == "add_offsite_building":
            effects.append({"type": "add_building", "building": field(chunk, "type")})
        elif name == "every_military_industrial_organization":
            effects.append({"type": "add_mio_funds"})
        elif name == "multiply_variable":
            m = re.search(r"value\s*=\s*(-?\d+)", chunk)
            if not m:
                m = re.search(r"=\s*(-?\d+)\s*\}", chunk)
            effects.append({"type": "multiply_variable", "by": int(m.group(1)) if m else 1})
        elif name == "add_popularity":
            effects.append({"type": "add_popularity", "ideology": field(chunk, "ideology")})
        elif name in ("add_manpower", "add_political_power", "add_stability", "add_war_support",
                      "add_threat", "army_experience", "navy_experience", "air_experience",
                      "add_command_power"):
            effects.append({"type": name})
        elif name == "add_resource":
            resource = field(chunk, "type")
            if not resource:
                m = re.search(r"\{\s*([a-z]+)\s*=", chunk)
                resource = m.group(1) if m else None
            effects.append({"type": "add_resource", "resource": resource})
        elif name == "add_equipment_to_stockpile":
            effects.append({"type": "add_equipment", "equipment": field(chunk, "type")})
        elif name == "if":
            problems.append("结算里有多余的 if 包裹，需要人工看：" + chunk.replace("\n", " ")[:120])
        elif name == "set_variable":
            problems.append("结算区里出现了不该有的 set_variable：" + chunk.replace("\n", " ")[:120])
        else:
            problems.append("不认识的结算语句：" + name)
    return effects


def parse_actions(group):
    """返回 {产品 id: effect 列表}。"""
    path = ROOT / "common" / "on_actions" / (group + "_on_actions.txt")
    if not path.exists():
        return {}
    text = read(path)
    result = {}
    for name, start, end in block_list(text, 1):
        if name != "on_weekly":
            continue
        chunk = body(text, start, end)
        m = re.search(r"num_equipment@([A-Za-z0-9_]+)\s*>\s*0", chunk)
        if not m:
            continue
        product = m.group(1)
        temp_match = re.search(r"var\s*=\s*([A-Za-z0-9_]+)\s*\n\s*value\s*=\s*var:num_equipment@" + product, chunk)
        if not temp_match:
            problems.append("%s 的 %s 找不到临时变量" % (group, product))
            continue
        temp = temp_match.group(1)
        lines = chunk.splitlines()
        deduct_end = None
        zero = None
        for i, line in enumerate(lines):
            if "add_equipment_to_stockpile" in line and deduct_end is None:
                depth = line.count("{") - line.count("}")
                j = i
                while depth > 0 and j + 1 < len(lines):
                    j += 1
                    depth += lines[j].count("{") - lines[j].count("}")
                deduct_end = j
                break
        if deduct_end is not None:
            for i in range(deduct_end + 1, len(lines)):
                line = lines[i]
                if re.match(r"\s*set_variable\s*=\s*\{", line):
                    tail = "\n".join(lines[i:i + 3])
                    if re.search(r"value\s*=\s*0\s*$", tail, re.M):
                        zero = i
                        break
        if deduct_end is None or zero is None:
            problems.append("%s 的 %s 找不到结算区边界" % (group, product))
            continue
        region = "\n".join(lines[deduct_end + 1:zero])
        result[product] = translate(region, temp)
    return result


def toml_quote(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def toml_array(values, indent="  "):
    if not values:
        return "[]"
    inner = ",\n".join(indent + toml_quote(v) for v in values)
    return "[\n" + inner + ",\n]"


def emit_group(group):
    equip_path = ROOT / "common" / "units" / "equipment" / (group + "_equipment.txt")
    if not equip_path.exists():
        return ""
    equip_text = read(equip_path)
    loc = parse_loc()
    sprites = parse_sprites()
    actions = parse_actions(group)

    archetypes = []
    products_by_archetype = {}
    info = {}
    for name, start, end in block_list(equip_text, 1):
        chunk = body(equip_text, start, end)
        info[name] = chunk
        if field(chunk, "is_archetype") == "yes":
            archetypes.append(name)
        else:
            parent = field(chunk, "archetype")
            if parent:
                products_by_archetype.setdefault(parent, []).append(name)

    tech_map = {}
    tech_path = ROOT / "common" / "technologies" / (group + "_tech.txt")
    if tech_path.exists():
        tech_text = read(tech_path)
        for name, start, end in block_list(tech_text, 1):
            chunk = body(tech_text, start, end)
            m = re.search(r"enable_equipments\s*=\s*\{(.*?)\}", chunk, re.S)
            for item in re.findall(r"([A-Za-z0-9_]+)", m.group(1)) if m else []:
                tech_map.setdefault(item, []).append(name)

    out = ["# %s 组生产线配置（由 tools/import_lines.py 反推，人工核对后使用）" % group, ""]
    for archetype in archetypes:
        products = sorted(products_by_archetype.get(archetype, []))
        if len(products) not in (1, 2, 3):
            problems.append("%s 的 archetype %s 产品数是 %d，超出 1~3：%s" % (group, archetype, len(products), products))
            continue
        first = info[products[0]]
        flag = re.search(r"has_country_flag\s*=\s*([A-Za-z0-9_]+)", first)
        flag = flag.group(1) if flag else None
        picture = field(info[archetype], "picture")
        line_id = archetype.replace("_in_warehouse", "")
        # 优先用已经存在的精灵，避免重复造；一个都不存在就沿用原声明，交给生成器补
        candidates = [picture, "archetype_" + line_id + "_equipment", "archetype_" + line_id]
        chosen = next((c for c in candidates if c and ("GFX_" + c) in sprites), picture)
        sprite = sprites.get("GFX_" + chosen) or sprites.get("GFX_" + products[0]) or {"texture": "", "frames": 1}
        texture = sprite["texture"]
        frames = sprite["frames"]
        picture = chosen
        techs = []
        for product in products:
            for candidate in tech_map.get(product, []):
                if candidate not in techs:
                    techs.append(candidate)
                    break

        out.append("[[production_line]]")
        out.append("id = " + toml_quote(line_id))
        out.append("group = " + toml_quote(group))
        for lang in ("chinese", "english", "russian"):
            out.append("name_" + lang + " = " + toml_quote(strip_roman(loc[lang].get(products[0], line_id))))
        if flag:
            out.append("country_flag = " + toml_quote(flag))
        archetype_resources = parse_resources(info[archetype])
        if archetype_resources:
            out.append("resources = { " + ", ".join(k + " = " + str(v) for k, v in archetype_resources.items()) + " }")
        if group in MANUAL_ACTIONS:
            out.append('actions = "manual"')
        out.append("archetype_equipment = " + toml_quote(archetype))
        if picture and picture != "archetype_" + line_id:
            out.append("picture_name = " + toml_quote(picture))
        if texture:
            out.append("texture_file = " + toml_quote(texture))
        if frames > 1:
            out.append("no_of_frames = " + str(frames))
        out.append("")

        for tier, product in enumerate(products):
            cost = field(info[product], "build_cost_ic")
            if tier == 0:
                cost = field(info[archetype], "build_cost_ic")
            out.append("[[production_line.equipment]]")
            out.append("id = " + toml_quote(product))
            out.append("year = " + (field(info[product], "year") or "1936"))
            out.append("build_cost = " + (cost or "0"))
            for lang in ("chinese", "english", "russian"):
                desc = loc[lang].get(product + "_desc")
                if desc:
                    out.append("description_" + lang + " = " + toml_quote(desc))
            own_resources = parse_resources(info[product])
            if own_resources:
                out.append("resources = { " + ", ".join(k + " = " + str(v) for k, v in own_resources.items()) + " }")
            out.append("")

        out.append("[production_line.technology]")
        out.append("identifiers = " + toml_array(techs))
        for lang in ("chinese", "english", "russian"):
            descs = [loc[lang].get(t + "_desc", "") for t in techs]
            if any(descs):
                out.append("descriptions_" + lang + " = " + toml_array(descs))
        out.append("")

        if group not in MANUAL_ACTIONS:
            per_tier = [actions.get(p, []) for p in products]
            buckets = {}
            order = []
            for tier, effects in enumerate(per_tier):
                key = repr(effects)
                if key not in buckets:
                    buckets[key] = {"effects": effects, "tiers": []}
                    order.append(key)
                buckets[key]["tiers"].append(tier + 1)
            for key in order:
                bucket = buckets[key]
                for effect in bucket["effects"]:
                    out.append("[[production_line.effect]]")
                    out.append("type = " + toml_quote(effect["type"]))
                    for name, value in effect.items():
                        if name == "type":
                            continue
                        out.append(name + " = " + (toml_quote(value) if isinstance(value, str) else str(value)))
                    if len(bucket["tiers"]) < len(products):
                        out.append("tiers = [" + ", ".join(str(t) for t in bucket["tiers"]) + "]")
                    out.append("")

    return "\n".join(out)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="从别的目录读源文件，默认是本仓库")
    parser.add_argument("--out", help="配置写到哪，默认 tools/lines_imported")
    args = parser.parse_args()
    if args.root:
        set_root(args.root)
    out_dir = Path(args.out) if args.out else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    for group in GROUPS:
        text = emit_group(group)
        if text:
            (out_dir / (group + ".toml")).write_text(text, encoding="utf-8", newline="\n")
    print("已写到 " + str(out_dir))
    if problems:
        print("--- 需要人工确认 %d 处 ---" % len(problems))
        for item in problems:
            print("  " + item)
    else:
        print("没有异常")


if __name__ == "__main__":
    main()
