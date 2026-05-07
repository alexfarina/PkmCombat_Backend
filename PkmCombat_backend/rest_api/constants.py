NATURES={
    #step up the attack
    "adamant":{"up_att": 1.1,"low_att_esp": 0.9},
    "lonely":{"up_att":1.1,"low_def":0.9},
    "naughty":{"up_att":1.1, "low_def_esp":0.9},
    "brave":{"up_att": 1.1, "low_speed":0.9},
    #step up the defense
    "impish":{"up_def":1.1, "low_att_esp":0.9},
    "bold":{"up_def": 1.1, "low_att":0.9},
    "lax:":{"up_def":1.1,"low_def_esp":0.9},
    "relaxed":{"up_def":1.1, "low_speed":0.9},
    #step up the att_special
    "modest":{"up_att_esp": 1.1, "low_att":0.9},
    "mild":{"up_att_esp":1.1, "low_def":0.9},
    "rash":{"up_att_esp":1.1, "low_def_esp":0.9},
    "quiet":{"up_att_esp":1.1, "low_speed":0.9},
    #step up the def_esp
    "careful":{"up_def_esp":1.1, "low_att_esp":0.9},
    "calm": {"up_def_esp":1.1, "low_att":0.9},
    "gentle": {"up_def_esp":1.1, "low_def":0.9},
    "sassy":{"up_def_esp":1.1, "low_speed":0.9},
    #step up the speed
    "jolly":{"up_speed":1.1, "low_att_esp": 0.9},
    "timid":{"up_speed":1.1, "low_att":0.9},
    "hasty":{"up_speed":1.1, "low_def":0.9},
    "naive":{"up_speed":1.1, "low_def_esp":0.9},
    #neutral natures
    "hardy":   {"up_att": 1.0, "low_att": 1.0},
    "docile":  {"up_def": 1.0, "low_def": 1.0},
    "bashful": {"up_att_esp": 1.0, "low_att_esp": 1.0},
    "quirky":  {"up_def_esp": 1.0, "low_def_esp": 1.0},
    "serious": {"up_speed": 1.0, "low_speed": 1.0}
}

POKEDEX_LIST = [
    "bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard",
    "squirtle", "wartortle", "blastoise", "caterpie", "metapod", "butterfree",
    "weedle", "kakuna", "beedrill", "pidgey", "pidgeotto", "pidgeot", "rattata",
    "raticate", "spearow", "fearow", "ekans", "arbok", "pikachu", "raichu",
    "sandshrew", "sandslash", "nidoran-f", "nidorina", "nidoqueen", "nidoran-m",
    "nidorino", "nidoking", "clefairy", "clefable", "vulpix", "ninetales",
    "jigglypuff", "wigglytuff", "zubat", "golbat", "oddish", "gloom", "vileplume",
    "paras", "parasect", "venonat", "venomoth", "diglett", "dugtrio", "meowth",
    "persian", "psyduck", "golduck", "mankey", "primeape", "growlithe", "arcanine",
    "poliwag", "poliwhirl", "poliwrath", "abra", "kadabra", "alakazam", "machop",
    "machoke", "machamp", "bellsprout", "weepinbell", "victreebel", "tentacool",
    "tentacruel", "geodude", "graveler", "golem", "ponyta", "rapidash", "slowpoke",
    "slowbro", "magnemite", "magneton", "farfetchd", "doduo", "dodrio", "seel",
    "dewgong", "grimer", "muk", "shellder", "cloyster", "gastly", "haunter",
    "gengar", "onix", "drowzee", "hypno", "krabby", "kingler", "voltorb",
    "electrode", "exeggcute", "exeggutor", "cubone", "marowak", "hitmonlee",
    "hitmonchan", "lickitung", "koffing", "weezing", "rhyhorn", "rhydon", "chansey",
    "tangela", "kangaskhan", "horsea", "seadra", "goldeen", "seaking", "staryu",
    "starmie", "mr-mime", "scyther", "jynx", "electabuzz", "magmar", "pinsir",
    "tauros", "magikarp", "gyarados", "lapras", "ditto", "eevee", "vaporeon",
    "jolteon", "flareon", "porygon", "omanyte", "omastar", "kabuto", "kabutops",
    "aerodactyl", "snorlax", "articuno", "zapdos", "moltres", "dratini",
    "dragonair", "dragonite", "mewtwo", "mew"
]

PRIORITY_MOVES = ["quick-attack", "extreme-speed", "aqua-jet", "ice-shard"]

TYPE_CHART = {
    "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 2.0, "bug": 2.0, "rock": 0.5, "dragon": 0.5, "steel": 2.0},
    "water": {"fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0, "rock": 2.0, "dragon": 0.5},
    "grass": {"fire": 0.5, "water": 2.0, "grass": 0.5, "poison": 0.5, "ground": 2.0, "flying": 0.5, "bug": 0.5, "rock": 2.0, "dragon": 0.5, "steel": 0.5},
    "electric": {"water": 2.0, "grass": 0.5, "electric": 0.5, "ground": 0, "flying": 2.0, "dragon": 0.5},
    "ice": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 0.5, "ground": 2.0, "flying": 2.0, "dragon": 2.0, "steel": 0.5},
    "fighting": {"normal": 2.0, "ice": 2.0, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2.0, "ghost": 0, "dark": 2.0, "steel": 2.0, "fairy": 0.5},
    "poison": {"grass": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "fairy": 2.0},
    "ground": {"fire": 2.0, "electric": 2.0, "grass": 0.5, "poison": 2.0, "flying": 0, "bug": 0.5, "rock": 2.0, "steel": 2.0},
    "flying": {"electric": 0.5, "grass": 2.0, "fighting": 2.0, "bug": 2.0, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "dark": 0, "steel": 0.5},
    "bug": {"fire": 0.5, "grass": 2.0, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2.0, "ghost": 0.5, "dark": 2.0, "steel": 0.5, "fairy": 0.5},
    "rock": {"fire": 2.0, "ice": 2.0, "fighting": 0.5, "ground": 0.5, "flying": 2.0, "bug": 2.0, "steel": 0.5},
    "ghost": {"normal": 0, "psychic": 2.0, "ghost": 2.0, "dark": 0.5},
    "dragon": {"dragon": 2.0, "steel": 0.5, "fairy": 0},
    "dark": {"fighting": 0.5, "psychic": 2.0, "ghost": 2.0, "dark": 0.5, "fairy": 0.5},
    "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2.0, "rock": 2.0, "steel": 0.5, "fairy": 2.0},
    "fairy": {"fire": 0.5, "fighting": 2.0, "poison": 0.5, "dragon": 2.0, "dark": 2.0, "steel": 0.5}
}