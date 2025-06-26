import inspect
from typing import Type, TypeVar, Dict, Callable, Any, Union, get_origin, get_args
from loguru import logger

# Define a TypeVar for the interface type for cleaner type hinting
I = TypeVar('I')

class DependencyContainer:
    """
    A simple Inversion of Control (IoC) container for dependency injection.
    Allows registering concrete implementations for interfaces/abstractions,
    and resolving instances with their dependencies automatically.
    Supports singletons and pre-registered instances.
    """
    def __init__(self):
        self._registrations: Dict[Any, Any] = {} # Key can be Type or (Origin, Args)
        self._singletons: Dict[Any, Any] = {}    # Stores instantiated singletons (keyed by abstraction key)
        logger.debug("DEBUG - DependencyContainer initialized.")

    def _get_key(self, abstraction: Type[I]) -> Any:
        """Internal helper to get the key for registration/resolution, handling generics."""
        if get_origin(abstraction):
            return (get_origin(abstraction), get_args(abstraction))
        return abstraction

    def register(self, abstraction: Type[I], concrete_impl: Union[Type[I], Callable[..., I]]):
        """
        Registers a concrete implementation class or a factory function for an abstraction.
        Instances will be new on each resolve (transient lifecycle), unless registered as singleton.
        """
        key = self._get_key(abstraction)
        self._registrations[key] = concrete_impl
        logger.debug(f"DEBUG - Registered {concrete_impl.__name__ if hasattr(concrete_impl, '__name__') else str(concrete_impl)} for {str(abstraction)} as transient.")

    def register_singleton(self, abstraction: Type[I], concrete_impl: Union[Type[I], Callable[..., I]] = None):
        """
        Registers a concrete implementation or a factory function for an abstraction as a singleton.
        The instance will be created on the first resolve and reused for subsequent resolves.
        If concrete_impl is None, assumes abstraction is also the concrete implementation.
        """
        key = self._get_key(abstraction)
        if concrete_impl is None:
            concrete_impl = abstraction # Assume abstraction is also the concrete class

        self._registrations[key] = concrete_impl
        # If it's a direct instance, store it immediately. Otherwise, it's lazy.
        if not inspect.isclass(concrete_impl) and not callable(concrete_impl):
            self._singletons[key] = concrete_impl
            logger.debug(f"DEBUG - Registered {str(concrete_impl)} for {str(abstraction)} as singleton (instance).")
        else:
            # Mark it as a singleton registration for lazy instantiation
            self._registrations[key] = {'type': 'singleton', 'impl': concrete_impl}
            logger.debug(f"DEBUG - Registered {concrete_impl.__name__ if hasattr(concrete_impl, '__name__') else str(concrete_impl)} for {str(abstraction)} as singleton (lazy).")

    def register_instance(self, abstraction: Type[I], instance: I):
        """
        Registers a pre-existing instance for an abstraction. This instance will always be returned.
        """
        key = self._get_key(abstraction)
        self._registrations[key] = instance
        self._singletons[key] = instance # Treat pre-registered instance as a singleton
        logger.debug(f"DEBUG - Registered pre-existing instance {str(instance)} for {str(abstraction)}.")

    def resolve(self, abstraction: Type[I]) -> I:
        """
        Resolves an instance of the requested abstraction, injecting its dependencies.
        """
        key = self._get_key(abstraction)

        # 1. Check if it's already a resolved singleton instance
        if key in self._singletons:
            logger.debug(f"DEBUG - Resolving existing singleton for {str(abstraction)}.")
            return self._singletons[key]

        # 2. Look up registration
        if key not in self._registrations:
            logger.error(f"ERROR - No implementation registered for abstraction: {str(abstraction)}.")
            raise ValueError(f"No implementation registered for abstraction: {str(abstraction)}")

        registration_entry = self._registrations[key]

        # 3. Handle singleton registration (lazy instantiation)
        is_singleton_registration = isinstance(registration_entry, dict) and registration_entry.get('type') == 'singleton'
        concrete_impl_or_factory = registration_entry['impl'] if is_singleton_registration else registration_entry

        # 4. Handle factory function
        if callable(concrete_impl_or_factory) and not inspect.isclass(concrete_impl_or_factory):
            logger.debug(f"DEBUG - Resolving {str(abstraction)} using a factory function.")
            instance = concrete_impl_or_factory()
            if is_singleton_registration: # Store result if it was marked as a singleton factory
                self._singletons[key] = instance
                logger.debug(f"DEBUG - Stored factory-resolved instance for singleton {str(abstraction)}.")
            return instance

        # 5. Handle concrete class (auto-inject dependencies)
        concrete_class = concrete_impl_or_factory
        signature = inspect.signature(concrete_class.__init__)
        dependencies = {}

        for name, param in signature.parameters.items():
            if name == 'self':
                continue

            if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD or \
               param.kind == inspect.Parameter.KEYWORD_ONLY:

                if param.annotation == inspect.Parameter.empty:
                    logger.warning(f"WARNING - Parameter '{name}' in {concrete_class.__name__}.__init__ has no type hint. Cannot auto-resolve.")
                    continue

                logger.debug(f"DEBUG - Resolving dependency '{name}' of type {str(param.annotation)} for {concrete_class.__name__}.")
                dependencies[name] = self.resolve(param.annotation) # Recursive resolution

        instance = concrete_class(**dependencies)
        logger.debug(f"DEBUG - Instantiated {concrete_class.__name__}.")

        if is_singleton_registration: # Store newly created instance if marked as singleton class
            self._singletons[key] = instance
            logger.debug(f"DEBUG - Stored newly created instance for singleton {str(abstraction)}.")

        return instance

    def reset(self):
        """Clears all registrations and singletons."""
        self._registrations.clear()
        self._singletons.clear()
        logger.debug("DEBUG - DependencyContainer reset.")
