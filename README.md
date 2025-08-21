# Pokémon Meetup Event Text Generator

A unified system for generating event text for Team Virrey's Pokémon Go meetups.

![Demo](demo.svg)

## Installation

First, install uv:

```bash
# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows:
powershell -c "irm https://astral.sh/uv/install.sh | iex"

# Or with pip:
pip install uv
```

Then install the project dependencies:

```bash
uv sync
```

## Quick Start

Run the main script to access all event generators:

```bash
uv run main.py
```

## Available Events

### 1. Dynamax Monday (6-7 PM)
- Generates text for Monday Dynamax battles
- Includes evolution and mega evolution information
- Shows CP values and shiny availability

### 2. Spotlight Hour Tuesday (6-7 PM)  
- Generates text for Tuesday Spotlight Hour events
- Includes bonus information (XP, candy, stardust)
- Shows mega evolution potential in evolution lines

### 3. Legendary Hour Wednesday (6-7 PM)
- Generates text for Wednesday Legendary Hour raids
- Shows weather boost information
- Includes CP values for levels 20 and 25

### 4. Max Battle Day (Saturday/Sunday 2-5 PM)
- Generates text for weekend Max Battle events
- Choose between Dynamax or Gigantamax
- Select Saturday or Sunday timing

## Features

- **Database Integration**: Caches Pokémon data to avoid repeated API calls
- **Interactive Prompts**: User-friendly 1/2 choice system
- **Search Functionality**: Find Pokémon by partial name matching
- **Shiny Override**: Manually set shiny availability per event
- **Template System**: Consistent Spanish formatting across all events
- **Evolution Data**: Shows evolution requirements and mega potential
- **Weather Integration**: Displays appropriate weather boost information

## Individual Scripts

You can also run individual event scripts directly:

```bash
uv run scripts/dynamax_monday.py
uv run scripts/spotlight_hour.py  
uv run scripts/legendary_hour.py
uv run scripts/max_battle_day.py
```

## Database Management

Use the database management script for maintenance:

```bash
uv run scripts/manage_database.py
```

## Requirements

- Python 3.13+
- uv for dependency management
- Internet connection for API calls

## Usage Tips

1. **First Run**: The system will fetch Pokémon data from the API and cache it
2. **Subsequent Runs**: Choose existing (1) or fresh (2) data when prompted
3. **Clipboard**: Install `pyperclip` for automatic clipboard copying
4. **Multiple Events**: Generate text for multiple events in one session

## Team Virrey

This system is designed specifically for Team Virrey's Pokémon Go meetups in Parque El Virrey, Bogotá. All generated text is in Spanish and includes location-specific information. 