import csv
from pathlib import Path
from Enumerators import Color, CardType, CardSuperType
from card import Card

class CardDataLoader:
    """
    Loads MTG card data from a semicolon-separated CSV file.
    Normalizes fields and returns a list of card dictionaries.
    """

    REQUIRED_FIELDS = [
        "name",
        "type",
        "manaCost",
        "color",
        "oracleText",
        "colorIdentity"
    ]

    OPTIONAL_FIELDS = [
        "P",
        "T",
        "supertype",
        "subtype"
    ]

    def load(self, path: str):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")

        if path.suffix.lower() != ".csv":
            raise ValueError("Only CSV files are supported for now")

        cards = self._load_csv(path)
        return [self._normalize(card) for card in cards]

    # ------------------------------------------------------------
    # CSV loader
    # ------------------------------------------------------------
    def _load_csv(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            return list(reader)

    # ------------------------------------------------------------
    # Normalization & validation
    # ------------------------------------------------------------
    def _normalize(self, cardDict: dict):
        # Validate required fields
        for field in self.REQUIRED_FIELDS:
            if field not in cardDict or not cardDict[field].strip():
                raise ValueError(f"Missing required field '{field}' in card: {cardDict}")

        # Strip whitespace
        cardDict = {k: v.strip() if isinstance(v, str) else v for k, v in cardDict.items()}

        # Normalize mana cost
        cardDict["manaCost"] = self._normalize_mana(cardDict["manaCost"])

        # Normalize oracle text
        cardDict["oracleText"] = self._normalize_oracle(cardDict["oracleText"], cardDict["name"])

        # Import the color as a color Enum
        cardDict["color"] = Color.set_from_symbol(cardDict["color"])

        # Import the type as a set of type Enum
        cardDict["type"] = CardType.set_from_symbol(cardDict["type"])

        # Import the supertype as a set of supertype Enum
        cardDict["supertype"] = CardSuperType.set_from_symbol(cardDict["supertype"])


        # Normalize P/T
        cardDict["P"] = cardDict["P"].strip() if cardDict.get("P") else None
        cardDict["T"] = cardDict["T"].strip() if cardDict.get("T") else None

        return Card(
            name=cardDict["name"],
            type=cardDict["type"],
            mana_cost=cardDict["manaCost"],
            color=cardDict["color"],
            colorIdentity=cardDict["colorIdentity"],
            supertype=cardDict["supertype"],
            subtype=cardDict["subtype"],
            power=cardDict.get("P") or None,
            toughness=cardDict.get("T") or None,
            oracle_text=cardDict["oracleText"],
            art = f"assets/art/{cardDict["name"]}"
        )


    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _normalize_mana(self, mana: str):
        """
        Converts mana strings like '3RR' into '{3}{R}{R}'.
        Leaves already-braced mana untouched.
        """
        if "{" in mana:
            return mana  # already formatted

        out = []
        buffer = ""

        for char in mana:
            if char.isdigit():
                buffer += char
            else:
                if buffer:
                    out.append(f"{{{buffer}}}")
                    buffer = ""
                out.append(f"{{{char.upper()}}}")

        if buffer:
            out.append(f"{{{buffer}}}")

        return "".join(out)

    def _normalize_oracle(self, text: str, name: str):
        """
        Cleans oracle text:
        - Converts literal '\n' into real newlines
        - Strips leading/trailing whitespace
        """
        text =  text.replace("\\n", "\n").strip()
        text =  text.replace("~", name).strip()
        return text