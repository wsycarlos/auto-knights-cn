# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Any, Dict, List, Text

import enum, json, copy

from . import data

class Character_Position(Text, enum.Enum):
    MELEE = "MELEE"          #近战
    RANGED = "RANGED"        #远程

class Character_Profession(Text, enum.Enum):
    PIONEER = "PIONEER"      #先锋
    WARRIOR = "WARRIOR"      #近卫
    SNIPER = "SNIPER"        #狙击
    CASTER = "CASTER"        #术士
    TANK = "TANK"            #重装
    MEDIC = "MEDIC"          #医疗
    SUPPORT = "SUPPORT"      #辅助
    SPECIAL = "SPECIAL"      #特种

class Character:
    name: Text
    tagList: List[Text]
    extendTagList: List[Text]
    rarity: int
    position: Character_Position
    profession: Character_Profession

    def __str__(self) -> str:
        return "[%s]:%s"%(self.name, self.extendTagList)


class Character_Table:

    instance: Character_Table

    _character_data: List[Character]
    
    json_data_path: Text

    _public_recruit_detail_text: Text

    _public_recruit_character_names: List[Text]
    
    _public_recruit_data: List[Character]

    def __init__(self, json_data_path: Text, gacha_data_path: Text) -> None:
        self.json_data_path = data.path(json_data_path)
        gacha_data_path = data.path(gacha_data_path)
        with open(self.json_data_path, "r", encoding="utf-8") as f0:
            self._character_data = self.parse_data(json.load(f0))
        with open(gacha_data_path, "r", encoding="utf-8") as f1:
            self._public_recruit_detail_text = json.load(f1)["recruitDetail"]
        self.parse_recruit_text()
        self.isolate_characters()

    def parse_data(self, _data: Dict[Text, Any]) -> List[Character]:
        result: List[Character] = []
        for v in _data.values():
            c = self.parse_character(v)
            result.append(c)
        return result

    def parse_character(self, _data: Dict[Text, Any]) -> Character:
        c = Character()
        c.name = _data["name"]
        c.rarity = _data["rarity"]
        c.position = _data["position"]
        c.profession = _data["profession"]
        c.tagList = _data["tagList"]
        if c.tagList != None and len(c.tagList) > 0:
            c.extendTagList = copy.deepcopy(c.tagList)
        else:
            c.extendTagList = []

        if c.rarity == 0:
            c.extendTagList.append("支援器械")
        #elif c.rarity == 1:
            #c.extendTagList.append("新手")
        elif c.rarity == 4:
            c.extendTagList.append("资深干员")
        elif c.rarity == 5:
            c.extendTagList.append("高级资深干员")

        if c.position == Character_Position.MELEE:
            c.extendTagList.append("近战位")
        elif c.position == Character_Position.RANGED:
            c.extendTagList.append("远程位")

        if c.profession == Character_Profession.PIONEER:
            c.extendTagList.append("先锋干员")
        elif c.profession == Character_Profession.WARRIOR:
            c.extendTagList.append("近卫干员")
        elif c.profession == Character_Profession.SNIPER:
            c.extendTagList.append("狙击干员")
        elif c.profession == Character_Profession.CASTER:
            c.extendTagList.append("术师干员")
        elif c.profession == Character_Profession.MEDIC:
            c.extendTagList.append("医疗干员")
        elif c.profession == Character_Profession.TANK:
            c.extendTagList.append("重装干员")
        elif c.profession == Character_Profession.SUPPORT:
            c.extendTagList.append("辅助干员")
        elif c.profession == Character_Profession.SPECIAL:
            c.extendTagList.append("特种干员")

        return c

    def parse_recruit_text(self):
        self._public_recruit_character_names: List[Text] = []
        lines = self._public_recruit_detail_text.splitlines()
        for line in lines:
            if line.startswith('★'):
                splits = line.split(' / ')
                for split in splits:
                    split = split.replace('★','')
                    split = split.replace('\\n','')
                    split = split.replace('<@rc.eml>','')
                    split = split.replace('</>','')
                    self._public_recruit_character_names.append(split)

    def isolate_characters(self):
        self._public_recruit_data: List[Character] = []
        for c in self._character_data:
            if c.name in self._public_recruit_character_names:
                self._public_recruit_data.append(c)


    @staticmethod
    def GetAllCharacterList() -> List[Character]:
        return Character_Table.instance._character_data

    @staticmethod
    def GetPublicRecruitCharacterList() -> List[Character]:
        return Character_Table.instance._public_recruit_data

Character_Table.instance = Character_Table("character_table.json", "gacha_table.json")