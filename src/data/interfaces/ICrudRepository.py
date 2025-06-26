from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any

# Define a TypeVar for the entity type the repository operates on
T = TypeVar('T')

class ICrudRepository(ABC, Generic[T]):
    """
    Interface (Abstract Base Class) for basic CRUD (Create, Read, Update, Delete)
    operations on an entity type T.

    This interface defines the contract that any concrete repository implementation
    (e.g., a database repository, an API repository) must adhere to.
    """

    @abstractmethod
    def create(self, item: T) -> T:
        """
        Creates a new item in the repository.

        Args:
            item: The item to create.

        Returns:
            The created item, potentially with updated information (e.g., ID).

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def read_by_id(self, item_id: Any) -> Optional[T]:
        """
        Reads an item from the repository by its unique identifier.

        Args:
            item_id: The unique identifier of the item. Use a more specific type
                     than Any in concrete implementations if possible.

        Returns:
            The item if found, otherwise None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def read_all(self) -> List[T]:
        """
        Reads all items from the repository.

        Returns:
            A list of all items.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, item: T) -> T:
        """
        Updates an existing item in the repository.

        Args:
            item: The item with updated information.

        Returns:
            The updated item.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: Any) -> None:
        """
        Deletes an item from the repository by its unique identifier.

        Args:
            item_id: The unique identifier of the item to delete. Use a more
                     specific type than Any in concrete implementations if possible.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError