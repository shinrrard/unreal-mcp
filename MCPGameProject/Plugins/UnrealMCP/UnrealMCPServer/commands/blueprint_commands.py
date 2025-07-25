"""
Blueprint-related command classes for Unreal MCP Server.

This module contains command classes for creating and manipulating Blueprint assets 
in Unreal Engine. All classes inherit from BaseCommand and provide type-safe 
interfaces for Blueprint operations.

Available Commands:
    - CreateBlueprintCommand: Create new Blueprint classes
    - AddComponentToBlueprintCommand: Add components to existing Blueprints
    - CompileBlueprintCommand: Compile Blueprint classes
    - SetBlueprintPropertyCommand: Set properties on Blueprints
    - SetStaticMeshPropertiesCommand: Configure StaticMesh component properties

Example Usage:
    ```python
    from commands import CreateBlueprintCommand, AddComponentToBlueprintCommand
    
    # Create a new Blueprint
    create_cmd = CreateBlueprintCommand(
        name="PlayerCharacter",
        parent_class="/Script/Engine.Character"
    )
    
    # Add a mesh component
    add_mesh_cmd = AddComponentToBlueprintCommand(
        blueprint_name="PlayerCharacter",
        component_type="SkeletalMeshComponent",
        component_name="CharacterMesh"
    )
    ```
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Union
from .base_command import BaseCommand


@dataclass
class CreateBlueprintCommand(BaseCommand):
    """
    Command to create a new Blueprint class in Unreal Engine.
    
    Attributes:
        name: Name of the Blueprint to create
        parent_class: Parent class for the Blueprint (default: Actor)
    
    Example:
        ```python
        cmd = CreateBlueprintCommand(
            name="MyActor",
            parent_class="/Script/Engine.Pawn"
        )
        print(cmd.type)  # "create_blueprint"
        print(cmd.to_json())  # {"type": "create_blueprint", "params": {...}}
        ```
    """
    name: str = ""
    parent_class: str = "/Script/Engine.Actor"
    
    def __post_init__(self):
        # Update params first, then call super() for validation
        self.params.update({
            "name": self.name,
            "parent_class": self.parent_class
        })
        super().__post_init__()
    
    def validate(self) -> bool:
        """Validate CreateBlueprint command parameters."""
        if not self.name.strip():
            raise ValueError("name cannot be empty")
        
        if not self.parent_class.strip():
            raise ValueError("parent_class cannot be empty")
        
        # Basic validation for Unreal class path format
        if not self.parent_class.startswith("/Script/"):
            import warnings
            warnings.warn(f"parent_class '{self.parent_class}' may not be a valid Unreal class path", 
                         UserWarning)
        
        return super().validate()


@dataclass
class AddComponentToBlueprintCommand(BaseCommand):
    """
    Command to add a component to an existing Blueprint.
    
    Attributes:
        blueprint_name: Name of the Blueprint to modify
        component_type: Type of component to add (e.g., "StaticMeshComponent")
        component_name: Optional name for the component
    
    Example:
        ```python
        cmd = AddComponentToBlueprintCommand(
            blueprint_name="MyActor",
            component_type="StaticMeshComponent",
            component_name="MeshComponent"
        )
        print(cmd.type)  # "add_component_to_blueprint"
        ```
    """
    blueprint_name: str = ""
    component_type: str = ""
    component_name: str = ""
    
    def __post_init__(self):
        self.params.update({
            "blueprint_name": self.blueprint_name,
            "component_type": self.component_type,
            "component_name": self.component_name
        })
        super().__post_init__()
    
    def validate(self) -> bool:
        """Validate AddComponentToBlueprint command parameters."""
        if not self.blueprint_name.strip():
            raise ValueError("blueprint_name cannot be empty")
        
        if not self.component_type.strip():
            raise ValueError("component_type cannot be empty")
        
        # Validate component type format
        valid_component_suffixes = ["Component", "Actor", "Object"]
        if not any(self.component_type.endswith(suffix) for suffix in valid_component_suffixes):
            import warnings
            warnings.warn(f"component_type '{self.component_type}' may not be a valid Unreal component type", 
                         UserWarning)
        
        return super().validate()


@dataclass
class CompileBlueprintCommand(BaseCommand):
    """
    Command to compile a Blueprint.
    
    Attributes:
        blueprint_name: Name of the Blueprint to compile
    
    Example:
        ```python
        cmd = CompileBlueprintCommand(blueprint_name="MyActor")
        print(cmd.type)  # "compile_blueprint"
        ```
    """
    blueprint_name: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.params.update({
            "blueprint_name": self.blueprint_name
        })


@dataclass
class SetBlueprintPropertyCommand(BaseCommand):
    """
    Command to set a property on a Blueprint.
    
    Attributes:
        blueprint_name: Name of the Blueprint to modify
        property_name: Name of the property to set
        property_value: Value to set for the property
        property_type: Optional type hint for the property
    
    Example:
        ```python
        cmd = SetBlueprintPropertyCommand(
            blueprint_name="MyActor",
            property_name="MaxHealth",
            property_value=100.0,
            property_type="float"
        )
        print(cmd.type)  # "set_blueprint_property"
        ```
    """
    blueprint_name: str = ""
    property_name: str = ""
    property_value: Any = None
    property_type: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.params.update({
            "blueprint_name": self.blueprint_name,
            "property_name": self.property_name,
            "property_value": self.property_value,
            "property_type": self.property_type
        })


@dataclass
class SetStaticMeshPropertiesCommand(BaseCommand):
    """
    Command to set properties on a StaticMeshComponent in a Blueprint.
    
    Attributes:
        blueprint_name: Name of the Blueprint containing the component
        component_name: Name of the StaticMeshComponent
        mesh_path: Path to the static mesh asset
        location: Optional location override
        rotation: Optional rotation override
        scale: Optional scale override
    
    Example:
        ```python
        cmd = SetStaticMeshPropertiesCommand(
            blueprint_name="MyActor",
            component_name="MeshComponent",
            mesh_path="/Game/Meshes/Cube",
            location={"x": 0, "y": 0, "z": 0}
        )
        print(cmd.type)  # "set_static_mesh_properties"
        ```
    """
    blueprint_name: str = ""
    component_name: str = ""
    mesh_path: str = ""
    location: Optional[Dict[str, float]] = None
    rotation: Optional[Dict[str, float]] = None
    scale: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        super().__post_init__()
        params_dict = {
            "blueprint_name": self.blueprint_name,
            "component_name": self.component_name,
            "mesh_path": self.mesh_path
        }
        
        # Only add optional parameters if they're provided
        if self.location is not None:
            params_dict["location"] = self.location
        if self.rotation is not None:
            params_dict["rotation"] = self.rotation
        if self.scale is not None:
            params_dict["scale"] = self.scale
            
        self.params.update(params_dict)