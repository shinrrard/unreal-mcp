"""
Base Command class for Unreal MCP Server.

Provides automatic type generation from class names and JSON serialization
for command objects sent to Unreal Engine.
"""

import json
import re
import warnings
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, Type


@dataclass
class BaseCommand:
    """
    Base class for all Unreal Engine commands.
    
    This class provides automatic command type generation from class names and JSON 
    serialization capabilities for communication with Unreal Engine via MCP protocol.
    
    Features:
        - Automatic type generation: Class names are converted to snake_case command types
        - JSON serialization: Commands can be serialized to JSON format expected by Unreal
        - Type safety: Full typing support with generic type parameters
        - Extensibility: Easy to create new command types by inheritance
    
    Class Name Conversion Rules:
        - CamelCase is converted to snake_case
        - 'Command' suffix is automatically removed
        - Examples:
            * CreateBlueprintCommand -> "create_blueprint"
            * AddComponentToBlueprintCommand -> "add_component_to_blueprint"
            * SetStaticMeshPropertiesCommand -> "set_static_mesh_properties"
    
    Attributes:
        params (Dict[str, Any]): Dictionary containing command parameters that will be 
            sent to Unreal Engine. This is automatically populated by subclasses in 
            their __post_init__ method.
    
    Properties:
        type (str): Automatically generated command type based on class name
    
    Methods:
        to_dict() -> Dict[str, Any]: Convert command to dictionary format
        to_json() -> str: Convert command to JSON string format
    
    Usage Examples:
        Basic usage with inheritance:
        ```python
        @dataclass
        class CreateBlueprintCommand(BaseCommand):
            blueprint_name: str = ""
            parent_class: str = "/Script/Engine.Actor"
            
            def __post_init__(self):
                super().__post_init__()
                self.params.update({
                    "blueprint_name": self.blueprint_name,
                    "parent_class": self.parent_class
                })
        
        # Create and use command
        cmd = CreateBlueprintCommand(name="MyBlueprint")
        print(cmd.type)      # "create_blueprint"
        print(cmd.to_json()) # {"type": "create_blueprint", "params": {...}}
        ```
        
        Direct usage (for generic commands):
        ```python
        cmd = BaseCommand()
        cmd.params["custom_param"] = "value"
        print(cmd.type)      # "base"
        print(cmd.to_dict()) # {"type": "base", "params": {"custom_param": "value"}}
        ```
    
    Notes:
        - While BaseCommand can be instantiated directly, it's recommended to create
          specific command classes for better type safety and IDE support
        - All command parameters should be JSON-serializable
        - The params dictionary is copied when calling to_dict() to prevent external modification
    """
    
    params: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def type(self) -> str:
        """
        Automatically generate command type from class name.
        
        Converts CamelCase class names to snake_case command types.
        Removes the 'Command' suffix if present.
        
        Examples:
            AddComponentToBlueprintCommand -> "add_component_to_blueprint"
            CreateBlueprintCommand -> "create_blueprint"
            SpawnActorCommand -> "spawn_actor"
            GetViewportInfoCommand -> "get_viewport_info"
            
        Returns:
            str: The snake_case command type
        """
        class_name = self.__class__.__name__
        
        # Remove 'Command' suffix if present
        if class_name.endswith('Command'):
            class_name = class_name[:-7]  # Remove 'Command' (7 characters)
        
        # Convert CamelCase to snake_case
        # Insert underscore before uppercase letters (except at the beginning)
        snake_case = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_case)
        
        return snake_case.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the command to a dictionary compatible with Unreal Engine protocol.
        
        Returns a dictionary in the format expected by Unreal Engine:
        {
            "type": "command_name",
            "params": {
                "param1": "value1",
                "param2": "value2"
            }
        }
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command
        """
        return {
            "type": self.type,
            "params": self.params.copy()  # Return a copy to prevent external modification
        }
    
    def to_json(self) -> str:
        """
        Convert the command to a JSON string.
        
        Returns:
            str: JSON string representation of the command
        """
        return json.dumps(self.to_dict())
    
    def validate(self) -> bool:
        """
        Validate the command parameters.
        
        This method can be overridden by subclasses to implement specific
        validation logic. The base implementation performs basic validation.
        
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            ValueError: If critical validation errors are found
            
        Example:
            ```python
            @dataclass
            class CreateBlueprintCommand(BaseCommand):
                blueprint_name: str = ""
                
                def validate(self) -> bool:
                    if not self.blueprint_name.strip():
                        raise ValueError("blueprint_name cannot be empty")
                    return super().validate()
            ```
        """
        # Validate params is a dictionary
        if not isinstance(self.params, dict):
            raise ValueError(f"params must be a dictionary, got {type(self.params)}")
        
        # Check for potentially problematic values
        self._check_for_circular_references()
        self._validate_json_serializable()
        
        return True
    
    def _check_for_circular_references(self) -> None:
        """Check for circular references in params that could cause JSON serialization issues."""
        try:
            json.dumps(self.params)
        except ValueError as e:
            if "circular reference" in str(e).lower():
                raise ValueError("Circular reference detected in command parameters") from e
    
    def _validate_json_serializable(self) -> None:
        """Validate that all params are JSON serializable."""
        try:
            json.dumps(self.params)
        except TypeError as e:
            raise ValueError(f"Command parameters are not JSON serializable: {e}") from e
        except ValueError as e:
            # Only re-raise ValueError if it's not a circular reference (handled elsewhere)
            if "circular reference" not in str(e).lower():
                raise ValueError(f"Command parameters are not JSON serializable: {e}") from e
    
    def __repr__(self) -> str:
        """
        Return a string representation of the command.
        
        This method provides a safe representation that avoids circular references
        and limits the output size to prevent overwhelming displays.
        
        Returns:
            str: String representation of the command
        """
        class_name = self.__class__.__name__
        
        # Safely represent params (limit size to prevent huge output)
        try:
            params_str = str(self.params)
            if len(params_str) > 100:
                params_str = params_str[:97] + "..."
        except Exception:
            params_str = "<unprintable params>"
        
        return f"{class_name}(type='{self.type}', params={params_str})"
    
    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        return f"{self.type} command with {len(self.params)} parameters"
    
    def copy(self) -> 'BaseCommand':
        """
        Create a deep copy of the command.
        
        Returns:
            BaseCommand: A new command instance with copied parameters
        """
        import copy
        
        # Get all current field values
        field_values = {}
        for field_name, field_value in self.__dict__.items():
            if not field_name.startswith('_'):
                field_values[field_name] = copy.deepcopy(field_value)
        
        # Create new instance with same field values
        new_cmd = self.__class__(**{k: v for k, v in field_values.items() if k != 'params'})
        new_cmd.params = field_values.get('params', {})
        
        return new_cmd
    
    def __post_init__(self):
        """
        Initialize the command after dataclass initialization.
        
        This method is called automatically after the dataclass fields are set.
        Subclasses should override this method to populate the params dictionary
        with their specific field values, then call super().__post_init__().
        
        Raises:
            ValueError: If validation fails during initialization
        """
        # Ensure params is always a dictionary
        if not isinstance(self.params, dict):
            self.params = {}
        
        # Perform automatic validation (can be disabled by setting _skip_validation)
        if not getattr(self, '_skip_validation', False):
            try:
                self.validate()
            except ValueError as e:
                # Add context about which command failed
                raise ValueError(f"{self.__class__.__name__} validation failed: {e}") from e