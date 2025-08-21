"""Pokémon service layer for managing data fetching and storage.

This service provides a high-level interface for working with Pokémon data,
integrating the database storage with the API client. It handles:
- Checking if Pokémon data exists in the database
- Fetching fresh data from the API when needed
- Storing/updating data in the database
- Providing user prompts for data management decisions
"""

from typing import Literal

from pokemon_meetup.database.models import PokemonDatabase, get_default_database
from pokemon_meetup.web.pokemon_api import (
    EvolutionData,
    MegaEvolutionData,
    PoGoAPIClient,
    PokemonData,
    search_pokemon_sync,
)


class PokemonService:
    """Service for managing Pokémon data with database integration."""

    def __init__(self, *, database: PokemonDatabase | None = None) -> None:
        """Initialize the service.

        Args:
            database: Database instance to use. If None, uses default database.
        """
        self.database = database or get_default_database()

    async def get_pokemon_data(
        self, *, name: str, force_refresh: bool = False, interactive: bool = True
    ) -> PokemonData | None:
        """Get Pokémon data, checking database first and optionally prompting user.

        Args:
            name: Pokémon name to fetch.
            force_refresh: If True, always fetch from API regardless of database.
            interactive: If True, prompt user when data exists in database.

        Returns:
            PokemonData object if found, None otherwise.
        """
        # First, try to get data from database
        existing_data = self.database.get_pokemon_by_name(name=name)

        if existing_data and not force_refresh:
            if interactive:
                print(f"✅ Found {existing_data.name} in database")
                print(f"   Last updated: {self._get_last_updated_display(existing_data)}")

                choice = input("Use existing data or fetch fresh data? (existing/fresh) (1/2): ").strip().lower()

                if choice in ["existing", "e", "use", "yes", "y", "1"]:
                    print("📖 Using existing data from database")
                    return existing_data
                elif choice in ["fresh", "f", "fetch", "new", "n", "2"]:
                    print("🔄 Fetching fresh data from API...")
                else:
                    print("❌ Invalid choice. Using existing data.")
                    return existing_data
            else:
                # Non-interactive mode: use existing data
                return existing_data

        # Fetch fresh data from API (either no existing data or user chose fresh)
        if not existing_data:
            print(f"🔍 {name} not found in database, fetching from API...")

        async with PoGoAPIClient() as client:
            fresh_data = await client.get_pokemon_data(name=name)

            if fresh_data:
                # Store/update in database
                self.database.upsert_pokemon(pokemon_data=fresh_data)

                if existing_data:
                    print(f"✅ Updated {fresh_data.name} data in database")
                else:
                    print(f"✅ Added {fresh_data.name} to database")

                return fresh_data
            else:
                print(f"❌ Could not fetch data for {name} from API")
                return existing_data  # Return existing data if API fails

    async def search_pokemon(
        self, *, partial_name: str, limit: int = 5, source: Literal["database", "api", "both"] = "both"
    ) -> list[str]:
        """Search for Pokémon names.

        Args:
            partial_name: Partial name to search for.
            limit: Maximum number of results.
            source: Where to search - database, API, or both.

        Returns:
            List of matching Pokémon names.
        """
        results = []

        if source in ["database", "both"]:
            # Search in database first
            db_results = self.database.search_pokemon_by_name(partial_name=partial_name, limit=limit)
            results.extend([pokemon.name for pokemon in db_results])

        if source in ["api", "both"] and len(results) < limit:
            # Search via API if we need more results
            remaining_limit = limit - len(results)
            api_results = search_pokemon_sync(partial_name=partial_name, limit=remaining_limit)

            # Add API results that aren't already in our list
            for name in api_results:
                if name not in results:
                    results.append(name)
                    if len(results) >= limit:
                        break

        return results[:limit]

    def get_database_stats(self) -> dict[str, object]:
        """Get database statistics.

        Returns:
            Dictionary with database statistics.
        """
        return self.database.get_database_stats()

    def list_cached_pokemon(self, *, limit: int | None = None) -> list[PokemonData]:
        """List Pokémon stored in the database.

        Args:
            limit: Optional limit on number of results.

        Returns:
            List of PokemonData objects from database.
        """
        return self.database.get_all_pokemon(limit=limit)

    def _get_last_updated_display(self, pokemon_data: PokemonData) -> str:
        """Get a human-readable display of when data was last updated.

        Args:
            pokemon_data: PokemonData object.

        Returns:
            Human-readable time string.
        """
        # Note: This is a simplified version since we don't store timestamps
        # in PokemonData. In a real implementation, we'd query the database
        # for the updated_at timestamp.
        return "Recently"  # Placeholder

    async def bulk_fetch_pokemon(
        self, *, pokemon_names: list[str], force_refresh: bool = False
    ) -> dict[str, PokemonData | None]:
        """Fetch multiple Pokémon data efficiently.

        Args:
            pokemon_names: List of Pokémon names to fetch.
            force_refresh: If True, always fetch from API.

        Returns:
            Dictionary mapping names to PokemonData objects (or None if not found).
        """
        results = {}

        for name in pokemon_names:
            print(f"🔄 Processing {name}...")
            try:
                data = await self.get_pokemon_data(
                    name=name,
                    force_refresh=force_refresh,
                    interactive=False,  # Non-interactive for bulk operations
                )
                results[name] = data
            except Exception as e:
                print(f"❌ Error processing {name}: {e}")
                results[name] = None

        return results

    def update_pokemon_fields(
        self, *, pokemon_data: PokemonData, is_shiny_available: bool | None = None, base_stardust: int | None = None
    ) -> bool:
        """Update specific fields for a Pokémon in the database.

        Args:
            pokemon_data: PokemonData object to update.
            is_shiny_available: New shiny availability status if provided.
            base_stardust: New base stardust amount if provided.

        Returns:
            True if the Pokémon was updated, False otherwise.
        """
        updated = self.database.update_pokemon_fields(
            pokemon_id=pokemon_data.id, is_shiny_available=is_shiny_available, base_stardust=base_stardust
        )

        if updated:
            # Update the in-memory object as well
            if is_shiny_available is not None:
                pokemon_data.is_shiny_available = is_shiny_available
            if base_stardust is not None:
                pokemon_data.base_stardust = base_stardust

        return updated

    async def get_evolution_data(self, *, pokemon_id: int, force_refresh: bool = False) -> EvolutionData | None:
        """Get evolution data for a Pokémon, checking database first.

        Args:
            pokemon_id: Pokémon ID to get evolution data for.
            force_refresh: If True, always fetch from API.

        Returns:
            EvolutionData object if found, None otherwise.
        """
        # Check database first unless force refresh
        if not force_refresh:
            existing_data = self.database.get_evolution_data(pokemon_id=pokemon_id)
            if existing_data:
                return existing_data

        # Fetch from API
        async with PoGoAPIClient() as client:
            evolution_data = await client.get_evolution_data(pokemon_id=pokemon_id)

            if evolution_data:
                # Store in database
                self.database.upsert_evolution_data(evolution_data=evolution_data)
                return evolution_data

        return None

    async def get_mega_evolution_data(
        self, *, pokemon_id: int, force_refresh: bool = False
    ) -> list[MegaEvolutionData]:
        """Get mega evolution data for a Pokémon, checking database first.

        Args:
            pokemon_id: Pokémon ID to get mega evolution data for.
            force_refresh: If True, always fetch from API.

        Returns:
            List of MegaEvolutionData objects.
        """
        # Check database first unless force refresh
        if not force_refresh:
            existing_data = self.database.get_mega_evolution_data(pokemon_id=pokemon_id)
            if existing_data:
                return existing_data

        # Fetch from API
        async with PoGoAPIClient() as client:
            mega_data = await client.get_mega_evolution_data(pokemon_id=pokemon_id)

            if mega_data:
                # Store in database
                self.database.upsert_mega_evolution_data(mega_data=mega_data)
                return mega_data

        return []

    async def check_evolution_line_has_mega(self, *, pokemon_id: int, force_refresh: bool = False) -> bool:
        """Check if a Pokémon's evolution line includes any mega evolutions.

        Args:
            pokemon_id: Pokémon ID to check.
            force_refresh: If True, always fetch from API.

        Returns:
            True if any Pokémon in the evolution line can mega evolve.
        """
        # Check database first unless force refresh
        if not force_refresh:
            has_mega = self.database.check_evolution_line_has_mega(pokemon_id=pokemon_id)
            if has_mega:
                return True

        # If not found in database or force refresh, check API
        async with PoGoAPIClient() as client:
            has_mega = await client.check_evolution_line_has_mega(pokemon_id=pokemon_id)

            # If we found mega evolution data via API, fetch and store it
            if has_mega:
                # Fetch and store evolution data
                evolution_data = await client.get_evolution_data(pokemon_id=pokemon_id)
                if evolution_data:
                    self.database.upsert_evolution_data(evolution_data=evolution_data)

                # Fetch and store mega evolution data for this Pokémon
                mega_data = await client.get_mega_evolution_data(pokemon_id=pokemon_id)
                if mega_data:
                    self.database.upsert_mega_evolution_data(mega_data=mega_data)

                # Also check evolutions for mega data
                if evolution_data and evolution_data.evolutions:
                    for evolution in evolution_data.evolutions:
                        evolution_mega_data = await client.get_mega_evolution_data(pokemon_id=evolution.pokemon_id)
                        if evolution_mega_data:
                            self.database.upsert_mega_evolution_data(mega_data=evolution_mega_data)

            return has_mega

    async def get_pokemon_with_evolution_info(
        self, *, name: str, force_refresh: bool = False, interactive: bool = True
    ) -> tuple[PokemonData | None, EvolutionData | None, list[MegaEvolutionData], bool]:
        """Get comprehensive Pokémon data including evolution and mega evolution info.

        Args:
            name: Pokémon name to fetch.
            force_refresh: If True, always fetch from API.
            interactive: If True, prompt user when data exists in database.

        Returns:
            Tuple of (PokemonData, EvolutionData, MegaEvolutionData list, has_mega_in_line).
        """
        # Get basic Pokémon data
        pokemon_data = await self.get_pokemon_data(name=name, force_refresh=force_refresh, interactive=interactive)

        if not pokemon_data:
            return None, None, [], False

        # Get evolution data
        evolution_data = await self.get_evolution_data(pokemon_id=pokemon_data.id, force_refresh=force_refresh)

        # Get mega evolution data
        mega_data = await self.get_mega_evolution_data(pokemon_id=pokemon_data.id, force_refresh=force_refresh)

        # Check if evolution line has mega
        has_mega_in_line = await self.check_evolution_line_has_mega(
            pokemon_id=pokemon_data.id, force_refresh=force_refresh
        )

        return pokemon_data, evolution_data, mega_data, has_mega_in_line


def get_pokemon_service(*, database: PokemonDatabase | None = None) -> PokemonService:
    """Get the default Pokémon service instance.

    Returns:
        PokemonService instance with default configuration.
    """
    return PokemonService(database=database)
