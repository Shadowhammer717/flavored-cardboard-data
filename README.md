# Flavored Cardboard card data

Free card lists and prices for the games in [Flavored Cardboard](https://github.com/Shadowhammer717/Flavored-Cardboard) that have no free database of their own: One Piece, Flesh and Blood, Digimon, Dragon Ball Super Fusion World, Star Wars: Unlimited, Cardfight!! Vanguard, Weiss Schwarz and Union Arena.

Every night a GitHub Action runs `build.py`, which reads [TCGCSV](https://tcgcsv.com) (a free daily copy of TCGplayer's catalog and prices) and writes one small file per game to the `data` branch:

https://raw.githubusercontent.com/Shadowhammer717/flavored-cardboard-data/data/cards/onepiece.json

The app downloads a game's file the first time you search that game and refreshes it once a day.

Run it yourself with `python build.py` (or `python build.py unionarena` for one game). Card names, images and prices belong to their publishers and TCGplayer; thanks to TCGCSV for the free data.
