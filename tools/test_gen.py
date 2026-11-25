#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成器自检：把工厂产出这一条渲染出来，检查输出结构对不对。

不写盘，纯字符串比对。
用法： python tools/test_gen.py
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_generator():
    spec = importlib.util.spec_from_file_location("gen", ROOT / "tools" / "gen.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    gen = load_generator()
    lines = [line for line in gen.load_lines() if line["id"] == "factory_output"]
    assert lines, "配置里找不到 factory_output"

    files, groups = gen.build_outputs(lines)
    equipment = files["common/units/equipment/factory_equipment.txt"]
    technology = files["common/technologies/factory_tech.txt"]
    actions = files["common/on_actions/factory_on_actions.txt"]
    sprites = gen.render_sprites(lines)

    assert equipment.count("{") == equipment.count("}"), "装备文件括号不平衡"
    assert equipment.count("can_be_produced = { has_country_flag = mp_tab_factory }") == 3
    for cost in ("1000", "500", "100"):
        assert "build_cost_ic = " + cost in equipment, "缺成本 " + cost
    assert "picture = archetype_factory_output" in equipment

    assert technology.count("{") == technology.count("}"), "科技文件括号不平衡"
    for name in ("factory_output_production_research", "factory_output_production_2_research",
                 "factory_output_production_3_research"):
        assert name + " = {" in technology, "缺科技 " + name

    assert actions.count("{") == actions.count("}"), "结算文件括号不平衡"
    assert actions.count("on_weekly = {") == 3
    assert actions.count("value = 100") == 3, "三档都要除 100"
    assert "var = more_production_industrial_capacity_factory" in actions
    assert "var = more_production_industrial_capacity_dockyard" in actions
    assert actions.count("value = 0") == 6, "六个临时变量都要清零"

    assert sprites.count("SpriteType = {") == 5, "应该是五个图标定义"
    for name in ("GFX_archetype_factory_output", "GFX_factory_output_in_warehouse_product",
                 "GFX_factory_output_in_warehouse_product_medium",
                 "GFX_factory_output_in_warehouse_product_2_medium",
                 "GFX_factory_output_in_warehouse_product_3_medium"):
        assert name in sprites, "缺图标 " + name

    for lang, suffix in (("chinese", "simp_chinese"), ("english", "english"), ("russian", "russian")):
        loc = files["localisation/%s/more_production_equipment_l_%s.yml" % (lang, suffix)]
        assert loc.count('"') == 12, lang + " 装备名应该是 6 条"
        tech_loc = files["localisation/%s/more_production_technology_l_%s.yml" % (lang, suffix)]
        assert tech_loc.count('"') == 12, lang + " 科技名应该是 6 条"

    print("生成器自检通过：装备 / 科技 / 结算 / 图标 / 三语言全部符合预期")


if __name__ == "__main__":
    main()
