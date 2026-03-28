from dataclasses import dataclass
from typing import Optional, Set
from Enumerators import Color, CardType, CardSuperType



@dataclass
class Card:
    PLACEHOLDER_IMG_PATH = "assets/art/placeHolder_Dwarf.png"

    name: str    
    type: Set[CardType]
    mana_cost: str
    color: Set[Color]
    colorIdentity: str
    supertype: Set[CardSuperType]
    subtype: str
    power: Optional[str] = None
    toughness: Optional[str] = None
    oracle_text: str = ""
    art: str = PLACEHOLDER_IMG_PATH