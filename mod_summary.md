# More_Production_mk2 — 模组档案总结

## 基本信息

| 项目 | 内容 |
|------|------|
| **模组名称** | More_Production_mk2（万能军工厂） |
| **版本** | 1.2 |
| **游戏版本** | Hearts of Iron IV v1.18.* |
| **Steam ID** | 3615184066 |
| **标签** | Technologies, Military, Gameplay, Fixes |
| **作者** | 基于 Space Maze 的"万能军工厂 v0.1"修改而来，原作者 Steam 链接：[万能军工厂](https://steamcommunity.com/sharedfiles/filedetails/?id=3378477376) |
| **修改说明** | 在原作基础上添加了煤（Coal）的生产 |

---

## 模组概述

本模组通过利用游戏内闲置装备系统，实现用 **军事工厂（Military Factory）生产几乎一切国家属性** 的机制。核心原理是：

1. 通过**决策**消耗"科研点"来解锁对应的**科技**
2. 科技解锁后，可在军工厂生产线中生产对应的**特殊装备**
3. 装备存入仓库后，**每周触发器（on_weekly）** 自动检测库存并将其转换为对应的国家资源/属性

---

## 目录结构

```
More_Production_coal/
├── descriptor.mod                 # 模组描述文件
├── readme.txt                     # 说明文档
├── mod_summary.md                 # 本档案总结文件
├── common/
│   ├── decisions/                 # 决策文件（共15个）
│   │   ├── categories/
│   │   │   ├── flag_decsion_category.txt        # 模式选择界面
│   │   │   └── more_production_category.txt     # 主决策界面
│   │   ├── flag_decision.txt                    # 模式选择（作弊/正常）
│   │   ├── factory_production_decisions.txt     # 工厂生产效率
│   │   ├── manpower_production_decisions.txt    # 人力生产
│   │   ├── political_production_decisions.txt   # 政治点数生产
│   │   ├── resource_production_decisions.txt    # 资源生产（煤、石油、钢等）
│   │   ├── research_point_production_decisions.txt  # 科研点生产
│   │   ├── ideology_production_decisions.txt    # 意识形态支持生产
│   │   ├── agency_production_decisions.txt      # 特务机构生产
│   │   ├── autonomy_production_decisions.txt    # 自治度生产
│   │   ├── diplomatic_production_decisions.txt  # 外交点数生产
│   │   ├── facility_breakthrough_production_decisions.txt  # 设施突破生产
│   │   ├── occupation_production_decisions.txt  # 占领/ Compliance 生产
│   │   ├── world_tension_production_decisions.txt  # 世界紧张度生产
│   │   └── xp_commandpp_production_decisions.txt   # 军事经验&指挥点数生产
│   ├── dynamic_modifiers/
│   │   └── more_production_modifiers.txt        # 动态修正（科研速度、工业产能、特务槽位）
│   ├── on_actions/                              # 每周触发器（共12个）
│   │   ├── factory_on_actions.txt
│   │   ├── manpower_on_actions.txt
│   │   ├── political_on_actions.txt
│   │   ├── resource_on_actions.txt
│   │   ├── research_points_on_actions.txt
│   │   ├── ideology_on_actions.txt
│   │   ├── agency_on_actions.txt
│   │   ├── autonomy_on_actions.txt
│   │   ├── facility_breakthrough_on_actions.txt
│   │   ├── occupation_on_actions.txt
│   │   ├── world_tension_on_actions.txt
│   │   └── xp_commandpp_on_actions.txt
│   ├── technologies/                            # 科技文件（共12个）
│   │   ├── factory_tech.txt
│   │   ├── manpower_tech.txt
│   │   ├── political_tech.txt
│   │   ├── resource_tech.txt
│   │   ├── research_point_tech.txt
│   │   ├── ideology_tech.txt
│   │   ├── agency_tech.txt
│   │   ├── autonomy_tech.txt
│   │   ├── facility_breakthrough_tech.txt
│   │   ├── occupation_tech.txt
│   │   ├── world_tension_tech.txt
│   │   └── xp_commandpp_tech.txt
│   └── units/
│       └── equipment/                           # 装备定义（共12个）
│           ├── factory_equipment.txt
│           ├── manpower_equipment.txt
│           ├── political_equipment.txt
│           ├── resource_equipment.txt
│           ├── research_point_equipment.txt
│           ├── ideology_equipment.txt
│           ├── agency_equipment.txt
│           ├── autonomy_equipment.txt
│           ├── facility_breakthrough_equipment.txt
│           ├── occupation_equipment.txt
│           ├── world_tension_equipment.txt
│           └── xp_commandpp_equipment.txt
├── gfx/
│   └── interface/
│       ├── archetypes/          # 装备图标
│       └── technologies/        # 科技图标
├── interface/
│   └── more_production.gfx     # SpriteType 定义文件
└── localisation/
    ├── chinese/                 # 简体中文本地化
    │   ├── more_production_decision_l_simp_chinese.yml
    │   ├── more_production_dynamic_modifiers_l_simp_chinese.yml
    │   ├── more_production_equipment_l_simp_chinese.yml
    │   └── more_production_technology_l_simp_chinese.yml
    ├── english/                 # 英文本地化
    │   ├── more_production_decision_l_english.yml
    │   ├── more_production_dynamic_modifiers_l_english.yml
    │   ├── more_production_equipment_l_english.yml
    │   └── more_production_technology_l_english.yml
    └── russian/                 # 俄文本地化
        ├── more_production_decision_l_russian.yml
        ├── more_production_dynamic_modifiers_l_russian.yml
        ├── more_production_equipment_l_russian.yml
        └── more_production_technology_l_russian.yml
```

---

## 核心机制详解

### 1. 双模式系统

- **作弊模式（Cheat Mode）**：无消耗解锁所有科技（通过 `flag_decision.txt` 中的决策开启）
- **正常模式（Normal Mode）**：消耗"科研点"来逐步解锁科技，科研点通过"科研点生产线"产出

### 2. 生产流程

```
军工厂生产特殊装备 → 装备存入仓库 → 每周触发器检测 → 转换为对应属性
```

### 3. 可生产项目一览

#### 工厂类（Factory）
| 项目 | 等级 | 说明 |
|------|------|------|
| 民用工厂 | I / II / III | 直接增加民用工厂数量 |
| 军用工厂 | I / II / III | 直接增加军用工厂数量 |
| 海军船坞 | I / II / III | 直接增加海军船坞数量 |

#### 人力类（Manpower）
| 项目 | 等级 | 说明 |
|------|------|------|
| 合成人力 | I / II / III | 生产合成人并加入人力池，III级产出×100倍 |

#### 资源类（Resource）
| 项目 | 等级 | 说明 |
|------|------|------|
| **煤（Coal）** | I / II / III | **本修改版新增**，生产煤资源 |
| 石油（Oil） | I / II / III | 生产石油资源 |
| 铝（Aluminum） | I / II / III | 生产铝资源 |
| 橡胶（Rubber） | I / II / III | 生产橡胶资源 |
| 钢（Steel） | I / II / III | 生产钢铁资源 |
| 钨（Tungsten） | I / II / III | 生产钨资源 |
| 铬（Chromium） | I / II / III | 生产铬资源 |

#### 政治/意识形态类
| 项目 | 等级 | 说明 |
|------|------|------|
| 政治点数 | I / II / III | 生产政治点数 |
| 稳定度 | I / II / III | 生产稳定度 |
| 战争支持度 | I / II / III | 生产战争支持度 |
| 意识形态支持 | 单级 | 生产民主/共产/中立/法西斯四种意识形态支持 |

#### 科研类
| 项目 | 等级 | 说明 |
|------|------|------|
| 科研点 | I / II / III | 科研点循环生产（核心资源） |
| 研究速度 | 动态修正 | 提高研究速度 |
| 特殊项目速度 | 动态修正 | 提高特殊项目研究速度 |

#### 军事经验类
| 项目 | 等级 | 说明 |
|------|------|------|
| 陆军经验 | I / II / III | 生产陆军经验 |
| 海军经验 | I / II / III | 生产海军经验 |
| 空军经验 | I / II / III | 生产空军经验 |
| 指挥点数 | I / II / III | 生产指挥点数 |

#### 特务/外交类
| 项目 | 等级 | 说明 |
|------|------|------|
| 特务机构 | I / II / III | 生产特务机构设施突破 |
| 特务槽位 | 动态修正 | 增加特务槽位 |
| 自治度 | I / II / III | 生产自治度 |
| 外交点数 | I / II / III | 生产外交点数 |

#### 占领/设施类
| 项目 | 等级 | 说明 |
|------|------|------|
| Compliance装备 | I / II / III | 提高非核心领土 compliance |
| 抵抗镇压装备 | I / II / III | 降低非核心领土抵抗度 |
| 陆军设施突破 | I / II / III | 陆军设施突破进度 |
| 海军设施突破 | I / II / III | 海军设施突破进度 |
| 空军设施突破 | I / II / III | 空军设施突破进度 |
| 核设施突破 | I / II / III | 核设施突破进度 |

#### 世界紧张度类
| 项目 | 说明 |
|------|------|
| 增加世界紧张度 | 通过生产提升世界紧张度 |
| 减少世界紧张度 | 通过生产降低世界紧张度 |

---

## 工业产能修正（Dynamic Modifiers）

| 修正名 | 效果 |
|--------|------|
| `research_speed_dymanic_modifier` | 研究速度 & 特殊项目速度提升 |
| `production_dymanic_modifier` | 民用工厂 & 海军船坞工业产能提升 |
| `operative_dymanic_modifier` | 特务槽位增加 |

---

## 本地化支持

模组支持三种语言：
- **简体中文**（`l_simp_chinese`）
- **English**（`l_english`）
- **Русский**（`l_russian`）

---

## 与原版差异（本修改版特色）

相比原模组"万能军工厂 v0.1"，本版本 **新增了煤（Coal）的生产线**：
- 新增 `coal_in_warehouse` 系列装备（原型 + I / II / III 三个等级）
- 新增对应科技 `coal_production_research` 系列
- 新增对应的决策、触发器、本地化文本
- 煤 III 级生产需要消耗 2 煤作为原料，形成正反馈循环
- 完整的 gfx 图标体系支持
