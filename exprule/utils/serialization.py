"""
Serialization utilities for experiences.
"""

import json
from typing import Any, Dict, Optional
from exprule.core.experience import Experience


def serialize_experience(experience: Experience, format: str = "json") -> str:
    """
    Serialize an experience to a string.
    
    Args:
        experience: Experience to serialize
        format: Output format ("json" or "dict")
        
    Returns:
        Serialized string or dict
    """
    data = experience.model_dump()
    if format == "json":
        return json.dumps(data, indent=2, default=str)
    elif format == "dict":
        return data
    else:
        raise ValueError(f"Unsupported format: {format}")


def deserialize_experience(data: Any, format: str = "json") -> Experience:
    """
    Deserialize an experience from a string or dict.
    
    Args:
        data: Serialized data
        format: Input format ("json" or "dict")
        
    Returns:
        Deserialized Experience
    """
    if format == "json":
        data = json.loads(data)
    return Experience(**data)


def export_experience_to_file(experience: Experience, filepath: str) -> None:
    """Export an experience to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(serialize_experience(experience))


def import_experience_from_file(filepath: str) -> Experience:
    """Import an experience from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = f.read()
    return deserialize_experience(data)
