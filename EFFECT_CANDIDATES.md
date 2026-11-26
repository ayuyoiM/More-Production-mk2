# COUNTRY 作用域 Effect 候选清单（1.20.0）

来源：游戏自带 `documentation/effects_documentation.md`，COUNTRY 作用域共 **323** 个 effect。
按「能不能当生产项」分三档。C 档只列名字，不逐个写说明。

## A 档 — 建议加

天然有上限、或一次性解锁，叠不起来。

| effect | 作用 | 上限 / 备注 |
| --- | --- | --- |
| `add_research_slot` | 增加科研槽，负数可减 | 游戏硬上限 5 个科研槽，超了无效 |
| `set_research_slots` | 直接设定科研槽数量 | 同上，且会覆盖原值 |
| `add_mio_size` | MIO 规模 +N | 每个 MIO 有 size 上限，满了不再出新政策 |
| `add_mio_funds` | MIO 资金 +N | 资金越过升规模线会自动升 size，size 满了才真溢出 |
| `complete_mio_trait` | 完成指定 MIO 特质 | 要具体 trait token，每个 MIO 树不同，没法一条通用 |
| `add_mio_task_capacity` | MIO 任务容量 +N | ⚠️ 无上限，能无限接任务 |
| `add_fuel` | 加燃料 | 受 fuel_capacity 卡死，不配加容量就是白给 |
| `set_fuel` | 直接设定燃料存量 | 同上 |
| `set_fuel_ratio` | 设定燃料占容量比例 | 同上，但按比例不浪费 |
| `add_intel` | 对目标国加情报 | 情报上限 100，需指定目标国 |
| `add_decryption` | 对目标国加破译进度 | 有上限，需指定目标国 |
| `add_collaboration` | 对目标国加合作政府进度 | 上限 100，需指定目标国 |
| `create_intelligence_agency` | 建立情报局 | 只能建一次，已有则无事 |
| `upgrade_intelligence_agency` | 升级情报局部门 | 情报局 5 个部门槽，有限 |
| `add_design_template_bonus` | 设计折扣（限次数） | 有 uses 次数上限 |
| `add_doctrine_cost_reduction` | 学说成本折扣（限次数） | 有 uses 次数上限 |
| `add_tech_bonus` | 科技加成（限次数） | 有 uses 次数上限 |
| `set_grand_doctrine` | 直接解锁并指定大师学说 | 一次性，已选会覆盖 |
| `set_sub_doctrine` | 直接解锁并指定子学说 | 一次性 |
| `add_cic` | 加国际市场中的经济产能盈余 | 看数值 |
| `add_equipment_subsidy` | 加装备补贴 | 需确认有没有上限 |
| `add_resource` | 州资源产出 +N | 州资源有上限 |
| `add_mines` | 战略区布雷 +N | 有上限 |
| `add_offsite_building` | 加场外建筑 | ⚠️ 无上限 |
| `add_equipment_production` | 直接建一条生产线 | 受工厂数限制 |
| `unlock_subunit` | 解锁兵种 | 一次性 |
| `add_breakthrough_points` | 特种项目突破点 +N | ⚠️ 无上限 |
| `add_operation_token` | 加间谍行动 token | 每次行动消耗 |
| `create_production_license` | 获得生产许可 | 一次性 |
| `unlock_tactic` | 解锁战术 | 一次性 |
| `add_to_tech_sharing_group` | 加入科技共享组 | 一次性 |
| `create_import` | 建立进口 | 有上限 |
| `generate_scientist_character` | 生成科学家 | 一次性 |
| `create_operative_leader` | 生成间谍 | 一次性 |
| `create_equipment_variant` | 创建装备变体 | 一次性，需参数 |

## B 档 — 能加但会超模

数值型，没上限，刷几次就崩。**这就是你说不加的那两百多个**。要加的话建议配上限（比如每周刷新量固定、或加个计数器）。

| effect | 作用 |
| --- | --- |
| `add_nuclear_bombs` | 加核弹 |
| `add_manpower` | 加人力 |
| `add_political_power` | 加政治点 |
| `set_political_power` | 直接设定政治点 |
| `add_scaled_political_power` | 按 IC 差加政治点 |
| `add_command_power` | 加指挥点 |
| `add_stability` | 加稳定度 |
| `set_stability` | 直接设定稳定度 |
| `add_war_support` | 加战争支持 |
| `set_war_support` | 直接设定战争支持 |
| `add_legitimacy` | 加合法性 |
| `add_popularity` | 加意识形态支持 |
| `set_popularities` | 设定全部意识形态支持 |
| `add_threat` | 加威胁度 |
| `add_named_threat` | 加具名威胁度 |
| `add_autonomy_ratio` | 按比例加自治度 |
| `add_autonomy_score` | 按点数加自治度 |
| `army_experience` | 加陆军经验 |
| `navy_experience` | 加海军经验 |
| `air_experience` | 加空军经验 |
| `add_mastery` | 加学说精通点 |
| `add_daily_mastery` | 每日加学说精通点 |
| `add_mastery_bonus` | 精通点获取加成 |
| `add_ideas` | 挂国家精神 |
| `add_timed_idea` | 挂限时国家精神 |
| `add_dynamic_modifier` | 挂动态修正 |
| `add_equipment_to_stockpile` | 直接给装备 |
| `add_equipment_bonus` | 加装备属性加成 |
| `add_unit_bonus` | 加部队属性加成 |
| `add_ace` | 加王牌飞行员 |
| `add_trait` | 给将领加特质 |
| `add_units_to_division_template` | 加师编制单位 |
| `add_opinion_modifier` | 加外交好感 |
| `add_relation_modifier` | 加双边关系修正 |
| `add_mio_policy_cost` | 改 MIO 政策基础成本 |
| `add_mio_policy_cooldown` | 改 MIO 政策基础冷却 |
| `set_mio_policy_cost` | 设定 MIO 政策成本 |
| `set_mio_policy_cooldown` | 设定 MIO 政策冷却 |
| `add_breakthrough_progress` | 加特种项目突破进度 |
| `inherit_technology` | 继承别国科技 |
| `steal_random_tech_bonus` | 偷科技 |
| `complete_special_project` | 直接完成特殊项目 |
| `set_technology` | 直给科技 |
| `unlock_national_focus` | 解锁国策 |
| `complete_national_focus` | 直接完成国策 |
| `reduce_focus_completion_cost` | 降低国策完成成本 |
| `set_division_template_cap` | 设定师模板上限 |
| `generate_character` | 生成角色 |

## C 档 — 不建议

外交、军事动作、剧情触发、调试工具、遍历容器。当生产项没意义。

```
activate_advisor  activate_decision  activate_mission  activate_mission_tooltip  activate_shine_on_focus  activate_targeted_decision
add_advisor_role  add_ai_strategy  add_civil_war_target  add_contested_owner  add_corps_commander_role  add_country_leader_role
add_country_leader_trait  add_days_mission_timeout  add_days_remove  add_faction_goal  add_faction_goal_slot  add_faction_influence_ratio
add_faction_influence_score  add_faction_initiative  add_faction_power_projection  add_field_marshal_role  add_naval_commander_role  add_relation_rule_override
add_scientist_role  add_state_claim  add_state_core  add_to_faction  add_to_war  ai_message
annex_country  become_exiled_in  break_embargo  capture_operative  career_profile_step_missiolini  character_list_tooltip
clear_division_template_cap  clear_rule  clr_country_flag  country_event  country_lock_all_division_template  create_colonial_division_template
create_corps_commander  create_country_leader  create_faction  create_faction_from_template  create_field_marshal  create_navy_leader
create_ship  create_wargoal  damage_building  deactivate_advisor  deactivate_shine_on_focus  declare_war_on
delete_unit  delete_unit_template_and_units  delete_units  destroy_ships  diplomatic_relation  dismantle_faction
division_template  drop_cosmetic_tag  end_exile  end_puppet  every_allied_country  every_army_leader
every_character  every_controlled_state  every_core_state  every_country_division  every_country_with_original_tag  every_enemy_country
every_faction_member  every_military_industrial_organization  every_navy_leader  every_neighbor_country  every_occupied_country  every_operative
every_other_country  every_owned_state  every_subject_country  every_unit_leader  force_update_dynamic_modifier  free_operative
free_random_operative  get_highest_scored_country  get_highest_scored_country_temp  get_sorted_scored_countries  get_sorted_scored_countries_temp  get_supply_vehicles
get_supply_vehicles_temp  give_guarantee  give_market_access  give_military_access  give_resource_rights  global_every_army_leader
goto_province  hold_election  kill_country_leader  kill_ideology_leader  kill_operative  launch_nuke
leave_faction  load_focus_tree  load_oob  mark_focus_tree_layout_dirty  mark_technology_tree_layout_dirty  modify_building_resources
modify_country_flag  modify_tech_sharing_bonus  modify_timed_idea  news_event  party_leader  print_variables
promote_character  puppet  random_allied_country  random_army_leader  random_character  random_controlled_state
random_core_state  random_country_division  random_enemy_country  random_military_industrial_organization  random_navy_leader  random_neighbor_country
random_occupied_country  random_operative  random_owned_controlled_state  random_owned_state  random_purchase_contract  random_subject_country
random_unit_leader  recall_attache  recall_volunteers_from  recruit_character  release  release_autonomy
release_captured_generals_from  release_on_controlled  release_puppet  release_puppet_on_controlled  remove_advisor_role  remove_building
remove_civil_war_target  remove_contested_owner  remove_country_leader_role  remove_country_leader_trait  remove_decision  remove_decision_on_cooldown
remove_dynamic_modifier  remove_faction_goal  remove_from_faction  remove_from_tech_sharing_group  remove_ideas  remove_ideas_with_trait
remove_mission  remove_operation_token  remove_opinion_modifier  remove_power_balance  remove_relation_modifier  remove_relation_rule_override
remove_resource_rights  remove_scientist_role  remove_state_claim  remove_state_core  remove_targeted_decision  remove_trait
remove_unit_leader  remove_unit_leader_role  remove_wargoal  reserve_dynamic_country  retire_character  retire_country_leader
retire_ideology_leader  reverse_add_opinion_modifier  scoped_play_song  scoped_sound_effect  select_tech_tree_icon_origin  send_embargo
send_equipment  send_equipment_fraction  set_air_oob  set_autonomy  set_can_be_fired_in_advisor_role  set_capital
set_character_name  set_collaboration  set_cosmetic_tag  set_country_flag  set_country_leader_description  set_country_leader_ideology
set_country_leader_name  set_country_leader_portrait  set_division_force_allow_recruiting  set_division_template_lock  set_equipment_fraction  set_equipment_version_number
set_faction_leader  set_faction_manifest  set_faction_member_upgrade_min  set_faction_name  set_faction_rule  set_faction_spymaster
set_faction_upgrade  set_keyed_oob  set_legitimacy  set_major  set_nationality  set_naval_oob
set_occupation_law  set_occupation_law_where_available  set_oob  set_party_name  set_party_rule  set_political_party
set_politics  set_portraits  set_power_balance  set_province_controller  set_relation_rule  set_rule
set_state_controller  set_state_owner  set_truce  show_ideas_tooltip  show_mio_tooltip  show_unit_leaders_tooltip
start_civil_war  start_peace_conference  state_event  swap_ideas  swap_ruler_traits  teleport_railway_guns_to_deploy_province
transfer_navy  transfer_ship  transfer_state  transfer_units_fraction  turn_operative  uncomplete_national_focus
unlock_decision_category_tooltip  unlock_decision_tooltip  unlock_military_industrial_organization_tooltip  white_peace
```

合计：A 35 + B 48 + C 244 = 327
