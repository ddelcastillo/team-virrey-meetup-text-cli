"""Raid Day text generation script with SQLite database integration.

This script generates Spanish text for Raid Day posts on Saturday or Sunday while using
English for all user interface elements. It integrates with a SQLite database
to cache Pokémon data and avoid unnecessary API calls.
"""

import asyncio
from typing import TYPE_CHECKING

from pokemon_meetup.services.pokemon_service import get_pokemon_service
from pokemon_meetup.templates.manager import get_template_manager
from pokemon_meetup.utils.date_utils import get_raid_day_date
from pokemon_meetup.web.pokemon_api import PokemonData

if TYPE_CHECKING:
    from pokemon_meetup.services.pokemon_service import PokemonService


def generate_raid_day_text(*, pokemon_data: PokemonData, day_choice: int, is_shiny_available: bool) -> str:
    """Generate the Raid Day text using the template system.

    Args:
        pokemon_data: PokemonData object with Pokémon information.
        day_choice: 1 for Saturday, 2 for Sunday.
        is_shiny_available: Whether shiny form is available for this event.

    Returns:
        Formatted Spanish text for Raid Day.
    """
    template_manager = get_template_manager()
    return template_manager.render_raid_day(
        pokemon_data=pokemon_data, day_choice=day_choice, is_shiny_available=is_shiny_available
    )


async def get_pokemon_input(*, service: "PokemonService") -> tuple[str, bool]:
    """Get Pokémon name input from user with search suggestions.

    Args:
        service: PokemonService instance for searching.

    Returns:
        Tuple of (pokemon_name, was_just_fetched) where was_just_fetched indicates
        if the data was just fetched from API in this function.
    """
    while True:
        pokemon_name = input("\n🔍 Enter Pokémon name for Raid Day: ").strip()

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


def get_day_choice_input() -> int:
    """Get day choice input from user.

    Returns:
        1 for Saturday, 2 for Sunday.
    """
    print("\n📅 Select event day:")
    print("  1. Saturday")
    print("  2. Sunday")

    while True:
        choice = input("Choose day (1/2): ").strip()

        if choice == "1":
            return 1
        elif choice == "2":
            return 2
        else:
            print("❌ Please enter '1' for Saturday or '2' for Sunday.")


def format_type_info(*, pokemon_data: PokemonData) -> str:
    """Format Pokémon type information with Spanish names and emojis.

    Args:
        pokemon_data: PokemonData object containing type information.

    Returns:
        Formatted string with type names and emojis in Spanish.
    """
    template_manager = get_template_manager()
    return template_manager._format_type_info(pokemon_data=pokemon_data)


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
    """Main function to run the Raid Day script."""
    print("🏟️ Raid Day Text Generator")
    print("=" * 50)

    try:
        # Initialize service
        service = get_pokemon_service()

        # Get day choice from user
        day_choice = get_day_choice_input()
        day_name = "Saturday" if day_choice == 1 else "Sunday"

        # Show date information
        event_date = get_raid_day_date(day_choice=day_choice)
        print(f"📅 Event date: {event_date}")

        # Check if today is the selected day
        from datetime import datetime

        today_weekday = datetime.now().weekday()
        target_weekday = 5 if day_choice == 1 else 6  # Saturday=5, Sunday=6

        if today_weekday == target_weekday:
            print(f"🎯 Today is {day_name} - generating for today's event!")
        else:
            # Calculate days until the selected day
            days_until = (target_weekday - today_weekday) % 7
            if days_until == 0:
                days_until = 7
            print(f"⏰ {days_until} day(s) until next {day_name}")

        # Get Pokémon name from user
        pokemon_name, was_just_fetched = await get_pokemon_input(service=service)

        print(f"\n🔄 Getting data for {pokemon_name}...")

        # Fetch Pokémon data
        pokemon_data = await service.get_pokemon_data(name=pokemon_name, interactive=not was_just_fetched)

        if not pokemon_data:
            print(f"❌ Error: Could not get data for {pokemon_name}")
            return

        print(f"✅ Successfully retrieved data for {pokemon_data.name}")

        # Display basic Pokémon information
        type_info = format_type_info(pokemon_data=pokemon_data)
        print(f"📊 Type: {type_info}")
        print(f"💪 CP Level 20: {pokemon_data.cp_level_20:,}")
        print(f"💪 CP Level 25: {pokemon_data.cp_level_25:,} (weather boosted)")

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

        # Generate and display the Spanish text
        raid_day_text = generate_raid_day_text(
            pokemon_data=pokemon_data, day_choice=day_choice, is_shiny_available=is_shiny_available
        )

        print("\n" + "=" * 60)
        print("📝 GENERATED RAID DAY TEXT:")
        print("=" * 60)
        print(raid_day_text)
        print("=" * 60)

        # Show template variables used
        print(f"\n📅 Generated for: {event_date}")

        # Ask if user wants to copy to clipboard
        copy_choice = input("\n📋 Copy text to clipboard? (y/n): ").strip().lower()
        if copy_choice in ["y", "yes"]:
            try:
                import pyperclip

                pyperclip.copy(raid_day_text)
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
