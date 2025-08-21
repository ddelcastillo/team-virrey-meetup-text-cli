"""Template manager for loading and processing text templates.

This module provides functionality for loading template files and substituting
variables using Python's string.Template class. Templates are stored in the
templates/ directory and use $variable syntax for substitution.
"""

from pathlib import Path
from string import Template

from pokemon_meetup.common.pokemon_types import get_type_emoji, get_type_spanish_name
from pokemon_meetup.common.weather import WeatherBoosts
from pokemon_meetup.utils.date_utils import (
    get_dynamax_monday_date,
    get_legendary_hour_date,
    get_legendary_wednesday_date,
    get_max_battle_day_date,
    get_raid_day_date,
    get_spotlight_tuesday_date,
    get_weekend_event_date,
)
from pokemon_meetup.web.pokemon_api import EvolutionData, MegaEvolutionData, PokemonData


class TemplateManager:
    """Manager for loading and processing text templates."""

    def __init__(self, *, templates_dir: Path | None = None) -> None:
        """Initialize the template manager.

        Args:
            templates_dir: Directory containing template files. If None, uses default.
        """
        if templates_dir is None:
            # Default to templates/ directory in project root
            project_root = Path(__file__).parent.parent.parent
            templates_dir = project_root / "templates"

        self.templates_dir = templates_dir
        self._template_cache: dict[str, Template] = {}

    def load_template(self, *, template_name: str) -> Template:
        """Load a template from file.

        Args:
            template_name: Name of the template file (without .txt extension).

        Returns:
            Template object ready for substitution.

        Raises:
            FileNotFoundError: If template file doesn't exist.
        """
        if template_name in self._template_cache:
            return self._template_cache[template_name]

        template_path = self.templates_dir / f"{template_name}.txt"

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)
        self._template_cache[template_name] = template

        return template

    def render_dynamax_monday(
        self,
        *,
        pokemon_data: PokemonData,
        is_shiny_available: bool,
        evolution_data: EvolutionData | None = None,
        mega_data: list[MegaEvolutionData] | None = None,
        has_mega_in_line: bool = False,
    ) -> str:
        """Render the Dynamax Monday template with Pokémon data.

        Args:
            pokemon_data: PokemonData object with Pokémon information.
            is_shiny_available: Whether shiny form will be available.
            evolution_data: Evolution data for the Pokémon.
            mega_data: Mega evolution data for the Pokémon.
            has_mega_in_line: Whether the evolution line has mega evolutions.

        Returns:
            Rendered template string.
        """
        template = self.load_template(template_name="dynamax_monday")

        if mega_data is None:
            mega_data = []

        variables = {
            "pokemon_name": pokemon_data.name,
            "pokemon_id": f"#{pokemon_data.id:03d}",
            "monday_date": get_dynamax_monday_date(),
            "type_info": self._format_type_info(pokemon_data=pokemon_data),
            "base_attack": pokemon_data.base_attack,
            "base_defense": pokemon_data.base_defense,
            "base_stamina": pokemon_data.base_stamina,
            "cp_level_20": f"{pokemon_data.cp_level_20:,}",
            "cp_level_25": f"{pokemon_data.cp_level_25:,}",
            "cp_level_30": f"{pokemon_data.cp_level_30:,}",
            "cp_level_40": f"{pokemon_data.cp_level_40:,}",
            "shiny_text": self._format_shiny_text(is_available=is_shiny_available, event_type="dynamax"),
            "evolution_info": self._format_evolution_info(
                evolution_data=evolution_data, mega_data=mega_data, has_mega_in_line=has_mega_in_line
            ),
            "mega_details": self._format_mega_details(mega_data=mega_data),
        }

        return template.substitute(**variables)

    def render_spotlight_hour(
        self,
        *,
        pokemon_data: PokemonData,
        bonus_type: str,
        bonus_description: str,
        bonus_details: str,
        is_shiny_available: bool | None = None,
        base_stardust: int | None = None,
        evolution_data: EvolutionData | None = None,
        mega_data: list[MegaEvolutionData] | None = None,
        has_mega_in_line: bool = False,
    ) -> str:
        """Render the Spotlight Hour template with Pokémon and bonus data.

        Args:
            pokemon_data: PokemonData object containing Pokémon information.
            bonus_type: Type of bonus (e.g., "catch_candy", "evolution_xp").
            bonus_description: Short description for the boost (e.g., "✨X2 XP por evolución ✨").
            bonus_details: Detailed explanation of the bonus.
            is_shiny_available: Override for shiny availability. If None, uses pokemon_data.is_shiny_available.
            base_stardust: Base stardust amount per catch if catch_stardust bonus is selected.
            evolution_data: Evolution data for the Pokémon.
            mega_data: Mega evolution data for the Pokémon.
            has_mega_in_line: Whether the evolution line has mega evolutions.

        Returns:
            Rendered template string.
        """
        template = self.load_template(template_name="spotlight_hour")

        if mega_data is None:
            mega_data = []

        # Format type information with Spanish names and emojis
        type_info = self._format_type_info(pokemon_data=pokemon_data)

        # Get the next Tuesday date in Spanish
        tuesday_date = get_spotlight_tuesday_date()

        # Determine shiny availability
        shiny_available = is_shiny_available if is_shiny_available is not None else pokemon_data.is_shiny_available
        shiny_text = self._format_shiny_text(is_available=shiny_available, event_type="spotlight")

        # Modify bonus details if it's catch_stardust and base_stardust is provided
        if bonus_type == "catch_stardust" and base_stardust is not None:
            bonus_details = self._format_stardust_details(base_stardust=base_stardust)

        # Format mega evolution information for spotlight hour
        mega_info = self._format_spotlight_mega_info(
            pokemon_data=pokemon_data,
            evolution_data=evolution_data,
            mega_data=mega_data,
            has_mega_in_line=has_mega_in_line,
        )

        # Prepare template variables
        template_vars = {
            "pokemon_name": pokemon_data.name,
            "pokemon_id": f"{pokemon_data.id:03d}",
            "type_info": type_info,
            "tuesday_date": tuesday_date,
            "bonus_type": bonus_type,
            "bonus_description": bonus_description,
            "bonus_details": bonus_details,
            "shiny_text": shiny_text,
            "mega_info": mega_info,
            "cp_level_20": f"{pokemon_data.cp_level_20:,}",
            "cp_level_25": f"{pokemon_data.cp_level_25:,}",
            "cp_level_30": f"{pokemon_data.cp_level_30:,}",
            "cp_level_40": f"{pokemon_data.cp_level_40:,}",
            "base_attack": pokemon_data.base_attack,
            "base_defense": pokemon_data.base_defense,
            "base_stamina": pokemon_data.base_stamina,
        }

        return template.substitute(**template_vars)

    def render_legendary_hour(
        self, *, pokemon_data: PokemonData, is_shiny_available: bool, day_choice: int = 3
    ) -> str:
        """Render the Legendary Hour template with Pokémon data.

        Args:
            pokemon_data: PokemonData object containing Pokémon information.
            is_shiny_available: Whether shiny form is available for this event.
            day_choice: Day choice (1=Monday, 2=Tuesday, etc.). Defaults to 3 (Wednesday).

        Returns:
            Rendered template string.
        """
        template = self.load_template(template_name="legendary_hour")

        # Format type information with Spanish names and emojis
        type_info = self._format_type_info(pokemon_data=pokemon_data)

        # Get the event date based on day choice
        event_date = get_legendary_hour_date(day_choice=day_choice)

        # Format shiny availability text
        shiny_text = self._format_shiny_text(is_available=is_shiny_available, event_type="legendary")

        # Get weather emojis for the Pokémon's types
        weather_emojis = WeatherBoosts.get_weather_emojis_for_types(pokemon_types=pokemon_data.types)

        # Prepare template variables
        template_vars = {
            "pokemon_name": pokemon_data.name,
            "event_date": event_date,
            "type_info": type_info,
            "type_verb": "es",  # Singular for single Pokémon
            "cp_level_20": f"{pokemon_data.cp_level_20:,}",
            "cp_level_25": f"{pokemon_data.cp_level_25:,}",
            "weather_emojis": weather_emojis,
            "shiny_text": shiny_text,
            "pokemon_details": "",  # Empty for single Pokémon
            "shiny_newline": "",  # No extra newline for single Pokémon
        }

        return template.substitute(**template_vars)

    def render_multiple_legendary_hour(self, *, pokemon_list: list[tuple[PokemonData, bool]], day_choice: int) -> str:
        """Render the Legendary Hour template with multiple Pokémon data.

        Args:
            pokemon_list: List of tuples containing (PokemonData, is_shiny_available).
            day_choice: Day choice (1=Monday, 2=Tuesday, etc.).

        Returns:
            Rendered template string for multiple Pokémon.
        """
        template = self.load_template(template_name="legendary_hour")

        # Get the event date based on day choice
        event_date = get_legendary_hour_date(day_choice=day_choice)

        # Format Pokémon information
        pokemon_info_list = []
        shiny_available_pokemon = []
        shiny_unavailable_pokemon = []

        for pokemon_data, is_shiny_available in pokemon_list:
            # Format type information with Spanish names and emojis
            type_info = self._format_type_info(pokemon_data=pokemon_data)

            # Get weather emojis for the Pokémon's types
            weather_emojis = WeatherBoosts.get_weather_emojis_for_types(pokemon_types=pokemon_data.types)

            pokemon_info = f"❖ {pokemon_data.name} ({type_info}) - CP: {pokemon_data.cp_level_20:,}, {pokemon_data.cp_level_25:,} con clima {weather_emojis}."
            pokemon_info_list.append(pokemon_info)

            # Track shiny availability
            if is_shiny_available:
                shiny_available_pokemon.append(pokemon_data.name)
            else:
                shiny_unavailable_pokemon.append(pokemon_data.name)

        # Combine Pokémon names for the main title
        pokemon_names = [pokemon_data.name for pokemon_data, _ in pokemon_list]
        if len(pokemon_names) == 2:
            pokemon_name = f"{pokemon_names[0]} y {pokemon_names[1]}"
        else:
            pokemon_name = ", ".join(pokemon_names[:-1]) + f" y {pokemon_names[-1]}"

        # Format detailed shiny availability text
        shiny_text = self._format_multiple_shiny_text(
            shiny_available=shiny_available_pokemon,
            shiny_unavailable=shiny_unavailable_pokemon,
            total_count=len(pokemon_list),
        )

        # Prepare template variables
        template_vars = {
            "pokemon_name": pokemon_name,
            "event_date": event_date,
            "type_info": "múltiples tipos",  # Fixed typo: removed "tipo"
            "type_verb": "son",  # Plural for multiple Pokémon
            "cp_level_20": "variado",  # Generic since we have multiple Pokémon
            "cp_level_25": "variado",  # Generic since we have multiple Pokémon
            "weather_emojis": "🌤️",  # Generic weather emoji
            "shiny_text": shiny_text,
            "pokemon_details": "\n".join(pokemon_info_list),
            "shiny_newline": "\n",  # Extra newline for multiple Pokémon
        }

        return template.substitute(**template_vars)

    def render_max_battle_day(
        self, *, pokemon_data: PokemonData, day_choice: int, max_type: str, is_shiny_available: bool
    ) -> str:
        """Render the Max Battle Day template with Pokémon data.

        Args:
            pokemon_data: PokemonData object containing Pokémon information.
            day_choice: 1 for Saturday, 2 for Sunday.
            max_type: Type of Max form ("Dynamax" or "Gigantamax").
            is_shiny_available: Whether shiny form is available for this event.

        Returns:
            Rendered template string.
        """
        template = self.load_template(template_name="max_battle_day")

        # Format type information with Spanish names and emojis
        type_info = self._format_type_info(pokemon_data=pokemon_data)

        # Get the event date based on day choice
        event_date = get_weekend_event_date(day_choice=day_choice)

        # Format shiny availability text
        shiny_text = self._format_shiny_text(is_available=is_shiny_available, event_type="max_battle")

        # Prepare template variables
        template_vars = {
            "pokemon_name": pokemon_data.name,
            "event_date": event_date,
            "max_type": max_type,
            "type_info": type_info,
            "cp_level_20": f"{pokemon_data.cp_level_20:,}",
            "shiny_text": shiny_text,
        }

        return template.substitute(**template_vars)

    def render_raid_day(self, *, pokemon_data: PokemonData, day_choice: int, is_shiny_available: bool) -> str:
        """Render the Raid Day template with Pokémon data.

        Args:
            pokemon_data: PokemonData object containing Pokémon information.
            day_choice: 1 for Saturday, 2 for Sunday.
            is_shiny_available: Whether shiny form is available for this event.

        Returns:
            Rendered template string.
        """
        template = self.load_template(template_name="raid_day")

        # Format type information with Spanish names and emojis
        type_info = self._format_type_info(pokemon_data=pokemon_data)

        # Get the event date based on day choice
        event_date = get_weekend_event_date(day_choice=day_choice)

        # Format shiny availability text
        shiny_text = self._format_shiny_text(is_available=is_shiny_available, event_type="legendary")

        # Get weather emojis for the Pokémon's types
        weather_emojis = WeatherBoosts.get_weather_emojis_for_types(pokemon_types=pokemon_data.types)

        # Prepare template variables
        template_vars = {
            "pokemon_name": pokemon_data.name,
            "event_date": event_date,
            "type_info": type_info,
            "cp_level_20": f"{pokemon_data.cp_level_20:,}",
            "cp_level_25": f"{pokemon_data.cp_level_25:,}",
            "weather_emojis": weather_emojis,
            "shiny_text": shiny_text,
        }

        return template.substitute(**template_vars)

    def render_template(self, *, template_name: str, **variables: str | int | bool) -> str:
        """Render any template with provided variables.

        Args:
            template_name: Name of the template to render.
            **variables: Variables to substitute in the template.

        Returns:
            Rendered template string.
        """
        template = self.load_template(template_name=template_name)
        return template.substitute(**variables)

    def list_available_templates(self) -> list[str]:
        """List all available template files.

        Returns:
            List of template names (without .txt extension).
        """
        if not self.templates_dir.exists():
            return []

        template_files = self.templates_dir.glob("*.txt")
        return [template_file.stem for template_file in template_files]

    def _format_type_info(self, *, pokemon_data: PokemonData) -> str:
        """Format Pokémon type information with Spanish names and emojis.

        Args:
            pokemon_data: PokemonData object containing type information.

        Returns:
            Formatted string with type names and emojis in Spanish.
        """
        if not pokemon_data.types:
            return "Tipo desconocido"

        type_strings = []
        for pokemon_type in pokemon_data.types:
            spanish_name = get_type_spanish_name(pokemon_type=pokemon_type)
            emoji = get_type_emoji(pokemon_type=pokemon_type)
            type_strings.append(f"{spanish_name} {emoji}")

        if len(type_strings) == 1:
            return type_strings[0]
        else:
            return " / ".join(type_strings)

    def _format_shiny_text(self, *, is_available: bool, event_type: str) -> str:
        """Format shiny availability text based on availability and event type.

        Args:
            is_available: Whether shiny form is available.
            event_type: Type of event ("dynamax", "spotlight", "legendary", or "max_battle").

        Returns:
            Formatted shiny text in Spanish.
        """
        if is_available:
            shiny_messages = {
                "dynamax": (
                    "La forma shiny estará disponible, pero tengan en cuenta que la "
                    "probabilidad base (1/512) no se incrementa en batallas Max. ✨"
                ),
                "spotlight": (
                    "La forma shiny estará disponible, pero tengan en cuenta que la "
                    "probabilidad base (1/512) no se incrementa durante la hora. ✨"
                ),
                "max_battle": "La forma shiny estará potenciada (alrededor de 1/20). ✨",
                "legendary": "La forma shiny estará disponible (alrededor de 1/20). ✨",
            }
            return shiny_messages.get(event_type, "La forma shiny estará disponible. ✨")
        else:
            return "La forma shiny no estará disponible. 🚫✨"

    def _format_multiple_shiny_text(
        self, *, shiny_available: list[str], shiny_unavailable: list[str], total_count: int
    ) -> str:
        """Format detailed shiny availability text for multiple Pokémon.

        Args:
            shiny_available: List of Pokémon names with shiny available.
            shiny_unavailable: List of Pokémon names with shiny unavailable.
            total_count: Total number of Pokémon.

        Returns:
            Formatted detailed shiny text in Spanish.
        """
        if total_count == 1:
            # Single Pokémon - use the standard format
            is_available = len(shiny_available) == 1
            return self._format_shiny_text(is_available=is_available, event_type="legendary")

        elif len(shiny_available) == total_count:
            # All Pokémon have shiny available
            return "La forma shiny estará disponible para todos (alrededor de 1/20). ✨"

        elif len(shiny_available) == 0:
            # No Pokémon have shiny available
            return "La forma shiny no estará disponible para ninguno. 🚫✨"

        else:
            # Some Pokémon have shiny, some don't
            available_text = self._format_pokemon_list(shiny_available)
            unavailable_text = self._format_pokemon_list(shiny_unavailable)

            return f"La forma shiny estará disponible para {available_text} (alrededor de 1/20), pero no para {unavailable_text}. ✨"

    def _format_pokemon_list(self, pokemon_names: list[str]) -> str:
        """Format a list of Pokémon names in Spanish.

        Args:
            pokemon_names: List of Pokémon names.

        Returns:
            Formatted string with proper Spanish grammar.
        """
        if len(pokemon_names) == 1:
            return pokemon_names[0]
        elif len(pokemon_names) == 2:
            return f"{pokemon_names[0]} y {pokemon_names[1]}"
        else:
            return ", ".join(pokemon_names[:-1]) + f" y {pokemon_names[-1]}"

    def _format_stardust_details(self, *, base_stardust: int) -> str:
        """Format stardust details based on the given base_stardust.

        Args:
            base_stardust: Base stardust amount per catch.

        Returns:
            Formatted stardust details in Spanish.
        """
        doubled_stardust = base_stardust * 2
        star_piece_stardust = int(doubled_stardust * 1.5)

        return f"Polvos estelares: cada captura otorgará {doubled_stardust}, {star_piece_stardust} con estrella. ⭐️"

    def _format_evolution_info(
        self, *, evolution_data: EvolutionData | None, mega_data: list[MegaEvolutionData], has_mega_in_line: bool
    ) -> str:
        """Format evolution and mega evolution information.

        Args:
            evolution_data: Evolution data for the Pokémon.
            mega_data: Mega evolution data for the Pokémon.
            has_mega_in_line: Whether the evolution line has mega evolutions.

        Returns:
            Formatted evolution information text.
        """
        info_parts = []

        # Direct mega evolution info
        if mega_data:
            mega_names = [mega.mega_name for mega in mega_data]
            if len(mega_names) == 1:
                info_parts.append(f"🌟 Puede megaevolucionar a {mega_names[0]}")
            else:
                mega_list = ", ".join(mega_names)
                info_parts.append(f"🌟 Puede megaevolucionar a: {mega_list}")

        # Evolution info
        if evolution_data and evolution_data.evolutions:
            evolution_names = []
            for evo in evolution_data.evolutions:
                evo_text = evo.pokemon_name
                if evo.candy_required > 0:
                    evo_text += f" ({evo.candy_required} caramelos)"
                if evo.item_required:
                    evo_text += f" + {evo.item_required}"
                evolution_names.append(evo_text)

            if len(evolution_names) == 1:
                info_parts.append(f"🔄 Evoluciona a {evolution_names[0]}")
            else:
                evo_list = ", ".join(evolution_names)
                info_parts.append(f"🔄 Puede evolucionar a: {evo_list}")

        # Mega potential in evolution line
        if has_mega_in_line and not mega_data:
            info_parts.append("⭐ Su línea evolutiva incluye megaevoluciones")

        if not info_parts:
            return "No evoluciona"

        return " | ".join(info_parts)

    def _format_mega_details(self, *, mega_data: list[MegaEvolutionData]) -> str:
        """Format detailed mega evolution information.

        Args:
            mega_data: List of mega evolution data.

        Returns:
            Formatted mega evolution details.
        """
        if not mega_data:
            return "No tiene megaevolución disponible"

        details = []
        for mega in mega_data:
            type_info = " / ".join([ptype.value.title() for ptype in mega.types])
            detail = (
                f"{mega.mega_name}: {type_info} "
                f"(ATK {mega.base_attack}, DEF {mega.base_defense}, STA {mega.base_stamina}) "
                f"- Energía: {mega.first_time_mega_energy_required} primera vez, "
                f"{mega.mega_energy_required} después"
            )
            details.append(detail)

        return " | ".join(details)

    def _format_spotlight_mega_info(
        self,
        *,
        pokemon_data: PokemonData,
        evolution_data: EvolutionData | None,
        mega_data: list[MegaEvolutionData],
        has_mega_in_line: bool,
    ) -> str:
        """Format mega evolution information for spotlight hour.

        Args:
            pokemon_data: The spotlight Pokémon data.
            evolution_data: Evolution data for the Pokémon.
            mega_data: Mega evolution data for the Pokémon.
            has_mega_in_line: Whether the evolution line has mega evolutions.

        Returns:
            Formatted mega evolution information for spotlight hour with newline, or empty string if none.
        """
        # If the spotlight Pokémon itself can mega evolve
        if mega_data:
            return f"❖ {pokemon_data.name} tiene mega-evolución disponible. 💎\n"

        # If any evolution can mega evolve, we need to find which one
        # Since we don't have access to the service here, we'll use a simpler approach
        # and assume the first evolution is the one with mega (this works for most cases)
        if has_mega_in_line and evolution_data and evolution_data.evolutions:
            # For most Pokémon, there's typically one main evolution that has mega
            # We'll show the first evolution name
            first_evolution = evolution_data.evolutions[0]
            return f"❖ {first_evolution.pokemon_name} tiene mega-evolución disponible. 💎\n"

        return ""

    def render_pokemon_summary(
        self,
        *,
        pokemon_data: PokemonData,
        evolution_data: EvolutionData | None = None,
        mega_data: list[MegaEvolutionData] | None = None,
        has_mega_in_line: bool = False,
    ) -> str:
        """Render the Pokémon summary template with data.

        Args:
            pokemon_data: PokemonData object with Pokémon information.
            evolution_data: Evolution data for the Pokémon.
            mega_data: Mega evolution data for the Pokémon.
            has_mega_in_line: Whether the evolution line has mega evolutions.

        Returns:
            Rendered template string.
        """
        template = self.load_template(template_name="pokemon_summary")

        if mega_data is None:
            mega_data = []

        variables = {
            "pokemon_name": pokemon_data.name,
            "pokemon_id": f"#{pokemon_data.id:03d}",
            "type_info": self._format_type_info(pokemon_data=pokemon_data),
            "base_attack": pokemon_data.base_attack,
            "base_defense": pokemon_data.base_defense,
            "base_stamina": pokemon_data.base_stamina,
            "cp_level_20": f"{pokemon_data.cp_level_20:,}",
            "cp_level_25": f"{pokemon_data.cp_level_25:,}",
            "cp_level_30": f"{pokemon_data.cp_level_30:,}",
            "cp_level_40": f"{pokemon_data.cp_level_40:,}",
            "evolution_info": self._format_evolution_info(
                evolution_data=evolution_data, mega_data=mega_data, has_mega_in_line=has_mega_in_line
            ),
            "mega_details": self._format_mega_details(mega_data=mega_data),
        }

        return template.substitute(**variables)


def get_template_manager() -> TemplateManager:
    """Get the default template manager instance.

    Returns:
        TemplateManager instance with default configuration.
    """
    return TemplateManager()
