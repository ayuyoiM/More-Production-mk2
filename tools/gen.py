#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从 tools/lines/*.toml 生成装备、科技、每周结算、图标、本地化。

用法：
  python tools/gen.py                     写到仓库
  python tools/gen.py --check             只比对，不写盘
  python tools/gen.py --only <id> --out <目录>   只渲染一条线到指定目录

配置改动请改 tools/lines/*.toml，不要手改生成出来的文件。
"""
import argparse
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "tools" / "lines"

INDENT = "\t"
SPRITE_BEGIN = "\t# 生成区开始"
SPRITE_END = "\t# 生成区结束"


def load_lines():
    lines = []
    for path in sorted(CONFIG_DIR.glob("*.toml")):
        with path.open("rb") as f:
            data = tomllib.load(f)
        for entry in data.get("production_line", []):
            entry["_source"] = path.name
            for field in ("id", "group", "archetype_equipment", "name_chinese",
                          "name_english", "name_russian"):
                if field not in entry:
                    sys.exit("%s 里的线缺少字段 %s" % (path.name, field))
            if len(entry.get("equipment", [])) != 3:
                sys.exit("%s 里的线 %s 需要正好三档装备" % (path.name, entry["id"]))
            lines.append(entry)
    return lines


def picture_name(line):
    return line.get("picture_name") or ("archetype_" + line["archetype_equipment"].replace("_in_warehouse", ""))


def product_ids(line):
    return [p["id"] for p in line["equipment"]]


def temp_name(line, tier):
    return line["id"] + "_product" + ("" if tier == 0 else "_" + str(tier + 1))


def render_equipment(lines):
    out = ["equipments = {", ""]
    for line in lines:
        flag = line.get("country_flag")
        archetype = line["archetype_equipment"]
        products = line["equipment"]
        out.append(INDENT + "# " + line["name_english"] + " production")
        out.append("")
        out.append(INDENT + archetype + " = {")
        out.append(INDENT * 2 + "year = " + str(products[0].get("year", 1936)))
        out.append("")
        out.append(INDENT * 2 + "is_archetype = yes")
        out.append("")
        out.append(INDENT * 2 + "picture = " + picture_name(line))
        out.append(INDENT * 2 + "is_buildable = no")
        out.append("")
        out.append(INDENT * 2 + "type = infantry")
        out.append(INDENT * 2 + "group_by = archetype")
        out.append("")
        out.append(INDENT * 2 + "interface_category = interface_category_land")
        out.append("")
        out.append(INDENT * 2 + "active = yes")
        out.append("")
        out.append(INDENT * 2 + "lend_lease_cost = 2")
        out.append("")
        out.append(INDENT * 2 + "build_cost_ic = " + str(products[0]["build_cost"]))
        resources = line.get("resources", {})
        if resources:
            out.append(INDENT * 2 + "resources = {")
            for key, value in resources.items():
                out.append(INDENT * 3 + key + " = " + str(value))
            out.append(INDENT * 2 + "}")
        else:
            out.append(INDENT * 2 + "resources = {")
            out.append(INDENT * 2 + "}")
        out.append(INDENT + "}")
        out.append("")
        for tier, product in enumerate(products):
            out.append(INDENT + product["id"] + " = {")
            if flag:
                out.append(INDENT * 2 + "can_be_produced = { has_country_flag = " + flag + " }")
            out.append(INDENT * 2 + "year = " + str(product.get("year", 1936)))
            out.append(INDENT * 2 + "archetype = " + archetype)
            if tier:
                out.append(INDENT * 2 + "parent = " + products[tier - 1]["id"])
                out.append(INDENT * 2 + "build_cost_ic = " + str(product["build_cost"]))
            out.append(INDENT * 2 + "priority = " + str((tier + 1) * 10))
            out.append(INDENT + "}")
            out.append("")
    out.append("}")
    return "\n".join(out) + "\n"


def render_technology(lines):
    out = ["technologies = {", ""]
    for line in lines:
        techs = line["technology"]["identifiers"]
        ids = product_ids(line)
        for tier in range(3):
            out.append(INDENT + techs[tier] + " = {")
            out.append("")
            out.append(INDENT * 2 + "enable_equipments = {")
            if tier == 0:
                out.append(INDENT * 3 + line["archetype_equipment"])
            out.append(INDENT * 3 + ids[tier])
            out.append(INDENT * 2 + "}")
            out.append("")
            out.append(INDENT * 2 + "research_cost = -1")
            out.append(INDENT * 2 + "ai_will_do = { factor = 0 }")
            out.append(INDENT + "}")
            out.append("")
    out.append("}")
    return "\n".join(out) + "\n"


def render_effects(line, tier):
    temp = temp_name(line, tier)
    out = []
    for effect in line.get("effect", []):
        kind = effect.get("type")
        if kind == "divide_variable":
            out += [
                INDENT * 4 + "divide_variable = {",
                INDENT * 5 + "var = " + temp,
                INDENT * 5 + "value = " + str(effect["by"]),
                INDENT * 4 + "}",
            ]
        elif kind == "add_to_variable":
            out += [
                INDENT * 4 + "add_to_variable = {",
                INDENT * 5 + "var = " + effect["target"],
                INDENT * 5 + "value = " + temp,
                INDENT * 4 + "}",
            ]
        elif kind == "add_building":
            out += [
                INDENT * 4 + "add_offsite_building = {",
                INDENT * 5 + "type = " + effect["building"],
                INDENT * 5 + "level = " + temp,
                INDENT * 4 + "}",
            ]
        elif kind == "add_mio_funds":
            out += [
                INDENT * 4 + "every_military_industrial_organization = {",
                INDENT * 5 + "add_mio_funds = " + temp,
                INDENT * 4 + "}",
            ]
        elif kind == "add_mastery":
            out += [
                INDENT * 4 + "add_to_variable = {",
                INDENT * 5 + "var = doctrine_mastery_pool",
                INDENT * 5 + "value = " + temp,
                INDENT * 4 + "}",
            ]
        elif kind in ("add_manpower", "add_political_power", "add_stability", "add_war_support"):
            out.append(INDENT * 4 + kind + " = " + temp)
        elif kind == "add_resource":
            out += [
                INDENT * 4 + "add_resource = {",
                INDENT * 5 + "type = " + effect["resource"],
                INDENT * 5 + "amount = " + temp,
                INDENT * 4 + "}",
            ]
        elif kind == "add_equipment":
            out += [
                INDENT * 4 + "add_equipment_to_stockpile = {",
                INDENT * 5 + "type = " + effect["equipment"],
                INDENT * 5 + "amount = " + temp,
                INDENT * 4 + "}",
            ]
        else:
            sys.exit("线 %s 里有不认识的结算类型：%s" % (line["id"], kind))
        out.append("")
    return out


def render_on_actions(lines):
    out = ["on_actions = {", ""]
    for line in lines:
        ids = product_ids(line)
        for tier in range(3):
            temp = temp_name(line, tier)
            out += [
                INDENT + "on_weekly = { # " + ids[tier],
                INDENT * 2 + "effect = {",
                INDENT * 3 + "if = {",
                INDENT * 4 + "limit = {",
                INDENT * 5 + "check_variable = {",
                INDENT * 6 + "var:num_equipment@" + ids[tier] + " > 0",
                INDENT * 5 + "}",
                INDENT * 4 + "}",
                "",
                INDENT * 4 + "set_variable = {",
                INDENT * 5 + "var = " + temp,
                INDENT * 5 + "value = var:num_equipment@" + ids[tier],
                INDENT * 4 + "}",
                INDENT * 4 + "set_variable = {",
                INDENT * 5 + "var = " + temp + "_negative",
                INDENT * 5 + "value = var:num_equipment@" + ids[tier],
                INDENT * 4 + "}",
                INDENT * 4 + "multiply_variable = {",
                INDENT * 5 + "var = " + temp + "_negative",
                INDENT * 5 + "value = -1",
                INDENT * 4 + "}",
                "",
                INDENT * 4 + "add_equipment_to_stockpile = {",
                INDENT * 5 + "type = " + ids[tier],
                INDENT * 5 + "amount = " + temp + "_negative",
                INDENT * 4 + "}",
                "",
            ]
            out += render_effects(line, tier)
            out += [
                INDENT * 4 + "set_variable = {",
                INDENT * 5 + "var = " + temp,
                INDENT * 5 + "value = 0",
                INDENT * 4 + "}",
                INDENT * 4 + "set_variable = {",
                INDENT * 5 + "var = " + temp + "_negative",
                INDENT * 5 + "value = 0",
                INDENT * 4 + "}",
                INDENT * 3 + "}",
                INDENT * 2 + "}",
                INDENT + "}",
                "",
            ]
    out.append("}")
    return "\n".join(out) + "\n"


def render_sprites(lines):
    out = []
    for line in lines:
        texture = line["texture_file"]
        names = [picture_name(line)] + [product_ids(line)[0], product_ids(line)[0] + "_medium",
                                        product_ids(line)[0] + "_2_medium", product_ids(line)[0] + "_3_medium"]
        for name in names:
            out += [
                INDENT + "SpriteType = {",
                INDENT * 2 + 'name = "GFX_' + name + '"',
                INDENT * 2 + 'texturefile = "' + texture + '"',
                INDENT + "}",
                "",
            ]
    return "\n".join(out)


def render_loc(lines, lang, kind):
    suffix = {"chinese": "simp_chinese", "english": "english", "russian": "russian"}[lang]
    out = ["l_" + suffix + ":"]
    for line in lines:
        name = line["name_" + lang]
        roman = ["I", "II", "III"]
        if kind == "equipment":
            out.append("  # " + name)
            for tier, product in enumerate(line["equipment"]):
                out.append('  %s: "%s %s"' % (product["id"], name, roman[tier]))
                desc = product.get("description_" + lang)
                if desc:
                    out.append('  %s_desc: "%s"' % (product["id"], desc))
        else:
            out.append("  # " + name)
            descs = line["technology"].get("descriptions_" + lang) or []
            for tier, tech in enumerate(line["technology"]["identifiers"]):
                out.append('  %s: "%s %s"' % (tech, name, roman[tier]))
                if tier < len(descs):
                    out.append('  %s_desc: "%s"' % (tech, descs[tier]))
    return "\n".join(out) + "\n"


def build_outputs(lines):
    """返回 {相对路径: 内容}。"""
    files = {}
    groups = {}
    for line in lines:
        groups.setdefault(line["group"], []).append(line)
    for group, group_lines in groups.items():
        files["common/units/equipment/%s_equipment.txt" % group] = render_equipment(group_lines)
        files["common/technologies/%s_tech.txt" % group] = render_technology(group_lines)
        files["common/on_actions/%s_on_actions.txt" % group] = render_on_actions(group_lines)
        for lang in ("chinese", "english", "russian"):
            suffix = {"chinese": "simp_chinese", "english": "english", "russian": "russian"}[lang]
            files["localisation/%s/more_production_equipment_l_%s.yml" % (lang, suffix)] = render_loc(group_lines, lang, "equipment")
            files["localisation/%s/more_production_technology_l_%s.yml" % (lang, suffix)] = render_loc(group_lines, lang, "technology")
    return files, groups


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--out")
    args = parser.parse_args()

    lines = load_lines()
    if args.only:
        lines = [l for l in lines if l["id"] == args.only]
        if not lines:
            sys.exit("没有找到 id 为 %s 的线" % args.only)

    files, groups = build_outputs(lines)
    sprite_text = render_sprites(lines)

    if args.out:
        target = Path(args.out)
        for rel, content in files.items():
            path = target / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\r\n")
        (target / "sprites.txt").write_text(sprite_text, encoding="utf-8", newline="\r\n")
        print("已写到 " + str(target))
        return

    print("渲染完成：" + ", ".join(sorted(groups)))
    if args.check:
        differ = 0
        for rel, content in files.items():
            path = ROOT / rel
            if not path.exists():
                print("缺文件 " + rel)
                differ += 1
            elif path.read_text(encoding="utf-8-sig").replace("\r\n", "\n") != content:
                print("内容不同 " + rel)
                differ += 1
        print("差异文件 %d 个" % differ)
        sys.exit(1 if differ else 0)
    print("落盘还没接，先用 --out 看样板。")


if __name__ == "__main__":
    main()
