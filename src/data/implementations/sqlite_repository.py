# /home/jdennis/Projects/JennAI/src/data/implementations/sqlite_repository.py

import sqlite3
import sys
from pathlib import Path
from typing import TypeVar, Generic, List, Optional, Any, Dict

# --- Root Project Path Setup ---
jennai_root_for_path = Path(__file__).resolve().parent.parent.parent.parent
if str(jennai_root_for_path) not in sys.path:
    sys.path.insert(0, str(jennai_root_for_path))

from src.data.interfaces.ICrudRepository import ICrudRepository
from config.loguru_setup import logger # Assuming logger is configured via setup_logging

# Define a TypeVar for the entity type
T = TypeVar('T')

class SQLiteRepository(ICrudRepository[T], Generic[T]):
    """
    A generic SQLite repository implementation for CRUD operations.
    
    This class provides a basic framework. For specific entities, you might need to:
    - Ensure the entity type T can be easily converted to/from a dictionary 
      (e.g., it's a dataclass, Pydantic model, or has a __dict__ attribute).
    - Override _entity_to_dict and _row_to_entity for custom mapping if necessary.
    - Ensure the database table is created with a schema that matches the entity.
    """

    def __init__(self, db_path: str, table_name: str, pk_column: str = "id"):
        """
        Initializes the SQLiteRepository.

        Args:
            db_path: Path to the SQLite database file.
            table_name: Name of the table this repository will manage.
            pk_column: Name of the primary key column in the table (default is "id").
        """
        self.db_path = Path(db_path)
        self.table_name = table_name
        self.pk_column = pk_column
        self._ensure_db_directory()
        logger.info(f"SQLiteRepository initialized for table '{self.table_name}' with DB: {self.db_path}")

    def _ensure_db_directory(self):
        """Ensures the directory for the SQLite DB file exists."""
        db_dir = self.db_path.parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")

    def _get_connection(self) -> sqlite3.Connection:
        """Establishes and returns a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Access columns by name
        return conn

    def _entity_to_dict(self, item: T) -> Dict[str, Any]:
        """
        Converts an entity T to a dictionary for database insertion/update.
        Assumes T is a dict, has a __dict__ attribute, or this method is overridden.
        """
        if isinstance(item, dict):
            return item
        if hasattr(item, '__dict__'):
            return vars(item)
        logger.error(f"Cannot convert item of type {type(item)} to dict for table {self.table_name}. Implement _entity_to_dict or ensure T is suitable.")
        raise TypeError(f"Item of type {type(item)} cannot be automatically converted to dict.")

    def _row_to_entity(self, row: sqlite3.Row) -> T:
        """
        Converts a database row (sqlite3.Row) to an entity T.
        Currently returns a dictionary. Subclasses should override this for specific
        entity types (e.g., to instantiate a dataclass or Pydantic model).
        """
        # For a generic implementation, returning a dict is the most straightforward.
        # If T is expected to be a specific class, this method MUST be overridden.
        # Example for a class T: return T(**dict(row))
        return dict(row) # type: ignore 

    def create(self, item: T) -> T:
        data = self._entity_to_dict(item)
        # Exclude PK if it's typically auto-generated and might be None or 0 in input
        # Or ensure it's not part of the insert if it's auto-incrementing
        columns_to_insert = {k: v for k, v in data.items() if k != self.pk_column or v is not None}

        columns = ', '.join(columns_to_insert.keys())
        placeholders = ', '.join(['?'] * len(columns_to_insert))
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(sql, list(columns_to_insert.values()))
                item_id = cursor.lastrowid
                
                # Update the item with the generated ID if possible
                if hasattr(item, self.pk_column):
                    setattr(item, self.pk_column, item_id)
                elif isinstance(item, dict):
                    item[self.pk_column] = item_id # type: ignore

                logger.success(f"Created item in '{self.table_name}' with {self.pk_column}: {item_id}")
                # For a more robust return, one might fetch the item: return self.read_by_id(item_id)
                return item 
        except sqlite3.Error as e:
            logger.error(f"Error creating item in '{self.table_name}': {e} (SQL: {sql}, Data: {columns_to_insert})")
            raise
        finally:
            conn.close()

    def read_by_id(self, item_id: Any) -> Optional[T]:
        sql = f"SELECT * FROM {self.table_name} WHERE {self.pk_column} = ?"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (item_id,))
            row = cursor.fetchone()
            if row:
                logger.debug(f"Read item with {self.pk_column} {item_id} from '{self.table_name}'")
                return self._row_to_entity(row)
            logger.debug(f"No item found with {self.pk_column} {item_id} in '{self.table_name}'")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error reading item {self.pk_column} {item_id} from '{self.table_name}': {e}")
            raise
        finally:
            conn.close()

    def read_all(self) -> List[T]:
        sql = f"SELECT * FROM {self.table_name}"
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            logger.debug(f"Read {len(rows)} items from '{self.table_name}'")
            return [self._row_to_entity(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error reading all items from '{self.table_name}': {e}")
            raise
        finally:
            conn.close()

    def update(self, item: T) -> Optional[T]:
        data = self._entity_to_dict(item)
        item_id = data.pop(self.pk_column, None) 
        if item_id is None:
            msg = f"Primary key '{self.pk_column}' not found in item or is None for update in table '{self.table_name}'."
            logger.error(msg)
            raise ValueError(msg)

        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        if not set_clause: # Nothing to update
            logger.warning(f"No fields to update for item ID {item_id} in '{self.table_name}'. Returning item as is.")
            # Consider if this should return item or None if no actual update query is run.
            return self.read_by_id(item_id) # Or return item if that's preferred for "no fields to update"
            
        sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.pk_column} = ?"
        values = list(data.values()) + [item_id]
        
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                if cursor.rowcount == 0:
                    logger.warning(f"No item found with {self.pk_column} {item_id} to update in '{self.table_name}'. Update had no effect.")
                    return None # Indicate that the item was not found/updated
                else:
                    logger.success(f"Updated item with {self.pk_column} {item_id} in '{self.table_name}'")
            # Return the updated item, potentially by re-reading it to get DB-generated values
            return self.read_by_id(item_id) # This ensures consistency
        except sqlite3.Error as e:
            logger.error(f"Error updating item {self.pk_column} {item_id} in '{self.table_name}': {e}")
            raise
        finally:
            conn.close()

    def delete(self, item_id: Any) -> None:
        sql = f"DELETE FROM {self.table_name} WHERE {self.pk_column} = ?"
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(sql, (item_id,))
                if cursor.rowcount == 0:
                    logger.warning(f"No item found with {self.pk_column} {item_id} to delete in '{self.table_name}'. Delete had no effect.")
                else:
                    logger.success(f"Deleted item with {self.pk_column} {item_id} from '{self.table_name}'")
        except sqlite3.Error as e:
            logger.error(f"Error deleting item {self.pk_column} {item_id} from '{self.table_name}': {e}")
            raise
        finally:
            conn.close()

    # Example utility: create table (should be part of a migration/setup process)
    def _create_table_if_not_exists(self, create_table_sql: str):
        conn = self._get_connection()
        try:
            with conn:
                logger.info(f"Attempting to create table '{self.table_name}' if not exists...")
                conn.execute(create_table_sql)
                logger.success(f"Table '{self.table_name}' ensured.")
        except sqlite3.Error as e:
            logger.error(f"Error creating table '{self.table_name}': {e}")
        finally:
            conn.close()
