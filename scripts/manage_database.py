"""Database management utility for Pokémon data.

This script provides tools for managing the SQLite database containing
Pokémon data, including viewing stored data, database statistics, and
maintenance operations.
"""

import asyncio
from typing import TYPE_CHECKING

from pokemon_meetup.services.pokemon_service import get_pokemon_service
from pokemon_meetup.templates.manager import get_template_manager
from pokemon_meetup.web.pokemon_api import PokemonData

if TYPE_CHECKING:
    from pokemon_meetup.services.pokemon_service import PokemonService


def format_type_info(*, pokemon_data: PokemonData) -> str:
    """Format Pokémon type information with Spanish names and emojis.

    Args:
        pokemon_data: PokemonData object containing type information.

    Returns:
        Formatted string with type names and emojis in Spanish.
    """
    template_manager = get_template_manager()
    return template_manager._format_type_info(pokemon_data=pokemon_data)


def display_all_pokemon(*, service: "PokemonService") -> None:
    """Display all Pokémon stored in the database with detailed information.

    Args:
        service: PokemonService instance.
    """
    all_pokemon = service.list_cached_pokemon()

    if not all_pokemon:
        print("📁 No Pokémon found in database.")
        return

    print(f"📁 Found {len(all_pokemon)} Pokémon in database:")
    print("=" * 80)

    for i, pokemon in enumerate(all_pokemon, 1):
        type_info = format_type_info(pokemon_data=pokemon)
        print(f"{i:3d}. {pokemon.name} (#{pokemon.id:03d})")
        print(f"     📊 Type: {type_info}")
        print(f"     💪 Max CP: {pokemon.max_cp:,}")
        print(f"     🎯 Rarity: {pokemon.rarity or 'Unknown'}")
        print(f"     ✨ Shiny: {'Yes' if pokemon.is_shiny_available else 'No'}")

        # Show base stardust if available
        if pokemon.base_stardust is not None:
            print(f"     💫 Base Stardust: {pokemon.base_stardust}")

        # Show base stats
        print(f"     📈 Stats: ATK {pokemon.base_attack} | DEF {pokemon.base_defense} | STA {pokemon.base_stamina}")

        # Show CP values
        print(
            f"     🏆 CP: L20({pokemon.cp_level_20:,}) L25({pokemon.cp_level_25:,}) "
            f"L30({pokemon.cp_level_30:,}) L40({pokemon.cp_level_40:,})"
        )

        # Show additional info if available
        extra_info = []
        if pokemon.buddy_distance:
            extra_info.append(f"🚶{pokemon.buddy_distance}km")
        if pokemon.candy_to_evolve:
            extra_info.append(f"🍬{pokemon.candy_to_evolve}")
        if extra_info:
            print(f"     i  {' | '.join(extra_info)}")

        print()


def show_pokemon_details(*, service: "PokemonService", pokemon_index: int) -> None:
    """Show detailed information for a specific Pokémon.

    Args:
        service: PokemonService instance.
        pokemon_index: 1-based index of the Pokémon to show.
    """
    all_pokemon = service.list_cached_pokemon()

    if not all_pokemon or pokemon_index < 1 or pokemon_index > len(all_pokemon):
        print("❌ Invalid Pokémon index.")
        return

    pokemon = all_pokemon[pokemon_index - 1]
    type_info = format_type_info(pokemon_data=pokemon)

    print(f"📄 Detailed information for {pokemon.name}:")
    print("=" * 50)
    print(f"🆔 ID: #{pokemon.id:03d}")
    print(f"📊 Type: {type_info}")
    print(f"🎯 Rarity: {pokemon.rarity or 'Unknown'}")
    print(f"✨ Shiny available: {'Yes' if pokemon.is_shiny_available else 'No'}")
    print(f"🎮 Released: {'Yes' if pokemon.is_released else 'No'}")

    if pokemon.buddy_distance:
        print(f"🚶 Buddy distance: {pokemon.buddy_distance} km")

    if pokemon.candy_to_evolve:
        print(f"🍬 Candy to evolve: {pokemon.candy_to_evolve}")

    print("\n📈 Base Stats:")
    print(f"   ⚔️  Attack: {pokemon.base_attack}")
    print(f"   🛡️  Defense: {pokemon.base_defense}")
    print(f"   ❤️  Stamina: {pokemon.base_stamina}")

    print("\n💪 CP Values (Perfect IVs):")
    print(f"   Level 20: {pokemon.cp_level_20:,} CP")
    print(f"   Level 25: {pokemon.cp_level_25:,} CP")
    print(f"   Level 30: {pokemon.cp_level_30:,} CP")
    print(f"   Level 40: {pokemon.cp_level_40:,} CP")
    print(f"   Maximum: {pokemon.max_cp:,} CP")


def show_database_stats(*, service: "PokemonService") -> None:
    """Display comprehensive database statistics.

    Args:
        service: PokemonService instance.
    """
    stats = service.get_database_stats()

    print("📊 Database Statistics:")
    print("=" * 40)
    print(f"Total Pokémon: {stats['total_pokemon']}")
    print(f"Database size: {stats['database_size_bytes']:,} bytes")
    print(f"Database path: {stats['database_path']}")

    if stats["last_updated"]:
        print(f"Last updated: {stats['last_updated']}")

    # Additional statistics
    total_pokemon = stats.get("total_pokemon", 0)
    if isinstance(total_pokemon, int) and total_pokemon > 0:
        all_pokemon = service.list_cached_pokemon()

        # Count by rarity
        rarity_counts: dict[str, int] = {}
        shiny_count = 0
        released_count = 0

        for pokemon in all_pokemon:
            rarity = pokemon.rarity or "Unknown"
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1

            if pokemon.is_shiny_available:
                shiny_count += 1
            if pokemon.is_released:
                released_count += 1

        print("\n📈 Breakdown:")
        print(f"Released Pokémon: {released_count}")
        print(f"Shiny available: {shiny_count}")

        print("\n🎯 By Rarity:")
        for rarity, count in sorted(rarity_counts.items()):
            print(f"   {rarity}: {count}")


async def search_pokemon_by_name(*, service: "PokemonService") -> None:
    """Search for a specific Pokémon by name and show detailed information.

    Args:
        service: PokemonService instance.
    """
    pokemon_name = input("\n🔍 Enter Pokémon name to view details: ").strip()

    if not pokemon_name:
        print("❌ Please enter a valid name.")
        return

    print(f"🔄 Searching for {pokemon_name}...")

    # First try exact match in database
    pokemon_data = service.database.get_pokemon_by_name(name=pokemon_name)

    if not pokemon_data:
        # If not found, search for similar names
        print(f"❌ '{pokemon_name}' not found in database. Searching for similar names...")
        suggestions = service.database.search_pokemon_by_name(partial_name=pokemon_name, limit=5)

        if not suggestions:
            print("❌ No similar Pokémon found in database.")
            return

        print("\n📋 Similar Pokémon found in database:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion.name}")
        print(f"  {len(suggestions) + 1}. Cancel")

        while True:
            try:
                choice = input(f"\n🎯 Select an option (1-{len(suggestions) + 1}): ").strip()
                choice_num = int(choice)

                if 1 <= choice_num <= len(suggestions):
                    pokemon_data = suggestions[choice_num - 1]
                    break
                elif choice_num == len(suggestions) + 1:
                    return
                else:
                    print(f"❌ Please enter a number between 1 and {len(suggestions) + 1}.")

            except ValueError:
                print("❌ Please enter a valid number.")

    # Show detailed information
    show_pokemon_details_data(pokemon_data=pokemon_data)


def show_pokemon_details_data(*, pokemon_data: PokemonData) -> None:
    """Show detailed information for a specific Pokémon.

    Args:
        pokemon_data: PokemonData object to display.
    """
    type_info = format_type_info(pokemon_data=pokemon_data)

    print(f"\n📄 Detailed information for {pokemon_data.name}:")
    print("=" * 60)
    print(f"🆔 ID: #{pokemon_data.id:03d}")
    print(f"📊 Type: {type_info}")
    print(f"🎯 Rarity: {pokemon_data.rarity or 'Unknown'}")
    print(f"✨ Shiny available: {'Yes' if pokemon_data.is_shiny_available else 'No'}")
    print(f"🎮 Released: {'Yes' if pokemon_data.is_released else 'No'}")

    if pokemon_data.buddy_distance:
        print(f"🚶 Buddy distance: {pokemon_data.buddy_distance} km")

    if pokemon_data.candy_to_evolve:
        print(f"🍬 Candy to evolve: {pokemon_data.candy_to_evolve}")

    if pokemon_data.base_stardust is not None:
        print(f"💫 Base stardust: {pokemon_data.base_stardust}")

    print("\n📈 Base Stats:")
    print(f"   ⚔️  Attack: {pokemon_data.base_attack}")
    print(f"   🛡️  Defense: {pokemon_data.base_defense}")
    print(f"   ❤️  Stamina: {pokemon_data.base_stamina}")

    print("\n💪 CP Values (Perfect IVs):")
    print(f"   Level 20: {pokemon_data.cp_level_20:,} CP")
    print(f"   Level 25: {pokemon_data.cp_level_25:,} CP")
    print(f"   Level 30: {pokemon_data.cp_level_30:,} CP")
    print(f"   Level 40: {pokemon_data.cp_level_40:,} CP")
    print(f"   Maximum: {pokemon_data.max_cp:,} CP")


async def search_and_add_pokemon(*, service: "PokemonService") -> None:
    """Interactive search and add Pokémon to database.

    Args:
        service: PokemonService instance.
    """
    pokemon_name = input("\n🔍 Enter Pokémon name to search and add: ").strip()

    if not pokemon_name:
        print("❌ Please enter a valid name.")
        return

    print(f"🔄 Searching for {pokemon_name}...")

    try:
        pokemon_data = await service.get_pokemon_data(name=pokemon_name, interactive=True)

        if pokemon_data:
            print(f"✅ Successfully added/updated {pokemon_data.name} in database")
        else:
            print(f"❌ Could not find or add {pokemon_name}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def main() -> None:
    """Main function for the database management utility."""
    print("🗂️  Pokémon Database Manager")
    print("=" * 40)

    service = get_pokemon_service()

    while True:
        print("\n📋 Available options:")
        print("  1. Show database statistics")
        print("  2. List all Pokémon (detailed view)")
        print("  3. View specific Pokémon details")
        print("  4. Search and add Pokémon")
        print("  5. Exit")

        try:
            choice = input("\n🎯 Select an option (1-5): ").strip()

            if choice == "1":
                print()
                show_database_stats(service=service)

            elif choice == "2":
                print()
                display_all_pokemon(service=service)

            elif choice == "3":
                await search_pokemon_by_name(service=service)

            elif choice == "4":
                await search_and_add_pokemon(service=service)

            elif choice == "5":
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid option. Please select 1-5.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
