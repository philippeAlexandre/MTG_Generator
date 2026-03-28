from enum import Enum
from typing import Set

class FromSymbolMixin:
    @classmethod
    def from_symbol(cls, symbol: str):
        symbol = symbol.strip()

        # Try exact match (case-sensitive)
        for member in cls:
            if member.value == symbol:
                return member

        # Try case-insensitive match
        symbol_lower = symbol.lower()
        for member in cls:
            if isinstance(member.value, str) and member.value.lower() == symbol_lower:
                return member

        raise ValueError(f"Unknown symbol for {cls.__name__}: {symbol}")
    
    @classmethod
    def set_from_symbol(cls, symbol_sequence: str):
        symbol_set = set[cls]()
        symbols = cls._split_symbol_sequence(symbol_sequence)
        for symbol in symbols:
            symbol_set.add(cls.from_symbol(symbol))
        return symbol_set
    
    @classmethod 
    def _split_symbol_sequence(cls, symbol_sequence: str):
        return symbol_sequence.split(" ")

    
    def to_string(self) -> str:
        return str(self.value)
    
    @classmethod
    def set_to_string(cls, values: set["FromSymbolMixin"]) -> str:
        """Convert a set of Enum members into a space-separated string of their values."""
        return " ".join(v.to_string() for v in values)



class Color(FromSymbolMixin, Enum):
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    MULTICOLOR = "M"
    COLORLESS = "C"

    @classmethod
    def from_symbol(cls, symbol: str):
        """
        Convert a single-letter mana symbol into a Color enum.
        Example: 'R' → Color.RED
        """
        symbol = symbol.upper().strip()

        for color in cls:
            if color.value == symbol:
                return color

        raise ValueError(f"Unknown color symbol: {symbol}")
    
    @classmethod 
    def _split_symbol_sequence(cls, symbol_sequence: str):
        return symbol_sequence
    
class CardType(FromSymbolMixin, Enum):
    CREATURE = "Creature"
    SORCERY = "Sorcery"
    INSTANT = "Instant"
    ENCHANTMENT = "Enchantment"
    ARTIFACT = "Artifact"
    PLANESWALKER = "Planeswalker"
    LAND = "Land"

    

class CardSuperType(FromSymbolMixin, Enum):
    LEGENDARY = "Legendary"
    TOKEN = "Token"