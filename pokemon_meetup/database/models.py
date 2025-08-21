"""Database models and schema for Pokémon data storage.

This module defines the SQLite database schema for storing Pokémon Go data
fetched from the PoGo API. The schema is designed to efficiently store
all relevant Pokémon information while avoiding data duplication.

Database Schema:
===============

Table: pokemon_data
------------------
- id (INTEGER PRIMARY KEY): Pokémon ID from PoGo API
- name (TEXT NOT NULL): Pokémon name
- types_json (TEXT NOT NULL): JSON array of type strings
- base_attack (INTEGER NOT NULL): Base attack stat
- base_defense (INTEGER NOT NULL): Base defense stat
- base_stamina (INTEGER NOT NULL): Base stamina stat
- cp_level_20 (INTEGER NOT NULL): CP at level 20 (perfect IVs)
- cp_level_25 (INTEGER NOT NULL): CP at level 25 (perfect IVs)
- cp_level_30 (INTEGER NOT NULL): CP at level 30 (perfect IVs)
- cp_level_40 (INTEGER NOT NULL): CP at level 40 (perfect IVs)
- max_cp (INTEGER NOT NULL): Maximum possible CP
- buddy_distance (INTEGER): Buddy walking distance in km (nullable)
- candy_to_evolve (INTEGER): Candy required to evolve (nullable)
- is_shiny_available (BOOLEAN NOT NULL): Whether shiny form is available
- is_released (BOOLEAN NOT NULL): Whether Pokémon is released in game
- rarity (TEXT): Rarity tier (nullable)
- form (TEXT NOT NULL): Pokémon form (default: "Normal")
- base_stardust (INTEGER): Base stardust required to evolve (nullable)
- created_at (TIMESTAMP NOT NULL): When record was created
- updated_at (TIMESTAMP NOT NULL): When record was last updated
- data_source (TEXT NOT NULL): Source of the data (e.g., "pogoapi.net")

Table: pokemon_evolutions
-------------------------
- id (INTEGER PRIMARY KEY AUTOINCREMENT): Unique evolution record ID
- from_pokemon_id (INTEGER NOT NULL): ID of the Pokémon that evolves
- to_pokemon_id (INTEGER NOT NULL): ID of the evolution target
- to_pokemon_name (TEXT NOT NULL): Name of the evolution target
- candy_required (INTEGER NOT NULL): Candy needed for evolution
- item_required (TEXT): Required evolution item (nullable)
- lure_required (TEXT): Required lure module (nullable)
- no_candy_cost_if_traded (BOOLEAN NOT NULL): Whether trading removes candy cost
- priority (INTEGER): Evolution priority (nullable)
- only_evolves_in_daytime (BOOLEAN NOT NULL): Daytime evolution requirement
- only_evolves_in_nighttime (BOOLEAN NOT NULL): Nighttime evolution requirement
- must_be_buddy_to_evolve (BOOLEAN NOT NULL): Buddy requirement
- buddy_distance_required (REAL): Required buddy walking distance (nullable)
- gender_required (TEXT): Required gender for evolution (nullable)
- created_at (TIMESTAMP NOT NULL): When record was created
- updated_at (TIMESTAMP NOT NULL): When record was last updated

Table: mega_evolutions
----------------------
- id (INTEGER PRIMARY KEY AUTOINCREMENT): Unique mega evolution record ID
- pokemon_id (INTEGER NOT NULL): ID of the Pokémon that can mega evolve
- pokemon_name (TEXT NOT NULL): Name of the Pokémon
- form (TEXT NOT NULL): Mega form identifier
- mega_name (TEXT NOT NULL): Display name of the mega form
- first_time_mega_energy_required (INTEGER NOT NULL): Initial mega energy cost
- mega_energy_required (INTEGER NOT NULL): Subsequent mega energy cost
- base_attack (INTEGER NOT NULL): Mega form base attack
- base_defense (INTEGER NOT NULL): Mega form base defense
- base_stamina (INTEGER NOT NULL): Mega form base stamina
- types_json (TEXT NOT NULL): JSON array of mega form types
- cp_multiplier_override (REAL): Custom CP multiplier (nullable)
- created_at (TIMESTAMP NOT NULL): When record was created
- updated_at (TIMESTAMP NOT NULL): When record was last updated

Indexes:
--------
- PRIMARY KEY on id for all tables
- INDEX on name for fast name-based lookups
- INDEX on updated_at for finding recently updated records
- INDEX on from_pokemon_id and to_pokemon_id for evolution lookups
- INDEX on pokemon_id for mega evolution lookups
"""

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pokemon_meetup.web.pokemon_api import EvolutionData, MegaEvolutionData, PokemonData


@dataclass
class DatabaseConfig:
    """Configuration for the SQLite database."""

    db_path: Path
    timeout: float = 30.0

    def __post_init__(self) -> None:
        """Ensure the database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)


class PokemonDatabase:
    """SQLite database manager for Pokémon data."""

    def __init__(self, *, config: DatabaseConfig) -> None:
        """Initialize the database manager.

        Args:
            config: Database configuration.
        """
        self.config = config
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Create the main pokemon_data table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pokemon_data (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    types_json TEXT NOT NULL,
                    base_attack INTEGER NOT NULL,
                    base_defense INTEGER NOT NULL,
                    base_stamina INTEGER NOT NULL,
                    cp_level_20 INTEGER NOT NULL,
                    cp_level_25 INTEGER NOT NULL,
                    cp_level_30 INTEGER NOT NULL,
                    cp_level_40 INTEGER NOT NULL,
                    max_cp INTEGER NOT NULL,
                    buddy_distance INTEGER,
                    candy_to_evolve INTEGER,
                    is_shiny_available BOOLEAN NOT NULL,
                    is_released BOOLEAN NOT NULL,
                    rarity TEXT,
                    form TEXT NOT NULL DEFAULT 'Normal',
                    base_stardust INTEGER,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    data_source TEXT NOT NULL DEFAULT 'pogoapi.net'
                )
            """
            )

            # Create pokemon_evolutions table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pokemon_evolutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_pokemon_id INTEGER NOT NULL,
                    to_pokemon_id INTEGER NOT NULL,
                    to_pokemon_name TEXT NOT NULL,
                    candy_required INTEGER NOT NULL,
                    item_required TEXT,
                    lure_required TEXT,
                    no_candy_cost_if_traded BOOLEAN NOT NULL DEFAULT 0,
                    priority INTEGER,
                    only_evolves_in_daytime BOOLEAN NOT NULL DEFAULT 0,
                    only_evolves_in_nighttime BOOLEAN NOT NULL DEFAULT 0,
                    must_be_buddy_to_evolve BOOLEAN NOT NULL DEFAULT 0,
                    buddy_distance_required REAL,
                    gender_required TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (from_pokemon_id) REFERENCES pokemon_data (id),
                    FOREIGN KEY (to_pokemon_id) REFERENCES pokemon_data (id)
                )
            """
            )

            # Create mega_evolutions table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mega_evolutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pokemon_id INTEGER NOT NULL,
                    pokemon_name TEXT NOT NULL,
                    form TEXT NOT NULL,
                    mega_name TEXT NOT NULL,
                    first_time_mega_energy_required INTEGER NOT NULL,
                    mega_energy_required INTEGER NOT NULL,
                    base_attack INTEGER NOT NULL,
                    base_defense INTEGER NOT NULL,
                    base_stamina INTEGER NOT NULL,
                    types_json TEXT NOT NULL,
                    cp_multiplier_override REAL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pokemon_id) REFERENCES pokemon_data (id)
                )
            """
            )

            # Migrate existing databases to add base_stardust column if it doesn't exist
            self._migrate_database(conn)

            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_name ON pokemon_data (name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_updated_at ON pokemon_data (updated_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evolution_from ON pokemon_evolutions (from_pokemon_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evolution_to ON pokemon_evolutions (to_pokemon_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mega_pokemon ON mega_evolutions (pokemon_id)")

            # Create triggers to automatically update the updated_at timestamp
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_pokemon_data_timestamp
                AFTER UPDATE ON pokemon_data
                BEGIN
                    UPDATE pokemon_data SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """
            )

            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_pokemon_evolutions_timestamp
                AFTER UPDATE ON pokemon_evolutions
                BEGIN
                    UPDATE pokemon_evolutions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """
            )

            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_mega_evolutions_timestamp
                AFTER UPDATE ON mega_evolutions
                BEGIN
                    UPDATE mega_evolutions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
            """
            )

            conn.commit()

    def _migrate_database(self, conn: sqlite3.Connection) -> None:
        """Migrate existing database to add new columns if they don't exist.

        Args:
            conn: SQLite connection object.
        """
        # Check if base_stardust column exists
        cursor = conn.execute("PRAGMA table_info(pokemon_data)")
        columns = [row[1] for row in cursor.fetchall()]

        if "base_stardust" not in columns:
            conn.execute("ALTER TABLE pokemon_data ADD COLUMN base_stardust INTEGER")
            print("✅ Added base_stardust column to existing database")

    def pokemon_exists(self, *, pokemon_id: int) -> bool:
        """Check if a Pokémon exists in the database.

        Args:
            pokemon_id: The Pokémon ID to check.

        Returns:
            True if the Pokémon exists, False otherwise.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            cursor = conn.execute("SELECT 1 FROM pokemon_data WHERE id = ? LIMIT 1", (pokemon_id,))
            return cursor.fetchone() is not None

    def get_pokemon_by_id(self, *, pokemon_id: int) -> PokemonData | None:
        """Retrieve a Pokémon by ID from the database.

        Args:
            pokemon_id: The Pokémon ID to retrieve.

        Returns:
            PokemonData object if found, None otherwise.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM pokemon_data WHERE id = ?", (pokemon_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_pokemon_data(row=row)

    def get_pokemon_by_name(self, *, name: str) -> PokemonData | None:
        """Retrieve a Pokémon by name from the database.

        Args:
            name: The Pokémon name to search for (case-insensitive).

        Returns:
            PokemonData object if found, None otherwise.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM pokemon_data WHERE LOWER(name) = LOWER(?)", (name,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_pokemon_data(row=row)

    def upsert_pokemon(self, *, pokemon_data: PokemonData) -> None:
        """Insert or update Pokémon data in the database.

        Args:
            pokemon_data: The PokemonData object to store.
        """
        types_json = json.dumps([ptype.value for ptype in pokemon_data.types])

        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO pokemon_data (
                    id, name, types_json, base_attack, base_defense, base_stamina,
                    cp_level_20, cp_level_25, cp_level_30, cp_level_40, max_cp,
                    buddy_distance, candy_to_evolve, is_shiny_available,
                    is_released, rarity, form, base_stardust, data_source,
                    created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    COALESCE((SELECT created_at FROM pokemon_data WHERE id = ?), CURRENT_TIMESTAMP),
                    CURRENT_TIMESTAMP
                )
            """,
                (
                    pokemon_data.id,
                    pokemon_data.name,
                    types_json,
                    pokemon_data.base_attack,
                    pokemon_data.base_defense,
                    pokemon_data.base_stamina,
                    pokemon_data.cp_level_20,
                    pokemon_data.cp_level_25,
                    pokemon_data.cp_level_30,
                    pokemon_data.cp_level_40,
                    pokemon_data.max_cp,
                    pokemon_data.buddy_distance,
                    pokemon_data.candy_to_evolve,
                    pokemon_data.is_shiny_available,
                    pokemon_data.is_released,
                    pokemon_data.rarity,
                    pokemon_data.form,
                    pokemon_data.base_stardust,
                    "pogoapi.net",
                    pokemon_data.id,  # For the COALESCE subquery
                ),
            )
            conn.commit()

    def search_pokemon_by_name(self, *, partial_name: str, limit: int = 10) -> list[PokemonData]:
        """Search for Pokémon by partial name match.

        Args:
            partial_name: Partial name to search for.
            limit: Maximum number of results to return.

        Returns:
            List of matching PokemonData objects.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM pokemon_data
                WHERE name LIKE ?
                ORDER BY name
                LIMIT ?
            """,
                (f"%{partial_name}%", limit),
            )

            rows = cursor.fetchall()
            return [self._row_to_pokemon_data(row=row) for row in rows]

    def get_all_pokemon(self, *, limit: int | None = None) -> list[PokemonData]:
        """Get all Pokémon from the database.

        Args:
            limit: Optional limit on number of results.

        Returns:
            List of all PokemonData objects.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            conn.row_factory = sqlite3.Row

            if limit:
                cursor = conn.execute("SELECT * FROM pokemon_data ORDER BY id LIMIT ?", (limit,))
            else:
                cursor = conn.execute("SELECT * FROM pokemon_data ORDER BY id")

            rows = cursor.fetchall()
            return [self._row_to_pokemon_data(row=row) for row in rows]

    def get_database_stats(self) -> dict[str, Any]:
        """Get statistics about the database.

        Returns:
            Dictionary with database statistics.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            # Get total count
            cursor = conn.execute("SELECT COUNT(*) FROM pokemon_data")
            total_count = cursor.fetchone()[0]

            # Get most recent update
            cursor = conn.execute("SELECT MAX(updated_at) FROM pokemon_data")
            last_updated = cursor.fetchone()[0]

            # Get database file size
            db_size = self.config.db_path.stat().st_size if self.config.db_path.exists() else 0

            return {
                "total_pokemon": total_count,
                "last_updated": last_updated,
                "database_size_bytes": db_size,
                "database_path": str(self.config.db_path),
            }

    def _row_to_pokemon_data(self, *, row: sqlite3.Row) -> PokemonData:
        """Convert a database row to a PokemonData object.

        Args:
            row: SQLite row object.

        Returns:
            PokemonData object.
        """
        from pokemon_meetup.common.pokemon_types import PokemonType

        # Parse types from JSON
        types_data = json.loads(row["types_json"])
        types = []
        for type_str in types_data:
            try:
                types.append(PokemonType(type_str))
            except ValueError:
                # Skip unknown types
                continue

        return PokemonData(
            name=row["name"],
            id=row["id"],
            types=types,
            base_attack=row["base_attack"],
            base_defense=row["base_defense"],
            base_stamina=row["base_stamina"],
            cp_level_20=row["cp_level_20"],
            cp_level_25=row["cp_level_25"],
            cp_level_30=row["cp_level_30"],
            cp_level_40=row["cp_level_40"],
            max_cp=row["max_cp"],
            buddy_distance=row["buddy_distance"],
            candy_to_evolve=row["candy_to_evolve"],
            is_shiny_available=bool(row["is_shiny_available"]),
            is_released=bool(row["is_released"]),
            rarity=row["rarity"],
            form=row["form"],
            base_stardust=row["base_stardust"],
        )

    def update_pokemon_fields(
        self, *, pokemon_id: int, is_shiny_available: bool | None = None, base_stardust: int | None = None
    ) -> bool:
        """Update specific fields for a Pokémon in the database.

        Args:
            pokemon_id: The Pokémon ID to update.
            is_shiny_available: New shiny availability status if provided.
            base_stardust: New base stardust amount if provided.

        Returns:
            True if the Pokémon was updated, False if not found.
        """
        if is_shiny_available is None and base_stardust is None:
            return False  # Nothing to update

        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            # Check if Pokémon exists
            cursor = conn.execute("SELECT 1 FROM pokemon_data WHERE id = ?", (pokemon_id,))
            if not cursor.fetchone():
                return False

            # Build dynamic update query
            update_clauses = []
            update_values: list[bool | int] = []

            if is_shiny_available is not None:
                update_clauses.append("is_shiny_available = ?")
                update_values.append(is_shiny_available)

            if base_stardust is not None:
                update_clauses.append("base_stardust = ?")
                update_values.append(base_stardust)

            # Always update the timestamp
            update_clauses.append("updated_at = CURRENT_TIMESTAMP")

            # Add pokemon_id for WHERE clause
            update_values.append(pokemon_id)

            # Build the query using proper parameterized approach
            set_clause = ", ".join(update_clauses)
            query = "UPDATE pokemon_data SET " + set_clause + " WHERE id = ?"  # noqa: S608

            conn.execute(query, update_values)
            conn.commit()
            return True

    def upsert_evolution_data(self, *, evolution_data: EvolutionData) -> None:
        """Insert or update evolution data in the database.

        Args:
            evolution_data: The EvolutionData object to store.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            # First, delete existing evolution data for this Pokémon
            conn.execute("DELETE FROM pokemon_evolutions WHERE from_pokemon_id = ?", (evolution_data.pokemon_id,))

            # Insert new evolution data
            if evolution_data.evolutions:
                for evolution in evolution_data.evolutions:
                    conn.execute(
                        """
                        INSERT INTO pokemon_evolutions (
                            from_pokemon_id, to_pokemon_id, to_pokemon_name, candy_required,
                            item_required, lure_required, no_candy_cost_if_traded, priority,
                            only_evolves_in_daytime, only_evolves_in_nighttime,
                            must_be_buddy_to_evolve, buddy_distance_required, gender_required
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            evolution_data.pokemon_id,
                            evolution.pokemon_id,
                            evolution.pokemon_name,
                            evolution.candy_required,
                            evolution.item_required,
                            evolution.lure_required,
                            evolution.no_candy_cost_if_traded,
                            evolution.priority,
                            evolution.only_evolves_in_daytime,
                            evolution.only_evolves_in_nighttime,
                            evolution.must_be_buddy_to_evolve,
                            evolution.buddy_distance_required,
                            evolution.gender_required,
                        ),
                    )
            conn.commit()

    def upsert_mega_evolution_data(self, *, mega_data: list[MegaEvolutionData]) -> None:
        """Insert or update mega evolution data in the database.

        Args:
            mega_data: List of MegaEvolutionData objects to store.
        """
        if not mega_data:
            return

        pokemon_id = mega_data[0].pokemon_id

        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            # First, delete existing mega evolution data for this Pokémon
            conn.execute("DELETE FROM mega_evolutions WHERE pokemon_id = ?", (pokemon_id,))

            # Insert new mega evolution data
            for mega in mega_data:
                types_json = json.dumps([ptype.value for ptype in mega.types])

                conn.execute(
                    """
                    INSERT INTO mega_evolutions (
                        pokemon_id, pokemon_name, form, mega_name,
                        first_time_mega_energy_required, mega_energy_required,
                        base_attack, base_defense, base_stamina, types_json,
                        cp_multiplier_override
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        mega.pokemon_id,
                        mega.pokemon_name,
                        mega.form,
                        mega.mega_name,
                        mega.first_time_mega_energy_required,
                        mega.mega_energy_required,
                        mega.base_attack,
                        mega.base_defense,
                        mega.base_stamina,
                        types_json,
                        mega.cp_multiplier_override,
                    ),
                )
            conn.commit()

    def get_evolution_data(self, *, pokemon_id: int) -> EvolutionData | None:
        """Get evolution data for a specific Pokémon.

        Args:
            pokemon_id: The Pokémon ID to get evolution data for.

        Returns:
            EvolutionData object if found, None otherwise.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            conn.row_factory = sqlite3.Row

            # Get the Pokémon name first
            pokemon_cursor = conn.execute("SELECT name FROM pokemon_data WHERE id = ?", (pokemon_id,))
            pokemon_row = pokemon_cursor.fetchone()
            if not pokemon_row:
                return None

            # Get evolution data
            cursor = conn.execute(
                """
                SELECT * FROM pokemon_evolutions
                WHERE from_pokemon_id = ?
                ORDER BY priority DESC, to_pokemon_name
            """,
                (pokemon_id,),
            )

            rows = cursor.fetchall()
            if not rows:
                return None

            # Convert to EvolutionData
            from pokemon_meetup.web.pokemon_api import EvolutionRequirement

            evolutions = []
            for row in rows:
                requirement = EvolutionRequirement(
                    pokemon_id=row["to_pokemon_id"],
                    pokemon_name=row["to_pokemon_name"],
                    candy_required=row["candy_required"],
                    item_required=row["item_required"],
                    lure_required=row["lure_required"],
                    no_candy_cost_if_traded=bool(row["no_candy_cost_if_traded"]),
                    priority=row["priority"],
                    only_evolves_in_daytime=bool(row["only_evolves_in_daytime"]),
                    only_evolves_in_nighttime=bool(row["only_evolves_in_nighttime"]),
                    must_be_buddy_to_evolve=bool(row["must_be_buddy_to_evolve"]),
                    buddy_distance_required=row["buddy_distance_required"],
                    gender_required=row["gender_required"],
                )
                evolutions.append(requirement)

            return EvolutionData(pokemon_id=pokemon_id, pokemon_name=pokemon_row["name"], evolutions=evolutions)

    def get_mega_evolution_data(self, *, pokemon_id: int) -> list[MegaEvolutionData]:
        """Get mega evolution data for a specific Pokémon.

        Args:
            pokemon_id: The Pokémon ID to get mega evolution data for.

        Returns:
            List of MegaEvolutionData objects.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM mega_evolutions
                WHERE pokemon_id = ?
                ORDER BY form
            """,
                (pokemon_id,),
            )

            rows = cursor.fetchall()
            result = []

            for row in rows:
                # Parse types from JSON
                from pokemon_meetup.common.pokemon_types import PokemonType

                types_data = json.loads(row["types_json"])
                types = []
                for type_str in types_data:
                    try:
                        types.append(PokemonType(type_str))
                    except ValueError:
                        continue

                mega = MegaEvolutionData(
                    pokemon_id=row["pokemon_id"],
                    pokemon_name=row["pokemon_name"],
                    form=row["form"],
                    mega_name=row["mega_name"],
                    first_time_mega_energy_required=row["first_time_mega_energy_required"],
                    mega_energy_required=row["mega_energy_required"],
                    base_attack=row["base_attack"],
                    base_defense=row["base_defense"],
                    base_stamina=row["base_stamina"],
                    types=types,
                    cp_multiplier_override=row["cp_multiplier_override"],
                )
                result.append(mega)

            return result

    def check_evolution_line_has_mega(self, *, pokemon_id: int) -> bool:
        """Check if a Pokémon's evolution line includes any mega evolutions.

        Args:
            pokemon_id: The Pokémon ID to check.

        Returns:
            True if any Pokémon in the evolution line can mega evolve.
        """
        with sqlite3.connect(self.config.db_path, timeout=self.config.timeout) as conn:
            # Check if this Pokémon can mega evolve
            cursor = conn.execute("SELECT COUNT(*) FROM mega_evolutions WHERE pokemon_id = ?", (pokemon_id,))
            if cursor.fetchone()[0] > 0:
                return True

            # Check if any of its evolutions can mega evolve
            cursor = conn.execute(
                """
                SELECT DISTINCT to_pokemon_id FROM pokemon_evolutions
                WHERE from_pokemon_id = ?
            """,
                (pokemon_id,),
            )

            for row in cursor.fetchall():
                evolution_id = row[0]
                evolution_cursor = conn.execute(
                    "SELECT COUNT(*) FROM mega_evolutions WHERE pokemon_id = ?", (evolution_id,)
                )
                if evolution_cursor.fetchone()[0] > 0:
                    return True

            return False


def get_default_database() -> PokemonDatabase:
    """Get the default database instance.

    Returns:
        PokemonDatabase instance with default configuration.
    """
    # Database will be stored in the project root under data/
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "pokemon.db"

    config = DatabaseConfig(db_path=db_path)
    return PokemonDatabase(config=config)
