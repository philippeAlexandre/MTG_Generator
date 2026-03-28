from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from card import Card
from Enumerators import CardType, CardSuperType, Color
import re
import math

class CardRenderer:
    WIDTH = 744
    HEIGHT = 1039

    # Layout constants
    NAME_X = 70
    NAME_Y = 60

    ART_X = 62
    ART_Y = 138
    ART_W = 620
    ART_H = 460

    TYPE_X = 70
    TYPE_Y = 600
    TYPE_W = 600

    ORACLE_X = 70
    ORACLE_Y = 660
    ORACLE_W = 600
    ORACLE_H = 310

    PT_X = 640
    PT_Y = 940

    MANA_COST_PADDING = 70

    FRAME_DIR = Path("assets/frames")
    OUTPUT_DIR = Path("output")
    

    FONT_NAME = "assets/fonts/Beleren2016.ttf"
    FONT_RULES = "assets/fonts/mplantin.ttf"

    NAME_FONT_SIZE = 40
    MANA_FONT_SIZE = 38
    TYPE_FONT_SIZE = (36, 34, 32, 30, 28)
    ORACLE_FONT_SIZE = (36, 32, 28)
    MANA_COST_ORACLE_DIF = 6
    MAX_LINE_ORACLE = 7
    PT_FONT_SIZE = 40

    MANA_PATTERN = re.compile(r"\{([^}]+)\}")

    TABLE_CHAR_TRANS = str.maketrans({
    "é": "e",
    "è": "e",
    "ê": "e",
    "ë": "e",
    "à": "a",
    "â": "a",
    "ô": "o",
    "î": "i",
    "ç": "c",
    "’": "",
    "'": "",
    ":": "",
    " ": "_",
    ",": "",
    })


    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def render_card(self, card: Card, output_path: Optional[str] = None) -> None:
        """Render a full MTG card to an image file."""
        self.canvas: Image.Image = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.canvas)

        self._draw_art(card)
        self._draw_frame(card)
        self._draw_name(card)
        self._draw_type_line(card)
        self._draw_oracle_text(card)
        self._draw_mana_cost(card)

        if card.power and card.toughness:
            self._draw_power_toughness(card)

        if output_path is None:
            card_name_safe = card.name.translate(self.TABLE_CHAR_TRANS)
            output_path = f"{self.OUTPUT_DIR}/{card.colorIdentity.upper()}/{card_name_safe}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.canvas.save(output_path)

    # ------------------------------------------------------------
    # Text helpers
    # ------------------------------------------------------------
    def _load_font(self, path: str, size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(path, size)

    def _wrap_text_pixel(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int
    ) -> Tuple[str, int]:
        """Pixel-accurate word wrapping."""
        words = text.replace("\n", " \n ").split(" ")
        lines = []
        current = ""

        for word in words:
            if word == "\n":
                lines.append(current.strip())
                current = ""
                continue

            test = current + word + " "
            if font.getlength(test) <= max_width:
                current = test
            else:
                lines.append(current.strip())
                current = word + " "

        if current.strip():
            lines.append(current.strip())

        return ("\n".join(lines), len(lines))

    def _smart_title_case(self, text: str) -> str:
        small_words = {
            "a", "an", "the",
            "and", "but", "or", "nor", "for", "so", "yet",
            "at", "by", "in", "of", "on", "to", "up", "off", "out",
            "over", "into", "with", "from"
        }

        words = text.split()
        result = []

        for i, word in enumerate(words):
            lower = word.lower()

            #searches for the first apostrophe and capitalizes the next character
            posApostrophe = lower.find("'") 
            if posApostrophe > -1:
                lower = lower[0:posApostrophe+1] + lower[posApostrophe+1].upper() + lower[posApostrophe+2:]

            if i == 0:
                result.append(lower[0].upper()+lower[1:])
            elif lower in small_words:
                result.append(lower)
            else:
                result.append(lower[0].upper()+lower[1:])

        return " ".join(result)

    # ------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------
    def _draw_text(
            self,
            text: str,
            x: int,
            y: int,
            font_path: str,
            size,
            max_width: Optional[int] = None,
            max_line: int = 1,
            centered_x: bool = False,
            centered_y_height: Optional[int] = None
        ) -> None:

        # 1. Determine font size (your existing logic)
        if max_width:
            text_ini = text
            n_lines = max_line + 1
            font_index = 0
            while n_lines > max_line and font_index < len(size):
                font = self._load_font(font_path, size[font_index])
                (text, n_lines) = self._wrap_text_pixel(text_ini, font, max_width)
                font_index += 1
        else:
            font = self._load_font(font_path, size)

        # 2. If centered, adjust x
        if centered_x:
            x = x - font.getlength(text) / 2

        # 3. Split into lines
        lines = text.split("\n")
        line_height = font.size + 4
        block_height = len(lines) * line_height

        if centered_y_height is not None:
            y = y + (centered_y_height - block_height) // 2

        line_y = y

        for line in lines:
            cursor_x = x

            # Split into text and mana tokens
            parts = self.MANA_PATTERN.split(line)
            # Example: "{R}, {T}: Deal 2 damage to any target" → ["{R}", ", ", "{T}", ": Deal 2 damage to any target"]

            is_token = False
            for part in parts:
                if not is_token:
                    # Normal text
                    self.draw.text((cursor_x, line_y), part, font=font, fill=(0, 0, 0, 255))
                    cursor_x += font.getlength(part)
                else:
                    # Mana symbol
                    cursor_x += self._draw_inline_mana(cursor_x, line_y + 2, part, size=font.size - self.MANA_COST_ORACLE_DIF)
                is_token = not is_token

            line_y += font.size + 4  # line spacing

    def _draw_inline_mana(self, x, y, token, size=20):
        """
        Draw a mana symbol inline with text.
        token is the inside of {...}, e.g. 'W', '2', 'W/U'
        """
        safe = token.replace("/", "_")
        path = f"assets/mana/{safe}.png"

        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize((size, size), Image.LANCZOS)
            self.canvas.paste(img, (math.ceil(x), math.ceil(y)), img)
            return size
        except FileNotFoundError:
            print(f"[WARN] Missing mana symbol PNG: {path}")
            return 0

    def _paste_image(
        self,
        img: Image.Image,
        x: int,
        y: int,
        w: Optional[int] = None,
        h: Optional[int] = None
    ) -> None:
        if w and h:
            img = img.resize((w, h), Image.LANCZOS)
        self.canvas.paste(img, (int(x), int(y)), img)

    def _draw_art_cover(
        self,
        path: str,
        x: int,
        y: int,
        w: int,
        h: int
    ) -> None:
        try:
            img = Image.open(path).convert("RGBA")
        except FileNotFoundError:
            img = Image.open(Card.PLACEHOLDER_IMG_PATH).convert("RGBA")
        img_w, img_h = img.size

        scale = max(w / img_w, h / img_h)
        scaled_w = int(img_w * scale)
        scaled_h = int(img_h * scale)

        img = img.resize((scaled_w, scaled_h), Image.LANCZOS)

        offset_x = int(x + (w - scaled_w) / 2)
        offset_y = int(y + (h - scaled_h) / 2)

        self.canvas.paste(img, (offset_x, offset_y), img)

    # ------------------------------------------------------------
    # Card components
    # ------------------------------------------------------------
    def _draw_frame(self, card: Card) -> None:

        if  Color.COLORLESS in card.color:
            ordered_color_symbol = "C"
        elif len(card.color) <= 2:
            color_symbol = ""
            for color in card.color:
                color_symbol += (color.value.upper())
            
            ordered_color_symbol = self._order_colors_cycle(color_symbol)
        else:
            ordered_color_symbol = "M"

        ordered_type=""
        for type in CardType:
            if type == CardType.INSTANT or type == CardType.SORCERY:
                continue
            if type in card.type:
                ordered_type += type.value
        
        for superType in CardSuperType:
            if superType in card.supertype:
                ordered_type += superType.value

        if "Vehicle" in card.subtype:
            ordered_type += "Vehicle"

        frame_path = self.FRAME_DIR / f"{ordered_color_symbol+ordered_type}.png"
        
        frame = Image.open(frame_path).convert("RGBA")
        self._paste_image(frame, 0, 0, self.WIDTH, self.HEIGHT)

    def _draw_art(self, card: Card) -> None:
        self._draw_art_cover(card.art, self.ART_X, self.ART_Y, self.ART_W, self.ART_H)

    def _draw_name(self, card: Card) -> None:
        self._draw_text(
            self._smart_title_case(card.name),
            self.NAME_X,
            self.NAME_Y,
            self.FONT_NAME,
            self.NAME_FONT_SIZE,
        )

    def _draw_type_line(self, card: Card) -> None:
        if len(card.subtype) > 0:
            type_line = f"{CardSuperType.set_to_string(card.supertype)} {CardType.set_to_string(card.type)} — {card.subtype}"
        else:
            type_line = f"{CardSuperType.set_to_string(card.supertype)} {CardType.set_to_string(card.type)}"
        self._draw_text(
            self._smart_title_case(type_line),
            self.TYPE_X,
            self.TYPE_Y,
            self.FONT_NAME,
            self.TYPE_FONT_SIZE,
            max_width = self.TYPE_W,
        )

    def _draw_oracle_text(self, card: Card) -> None:
        self._draw_text(
            card.oracle_text,
            self.ORACLE_X,
            self.ORACLE_Y,
            self.FONT_RULES,
            self.ORACLE_FONT_SIZE,
            max_width=self.ORACLE_W,
            max_line=self.MAX_LINE_ORACLE,
            centered_y_height= self.ORACLE_H
        )

    def _draw_power_toughness(self, card: Card) -> None:
        pt = f"{card.power}/{card.toughness}"
        self._draw_text(
            pt,
            self.PT_X,
            self.PT_Y,
            self.FONT_NAME,
            self.PT_FONT_SIZE,
            centered_x = True
        )

    def _draw_mana_cost(self, card: Card) -> None:
        """Draw mana cost in the top-right corner using PNG symbols + MPlantin numbers."""
        if not card.mana_cost:
            return

        tokens = self._parse_mana_cost(card.mana_cost)

        # Starting point: right-aligned
        x = self.WIDTH - 70   # right padding
        y = self.NAME_Y

        # Draw right-to-left for easy alignment
        for token in reversed(tokens):
            # Always use the symbol to print the cost (1, 12, W, U, B, R, G, X, 2/W, W/U, etc.)
            safe_token = token.replace("/", "_")
            symbol_path = Path(f"assets/mana/{safe_token}.png")

            if not symbol_path.exists():
                print(f"[WARN] Missing mana symbol PNG: {symbol_path}")
                continue

            img = Image.open(symbol_path).convert("RGBA")

            # Resize to match your name font height
            size = self.MANA_FONT_SIZE
            img = img.resize((size, size), Image.LANCZOS)

            x -= (size+2)
            self.canvas.paste(img, (x, y), img)

    # ------------------------------------------------------------
    # Mana helpers
    # ------------------------------------------------------------

    def _parse_mana_cost(self, cost: str) -> list[str]:
        """
        Extract tokens from a mana cost string.
        Example: "{3}{W}{U}{2/W}" → ["3", "W", "U", "2/W"]
        """
        return self.MANA_PATTERN.findall(cost)
    
    def _order_colors_cycle(self, symbols: str) -> str:
        """
        Order MTG colors by minimizing the arc distance on the WUBRG cycle.
        Example: 'UG' → 'GU'
                'RWU' → 'URW'
                'BG' → 'GB'
        """

        cycle = ["W", "U", "B", "R", "G"]
        idx = {c: i for i, c in enumerate(cycle)}

        colors = set(symbols)

        best = None

        for start in colors:
            start_i = idx[start]
            ordered = [start]

            # Walk clockwise until all colors are collected
            i = (start_i + 1) % 5
            while len(ordered) < len(colors):
                c = cycle[i]
                if c in colors and c not in ordered:
                    ordered.append(c)
                i = (i + 1) % 5

            # Evaluate arc length
            arc_length = (idx[ordered[-1]] - idx[start]) % 5

            candidate = ("".join(ordered), arc_length)

            if best is None or candidate[1] < best[1] or (
                candidate[1] == best[1] and candidate[0] < best[0]
            ):
                best = candidate

        return best[0]
    