from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

# For type hinting, you might define a UserDTO or User model elsewhere,
# for now, we'll use Dict[str, Any] as a placeholder for user data.
UserDataType = Dict[str, Any]

class IUserManager(ABC):
    """
    Interface (Abstract Base Class) for user management services.
    Defines the contract for operations related to user accounts,
    authentication, and profiles.
    """

    @abstractmethod
    def create_user(self, user_data: UserDataType) -> UserDataType:
        """
        Creates a new user.

        Args:
            user_data: A dictionary containing the new user's information.

        Returns:
            A dictionary representing the created user, possibly with an assigned ID.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_by_id(self, user_id: Any) -> Optional[UserDataType]:
        """
        Retrieves a user by their unique identifier.

        Args:
            user_id: The unique ID of the user.

        Returns:
            A dictionary representing the user if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[UserDataType]:
        """
        Retrieves a user by their email address.

        Args:
            email: The email address of the user.

        Returns:
            A dictionary representing the user if found, otherwise None.
        """
        raise NotImplementedError

    # You can add more methods like update_user, delete_user, authenticate_user, etc.