"""
Command classes for Unreal MCP Server.

This package contains the command class hierarchy that provides type-safe
alternatives to string-based commands, with automatic type generation and
JSON serialization support.
"""

from .base_command import BaseCommand
from .blueprint_commands import (
    CreateBlueprintCommand,
    AddComponentToBlueprintCommand,
    CompileBlueprintCommand,
    SetBlueprintPropertyCommand,
    SetStaticMeshPropertiesCommand
)

__all__ = [
    'BaseCommand',
    'CreateBlueprintCommand',
    'AddComponentToBlueprintCommand', 
    'CompileBlueprintCommand',
    'SetBlueprintPropertyCommand',
    'SetStaticMeshPropertiesCommand'
]