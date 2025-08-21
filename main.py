#!/usr/bin/env python3
"""Unified Pokémon Meetup Event Text Generator.

This is the main entry point for all event text generation scripts.
Users can select which type of event they want to generate text for:
- Dynamax Monday
- Spotlight Hour Tuesday
- Legendary Hour Wednesday
- Max Battle Day (Saturday/Sunday)
- Raid Day (Saturday/Sunday)
"""

import asyncio

# Import all the individual script main functions
from scripts.dynamax_monday import main as dynamax_main
from scripts.legendary_hour import main as legendary_main
from scripts.max_battle_day import main as max_battle_main
from scripts.raid_day import main as raid_day_main
from scripts.spotlight_hour import main as spotlight_main


def show_welcome_banner() -> None:
    """Display the welcome banner and available options."""
    print("🎮 Pokémon Meetup Event Text Generator")
    print("=" * 50)
    print("Welcome to Team Virrey's event text generator!")
    print("Select which event you want to generate text for:")
    print()


def get_event_choice() -> int:
    """Get the user's choice of which event to generate.

    Returns:
        Integer representing the chosen event (1-6).
    """
    print("📅 Available Events:")
    print("  1. Dynamax Monday (6-7 PM)")
    print("  2. Spotlight Hour Tuesday (6-7 PM)")
    print("  3. Legendary Hour Wednesday (6-7 PM)")
    print("  4. Max Battle Day (Saturday/Sunday 2-5 PM)")
    print("  5. Raid Day (Saturday/Sunday 2-5 PM)")
    print("  6. Exit")
    print()

    while True:
        try:
            choice = input("🎯 Select an event (1-6): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= 6:
                return choice_num
            else:
                print("❌ Please enter a number between 1 and 6.")

        except ValueError:
            print("❌ Please enter a valid number.")


async def run_selected_event(*, event_choice: int) -> None:
    """Run the selected event script.

    Args:
        event_choice: The event number chosen by the user.
    """
    print("\n" + "=" * 50)

    if event_choice == 1:
        print("🎮 Starting Dynamax Monday Generator...")
        await dynamax_main()
    elif event_choice == 2:
        print("✨ Starting Spotlight Hour Generator...")
        await spotlight_main()
    elif event_choice == 3:
        print("🌟 Starting Legendary Hour Generator...")
        await legendary_main()
    elif event_choice == 4:
        print("⚔️ Starting Max Battle Day Generator...")
        await max_battle_main()
    elif event_choice == 5:
        print("⚔️ Starting Raid Day Generator...")
        await raid_day_main()
    elif event_choice == 6:
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice. This shouldn't happen!")
        return

    # Ask if user wants to generate another event
    print("\n" + "=" * 50)
    another = input("🔄 Generate text for another event? (y/n): ").strip().lower()

    if another in ["y", "yes"]:
        print("\n")
        await main()  # Restart the main menu


async def main() -> None:
    """Main function that orchestrates the event selection and execution."""
    try:
        show_welcome_banner()
        event_choice = get_event_choice()
        await run_selected_event(event_choice=event_choice)

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("🐛 Please report this error if it persists.")


if __name__ == "__main__":
    asyncio.run(main())
