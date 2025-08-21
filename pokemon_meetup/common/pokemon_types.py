"""Pokémon type definitions with Spanish names and emojis."""

from enum import Enum


class PokemonType(Enum):
    """Pokémon types enum."""

    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    FAIRY = "fairy"


# Spanish names mapping
_SPANISH_NAMES: dict[PokemonType, str] = {
    PokemonType.NORMAL: "Normal",
    PokemonType.FIRE: "Fuego",
    PokemonType.WATER: "Agua",
    PokemonType.ELECTRIC: "Eléctrico",
    PokemonType.GRASS: "Planta",
    PokemonType.ICE: "Hielo",
    PokemonType.FIGHTING: "Lucha",
    PokemonType.POISON: "Veneno",
    PokemonType.GROUND: "Tierra",
    PokemonType.FLYING: "Volador",
    PokemonType.PSYCHIC: "Psíquico",
    PokemonType.BUG: "Bicho",
    PokemonType.ROCK: "Roca",
    PokemonType.GHOST: "Fantasma",
    PokemonType.DRAGON: "Dragón",
    PokemonType.DARK: "Siniestro",
    PokemonType.STEEL: "Acero",
    PokemonType.FAIRY: "Hada",
}

# Emoji mapping
_TYPE_EMOJIS: dict[PokemonType, str] = {
    PokemonType.NORMAL: "⚪",
    PokemonType.FIRE: "🔥",
    PokemonType.WATER: "💧",
    PokemonType.ELECTRIC: "⚡️",
    PokemonType.GRASS: "🌿",
    PokemonType.ICE: "❄️",
    PokemonType.FIGHTING: "🥊",
    PokemonType.POISON: "☠️",
    PokemonType.GROUND: "🌋",
    PokemonType.FLYING: "🪽",
    PokemonType.PSYCHIC: "🔮",
    PokemonType.BUG: "🐛",
    PokemonType.ROCK: "🪨",
    PokemonType.GHOST: "👻",
    PokemonType.DRAGON: "🐉",
    PokemonType.DARK: "🌑",
    PokemonType.STEEL: "⚙️",
    PokemonType.FAIRY: "🧚",
}


def get_type_spanish_name(*, pokemon_type: PokemonType) -> str:
    """Get the Spanish name for a Pokémon type.

    Args:
        pokemon_type: The Pokémon type enum value.

    Returns:
        The Spanish name of the type.
    """
    return _SPANISH_NAMES[pokemon_type]


def get_type_emoji(*, pokemon_type: PokemonType) -> str:
    """Get the emoji for a Pokémon type.

    Args:
        pokemon_type: The Pokémon type enum value.

    Returns:
        The emoji representing the type.
    """
    return _TYPE_EMOJIS[pokemon_type]
