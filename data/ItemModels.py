from enum import StrEnum

from ..Items import ProgressiveUpgrade, SuitUpgrade


class ItemModel(StrEnum):
    IceBeam = "Ice Beam"
    WaveBeam = "Wave Beam"
    PlasmaBeam = "Plasma Beam"
    Missile = "Missile"
    ShinyMissile = "ShinyMissile"
    ScanVisor = "Scan Visor"
    MorphBallBomb = "Morph Ball Bomb"
    PowerBombExpansion = "Power Bomb Expansion"
    Flamethrower = "Flamethrower"
    ThermalVisor = "Thermal Visor"
    ChargeBeam = "Charge Beam"
    SuperMissile = "Super Missile"
    GrappleBeam = "Grapple Beam"
    XRayVisor = "X-Ray Visor"
    IceSpreader = "Ice Spreader"
    SpaceJumpBoots = "Space Jump Boots"
    MorphBall = "Morph Ball"
    CombatVisor = "Combat Visor"
    BoostBall = "Boost Ball"
    SpiderBall = "Spider Ball"
    GravitySuit = "Gravity Suit"
    VariaSuit = "Varia Suit"
    PhazonSuit = "Phazon Suit"
    EnergyTank = "Energy Tank"
    Wavebuster = "Wavebuster"
    PowerBomb = "Power Bomb"
    Cog = "Cog"
    GameCube = "GameCube"
    Zoomer = "Zoomer"
    Metroid = "Nothing"

native_item_mapping: dict[str, str] = {
    SuitUpgrade.Missile_Expansion.value: ItemModel.Missile,
    SuitUpgrade.Missile_Launcher.value: ItemModel.ShinyMissile,
    SuitUpgrade.Main_Power_Bomb.value: ItemModel.PowerBomb,
    SuitUpgrade.Power_Beam.value: ItemModel.SuperMissile,
    ProgressiveUpgrade.Progressive_Power_Beam.value: ItemModel.SuperMissile,
    ProgressiveUpgrade.Progressive_Wave_Beam.value: ItemModel.WaveBeam,
    ProgressiveUpgrade.Progressive_Ice_Beam.value: ItemModel.IceBeam,
    ProgressiveUpgrade.Progressive_Plasma_Beam.value: ItemModel.PlasmaBeam,
}

remote_item_mapping: dict[tuple[str, str], str] = {
    ("Super Metroid", "Energy Tank"): ItemModel.EnergyTank,
    ("Super Metroid", "Missile"): ItemModel.Missile,
    ("Super Metroid", "Super Missile"): ItemModel.ShinyMissile,  # Preferred over Prime super missile model, or nothing?
    ("Super Metroid", "Power Bomb"): ItemModel.PowerBombExpansion,
    ("Super Metroid", "Bomb"): ItemModel.MorphBallBomb,
    ("Super Metroid", "Charge Beam"): ItemModel.ChargeBeam,
    ("Super Metroid", "Ice Beam"): ItemModel.IceBeam,
    # ("Super Metroid", "Hi-Jump Boots"): ItemModel.SpaceJumpBoots,  # Maybe?
    # ("Super Metroid", "Speed Booster"): ItemModel.BoostBall,  # Feels too different
    ("Super Metroid", "Wave Beam"): ItemModel.WaveBeam,
    ("Super Metroid", "Spazer Beam"): ItemModel.SuperMissile,  # Similar reasoning to Power Beam
    ("Super Metroid", "Varia Suit"): ItemModel.VariaSuit,
    ("Super Metroid", "Plasma Beam"): ItemModel.PlasmaBeam,
    ("Super Metroid", "Grappling Beam"): ItemModel.GrappleBeam,
    ("Super Metroid", "Morph Ball"): ItemModel.MorphBall,
    # ("Super Metroid", "Reserve Tank"): ItemModel.EnergyTank,
    ("Super Metroid", "Gravity Suit"): ItemModel.GravitySuit,
    # ("Super Metroid", "X-Ray Scope"): ItemModel.XRayVisor,
    ("Super Metroid", "Space Jump"): ItemModel.SpaceJumpBoots,

    ("SMZ3", "Missile"): ItemModel.Missile,
    ("SMZ3", "Super"): ItemModel.ShinyMissile,
    ("SMZ3", "PowerBomb"): ItemModel.PowerBombExpansion,
    ("SMZ3", "Grapple"): ItemModel.GrappleBeam,
    # ("SMZ3", "XRay"): ItemModel.XRayVisor,
    ("SMZ3", "ETank"): ItemModel.EnergyTank,
    # ("SMZ3", "ReserveTank"): ItemModel.EnergyTank,
    ("SMZ3", "Charge"): ItemModel.ChargeBeam,
    ("SMZ3", "Ice"): ItemModel.IceBeam,
    ("SMZ3", "Wave"): ItemModel.WaveBeam,
    ("SMZ3", "Spazer"): ItemModel.SuperMissile,
    ("SMZ3", "Plasma"): ItemModel.PlasmaBeam,
    ("SMZ3", "Varia"): ItemModel.VariaSuit,
    ("SMZ3", "Gravity"): ItemModel.GravitySuit,
    ("SMZ3", "Morph"): ItemModel.MorphBall,
    ("SMZ3", "Bombs"): ItemModel.MorphBallBomb,
    ("SMZ3", "SpaceJump"): ItemModel.SpaceJumpBoots,
    # ("SMZ3", "HiJump"): ItemModel.SpaceJumpBoots,
    # ("SMZ3", "SpeedBooster"): ItemModel.BoostBall,

    ("Super Metroid Map Rando", "ETank"): ItemModel.EnergyTank,
    ("Super Metroid Map Rando", "Missile"): ItemModel.Missile,
    ("Super Metroid Map Rando", "Super"): ItemModel.ShinyMissile,
    ("Super Metroid Map Rando", "PowerBomb"): ItemModel.PowerBombExpansion,
    ("Super Metroid Map Rando", "Bombs"): ItemModel.MorphBallBomb,
    ("Super Metroid Map Rando", "Charge"): ItemModel.ChargeBeam,
    ("Super Metroid Map Rando", "Ice"): ItemModel.IceBeam,
    # ("Super Metroid Map Rando", "HiJump"): ItemModel.SpaceJumpBoots,
    # ("Super Metroid Map Rando", "SpeedBooster"): ItemModel.BoostBall,
    ("Super Metroid Map Rando", "Wave"): ItemModel.WaveBeam,
    ("Super Metroid Map Rando", "Spazer"): ItemModel.SuperMissile,
    ("Super Metroid Map Rando", "Varia"): ItemModel.VariaSuit,
    ("Super Metroid Map Rando", "Gravity"): ItemModel.GravitySuit,
    # ("Super Metroid Map Rando", "XRay"): ItemModel.XRayVisor,
    ("Super Metroid Map Rando", "Plasma"): ItemModel.PlasmaBeam,
    ("Super Metroid Map Rando", "Grapple"): ItemModel.GrappleBeam,
    ("Super Metroid Map Rando", "SpaceJump"): ItemModel.SpaceJumpBoots,
    ("Super Metroid Map Rando", "Morph"): ItemModel.MorphBall,
    # ("Super Metroid Map Rando", "ReserveTank"): ItemModel.EnergyTank,
    # ("Super Metroid Map Rando", "WallJump"): ItemModel.SpaceJumpBoots,

    ("Metroid Zero Mission", "Energy Tank"): ItemModel.EnergyTank,
    ("Metroid Zero Mission", "Missile Tank"): ItemModel.Missile,
    ("Metroid Zero Mission", "Super Missile Tank"): ItemModel.ShinyMissile,
    ("Metroid Zero Mission", "Power Bomb Tank"): ItemModel.PowerBombExpansion,
    ("Metroid Zero Mission", "Long Beam"): ItemModel.SuperMissile,
    ("Metroid Zero Mission", "Charge Beam"): ItemModel.ChargeBeam,
    ("Metroid Zero Mission", "Ice Beam"): ItemModel.IceBeam,
    ("Metroid Zero Mission", "Wave Beam"): ItemModel.WaveBeam,
    ("Metroid Zero Mission", "Plasma Beam"): ItemModel.PlasmaBeam,
    ("Metroid Zero Mission", "Bomb"): ItemModel.MorphBallBomb,
    ("Metroid Zero Mission", "Varia Suit"): ItemModel.VariaSuit,
    ("Metroid Zero Mission", "Gravity Suit"): ItemModel.GravitySuit,
    ("Metroid Zero Mission", "Morph Ball"): ItemModel.MorphBall,
    # ("Metroid Zero Mission", "Speed Booster"): ItemModel.BoostBall,
    # ("Metroid Zero Mission", "Hi-Jump"): ItemModel.SpaceJumpBoots,
    ("Metroid Zero Mission", "Space Jump"): ItemModel.SpaceJumpBoots,
}
