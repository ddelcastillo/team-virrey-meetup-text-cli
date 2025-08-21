#!/usr/bin/env python3
"""Legendary Hour text generation script with SQLite database integration.

This script generates Spanish text for Legendary Hour posts on Wednesday while using
English for all user interface elements. It integrates with a SQLite database
to cache Pokémon data and avoid unnecessary API calls.
"""

import asyncio
from typing import TYPE_CHECKING

from pokemon_meetup.services.pokemon_service import PokemonService, get_pokemon_service
from pokemon_meetup.templates.manager import get_template_manager
from pokemon_meetup.utils.date_utils import get_legendary_wednesday_date
from pokemon_meetup.web.pokemon_api import PokemonData

if TYPE_CHECKING:
    from pokemon_meetup.services.pokemon_service import PokemonService


def get_day_choice() -> int:
    """Get the day choice from user for the legendary hour event.

    Returns:
        Integer representing the chosen day (1=Monday, 2=Tuesday, etc.).
    """
    print("\n📅 Select the day for Legendary Hour:")
    print("  1. Monday")
    print("  2. Tuesday")
    print("  3. Wednesday")
    print("  4. Thursday")
    print("  5. Friday")
    print("  6. Saturday")
    print("  7. Sunday")

    while True:
        try:
            choice = input("\n🎯 Select day (1-7): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= 7:
                return choice_num
            else:
                print("❌ Please enter a number between 1 and 7.")

        except ValueError:
            print("❌ Please enter a valid number.")


def get_number_of_pokemon() -> int:
    """Get the number of legendary Pokémon from user.

    Returns:
        Number of Pokémon to include in the event.
    """
    while True:
        try:
            count_input = input("\n🔢 How many legendary Pokémon? (1-10): ").strip()
            count = int(count_input)

            if 1 <= count <= 10:
                return count
            else:
                print("❌ Please enter a number between 1 and 10.")

        except ValueError:
            print("❌ Please enter a valid number.")


def generate_legendary_hour_text(*, pokemon_data: PokemonData, is_shiny_available: bool, day_choice: int) -> str:
    """Generate the Legendary Hour text using the template system.

    Args:
        pokemon_data: PokemonData object with Pokémon information.
        is_shiny_available: Whether shiny form is available for this event.
        day_choice: Day choice (1=Monday, 2=Tuesday, etc.).

    Returns:
        Formatted Spanish text for Legendary Hour.
    """
    template_manager = get_template_manager()
    return template_manager.render_legendary_hour(
        pokemon_data=pokemon_data, is_shiny_available=is_shiny_available, day_choice=day_choice
    )


def generate_multiple_legendary_hour_text(*, pokemon_list: list[tuple[PokemonData, bool]], day_choice: int) -> str:
    """Generate the Legendary Hour text for multiple Pokémon using the template system.

    Args:
        pokemon_list: List of tuples containing (PokemonData, is_shiny_available).
        day_choice: Day choice (1=Monday, 2=Tuesday, etc.).

    Returns:
        Formatted Spanish text for Legendary Hour with multiple Pokémon.
    """
    template_manager = get_template_manager()
    return template_manager.render_multiple_legendary_hour(pokemon_list=pokemon_list, day_choice=day_choice)


async def get_pokemon_input(*, service: "PokemonService") -> tuple[str, bool]:
    """Get Pokémon name input from user with search suggestions.

    Args:
        service: PokemonService instance for searching.

    Returns:
        Tuple of (pokemon_name, was_just_fetched) where was_just_fetched indicates
        if the data was just fetched from API in this function.
    """
    while True:
        pokemon_name = input("\n🔍 Enter Pokémon name for Legendary Hour: ").strip()

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
    print(f"\n✨ Shiny availability for {pokemon_data.name}:")
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
    """Main function to run the Legendary Hour script."""
    print("🌟 Legendary Hour Text Generator")
    print("=" * 50)

    try:
        # Initialize service
        service = get_pokemon_service()

        # Get day choice from user
        day_choice = get_day_choice()

        # Get number of Pokémon
        num_pokemon = get_number_of_pokemon()

        # Show date information based on day choice
        from datetime import datetime

        from pokemon_meetup.utils.date_utils import (
            format_spanish_date,
            get_next_friday,
            get_next_monday,
            get_next_saturday,
            get_next_sunday,
            get_next_thursday,
            get_next_tuesday,
            get_next_wednesday,
            get_weekend_event_date,
        )

        # Get the appropriate date based on day choice
        if day_choice == 1:
            event_date = get_next_monday()
        elif day_choice == 2:
            event_date = get_next_tuesday()
        elif day_choice == 3:
            event_date = get_next_wednesday()
        elif day_choice == 4:
            event_date = get_next_thursday()
        elif day_choice == 5:
            event_date = get_next_friday()
        elif day_choice == 6:
            event_date = get_next_saturday()
        else:  # day_choice == 7
            event_date = get_next_sunday()

        formatted_date = format_spanish_date(date=event_date, format_type="full")
        print(f"📅 Event date: {formatted_date}")

        # Check if today is the selected day
        current_weekday = datetime.now().weekday()
        selected_weekday = day_choice - 1  # Convert to 0-based index

        if current_weekday == selected_weekday:
            print("🎯 Today is the selected day - generating for today's event!")
        else:
            # Calculate days until the selected day
            days_until = (selected_weekday - current_weekday) % 7
            if days_until == 0:
                days_until = 7
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            print(f"⏰ {days_until} day(s) until next {day_names[selected_weekday]}")

        if num_pokemon == 1:
            # Single Pokémon flow
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
            print(f"💪 CP Level 25: {pokemon_data.cp_level_25:,}")

            # Show weather boost information
            from pokemon_meetup.common.weather import WeatherBoosts

            weather_emojis = WeatherBoosts.get_weather_emojis_for_types(pokemon_types=pokemon_data.types)
            if weather_emojis:
                print(f"🌤️ Weather boost: {weather_emojis}")
            else:
                print("🌤️ No weather boost available")

            # Get shiny availability from user
            is_shiny_available = get_shiny_availability_input(pokemon_data=pokemon_data)
            shiny_status = "Available" if is_shiny_available else "Not available"
            print(f"✅ Shiny status: {shiny_status}")

            # Update database with user-provided shiny availability if different from API data
            if is_shiny_available != pokemon_data.is_shiny_available:
                service.update_pokemon_fields(pokemon_data=pokemon_data, is_shiny_available=is_shiny_available)
                print("💾 Updated shiny availability in database")

            # Generate and display the Spanish text
            legendary_text = generate_legendary_hour_text(
                pokemon_data=pokemon_data, is_shiny_available=is_shiny_available, day_choice=day_choice
            )

        else:
            # Multiple Pokémon flow
            pokemon_list = []

            for i in range(num_pokemon):
                print(f"\n{'=' * 40}")
                print(f"🎯 Pokémon {i + 1} of {num_pokemon}")
                print(f"{'=' * 40}")

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
                print(f"💪 CP Level 25: {pokemon_data.cp_level_25:,}")

                # Show weather boost information
                from pokemon_meetup.common.weather import WeatherBoosts

                weather_emojis = WeatherBoosts.get_weather_emojis_for_types(pokemon_types=pokemon_data.types)
                if weather_emojis:
                    print(f"🌤️ Weather boost: {weather_emojis}")
                else:
                    print("🌤️ No weather boost available")

                # Get shiny availability from user
                is_shiny_available = get_shiny_availability_input(pokemon_data=pokemon_data)
                shiny_status = "Available" if is_shiny_available else "Not available"
                print(f"✅ Shiny status: {shiny_status}")

                # Update database with user-provided shiny availability if different from API data
                if is_shiny_available != pokemon_data.is_shiny_available:
                    service.update_pokemon_fields(pokemon_data=pokemon_data, is_shiny_available=is_shiny_available)
                    print("💾 Updated shiny availability in database")

                pokemon_list.append((pokemon_data, is_shiny_available))

            # Generate and display the Spanish text for multiple Pokémon
            legendary_text = generate_multiple_legendary_hour_text(pokemon_list=pokemon_list, day_choice=day_choice)

        # Show database stats after processing
        stats = service.get_database_stats()
        print(f"\n📊 Database now contains {stats['total_pokemon']} Pokémon")

        print("\n" + "=" * 60)
        print("📝 GENERATED LEGENDARY HOUR TEXT:")
        print("=" * 60)
        print(legendary_text)
        print("=" * 60)

        # Show template variables used
        print(f"\n📅 Generated for: {formatted_date}")

        # Ask if user wants to copy to clipboard
        copy_choice = input("\n📋 Copy text to clipboard? (y/n): ").strip().lower()
        if copy_choice in ["y", "yes"]:
            try:
                import pyperclip

                pyperclip.copy(legendary_text)
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
