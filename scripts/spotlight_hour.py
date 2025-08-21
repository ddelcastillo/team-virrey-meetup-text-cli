"""Spotlight Hour text generation script with SQLite database integration.

This script generates Spanish text for Spotlight Hour posts on Tuesday while using
English for all user interface elements. It integrates with a SQLite database
to cache Pokémon data and includes bonus type selection.
"""

import asyncio
from typing import TYPE_CHECKING

from pokemon_meetup.services.pokemon_service import get_pokemon_service
from pokemon_meetup.templates.manager import get_template_manager
from pokemon_meetup.utils.date_utils import get_spotlight_tuesday_date
from pokemon_meetup.web.pokemon_api import EvolutionData, MegaEvolutionData, PokemonData

if TYPE_CHECKING:
    from pokemon_meetup.services.pokemon_service import PokemonService

# Spotlight Hour bonus types with descriptions
SPOTLIGHT_BONUSES = {
    1: {
        "type": "catch_candy",
        "description": "✨X2 caramelos por captura ✨",
        "details": "Obtendrán el doble de caramelos por cada captura durante la hora destacada.",
    },
    2: {
        "type": "evolution_xp",
        "description": "✨X2 XP por evolución ✨",
        "details": "XP por evolución: 1000 XP por evolución normal, 2000 XP por nueva "
        "entrada en su Pokédex (4000 XP y 6000 XP, respectivamente, con huevo "
        "suerte activo 🥚).",
    },
    3: {
        "type": "catch_xp",
        "description": "✨X2 XP por captura ✨",
        "details": "XP por captura: hasta 2340 XP por captura (4680 XP con huevo suerte "
        "🥚, por cada captura con tiro excelente, bola curva, y primera bola.",
    },
    4: {
        "type": "catch_stardust",
        "description": "✨X2 polvo estelar por captura ✨",
        "details": "Obtendrán el doble de polvo estelar por cada captura durante la hora destacada.",
    },
    5: {
        "type": "transfer_candy",
        "description": "✨X2 caramelos por transferencia ✨",
        "details": "Obtendrán el doble de caramelos al transferir Pokémon durante la hora destacada.",
    },
}


def generate_spotlight_hour_text(
    *,
    pokemon_data: PokemonData,
    bonus_type: str,
    bonus_description: str,
    bonus_details: str,
    is_shiny_available: bool,
    base_stardust: int | None = None,
    evolution_data: EvolutionData | None = None,
    mega_data: list[MegaEvolutionData] | None = None,
    has_mega_in_line: bool = False,
) -> str:
    """Generate the Spotlight Hour text using the template system.

    Args:
        pokemon_data: PokemonData object with Pokémon information.
        bonus_type: Type of bonus selected.
        bonus_description: Short description of the bonus.
        bonus_details: Detailed explanation of the bonus.
        is_shiny_available: Whether shiny form is available for this event.
        base_stardust: Base stardust amount per catch if catch_stardust bonus is selected.
        evolution_data: Evolution data for the Pokémon.
        mega_data: Mega evolution data for the Pokémon.
        has_mega_in_line: Whether the evolution line has mega evolutions.

    Returns:
        Formatted Spanish text for Spotlight Hour.
    """
    template_manager = get_template_manager()
    return template_manager.render_spotlight_hour(
        pokemon_data=pokemon_data,
        bonus_type=bonus_type,
        bonus_description=bonus_description,
        bonus_details=bonus_details,
        is_shiny_available=is_shiny_available,
        base_stardust=base_stardust,
        evolution_data=evolution_data,
        mega_data=mega_data,
        has_mega_in_line=has_mega_in_line,
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
        pokemon_name = input("\n🔍 Enter Pokémon name for Spotlight Hour: ").strip()

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


def get_bonus_selection() -> tuple[str, str, str]:
    """Get bonus type selection from user.

    Returns:
        Tuple of (bonus_type, bonus_description, bonus_details).
    """
    print("\n🎁 Select Spotlight Hour bonus:")
    print("=" * 40)

    for num, bonus_info in SPOTLIGHT_BONUSES.items():
        print(f"  {num}. {bonus_info['description']}")

    while True:
        try:
            choice = input(f"\n🎯 Select bonus type (1-{len(SPOTLIGHT_BONUSES)}): ").strip()
            choice_num = int(choice)

            if choice_num in SPOTLIGHT_BONUSES:
                bonus_info = SPOTLIGHT_BONUSES[choice_num]
                return (bonus_info["type"], bonus_info["description"], bonus_info["details"])
            else:
                print(f"❌ Please enter a number between 1 and {len(SPOTLIGHT_BONUSES)}.")

        except ValueError:
            print("❌ Please enter a valid number.")


def get_base_stardust_input() -> int:
    """Get base stardust per catch input from user.

    Returns:
        Base stardust amount per catch.
    """
    print("\n✨ Stardust calculation:")
    print("   Enter the base stardust amount per catch for this Pokémon")
    print("   (Common values: 100, 500, 750, 1000, 1250)")

    while True:
        try:
            stardust_input = input("💫 Base stardust per catch: ").strip()
            base_stardust = int(stardust_input)

            if base_stardust <= 0:
                print("❌ Please enter a positive number.")
                continue

            # Confirm the input
            doubled_stardust = base_stardust * 2
            star_piece_stardust = int(doubled_stardust * 1.5)

            print(f"✅ Base: {base_stardust}, Doubled: {doubled_stardust}, With Star Piece: {star_piece_stardust}")

            confirm = input("Is this correct? (y/n): ").strip().lower()
            if confirm in ["y", "yes", "1"]:
                return base_stardust
            else:
                print("Let's try again...")
                continue

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
    """Main function to run the Spotlight Hour script."""
    print("🌟 Spotlight Hour Text Generator")
    print("=" * 50)

    try:
        # Initialize service
        service = get_pokemon_service()

        # Show date information
        tuesday_date = get_spotlight_tuesday_date()

        print(f"📅 Event date: {tuesday_date}")

        # Check if today is Tuesday
        from datetime import datetime

        if datetime.now().weekday() == 1:  # Tuesday
            print("🎯 Today is Tuesday - generating for today's event!")
        else:
            # Calculate days until Tuesday
            days_until = (1 - datetime.now().weekday()) % 7
            if days_until == 0:
                days_until = 7
            print(f"⏰ {days_until} day(s) until next Tuesday")

        # Get Pokémon name from user
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

        # Get bonus selection
        bonus_type, bonus_description, bonus_details = get_bonus_selection()

        print(f"\n✅ Selected bonus: {bonus_description}")

        # Get base stardust input if catch_stardust bonus is selected
        base_stardust = None
        if bonus_type == "catch_stardust":
            base_stardust = get_base_stardust_input()
            print(f"✅ Base stardust: {base_stardust}")

        # Get shiny availability from user
        is_shiny_available = get_shiny_availability_input(pokemon_data=pokemon_data)
        shiny_status = "Available" if is_shiny_available else "Not available"
        print(f"✅ Shiny status: {shiny_status}")

        # Update database with user-provided values
        updates_made = []

        # Update shiny availability if different from API data
        if is_shiny_available != pokemon_data.is_shiny_available:
            service.update_pokemon_fields(pokemon_data=pokemon_data, is_shiny_available=is_shiny_available)
            updates_made.append("shiny availability")

        # Update base stardust if provided
        if base_stardust is not None:
            service.update_pokemon_fields(pokemon_data=pokemon_data, base_stardust=base_stardust)
            updates_made.append("base stardust")

        if updates_made:
            print(f"💾 Updated {', '.join(updates_made)} in database")

        # Show database stats after processing
        stats = service.get_database_stats()
        print(f"\n📊 Database now contains {stats['total_pokemon']} Pokémon")

        # Generate and display the Spanish text
        spotlight_text = generate_spotlight_hour_text(
            pokemon_data=pokemon_data,
            bonus_type=bonus_type,
            bonus_description=bonus_description,
            bonus_details=bonus_details,
            is_shiny_available=is_shiny_available,
            base_stardust=base_stardust,
            evolution_data=evolution_data,
            mega_data=mega_data,
            has_mega_in_line=has_mega_in_line,
        )

        print("\n" + "=" * 60)
        print("📝 GENERATED SPOTLIGHT HOUR TEXT:")
        print("=" * 60)
        print(spotlight_text)
        print("=" * 60)

        # Show template variables used
        print(f"\n📅 Generated for: {tuesday_date}")
        print(f"🎁 Bonus: {bonus_description}")

        # Ask if user wants to copy to clipboard
        copy_choice = input("\n📋 Copy text to clipboard? (y/n): ").strip().lower()
        if copy_choice in ["y", "yes"]:
            try:
                import pyperclip

                pyperclip.copy(spotlight_text)
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
