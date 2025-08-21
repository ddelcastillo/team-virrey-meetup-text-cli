"""Dynamax Monday text generation script with SQLite database integration.

This script generates Spanish text for Dynamax Monday posts while using
English for all user interface elements. It integrates with a SQLite database
to cache Pokémon data and avoid unnecessary API calls.
"""

import asyncio
from typing import TYPE_CHECKING

from pokemon_meetup.services.pokemon_service import get_pokemon_service
from pokemon_meetup.templates.manager import get_template_manager
from pokemon_meetup.utils.date_utils import get_current_week_info, get_dynamax_monday_date
from pokemon_meetup.web.pokemon_api import PokemonData

if TYPE_CHECKING:
    from pokemon_meetup.services.pokemon_service import PokemonService


def generate_dynamax_monday_text(*, pokemon_data: PokemonData, is_shiny_available: bool) -> str:
    """Generate the Dynamax Monday text using the template system.

    Args:
        pokemon_data: PokemonData object with Pokémon information.
        is_shiny_available: Whether shiny form is available for this event.

    Returns:
        Formatted Spanish text for Dynamax Monday.
    """
    template_manager = get_template_manager()
    return template_manager.render_dynamax_monday(pokemon_data=pokemon_data, is_shiny_available=is_shiny_available)


def format_type_info(*, pokemon_data: PokemonData) -> str:
    """Format Pokémon type information with Spanish names and emojis.

    Args:
        pokemon_data: PokemonData object containing type information.

    Returns:
        Formatted string with type names and emojis in Spanish.
    """
    template_manager = get_template_manager()
    return template_manager._format_type_info(pokemon_data=pokemon_data)


async def get_pokemon_input(*, service: "PokemonService") -> tuple[str, bool]:
    """Get Pokémon name input from user with search suggestions.

    Args:
        service: PokemonService instance for searching.

    Returns:
        Tuple of (pokemon_name, was_just_fetched) where was_just_fetched indicates
        if the data was just fetched from API in this function.
    """
    while True:
        pokemon_name = input("\n🔍 Enter Pokémon name: ").strip()

        if not pokemon_name:
            print("❌ Please enter a valid name.")
            continue

        # Check if Pokémon exists in database first
        existing_data = service.database.get_pokemon_by_name(name=pokemon_name)

        if existing_data:
            # Found in database, no need to fetch
            return pokemon_name, False

        # Try to find exact match from API
        pokemon_data = await service.get_pokemon_data(name=pokemon_name, interactive=False)
        if pokemon_data:
            return pokemon_name, True  # Just fetched from API

        # If no exact match, search for similar names
        print(f"❌ '{pokemon_name}' not found. Searching for similar names...")
        suggestions = await service.search_pokemon(partial_name=pokemon_name, limit=5)

        if not suggestions:
            print("❌ No similar Pokémon found. Try another name.")
            continue

        print("\n📋 Pokémon found:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
        print(f"  {len(suggestions) + 1}. Search for another name")

        while True:
            try:
                choice = input(f"\n🎯 Select an option (1-{len(suggestions) + 1}): ").strip()
                choice_num = int(choice)

                if 1 <= choice_num <= len(suggestions):
                    selected_name = suggestions[choice_num - 1]
                    # Check if this selected Pokémon exists in database
                    existing_selected = service.database.get_pokemon_by_name(name=selected_name)
                    return (selected_name, not existing_selected)  # True if not in DB (will be fetched)
                elif choice_num == len(suggestions) + 1:
                    break  # Go back to name input
                else:
                    print(f"❌ Please enter a number between 1 and {len(suggestions) + 1}.")

            except ValueError:
                print("❌ Please enter a valid number.")


def show_database_stats(*, service: "PokemonService") -> None:
    """Display database statistics.

    Args:
        service: PokemonService instance.
    """
    stats = service.get_database_stats()

    print("\n📊 Database Statistics:")
    print("=" * 40)
    print(f"Total Pokémon: {stats['total_pokemon']}")
    print(f"Database size: {stats['database_size_bytes']:,} bytes")
    print(f"Database path: {stats['database_path']}")
    if stats["last_updated"]:
        print(f"Last updated: {stats['last_updated']}")
    print()


def show_cached_pokemon(*, service: "PokemonService", limit: int = 10) -> None:
    """Display recently cached Pokémon.

    Args:
        service: PokemonService instance.
        limit: Maximum number of Pokémon to show.
    """
    cached_pokemon = service.list_cached_pokemon(limit=limit)

    if not cached_pokemon:
        print("📁 No Pokémon found in database.")
        return

    print(f"\n📁 Recently cached Pokémon (showing {len(cached_pokemon)}):")
    print("=" * 50)

    for i, pokemon in enumerate(cached_pokemon, 1):
        type_info = format_type_info(pokemon_data=pokemon)
        print(f"{i:2d}. {pokemon.name} (#{pokemon.id:03d})")
        print(f"    📊 Type: {type_info}")
        print(f"    💪 Max CP: {pokemon.max_cp:,}")
        print()


def get_shiny_availability_input(*, pokemon_data: PokemonData) -> bool:
    """Get shiny availability input from user.

    Args:
        pokemon_data: PokemonData object to show current API data.

    Returns:
        True if shiny is available, False otherwise.
    """
    api_shiny_status = "Yes" if pokemon_data.is_shiny_available else "No"
    print("\n✨ Shiny availability check:")
    print(f"   API data shows: {api_shiny_status}")

    while True:
        choice = input("Is shiny available for this event? (y/n): ").strip().lower()

        if choice in ["y", "yes", "1"]:
            return True
        elif choice in ["n", "no", "0"]:
            return False
        else:
            print("❌ Please enter 'y' for yes or 'n' for no.")


async def main() -> None:
    """Main function to run the Dynamax Monday script."""
    print("🎮 Dynamax Monday Text Generator")
    print("=" * 50)

    try:
        # Initialize service
        service = get_pokemon_service()

        # Show date information
        week_info = get_current_week_info()
        monday_date = get_dynamax_monday_date()

        print(f"📅 Event date: {monday_date}")
        if week_info["is_today_monday"]:
            print("🎯 Today is Monday - generating for today's event!")
        else:
            days_until = week_info["days_until_monday"]
            print(f"⏰ {days_until} day(s) until next Monday")

        # Get Pokémon name from user first
        pokemon_name, was_just_fetched = await get_pokemon_input(service=service)

        print(f"\n🔄 Getting comprehensive data for {pokemon_name}...")

        # Fetch comprehensive Pokémon data including evolution and mega evolution info
        (pokemon_data, evolution_data, mega_data, has_mega_in_line) = await service.get_pokemon_with_evolution_info(
            name=pokemon_name, interactive=not was_just_fetched
        )

        if not pokemon_data:
            print(f"❌ Error: Could not get data for {pokemon_name}")
            return

        print(f"✅ Successfully retrieved data for {pokemon_data.name}")

        # Display evolution information if available
        if evolution_data and evolution_data.evolutions:
            print(f"\n🔄 {pokemon_data.name} can evolve into:")
            for evo in evolution_data.evolutions:
                evo_info = f"   • {evo.pokemon_name} ({evo.candy_required} candy)"
                if evo.item_required:
                    evo_info += f" + {evo.item_required}"
                if evo.lure_required:
                    evo_info += f" + {evo.lure_required}"
                if evo.must_be_buddy_to_evolve:
                    evo_info += " (buddy required)"
                print(evo_info)

        # Display mega evolution information if available
        if mega_data:
            print(f"\n🌟 {pokemon_data.name} can mega evolve:")
            for mega in mega_data:
                type_info = " / ".join([ptype.value.title() for ptype in mega.types])
                print(f"   • {mega.mega_name} ({type_info})")
                print(
                    f"     Energy: {mega.first_time_mega_energy_required} first time, "
                    f"{mega.mega_energy_required} after"
                )

        # Display mega potential in evolution line
        if has_mega_in_line and not mega_data:
            print(f"\n⭐ {pokemon_data.name}'s evolution line includes mega evolutions!")

        # Get shiny availability from user
        is_shiny_available = get_shiny_availability_input(pokemon_data=pokemon_data)
        shiny_status = "Available" if is_shiny_available else "Not available"
        print(f"✅ Shiny status: {shiny_status}")

        # Update database with user-provided shiny availability if different from API data
        if is_shiny_available != pokemon_data.is_shiny_available:
            service.update_pokemon_fields(pokemon_data=pokemon_data, is_shiny_available=is_shiny_available)
            print("💾 Updated shiny availability in database")

        # Show database stats after processing
        stats = service.get_database_stats()
        print(f"\n📊 Database now contains {stats['total_pokemon']} Pokémon")

        # Generate and display the Spanish text with evolution info
        template_manager = get_template_manager()
        dynamax_text = template_manager.render_dynamax_monday(
            pokemon_data=pokemon_data,
            is_shiny_available=is_shiny_available,
            evolution_data=evolution_data,
            mega_data=mega_data,
            has_mega_in_line=has_mega_in_line,
        )

        print("\n" + "=" * 60)
        print("📝 GENERATED DYNAMAX MONDAY TEXT:")
        print("=" * 60)
        print(dynamax_text)
        print("=" * 60)

        # Show template variables used
        print(f"\n📅 Generated for: {monday_date}")

        # Ask if user wants to copy to clipboard
        copy_choice = input("\n📋 Copy text to clipboard? (y/n): ").strip().lower()
        if copy_choice in ["y", "yes"]:
            try:
                import pyperclip

                pyperclip.copy(dynamax_text)
                print("✅ Text copied to clipboard!")
            except ImportError:
                print("❌ Could not copy to clipboard. Install 'pyperclip' for this feature.")
                print("💡 Command: pip install pyperclip")

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("🐛 Please report this error if it persists.")


if __name__ == "__main__":
    asyncio.run(main())
