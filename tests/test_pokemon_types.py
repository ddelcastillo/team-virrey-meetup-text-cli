"""Tests for Pokémon types module."""

from pokemon_meetup.common.pokemon_types import PokemonType, get_type_emoji, get_type_spanish_name


class TestPokemonTypes:
    """Test cases for Pokémon types functionality."""

    def test_pokemon_type_enum_values(self) -> None:
        """Test that PokemonType enum has expected values."""
        assert PokemonType.FIRE.value == "fire"
        assert PokemonType.WATER.value == "water"
        assert PokemonType.GRASS.value == "grass"

    def test_get_type_spanish_name(self) -> None:
        """Test Spanish name retrieval for Pokémon types."""
        assert get_type_spanish_name(pokemon_type=PokemonType.FIRE) == "Fuego"
        assert get_type_spanish_name(pokemon_type=PokemonType.WATER) == "Agua"
        assert get_type_spanish_name(pokemon_type=PokemonType.ELECTRIC) == "Eléctrico"
        assert get_type_spanish_name(pokemon_type=PokemonType.PSYCHIC) == "Psíquico"

    def test_get_type_emoji(self) -> None:
        """Test emoji retrieval for Pokémon types."""
        assert get_type_emoji(pokemon_type=PokemonType.FIRE) == "🔥"
        assert get_type_emoji(pokemon_type=PokemonType.WATER) == "💧"
        assert get_type_emoji(pokemon_type=PokemonType.ELECTRIC) == "⚡️"
        assert get_type_emoji(pokemon_type=PokemonType.GHOST) == "👻"

    def test_all_types_have_spanish_names(self) -> None:
        """Test that all Pokémon types have Spanish names defined."""
        for pokemon_type in PokemonType:
            spanish_name = get_type_spanish_name(pokemon_type=pokemon_type)
            assert isinstance(spanish_name, str)
            assert len(spanish_name) > 0

    def test_all_types_have_emojis(self) -> None:
        """Test that all Pokémon types have emojis defined."""
        for pokemon_type in PokemonType:
            emoji = get_type_emoji(pokemon_type=pokemon_type)
            assert isinstance(emoji, str)
            assert len(emoji) > 0
