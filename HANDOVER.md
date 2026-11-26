# More_Production_coal 交接文档

最后更新：模组版本 1.3.4 / HOI4 1.20.*

## 一、位置

| 用途 | 路径 |
|------|------|
| 开发目录（本仓库） | `D:\<用户>\File\Game\HOI4\More_Production_coal` |
| 游戏加载目录 | `%USERPROFILE%\Documents\Paradox Interactive\Hearts of Iron IV\mod\More_Production_coal` |

两者用**目录 junction** 连在一起，游戏加载目录指向开发目录。改开发目录即刻生效，不需要复制。

`Documents\...\mod\More_Production_coal.mod` 是独立的描述文件，不在 junction 内，改版本号要单独动。目前已是 `1.20.*`，和 `descriptor.mod` 一致。

游戏本体：`D:\Program Files\Steam\steamapps\common\Hearts of Iron IV`

## 二、目录结构

```
common/
  decisions/
    categories/more_production_category.txt   6 个 category 定义
    flag_decision.txt                          模式选择（作弊/正常）
    production_lines.txt                       生产线管理：三个大类的启用/停用总开关 + 占领自动化
    <类别>_production_decisions.txt            15 个，各类研究决策 + 细类开关
    debug_production_decisions.txt             调试：一键解锁（仅 -debug）
  units/equipment/<类别>_equipment.txt         15 个，虚拟装备定义
  technologies/<类别>_tech.txt                 15 个，解锁装备的科技
  on_actions/<类别>_on_actions.txt             15 个，定期转换逻辑
  on_actions/more_production_misc_on_actions.txt  手写，维护决策提示用的换算值
  dynamic_modifiers/more_production_modifiers.txt
localisation/{chinese,english,russian}/        三语言，各 4 个 yml
interface/more_production.gfx
gfx/interface/{archetypes,technologies}/
tools/
  check.py                                    静态校验，改完必跑
  gen.py                                      生成器
  test_gen.py                                 生成器自检
  import_lines.py                             从现有 txt 反推配置，迁移用
  compare_gen.py                              比对生成结果和现有文件的结构
  format_txt.py                               缩进统一成 tab
  lines/<组>.toml                             生产线配置（要手改的就这里）
descriptor.mod
readme.txt
HANDOVER.md
```

`common/units/equipment`、`common/technologies`、`common/on_actions` 这三组文件，以及装备名和科技名的三语言 yml，都由 `tools/gen.py` 生成，不要手改。改配置表再跑生成器。

所有生产线都已经迁进配置表，上面那几类文件全部由生成器产出。改生产线就改 `tools/lines/<组>.toml`，改完跑 `python tools/gen.py`，别直接动生成出来的文件。

## 三、数据流

```
决策「研究」→ set_technology 解锁装备
决策「启用生产线」→ set_country_flag = mp_tab_xxx
装备 can_be_produced 检查该 flag → 出现在生产界面
军事工厂生产虚拟装备 → 进仓库
on_weekly / on_daily 扫描仓库 → 转换成真实属性 → 扣掉虚拟装备
```

## 四、四层文件的职责

| 层 | 文件 | 作用 |
|----|------|------|
| 装备 | `*_equipment.txt` | archetype（不可建造）+ 三档 product（可建造）。product 带 `can_be_produced` |
| 科技 | `*_tech.txt` | `enable_equipments` 解锁装备。`research_cost = -1`，`ai_will_do = 0`，不进科技树 |
| 决策 | `*_decisions.txt` | 研究决策（花科研点给科技）+ 细类生产线开关 |
| 触发器 | `*_on_actions.txt` | 定期把仓库装备换成真实属性 |

## 五、加一条新生产线的完整步骤

装备、科技、每周结算、图标、装备名和科技名这五类现在由生成器产出。手写的只剩决策和决策相关的本地化。

1. **写配置**：在 `tools/lines/<组>.toml` 里加一段 `[[production_line]]`，填 id、组、三语名字、国家标记、archetype、三档装备（id / 年份 / 成本 / 三语描述）、三个科技 id、结算动作、贴图路径。

2. **跑生成器**：`python tools/gen.py`。上面五类文件自动更新。想先看效果就 `python tools/gen.py --only <id> --out <目录>`。

3. **写决策**：照现有文件抄三条研究决策（`set_technology`，`available` 里带 `NOT = { has_tech = <目标科技> }`），要独立开关就加一对 `mp_enable_<细类>_tab` / `mp_disable_<细类>_tab`。

4. **补决策本地化**：`more_production_decision_l_*.yml` 三语言，决策名 + flag 名。

5. **校验**：`python tools/check.py` 错误必须清零，`python tools/test_gen.py` 跑一下生成器自检。

6. **进游戏**：看 error.log 有没有本模组报错，看生产界面图标和数值。

### 结算动作怎么写

配置里 `[[production_line.effect]]` 按顺序执行，可用的 type：

| type | 参数 | 效果 |
|---|---|---|
| `divide_variable` | `by` | 把这一档的件数除以 N |
| `add_to_variable` | `target` | 加到指定变量 |
| `add_building` | `building` | 加建筑，如 `industrial_complex` |
| `add_resource` | `resource` | 加资源 |
| `add_manpower` / `add_political_power` / `add_stability` / `add_war_support` | 无 | 加对应国家属性 |
| `add_mio_funds` | 无 | 加军工组织资金 |
| `add_mastery` | 无 | 加学说精通（写进 `doctrine_mastery_pool`） |
| `add_equipment` | `equipment` | 加装备 |

写了表里没有的 type，生成器直接报错退出。

## 六、已知陷阱（都踩过）

1. **决策文件的格式**
   决策文件的外层块名**必须等于 category 名**，决策内部**不能写 `category = ...`**。写错会报 `Unknown category` / `Unexpected token: category`，决策被静默忽略。
   ```
   mp_cat_civilian = {          ← 外层就是 category
       some_decision = { ... }
   }
   ```
   多个文件用同一个外层名会合并，可以把一个大类拆到多个文件。

2. **`available` 和 `visible` 的区别**
   - `visible` 控制显不显示
   - `available` 只控制灰/亮，决策仍然占着界面

   想让决策点完消失，条件要写在 `visible` 里。写成 `available` 会变成「点了变灰但还在」。

3. **flag 需要本地化**
   `has_country_flag` 在 tooltip 里显示的是 flag 名，而 flag 名会被当成本地化 key 去查。不加条目就显示 `mp_tab_factory` 这种原始 key。每个 `mp_tab_*` 都要在 yml 里加一行。

4. **同名 on_action 依赖引擎合并**
   每个 `on_actions` 文件里有多个同名的 `on_weekly` / `on_daily` 块，靠引擎把同名块合并执行。这是现有写法，没出过问题，但属于隐性依赖，别随手去重。

5. **缩进不统一**
   有的文件用 tab，有的用 4 空格，甚至同一文件混用（`agency_production_decisions.txt` 就是）。写批量脚本时按**视觉缩进**（tab 当 4 空格）判断层级，别按字符长度。

6. **批量改本地化别用「删所有 mp_ 行」**
   flag 条目也在 `mp_` 前缀下，粗暴过滤会一起扫掉，tooltip 又会变回原始 key。

7. **`descriptor.mod` 和 `.mod` 是两份**
   工作区里的 `descriptor.mod` 改了，`Documents\...\mod\More_Production_coal.mod` 不会跟着变。后者决定启动器显示的版本和过时警告。

8. **科研点 / 占领两条线没有开关**
   这两类的装备常驻生产界面，不检查 flag。加新细类时别照抄这两类的写法。

9. **`add_mastery` 不加 filter 会灌所有活跃 track**
   文档：不给 `folder` / `grand_doctrine` / `sub_doctrine` / `track` 等 filter 时，mastery 加到所有已激活的 track。它也只对已激活的 track 生效，没选大战略时点了白扣池子，所以三条投入决议的 `available` 里加了 `has_any_grand_doctrine` 门槛。`doctrine_mastery_pool` 在模式选择决策里初始化为 0。

10. **新生产线的成本别抄人力线**
    人力线是 `0.17 / 0.01 / 0.001`，因为 1 件只给 1 点人力，人力不值钱。学说、军工组织、情报这三条早期照抄了这个价，结果一件的成本比政治点线便宜一百多倍，一周刷出几万件。现在统一按政治点线定价：`30 / 15 / 5`，整数，三档递减。目标是小数百分比字段的（情报的两个 factor），结算时再 `divide_variable`，情报是除 100，参照政治点线里稳定度的写法。

11. **`clamp_variable` 的 `max` 引用变量前要判存在**
    `max = mp_loop_cap` 这种写法，变量不存在时按 0 处理，会把已有加成一次性清空。生成器现在给 clamp 外面包了 `check_variable = { mp_loop_cap > 0 }`，老存档没有这个变量时直接跳过封顶。以后加新的可调上限照这个写法。

## 七、当前状态

已完成：
- 生产项按民生 / 军事 / 科研 / 外交政治四大类拆分
- 每个大类内部有细类生产线开关
- 生产线管理里的大类总开关（先启用后停用，分段排列）
- 六个分类 priority 设为 -1 ~ -6，排在所有原版决议分类（最低 0）之后
- 占领设备自动化决策在生产线管理（mp_cat_lines）里
- 调试分类一键解锁全部（`activate_decision` 逐个激活研究决策）
- 三语言本地化
- 三条新生产线：情报破译、军工组织、学说
- 全部决策与科技图标补齐，六个分类各配独立图标
- 占领设备决策搬到外交政治分类
- 学说精通度改为决议投入（`doctrine_mastery_invest_100/1000/10000`），三语言本地化已补
- 三个历史决策缺的本地化键已补齐
- 学说 / 军工组织 / 情报破译三条线成本改为 30 / 15 / 5，情报结算除 100
- 工厂线新增生产效率生产项（成本 1000 / 500 / 100，结算除 100，喂 `production_factory_efficiency_gain_factor` 和 `production_factory_max_efficiency_factor`）
- 工厂线新增建设速度（喂 `production_speed_buildings_factor`）
- 核弹制造生产线已移除（原版核弹靠特殊项目产出，这条线收益绕、门槛还卡在特殊项目上）
- 装备 / 科技 / 每周结算 / 图标 / 装备名与科技名改由 `tools/gen.py` 从 `tools/lines/*.toml` 生成
- `tools/check.py` 静态校验：括号、逗号、重名精灵、多帧贴图、本地化键覆盖、变量初始化
- `tools/format_txt.py` 统一 txt 缩进为 tab
- 正反馈上限五档（`mp_loop_cap`，管工厂产出 / 生产效率 / 建设速度三条线，入口在生产线管理分类）
- 资源线七条的第一档补上 0.5 资源消耗
- 军事总开关不再误开占领线；一键解锁全部改为一次性

未做：
- `mod_summary.md` 已过时，内容被本文档取代，可以删
- 生产线管理分类的描述没做出来：普通分类不支持 `desc`，动态分类要按国家写 `custom_icon`，做不出通用描述
- 有 11 条线整条三档都不配 `resources`（agency 一条、autonomy 两条、factory 六条、核弹线已删），生产不消耗资源，暂时不补
