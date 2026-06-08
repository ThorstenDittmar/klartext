"""Pydantic schemas for the debug object graph endpoint."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class DebugNode(BaseModel):
    """A single domain object instance in the object graph."""

    id: str
    class_name: str
    fields: dict[str, Any]


class DebugEdge(BaseModel):
    """A directed relationship between two nodes. The label is the field name."""

    id: str
    source: str
    target: str
    label: str


class DebugGraphResponse(BaseModel):
    """Full object graph for a user — all domain instances plus their relationships."""

    nodes: list[DebugNode]
    edges: list[DebugEdge]
