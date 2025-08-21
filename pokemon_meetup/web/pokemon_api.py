"""Pokémon Go API client for fetching Pokémon data from PoGoAPI.net."""

import asyncio
from dataclasses import dataclass
from typing import Any, Self

import httpx

from pokemon_meetup.common.pokemon_types import PokemonType


@dataclass
class EvolutionRequirement:
    """Requirements for a Pokémon evolution."""

    pokemon_id: int
    pokemon_name: str
    candy_required: int
    item_required: str | None = None
    lure_required: str | None = None
    no_candy_cost_if_traded: bool = False
    priority: int | None = None
    only_evolves_in_daytime: bool = False
    only_evolves_in_nighttime: bool = False
    must_be_buddy_to_evolve: bool = False
    buddy_distance_required: float | None = None
    gender_required: str | None = None


@dataclass
class EvolutionData:
    """Evolution data for a Pokémon."""

    pokemon_id: int
    pokemon_name: str
    form: str | None = None
    evolutions: list[EvolutionRequirement] | None = None

    def __post_init__(self) -> None:
        """Initialize evolutions list if None."""
        if self.evolutions is None:
            self.evolutions = []


@dataclass
class MegaEvolutionData:
    """Mega evolution data for a Pokémon."""

    pokemon_id: int
    pokemon_name: str
    form: str
    mega_name: str
    first_time_mega_energy_required: int
    mega_energy_required: int
    base_attack: int
    base_defense: int
    base_stamina: int
    types: list[PokemonType]
    cp_multiplier_override: float | None = None


@dataclass
class PokemonData:
    """Data structure for Pokémon Go information."""

    name: str
    id: int
    types: list[PokemonType]
    base_attack: int
    base_defense: int
    base_stamina: int
    cp_level_20: int
    cp_level_25: int
    cp_level_30: int
    cp_level_40: int
    # Additional Pokémon Go specific data
    max_cp: int
    buddy_distance: int | None = None
    candy_to_evolve: int | None = None
    is_shiny_available: bool = False
    is_released: bool = True
    rarity: str | None = None
    form: str = "Normal"
    base_stardust: int | None = None


class PoGoAPIClient:
    """Client for fetching Pokémon data from PoGoAPI.net."""

    def __init__(self) -> None:
        """Initialize the API client."""
        self.base_url: str = "https://pogoapi.net/api/v1"
        self.client: httpx.AsyncClient = httpx.AsyncClient(timeout=30.0)

        # Cache for API data to reduce requests
        self._pokemon_stats_cache: dict[int, Any] | None = None
        self._pokemon_names_cache: dict[int, Any] | None = None
        self._pokemon_types_cache: dict[int, Any] | None = None
        self._pokemon_max_cp_cache: dict[int, Any] | None = None
        self._shiny_pokemon_cache: dict[int, bool] | None = None
        self._released_pokemon_cache: dict[int, bool] | None = None
        self._buddy_distances_cache: dict[int, int] | None = None
        self._candy_to_evolve_cache: dict[int, int] | None = None
        self._pokemon_rarity_cache: dict[int, str] | None = None
        self._cp_multiplier_cache: list[Any] | None = None
        self._pokemon_evolutions_cache: dict[int, Any] | None = None
        self._mega_pokemon_cache: dict[int, list[Any]] | None = None

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object | None
    ) -> None:
        """Async context manager exit."""
        await self.client.aclose()

    async def _fetch_json(self, *, endpoint: str) -> dict[str, Any] | list[Any] | None:
        """Fetch JSON data from a PoGo API endpoint.

        Args:
            endpoint: The API endpoint to fetch from.

        Returns:
            JSON data or None if request fails.
        """
        try:
            response = await self.client.get(f"{self.base_url}/{endpoint}")
            response.raise_for_status()
            json_data: dict[str, Any] | list[Any] = response.json()
            return json_data
        except (httpx.HTTPError, ValueError) as e:
            print(f"Error fetching {endpoint}: {e}")
            return None

    async def _get_pokemon_stats(self) -> dict[int, Any]:
        """Get cached Pokemon stats data."""
        if self._pokemon_stats_cache is None:
            stats_data = await self._fetch_json(endpoint="pokemon_stats.json")
            if stats_data and isinstance(stats_data, list):
                # Convert list to dict for easier lookup by ID
                # Handle multiple forms by preferring "Normal" form
                self._pokemon_stats_cache = {}
                for pokemon in stats_data:
                    if isinstance(pokemon, dict) and "pokemon_id" in pokemon:
                        pokemon_id = pokemon["pokemon_id"]
                        # Prefer Normal form, but use any form if Normal not available
                        if pokemon_id not in self._pokemon_stats_cache or pokemon.get("form", "Normal") == "Normal":
                            self._pokemon_stats_cache[pokemon_id] = pokemon
            else:
                self._pokemon_stats_cache = {}
        return self._pokemon_stats_cache

    async def _get_pokemon_names(self) -> dict[int, Any]:
        """Get cached Pokemon names data."""
        if self._pokemon_names_cache is None:
            names_data = await self._fetch_json(endpoint="pokemon_names.json")
            if names_data and isinstance(names_data, dict):
                # Convert string keys to int keys
                self._pokemon_names_cache = {}
                for k, v in names_data.items():
                    if isinstance(k, str) and k.isdigit():
                        self._pokemon_names_cache[int(k)] = v
            else:
                self._pokemon_names_cache = {}
        return self._pokemon_names_cache

    async def _get_pokemon_types(self) -> dict[int, Any]:
        """Get cached Pokemon types data."""
        if self._pokemon_types_cache is None:
            types_data = await self._fetch_json(endpoint="pokemon_types.json")
            if types_data and isinstance(types_data, list):
                # Convert list to dict for easier lookup by ID
                self._pokemon_types_cache = {}
                for pokemon in types_data:
                    if isinstance(pokemon, dict) and "pokemon_id" in pokemon:
                        self._pokemon_types_cache[pokemon["pokemon_id"]] = pokemon
            else:
                self._pokemon_types_cache = {}
        return self._pokemon_types_cache

    async def _get_pokemon_max_cp(self) -> dict[int, Any]:
        """Get cached Pokemon max CP data."""
        if self._pokemon_max_cp_cache is None:
            max_cp_data = await self._fetch_json(endpoint="pokemon_max_cp.json")
            if max_cp_data and isinstance(max_cp_data, list):
                # Convert list to dict for easier lookup by ID
                # Handle multiple forms by preferring "Normal" form
                self._pokemon_max_cp_cache = {}
                for pokemon in max_cp_data:
                    if isinstance(pokemon, dict) and "pokemon_id" in pokemon:
                        pokemon_id = pokemon["pokemon_id"]
                        # Prefer Normal form, but use any form if Normal not available
                        if pokemon_id not in self._pokemon_max_cp_cache or pokemon.get("form", "Normal") == "Normal":
                            self._pokemon_max_cp_cache[pokemon_id] = pokemon
            else:
                self._pokemon_max_cp_cache = {}
        return self._pokemon_max_cp_cache

    async def _get_shiny_pokemon(self) -> dict[int, bool]:
        """Get cached shiny Pokemon data."""
        if self._shiny_pokemon_cache is None:
            shiny_data = await self._fetch_json(endpoint="shiny_pokemon.json")
            if shiny_data and isinstance(shiny_data, dict):
                # Convert string keys to int keys
                self._shiny_pokemon_cache = {}
                for k, v in shiny_data.items():
                    if isinstance(k, str) and k.isdigit():
                        self._shiny_pokemon_cache[int(k)] = bool(v)
            else:
                self._shiny_pokemon_cache = {}
        return self._shiny_pokemon_cache

    async def _get_released_pokemon(self) -> dict[int, bool]:
        """Get cached released Pokemon data."""
        if self._released_pokemon_cache is None:
            released_data = await self._fetch_json(endpoint="released_pokemon.json")
            if released_data and isinstance(released_data, dict):
                # Convert string keys to int keys
                self._released_pokemon_cache = {}
                for k, v in released_data.items():
                    if isinstance(k, str) and k.isdigit():
                        self._released_pokemon_cache[int(k)] = bool(v)
            else:
                self._released_pokemon_cache = {}
        return self._released_pokemon_cache

    async def _get_buddy_distances(self) -> dict[int, int]:
        """Get cached buddy distances data."""
        if self._buddy_distances_cache is None:
            buddy_data = await self._fetch_json(endpoint="pokemon_buddy_distances.json")
            if buddy_data and isinstance(buddy_data, dict):
                # Flatten the structure for easier lookup
                self._buddy_distances_cache = {}
                for distance, pokemon_list in buddy_data.items():
                    if isinstance(pokemon_list, list):
                        for pokemon in pokemon_list:
                            if isinstance(pokemon, dict) and "pokemon_id" in pokemon:
                                self._buddy_distances_cache[pokemon["pokemon_id"]] = int(distance)
            else:
                self._buddy_distances_cache = {}
        return self._buddy_distances_cache

    async def _get_candy_to_evolve(self) -> dict[int, int]:
        """Get cached candy to evolve data."""
        if self._candy_to_evolve_cache is None:
            candy_data = await self._fetch_json(endpoint="pokemon_candy_to_evolve.json")
            if candy_data and isinstance(candy_data, dict):
                # Flatten the structure for easier lookup
                self._candy_to_evolve_cache = {}
                for candy_amount, pokemon_list in candy_data.items():
                    if isinstance(pokemon_list, list):
                        for pokemon in pokemon_list:
                            if isinstance(pokemon, dict) and "pokemon_id" in pokemon:
                                self._candy_to_evolve_cache[pokemon["pokemon_id"]] = int(candy_amount)
            else:
                self._candy_to_evolve_cache = {}
        return self._candy_to_evolve_cache

    async def _get_pokemon_rarity(self) -> dict[int, str]:
        """Get cached Pokemon rarity data."""
        if self._pokemon_rarity_cache is None:
            rarity_data = await self._fetch_json(endpoint="pokemon_rarity.json")
            if rarity_data and isinstance(rarity_data, dict):
                # Flatten the structure for easier lookup
                self._pokemon_rarity_cache = {}
                for rarity, pokemon_list in rarity_data.items():
                    if isinstance(pokemon_list, list):
                        for pokemon in pokemon_list:
                            if isinstance(pokemon, dict) and "pokemon_id" in pokemon:
                                self._pokemon_rarity_cache[pokemon["pokemon_id"]] = rarity
            else:
                self._pokemon_rarity_cache = {}
        return self._pokemon_rarity_cache

    async def _get_cp_multiplier(self) -> list[Any]:
        """Get cached CP multiplier data."""
        if self._cp_multiplier_cache is None:
            cp_data = await self._fetch_json(endpoint="cp_multiplier.json")
            if cp_data and isinstance(cp_data, list):
                self._cp_multiplier_cache = cp_data
            else:
                self._cp_multiplier_cache = []
        return self._cp_multiplier_cache

    async def _get_pokemon_evolutions(self) -> dict[int, Any]:
        """Get cached Pokemon evolution data."""
        if self._pokemon_evolutions_cache is None:
            evolution_data = await self._fetch_json(endpoint="pokemon_evolutions.json")
            if evolution_data and isinstance(evolution_data, list):
                # Convert list to dict for easier lookup by ID
                self._pokemon_evolutions_cache = {}
                for evolution in evolution_data:
                    if isinstance(evolution, dict) and "pokemon_id" in evolution:
                        pokemon_id = evolution["pokemon_id"]
                        self._pokemon_evolutions_cache[pokemon_id] = evolution
            else:
                self._pokemon_evolutions_cache = {}
        return self._pokemon_evolutions_cache

    async def _get_mega_pokemon(self) -> dict[int, list[Any]]:
        """Get cached mega Pokemon data."""
        if self._mega_pokemon_cache is None:
            mega_data = await self._fetch_json(endpoint="mega_pokemon.json")
            if mega_data and isinstance(mega_data, list):
                # Convert list to dict for easier lookup by ID
                self._mega_pokemon_cache = {}
                for mega in mega_data:
                    if isinstance(mega, dict) and "pokemon_id" in mega:
                        pokemon_id = mega["pokemon_id"]
                        # Handle multiple mega forms
                        if pokemon_id not in self._mega_pokemon_cache:
                            self._mega_pokemon_cache[pokemon_id] = []
                        self._mega_pokemon_cache[pokemon_id].append(mega)
            else:
                self._mega_pokemon_cache = {}
        return self._mega_pokemon_cache

    def _calculate_cp_for_level(
        self, *, base_attack: int, base_defense: int, base_stamina: int, level: float, cp_multipliers: list[Any]
    ) -> int:
        """Calculate CP for a specific level using PoGo formula.

        Args:
            base_attack: Base attack stat.
            base_defense: Base defense stat.
            base_stamina: Base stamina stat.
            level: Pokemon level.
            cp_multipliers: List of CP multipliers from API.

        Returns:
            Calculated CP value.
        """
        # Find the multiplier for the given level
        multiplier = 0.5  # Default fallback

        for cp_data in cp_multipliers:
            if cp_data["level"] == level:
                multiplier = cp_data["multiplier"]
                break

        # Use perfect IVs (15/15/15) for max CP calculation
        attack = (base_attack + 15) * multiplier
        defense = (base_defense + 15) * multiplier
        stamina = (base_stamina + 15) * multiplier

        # PoGo CP formula
        cp = int((attack * (defense**0.5) * (stamina**0.5)) / 10)
        return max(cp, 10)  # Minimum CP is 10

    async def get_pokemon_data(self, *, name: str) -> PokemonData | None:
        """Fetch Pokémon data by name.

        Args:
            name: The Pokémon name to search for.

        Returns:
            PokemonData object if found, None otherwise.
        """
        try:
            # Get all cached data
            pokemon_stats = await self._get_pokemon_stats()
            pokemon_names = await self._get_pokemon_names()
            pokemon_types = await self._get_pokemon_types()
            pokemon_max_cp = await self._get_pokemon_max_cp()
            shiny_pokemon = await self._get_shiny_pokemon()
            released_pokemon = await self._get_released_pokemon()
            buddy_distances = await self._get_buddy_distances()
            candy_to_evolve = await self._get_candy_to_evolve()
            pokemon_rarity = await self._get_pokemon_rarity()
            cp_multipliers = await self._get_cp_multiplier()

            # Find Pokemon by name (case-insensitive)
            pokemon_id = None
            pokemon_name = None

            for pid, pdata in pokemon_names.items():
                if pdata["name"].lower() == name.lower():
                    pokemon_id = pid
                    pokemon_name = pdata["name"]
                    break

            if pokemon_id is None:
                return None

            # At this point, pokemon_name should also be set
            if pokemon_name is None:
                print(f"Error: pokemon_name is None for pokemon_id {pokemon_id}")
                return None

            # Get stats
            stats = pokemon_stats.get(pokemon_id)
            if not stats:
                return None

            # Get types
            types_data = pokemon_types.get(pokemon_id)
            types = []
            if types_data:
                for type_name in types_data["type"]:
                    try:
                        # Convert PoGo type names to our enum format
                        type_name_lower = type_name.lower()
                        pokemon_type = PokemonType(type_name_lower)
                        types.append(pokemon_type)
                    except ValueError:
                        # Skip unknown types
                        continue

            # Get base stats
            base_attack = int(stats["base_attack"])
            base_defense = int(stats["base_defense"])
            base_stamina = int(stats["base_stamina"])

            # Calculate CP values for different levels
            cp_level_20 = self._calculate_cp_for_level(
                base_attack=base_attack,
                base_defense=base_defense,
                base_stamina=base_stamina,
                level=20.0,
                cp_multipliers=cp_multipliers,
            )
            cp_level_25 = self._calculate_cp_for_level(
                base_attack=base_attack,
                base_defense=base_defense,
                base_stamina=base_stamina,
                level=25.0,
                cp_multipliers=cp_multipliers,
            )
            cp_level_30 = self._calculate_cp_for_level(
                base_attack=base_attack,
                base_defense=base_defense,
                base_stamina=base_stamina,
                level=30.0,
                cp_multipliers=cp_multipliers,
            )
            cp_level_40 = self._calculate_cp_for_level(
                base_attack=base_attack,
                base_defense=base_defense,
                base_stamina=base_stamina,
                level=40.0,
                cp_multipliers=cp_multipliers,
            )

            # Get max CP (level 40 perfect)
            max_cp_data = pokemon_max_cp.get(pokemon_id, {})
            max_cp = max_cp_data.get("max_cp", cp_level_40)

            # Get additional data
            is_shiny_available = pokemon_id in shiny_pokemon
            is_released = pokemon_id in released_pokemon
            buddy_distance = buddy_distances.get(pokemon_id)
            candy_required = candy_to_evolve.get(pokemon_id)
            rarity = pokemon_rarity.get(pokemon_id, "Standard")

            return PokemonData(
                name=pokemon_name,
                id=pokemon_id,
                types=types,
                base_attack=base_attack,
                base_defense=base_defense,
                base_stamina=base_stamina,
                cp_level_20=cp_level_20,
                cp_level_25=cp_level_25,
                cp_level_30=cp_level_30,
                cp_level_40=cp_level_40,
                max_cp=max_cp,
                buddy_distance=buddy_distance,
                candy_to_evolve=candy_required,
                is_shiny_available=is_shiny_available,
                is_released=is_released,
                rarity=rarity,
                form="Normal",
                base_stardust=None,
            )

        except Exception as e:
            print(f"Error fetching data for {name}: {e}")
            return None

    async def search_pokemon_by_partial_name(self, *, partial_name: str, limit: int = 5) -> list[str]:
        """Search for Pokémon names that match a partial name.

        Args:
            partial_name: Partial Pokémon name to search for.
            limit: Maximum number of results to return.

        Returns:
            List of matching Pokémon names.
        """
        try:
            pokemon_names = await self._get_pokemon_names()

            # Filter by partial name match
            matches = []
            partial_lower = partial_name.lower()

            for pokemon_data in pokemon_names.values():
                if partial_lower in pokemon_data["name"].lower():
                    matches.append(pokemon_data["name"])
                    if len(matches) >= limit:
                        break

            return sorted(matches)

        except Exception as e:
            print(f"Error searching for Pokémon: {e}")
            return []

    async def get_evolution_data(self, *, pokemon_id: int) -> EvolutionData | None:
        """Get evolution data for a specific Pokémon.

        Args:
            pokemon_id: The Pokémon ID to get evolution data for.

        Returns:
            EvolutionData object if found, None otherwise.
        """
        try:
            evolutions_data = await self._get_pokemon_evolutions()
            evolution_info = evolutions_data.get(pokemon_id)

            if not evolution_info:
                return None

            # Parse evolution requirements
            evolution_requirements = []
            for evo in evolution_info.get("evolutions", []):
                requirement = EvolutionRequirement(
                    pokemon_id=evo["pokemon_id"],
                    pokemon_name=evo["pokemon_name"],
                    candy_required=evo.get("candy_required", 0),
                    item_required=evo.get("item_required"),
                    lure_required=evo.get("lure_required"),
                    no_candy_cost_if_traded=evo.get("no_candy_cost_if_traded", False),
                    priority=evo.get("priority"),
                    only_evolves_in_daytime=evo.get("only_evolves_in_daytime", False),
                    only_evolves_in_nighttime=evo.get("only_evolves_in_nighttime", False),
                    must_be_buddy_to_evolve=evo.get("must_be_buddy_to_evolve", False),
                    buddy_distance_required=evo.get("buddy_distance_required"),
                    gender_required=evo.get("gender_required"),
                )
                evolution_requirements.append(requirement)

            return EvolutionData(
                pokemon_id=evolution_info["pokemon_id"],
                pokemon_name=evolution_info["pokemon_name"],
                form=evolution_info.get("form"),
                evolutions=evolution_requirements,
            )

        except Exception as e:
            print(f"Error fetching evolution data for ID {pokemon_id}: {e}")
            return None

    async def get_mega_evolution_data(self, *, pokemon_id: int) -> list[MegaEvolutionData]:
        """Get mega evolution data for a specific Pokémon.

        Args:
            pokemon_id: The Pokémon ID to get mega evolution data for.

        Returns:
            List of MegaEvolutionData objects (can have multiple forms).
        """
        try:
            mega_data = await self._get_mega_pokemon()
            mega_forms = mega_data.get(pokemon_id, [])

            result = []
            for mega in mega_forms:
                # Parse types
                types = []
                for type_name in mega.get("type", []):
                    try:
                        type_name_lower = type_name.lower()
                        pokemon_type = PokemonType(type_name_lower)
                        types.append(pokemon_type)
                    except ValueError:
                        continue

                mega_evolution = MegaEvolutionData(
                    pokemon_id=mega["pokemon_id"],
                    pokemon_name=mega["pokemon_name"],
                    form=mega["form"],
                    mega_name=mega["mega_name"],
                    first_time_mega_energy_required=mega["first_time_mega_energy_required"],
                    mega_energy_required=mega["mega_energy_required"],
                    base_attack=mega["stats"]["base_attack"],
                    base_defense=mega["stats"]["base_defense"],
                    base_stamina=mega["stats"]["base_stamina"],
                    types=types,
                    cp_multiplier_override=mega.get("cp_multiplier_override"),
                )
                result.append(mega_evolution)

            return result

        except Exception as e:
            print(f"Error fetching mega evolution data for ID {pokemon_id}: {e}")
            return []

    async def check_evolution_line_has_mega(self, *, pokemon_id: int) -> bool:
        """Check if a Pokémon's evolution line includes any mega evolutions.

        Args:
            pokemon_id: The Pokémon ID to check.

        Returns:
            True if any Pokémon in the evolution line can mega evolve.
        """
        try:
            # Check if this Pokémon can mega evolve
            mega_data = await self.get_mega_evolution_data(pokemon_id=pokemon_id)
            if mega_data:
                return True

            # Check if any of its evolutions can mega evolve
            evolution_data = await self.get_evolution_data(pokemon_id=pokemon_id)
            if evolution_data and evolution_data.evolutions:
                for evolution in evolution_data.evolutions:
                    evolution_mega_data = await self.get_mega_evolution_data(pokemon_id=evolution.pokemon_id)
                    if evolution_mega_data:
                        return True

            return False

        except Exception as e:
            print(f"Error checking mega evolution line for ID {pokemon_id}: {e}")
            return False


# Synchronous wrapper functions for easier use
def get_pokemon_data_sync(*, name: str) -> PokemonData | None:
    """Synchronous wrapper for getting Pokémon data.

    Args:
        name: The Pokémon name to search for.

    Returns:
        PokemonData object if found, None otherwise.
    """

    async def _fetch() -> PokemonData | None:
        async with PoGoAPIClient() as client:
            return await client.get_pokemon_data(name=name)

    return asyncio.run(_fetch())


def search_pokemon_sync(*, partial_name: str, limit: int = 5) -> list[str]:
    """Synchronous wrapper for searching Pokémon.

    Args:
        partial_name: Partial Pokémon name to search for.
        limit: Maximum number of results to return.

    Returns:
        List of matching Pokémon names.
    """

    async def _search() -> list[str]:
        async with PoGoAPIClient() as client:
            return await client.search_pokemon_by_partial_name(partial_name=partial_name, limit=limit)

    return asyncio.run(_search())
