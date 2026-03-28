from dataclasses import dataclass
from typing import Optional, Set
from Enumerators import Color, CardType, CardSuperType



@dataclass
class Card:
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
    art: str = "assets/art/placeHolder_Lockwell.jpg"