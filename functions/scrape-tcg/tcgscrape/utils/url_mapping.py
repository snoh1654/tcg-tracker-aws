class URL_Mapping:

    POKEMON = "Pokemon"
    YUGIOH = "Yu-Gi-Oh!"
    MAGIC = "Magic: The Gathering"
    WEISS_SCHWARZ = "Weiss Schwarz"
    ONE_PIECE = "One Piece Card Game"
    TCG_NAMES = [POKEMON, YUGIOH, MAGIC, WEISS_SCHWARZ, ONE_PIECE]

    def __init__(self, url_mapping: list[tuple[str, str, str]]):

        self.url_mapping = {}

        for tcg_name, set_name, url in url_mapping:
            if tcg_name not in self.TCG_NAMES:
                raise ValueError(f"Invalid TCG name: {tcg_name}")
            
            if (tcg_name, set_name) in self.url_mapping:
                raise ValueError(f"Duplicate TCG set: {(tcg_name, set_name)}")
            
            self.url_mapping[(tcg_name, set_name)] = url

    def get_url(self, tcg_name: str, set_name: str):
        return self.url_mapping[(tcg_name, set_name)]
        
    def get_tcg_sets(self):
        return list(self.url_mapping.keys())

    def get_urls(self):
        return list(self.url_mapping.values())
