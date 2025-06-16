# C:\Users\jarde\Projects\JennAI\core\dependency_container.py

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
    """
    def __init__(self):
        self._registrations: Dict[Type, Any] = {} 
        self._singletons: Dict[Type, Any] = {} 
        logger.debug("DEBUG - DependencyContainer initialized.")

    def register(self, abstraction: Type[I], concrete_impl: Union[Type[I], Callable[..., I]]): 
        """
        Registers a concrete implementation or a factory function for an abstraction.
        """
        if get_origin(abstraction):
            key = (get_origin(abstraction), get_args(abstraction))
        else:
            key = abstraction

        self._registrations[key] = concrete_impl
        logger.debug(f"DEBUG - Registered {concrete_impl.__name__ if hasattr(concrete_impl, '__name__') else str(concrete_impl)} for {str(abstraction)}.")

    def resolve(self, abstraction: Type[I]) -> I:
        """
        Resolves an instance of the requested abstraction, injecting its dependencies.
        """
        if get_origin(abstraction):
            key = (get_origin(abstraction), get_args(abstraction))
        else:
            key = abstraction

        if key not in self._registrations:
            logger.error(f"ERROR - No implementation registered for abstraction: {str(abstraction)}.")
            raise ValueError(f"No implementation registered for abstraction: {str(abstraction)}")

        concrete_impl_or_factory = self._registrations[key]

        if callable(concrete_impl_or_factory) and not inspect.isclass(concrete_impl_or_factory):
            logger.debug(f"DEBUG - Resolving {str(abstraction)} using a factory function.")
            return concrete_impl_or_factory()

        concrete_class = concrete_impl_or_factory

        if concrete_class in self._singletons:
            logger.debug(f"DEBUG - Resolving singleton instance for {concrete_class.__name__}.")
            return self._singletons[concrete_class]

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
                dependencies[name] = self.resolve(param.annotation)

        instance = concrete_class(**dependencies)
        logger.debug(f"DEBUG - Instantiated {concrete_class.__name__}.")
        return instance