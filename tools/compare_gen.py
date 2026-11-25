#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""比对「现有文件」和「生成结果」的结构是否等价。

不看文本格式，只看装备 id / 成本 / 年份 / 国家标记 / 贴图 / 科技解锁关系 / 结算动作。
用法： python tools/compare_gen.py [--config-dir tools/lines_imported]
"""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = load_module("gen", ROOT / "tools" / "gen.py")
imp = load_module("imp", ROOT / "tools" / "import_lines.py")

diffs = []


def note(msg):
    diffs.append(msg)


def parse_equipment(text):
    out = {}
    for name, start, end in imp.block_list(text, 1):
        chunk = imp.body(text, start, end)
        flag = re.search(r"has_country_flag\s*=\s*([A-Za-z0-9_]+)", chunk)
        out[name] = {
            "is_archetype": imp.field(chunk, "is_archetype") == "yes",
            "picture": imp.field(chunk, "picture"),
            "cost": imp.field(chunk, "build_cost_ic"),
            "year": imp.field(chunk, "year"),
            "flag": flag.group(1) if flag else None,
            "archetype": imp.field(chunk, "archetype"),
        }
    return out


def parse_tech(text):
    out = {}
    for name, start, end in imp.block_list(text, 1):
        chunk = imp.body(text, start, end)
        m = re.search(r"enable_equipments\s*=\s*\{(.*?)\}", chunk, re.S)
        out[name] = sorted(re.findall(r"([A-Za-z0-9_]+)", m.group(1))) if m else []
    return out


def parse_actions(text):
    out = {}
    for name, start, end in imp.block_list(text, 1):
        if name != "on_weekly":
            continue
        chunk = imp.body(text, start, end)
        m = re.search(r"num_equipment@([A-Za-z0-9_]+)\s*>\s*0", chunk)
        if not m:
            continue
        product = m.group(1)
        lines = chunk.splitlines()
        deduct_end = None
        for i, line in enumerate(lines):
            if "add_equipment_to_stockpile" in line:
                depth = line.count("{") - line.count("}")
                j = i
                while depth > 0 and j + 1 < len(lines):
                    j += 1
                    depth += lines[j].count("{") - lines[j].count("}")
                deduct_end = j
                break
        zero = None
        if deduct_end is not None:
            for i in range(deduct_end + 1, len(lines)):
                if re.match(r"\s*set_variable\s*=\s*\{", lines[i]):
                    tail = "\n".join(lines[i:i + 3])
                    if re.search(r"value\s*=\s*0\s*$", tail, re.M):
                        zero = i
                        break
        if deduct_end is None or zero is None:
            note("%s 的 %s 找不到结算区" % (product, "?"))
            continue
        region = "\n".join(lines[deduct_end + 1:zero])
        temp = re.search(r"var\s*=\s*([A-Za-z0-9_]+)", chunk)
        saved = list(imp.problems)
        imp.problems = []
        effects = imp.translate(region, temp.group(1) if temp else "")
        imp.problems = saved
        out[product] = effects
    return out


def normalize_effects(effects):
    out = []
    for e in effects:
        item = dict(e)
        item.pop("target", None) if item.get("type") == "add_to_variable" else None
        out.append(tuple(sorted(item.items())))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-dir", default="tools/lines_imported")
    args = parser.parse_args()

    lines = gen.load_lines(ROOT / args.config_dir)
    files, groups = gen.build_outputs(lines)

    for group in sorted(groups):
        old_equip = parse_equipment((ROOT / "common/units/equipment" / (group + "_equipment.txt")).read_text(encoding="utf-8-sig"))
        new_equip = parse_equipment(files["common/units/equipment/%s_equipment.txt" % group])
        if set(old_equip) != set(new_equip):
            note("%s 装备 id 不一致：多 %s 少 %s" % (group,
                 sorted(set(new_equip) - set(old_equip)), sorted(set(old_equip) - set(new_equip))))
        for key in sorted(set(old_equip) & set(new_equip)):
            if old_equip[key] != new_equip[key]:
                note("%s 装备 %s 字段不同：%s -> %s" % (group, key, old_equip[key], new_equip[key]))

        old_tech = parse_tech((ROOT / "common/technologies" / (group + "_tech.txt")).read_text(encoding="utf-8-sig"))
        new_tech = parse_tech(files["common/technologies/%s_tech.txt" % group])
        if set(old_tech) != set(new_tech):
            note("%s 科技 id 不一致：多 %s 少 %s" % (group,
                 sorted(set(new_tech) - set(old_tech)), sorted(set(old_tech) - set(new_tech))))
        for key in sorted(set(old_tech) & set(new_tech)):
            if old_tech[key] != new_tech[key]:
                note("%s 科技 %s 解锁不同：%s -> %s" % (group, key, old_tech[key], new_tech[key]))

        actions_key = "common/on_actions/%s_on_actions.txt" % group
        if actions_key not in files:
            continue
        old_actions = parse_actions((ROOT / "common/on_actions" / (group + "_on_actions.txt")).read_text(encoding="utf-8-sig"))
        new_actions = parse_actions(files[actions_key])
        if set(old_actions) != set(new_actions):
            note("%s 结算块不一致：多 %s 少 %s" % (group,
                 sorted(set(new_actions) - set(old_actions)), sorted(set(old_actions) - set(new_actions))))
        for key in sorted(set(old_actions) & set(new_actions)):
            if normalize_effects(old_actions[key]) != normalize_effects(new_actions[key]):
                note("%s 结算 %s 不同：%s -> %s" % (group, key, old_actions[key], new_actions[key]))

    if diffs:
        print("结构差异 %d 处：" % len(diffs))
        for item in diffs:
            print("  " + item)
        sys.exit(1)
    print("结构与现有文件完全一致")


if __name__ == "__main__":
    main()
