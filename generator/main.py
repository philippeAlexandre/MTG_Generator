import os

deps = os.path.join(os.path.dirname(__file__), "dependencies")
os.environ["PATH"] = deps + os.pathsep + os.environ["PATH"]

from persistence import CardDataLoader
from render import CardRenderer



def main():
    loader = CardDataLoader()
    renderer = CardRenderer()
    cards = loader.load("data/cards.csv")

    for card in cards:
        renderer.render_card(card)

if __name__ == "__main__":
    main()