# Templates Directory

This directory contains text templates for generating Pokémon-related content. Templates use Python's `string.Template` format with `$variable` syntax for variable substitution.

## Available Templates

### `dynamax_monday.txt`
The main template for generating Dynamax Monday social media posts in Spanish.

**Variables:**
- `$pokemon_name` - Pokémon name
- `$pokemon_id` - Pokémon ID (formatted as 3 digits, e.g., "025")
- `$type_info` - Formatted type information with Spanish names first, then emojis (e.g., "Eléctrico ⚡" or "Fuego 🔥 / Volador 🌪️")
- `$monday_date` - Automatically calculated current or next Monday date in Spanish (e.g., "lunes 3 de junio")
- `$shiny_text` - Dynamic shiny availability text based on user input
- `$cp_level_20` - CP at level 20 (formatted with commas)
- `$cp_level_25` - CP at level 25 (formatted with commas)
- `$cp_level_30` - CP at level 30 (formatted with commas)
- `$cp_level_40` - CP at level 40 (formatted with commas)
- `$base_attack` - Base attack stat
- `$base_defense` - Base defense stat
- `$base_stamina` - Base stamina stat

### `spotlight_hour.txt`
Template for generating Spotlight Hour social media posts on Tuesday.

**Variables:**
- `$pokemon_name` - Pokémon name
- `$pokemon_id` - Pokémon ID (formatted as 3 digits, e.g., "025")
- `$type_info` - Formatted type information with Spanish names first, then emojis
- `$tuesday_date` - Automatically calculated current or next Tuesday date in Spanish (e.g., "martes 4 de junio")
- `$bonus_type` - Type of bonus (e.g., "catch_candy", "evolution_xp")
- `$bonus_description` - Short description for the boost (e.g., "✨X2 XP por evolución ✨")
- `$bonus_details` - Detailed explanation of the bonus
- `$shiny_text` - Dynamic shiny availability text based on user input
- `$cp_level_20` - CP at level 20 (formatted with commas)
- `$cp_level_25` - CP at level 25 (formatted with commas)
- `$cp_level_30` - CP at level 30 (formatted with commas)
- `$cp_level_40` - CP at level 40 (formatted with commas)
- `$base_attack` - Base attack stat
- `$base_defense` - Base defense stat
- `$base_stamina` - Base stamina stat

### `pokemon_summary.txt`
A compact summary template for Pokémon information.

**Variables:** (same as above, except date and bonus variables are not automatically included)

## Usage

### In Python Code

```python
from pokemon_meetup.templates.manager import get_template_manager

# Get template manager
template_manager = get_template_manager()

# Render Dynamax Monday template (includes automatic date calculation)
text = template_manager.render_dynamax_monday(pokemon_data=pokemon_data)

# Render Spotlight Hour template (includes automatic date calculation)
text = template_manager.render_spotlight_hour(
    pokemon_data=pokemon_data,
    bonus_type="evolution_xp",
    bonus_description="✨X2 XP por evolución ✨",
    bonus_details="Obtendrán 2000 XP por evolución..."
)

# Render any template with custom variables
text = template_manager.render_template(
    template_name="pokemon_summary",
    pokemon_name="Pikachu",
    pokemon_id="025",
    type_info="Eléctrico ⚡",
    # ... other variables
)
```

### Date Calculation

The `monday_date` and `tuesday_date` variables are automatically calculated to show:
- **Today's date** if today is the target day (Monday/Tuesday)
- **Next target day's date** if today is any other day

The date is formatted in Spanish as "día de la semana DD de mes" (e.g., "lunes 3 de junio").

### Shiny Availability

The `$shiny_text` variable dynamically changes based on user input during script execution:

**When shiny is available:**
- **Dynamax Monday**: "La forma shiny estará disponible, pero tengan en cuenta que la probabilidad base (1/512) no se incrementa en batallas Max. ✨"
- **Spotlight Hour**: "La forma shiny estará disponible, pero tengan en cuenta que la probabilidad base (1/512) no se incrementa durante la hora. ✨"

**When shiny is not available:**
- **Both events**: "La forma shiny no estará disponible. 🚫✨"

### Creating New Templates

1. Create a new `.txt` file in this directory
2. Use `$variable_name` syntax for substitution points
3. The template will be automatically available via `template_manager.render_template()`

### Template Variables

All templates have access to these standard variables when using `render_dynamax_monday()`:

- Pokémon identification: `pokemon_name`, `pokemon_id`
- Type information: `type_info` (formatted with Spanish names first, then emojis)
- Event date: `monday_date` (automatically calculated current/next Monday)
- CP values: `cp_level_20`, `cp_level_25`, `cp_level_30`, `cp_level_40`
- Base stats: `base_attack`, `base_defense`, `base_stamina`

## Examples

### Custom Template Example

Create `templates/raid_announcement.txt`:
```
🚨 ¡RAID ALERT! 🚨

$pokemon_name aparece en raids de nivel 5
💪 CP: $cp_level_20 - $cp_level_40
📊 Tipo: $type_info

¡No te lo pierdas!
```

Then use it:
```python
text = template_manager.render_template(
    template_name="raid_announcement",
    **template_vars
)
```

### Date Utilities

For custom date handling:
```python
from pokemon_meetup.utils.date_utils import get_dynamax_monday_date, get_current_week_info

# Get formatted Monday date
monday_date = get_dynamax_monday_date()  # "lunes 3 de junio"

# Get detailed week information
week_info = get_current_week_info()
# Returns: {
#   "next_monday_date": "lunes 3 de junio",
#   "next_monday_short": "3 de junio", 
#   "is_today_monday": False,
#   "days_until_monday": 2,
#   "current_date": "sábado 1 de junio"
# }
``` 