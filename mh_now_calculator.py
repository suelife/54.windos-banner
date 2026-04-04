"""
Monster Hunter Now - 配裝與素材計算工具 (最簡版)

資料結構設計：
  Material   - 素材
  Skill      - 技能
  Equipment  - 裝備（武器或防具）
  Build      - 配裝（一組裝備）
  Calculator - 計算所需素材
"""

from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────
# 資料結構
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class Material:
    id: str
    name: str

    def __repr__(self):
        return f"Material({self.name})"


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    max_level: int

    def __repr__(self):
        return f"Skill({self.name})"


@dataclass
class CraftRequirement:
    """一個裝備在某個等級所需的素材"""
    material: Material
    quantity: int


@dataclass
class UpgradeLevel:
    """裝備升到這個等級的需求"""
    level: int
    craft_requirements: list[CraftRequirement]


@dataclass
class Equipment:
    id: str
    name: str
    kind: str                          # "weapon" | "head" | "chest" | "arm" | "waist" | "leg"
    skills: dict[Skill, int]           # 技能 → 等級
    upgrade_levels: list[UpgradeLevel] # 每個升級階段的素材需求

    def materials_up_to(self, target_level: int) -> dict[Material, int]:
        """計算升到 target_level 所需的全部素材"""
        totals: dict[Material, int] = {}
        for ul in self.upgrade_levels:
            if ul.level <= target_level:
                for req in ul.craft_requirements:
                    totals[req.material] = totals.get(req.material, 0) + req.quantity
        return totals

    def __repr__(self):
        return f"Equipment({self.name}, {self.kind})"


@dataclass
class BuildSlot:
    equipment: Equipment
    target_level: int


@dataclass
class Build:
    name: str
    slots: list[BuildSlot] = field(default_factory=list)

    def add(self, equipment: Equipment, target_level: int):
        self.slots.append(BuildSlot(equipment, target_level))

    def total_materials(self) -> dict[Material, int]:
        """統計整套配裝所需素材"""
        totals: dict[Material, int] = {}
        for slot in self.slots:
            for mat, qty in slot.equipment.materials_up_to(slot.target_level).items():
                totals[mat] = totals.get(mat, 0) + qty
        return totals

    def active_skills(self) -> dict[str, int]:
        """統計整套配裝的技能總等級"""
        skills: dict[str, int] = {}
        for slot in self.slots:
            for skill, lv in slot.equipment.skills.items():
                skills[skill.name] = skills.get(skill.name, 0) + lv
        return skills


# ──────────────────────────────────────────────
# 假資料
# ──────────────────────────────────────────────

# 素材
BONE_S   = Material("bone_s",   "骨頭小")
BONE_M   = Material("bone_m",   "骨頭中")
IRON_ORE = Material("iron_ore", "鐵礦石")
RATHALOS_SCALE  = Material("rath_scale",  "雷狼龍鱗片")
RATHALOS_WING   = Material("rath_wing",   "雷狼龍翼")
ZINOGRE_CLAW    = Material("zino_claw",   "雷狼龍爪")
ZINOGRE_THUNDER = Material("zino_thunder","雷狼龍雷電袋")

# 技能
SKILL_ATK  = Skill("atk",  "攻擊",     7)
SKILL_CRIT = Skill("crit", "看破",     7)
SKILL_GUARD= Skill("guard","守勢",     5)
SKILL_WEX  = Skill("wex",  "弱點特效", 3)

# 裝備：骨頭大劍 (weapon)
BONE_GS = Equipment(
    id="bone_gs",
    name="骨頭大劍",
    kind="weapon",
    skills={SKILL_ATK: 1},
    upgrade_levels=[
        UpgradeLevel(1, [CraftRequirement(BONE_S, 2)]),
        UpgradeLevel(2, [CraftRequirement(BONE_S, 4)]),
        UpgradeLevel(3, [CraftRequirement(BONE_M, 2), CraftRequirement(IRON_ORE, 1)]),
        UpgradeLevel(4, [CraftRequirement(BONE_M, 4), CraftRequirement(IRON_ORE, 2)]),
        UpgradeLevel(5, [CraftRequirement(BONE_M, 6), CraftRequirement(IRON_ORE, 3)]),
    ]
)

# 裝備：雷狼龍頭盔 (head)
ZINOGRE_HELM = Equipment(
    id="zino_helm",
    name="雷狼龍頭盔",
    kind="head",
    skills={SKILL_CRIT: 2, SKILL_WEX: 1},
    upgrade_levels=[
        UpgradeLevel(1, [CraftRequirement(ZINOGRE_CLAW, 1)]),
        UpgradeLevel(2, [CraftRequirement(ZINOGRE_CLAW, 2)]),
        UpgradeLevel(3, [CraftRequirement(ZINOGRE_CLAW, 2), CraftRequirement(ZINOGRE_THUNDER, 1)]),
    ]
)

# 裝備：火龍胸甲 (chest)
RATHALOS_CHEST = Equipment(
    id="rath_chest",
    name="火龍胸甲",
    kind="chest",
    skills={SKILL_ATK: 2, SKILL_CRIT: 1},
    upgrade_levels=[
        UpgradeLevel(1, [CraftRequirement(RATHALOS_SCALE, 2)]),
        UpgradeLevel(2, [CraftRequirement(RATHALOS_SCALE, 4)]),
        UpgradeLevel(3, [CraftRequirement(RATHALOS_SCALE, 4), CraftRequirement(RATHALOS_WING, 1)]),
        UpgradeLevel(4, [CraftRequirement(RATHALOS_SCALE, 6), CraftRequirement(RATHALOS_WING, 2)]),
    ]
)


# ──────────────────────────────────────────────
# 計算工具
# ──────────────────────────────────────────────

def print_build_summary(build: Build):
    print(f"\n{'='*50}")
    print(f"  配裝名稱：{build.name}")
    print(f"{'='*50}")

    print("\n【裝備清單】")
    for slot in build.slots:
        eq = slot.equipment
        print(f"  {eq.kind:6s} | {eq.name} → 升到 Lv{slot.target_level}")

    print("\n【技能總覽】")
    for skill_name, total_lv in sorted(build.active_skills().items()):
        print(f"  {skill_name:10s} Lv{total_lv}")

    print("\n【所需素材】")
    for mat, qty in sorted(build.total_materials().items(), key=lambda x: x[0].name):
        print(f"  {mat.name:16s} x{qty}")

    print()


# ──────────────────────────────────────────────
# 範例執行
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # 配裝 A：骨頭大劍 + 雷狼龍頭盔 + 火龍胸甲
    build_a = Build("攻擊流配裝")
    build_a.add(BONE_GS,       target_level=5)
    build_a.add(ZINOGRE_HELM,  target_level=3)
    build_a.add(RATHALOS_CHEST,target_level=4)

    print_build_summary(build_a)

    # 只查單件裝備所需素材
    print("──── 只升雷狼龍頭盔到 Lv2 需要 ────")
    for mat, qty in ZINOGRE_HELM.materials_up_to(2).items():
        print(f"  {mat.name} x{qty}")
