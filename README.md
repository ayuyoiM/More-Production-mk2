我个菜荀子：
Hi, I have made this mod from the code base of another cereator, huge credit to: Space Maze

Space Maze:
Here's the message from the previous creator explaining how this mod works:

"Hi, if you're reading this, then most likely you're interested in how this mod works.
In fact, everything is simple. An unused, separate equipment with the name and design of manpower has been added.
When it is produced and accumulated in the warehouse, a hidden trigger occurs every week,
which takes away all the manpower produced in the warehouse and adds this number to the current manpower of the country.
Using this technology, you can make the production of anything: stability, political power, research cells, military experience, and so on.
 If you do something similar using my technology, you can use it with credit XD

Have fun!"

 Feels free to make another mod based on my current mod, just make sure to credit me XD

# 万能军工厂

[![Steam](https://img.shields.io/badge/%E5%88%9B%E6%84%8F%E5%B7%A5%E5%9D%8A-Steam?style=flat-square&logo=Steam&label=Steam&color=%23000000)](https://steamcommunity.com/sharedfiles/filedetails/?id=3615184066)
[![Steam Update Date](https://img.shields.io/steam/update-date/3615184066?style=flat-square&label=工坊更新时间)](https://steamcommunity.com/sharedfiles/filedetails/changelog/3615184066)

基于[“我个菜荀子”的万能军工厂](https://steamcommunity.com/sharedfiles/filedetails/?id=3378477376) v0.1 修改而来，新增煤、情报破译、军工组织、学说、核弹制造五条生产线，工厂线补了生产效率和建设速度，并做了分类重构。

游戏 AI 不会使用

适用版本：HOI4 1.20.*

模组版本：1.3.4

更新日志：[CHANGELOG.md](CHANGELOG.md)

## 功能

作弊向模组。用军事工厂生产「虚拟装备」，

装备进仓库后由脚本定期转换成国家的真实资源或属性。

把产能变成工厂、资源、政治点、科研点、人力、经验、军工组织资金、学说精通度、生产效率、建造速度和核弹产能等等。

## 界面结构

决策界面分为：

```t
  生产线管理    三个大类总开关，一次开/关一整个大类；另有占领设备的自动使用开关
  民生          工厂（含生产效率和建设速度）、资源、人力
  军事          设施突破、经验与指挥点、军工组织、学说、核弹制造
  科研          科研点
  外交政治      政治、意识形态、特务、自治、紧张度、情报破译、占领
```

每个大类内部还有逐条的生产线开关，可以只开其中一两条。

科研点线的装备没有开关，常驻生产界面。

生产界面默认什么都不显示，开启对应生产线后装备才会出现。

## 实现原理

- 每种可生产项对应一个不可建造的虚拟装备（archetype + 三档 product）。
- 装备的 can_be_produced 检查国家 flag，flag 由决策开关设置。
- on_weekly / on_daily 定期扫描仓库里的虚拟装备数量，转换成真实属性，
  同时把虚拟装备扣掉。
- 科技只负责解锁装备（enable_equipments），本身不进科技树
  （research_cost = -1，ai_will_do = 0）。

## 致谢

原原模组作者：Space Maze

原模组作者：我个菜荀子

LLM 大语言模型：DeepSeek 4.1 Flash

## 许可证

[MIT](LICENSE)
