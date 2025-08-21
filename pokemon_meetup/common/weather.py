"""Weather conditions and type boost mappings."""

from enum import Enum
from types import MappingProxyType

from .pokemon_types import PokemonType


class Weather(Enum):
    """Weather conditions in Pokémon Go."""

    CLEAR = "clear"
    SUNNY = "sunny"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    WINDY = "windy"


# Weather emoji mapping
_WEATHER_EMOJIS: dict[Weather, str] = {
    Weather.CLEAR: "🌙",
    Weather.SUNNY: "☀️",
    Weather.PARTLY_CLOUDY: "⛅",
    Weather.CLOUDY: "☁️",
    Weather.RAIN: "🌧️",
    Weather.SNOW: "❄️",
    Weather.FOG: "🌫️",
    Weather.WINDY: "🪁",
}


def get_weather_emoji(*, weather: Weather) -> str:
    """Get the emoji for a weather condition.

    Args:
        weather: The weather condition.

    Returns:
        The emoji representing the weather.
    """
    return _WEATHER_EMOJIS[weather]


class WeatherBoosts:
    """Weather boost mappings for Pokémon types."""

    # Mapping of weather conditions to boosted types
    _WEATHER_BOOSTS = MappingProxyType(
        {
            Weather.CLEAR: {PokemonType.FIRE, PokemonType.GRASS, PokemonType.GROUND},
            Weather.SUNNY: {PokemonType.FIRE, PokemonType.GRASS, PokemonType.GROUND},
            Weather.PARTLY_CLOUDY: {PokemonType.NORMAL, PokemonType.ROCK},
            Weather.CLOUDY: {PokemonType.FIGHTING, PokemonType.POISON, PokemonType.FAIRY},
            Weather.RAIN: {PokemonType.WATER, PokemonType.ELECTRIC, PokemonType.BUG},
            Weather.SNOW: {PokemonType.ICE, PokemonType.STEEL},
            Weather.FOG: {PokemonType.DARK, PokemonType.GHOST},
            Weather.WINDY: {PokemonType.FLYING, PokemonType.DRAGON, PokemonType.PSYCHIC},
        }
    )

    @classmethod
    def get_boosted_types(cls, *, weather: Weather) -> set[PokemonType]:
        """Get the Pokémon types boosted by a specific weather condition.

        Args:
            weather: The weather condition.

        Returns:
            Set of Pokémon types that are boosted by the weather.
        """
        return cls._WEATHER_BOOSTS.get(weather, set())

    @classmethod
    def is_type_boosted(cls, *, pokemon_type: PokemonType, weather: Weather) -> bool:
        """Check if a Pokémon type is boosted by a specific weather condition.

        Args:
            pokemon_type: The Pokémon type to check.
            weather: The weather condition.

        Returns:
            True if the type is boosted by the weather, False otherwise.
        """
        return pokemon_type in cls.get_boosted_types(weather=weather)

    @classmethod
    def get_weather_for_type(cls, *, pokemon_type: PokemonType) -> set[Weather]:
        """Get all weather conditions that boost a specific Pokémon type.

        Args:
            pokemon_type: The Pokémon type.

        Returns:
            Set of weather conditions that boost the type.
        """
        boosting_weathers = set()
        for weather, boosted_types in cls._WEATHER_BOOSTS.items():
            if pokemon_type in boosted_types:
                boosting_weathers.add(weather)
        return boosting_weathers

    @classmethod
    def get_weather_emojis_for_types(cls, *, pokemon_types: list[PokemonType]) -> str:
        """Get weather emojis for Pokémon types that boost them.

        Excludes clear weather since events are during daytime (up to 6 PM).

        Args:
            pokemon_types: List of Pokémon types.

        Returns:
            String of weather emojis that boost any of the given types.
        """
        boosting_weathers = set()
        for pokemon_type in pokemon_types:
            boosting_weathers.update(cls.get_weather_for_type(pokemon_type=pokemon_type))

        # Remove clear weather since events are during daytime
        boosting_weathers.discard(Weather.CLEAR)

        if not boosting_weathers:
            return ""

        # Sort weathers for consistent output and get unique emojis
        sorted_weathers = sorted(boosting_weathers, key=lambda w: w.value)
        emojis = []
        for weather in sorted_weathers:
            emoji = get_weather_emoji(weather=weather)
            if emoji not in emojis:  # Avoid duplicates
                emojis.append(emoji)

        return "".join(emojis)
