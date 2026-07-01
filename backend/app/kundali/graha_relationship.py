"""Reusable natural Graha relationship helpers."""

from __future__ import annotations

from typing import Literal, TypedDict

RelationshipStatus = Literal["friend", "neutral", "enemy", "unsupported"]

CLASSICAL_PLANETS: tuple[str, ...] = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
)


class NaturalRelationship(TypedDict):
    """Natural relationship groups for a classical planet."""

    friends: tuple[str, ...]
    neutrals: tuple[str, ...]
    enemies: tuple[str, ...]


NATURAL_RELATIONSHIPS: dict[str, NaturalRelationship] = {
    "sun": {
        "friends": ("moon", "mars", "jupiter"),
        "neutrals": ("mercury",),
        "enemies": ("venus", "saturn"),
    },
    "moon": {
        "friends": ("sun", "mercury"),
        "neutrals": ("mars", "jupiter", "venus", "saturn"),
        "enemies": (),
    },
    "mars": {
        "friends": ("sun", "moon", "jupiter"),
        "neutrals": ("venus", "saturn"),
        "enemies": ("mercury",),
    },
    "mercury": {
        "friends": ("sun", "venus"),
        "neutrals": ("mars", "jupiter", "saturn"),
        "enemies": ("moon",),
    },
    "jupiter": {
        "friends": ("sun", "moon", "mars"),
        "neutrals": ("saturn",),
        "enemies": ("mercury", "venus"),
    },
    "venus": {
        "friends": ("mercury", "saturn"),
        "neutrals": ("mars", "jupiter"),
        "enemies": ("sun", "moon"),
    },
    "saturn": {
        "friends": ("mercury", "venus"),
        "neutrals": ("jupiter",),
        "enemies": ("sun", "moon", "mars"),
    },
}


def get_natural_relationship(planet: str, other_planet: str) -> RelationshipStatus:
    """Return the natural relationship from one planet toward another."""

    planet_key = _normalize_supported_planet(planet)
    other_planet_key = _normalize_supported_planet(other_planet)
    if planet_key is None or other_planet_key is None:
        return "unsupported"

    relationship = NATURAL_RELATIONSHIPS[planet_key]
    if other_planet_key in relationship["friends"]:
        return "friend"

    if other_planet_key in relationship["neutrals"]:
        return "neutral"

    if other_planet_key in relationship["enemies"]:
        return "enemy"

    return "unsupported"


def get_planet_friends(planet: str) -> tuple[str, ...]:
    """Return natural friends for a supported classical planet."""

    return _get_relationship_group(planet, "friends")


def get_planet_neutrals(planet: str) -> tuple[str, ...]:
    """Return natural neutrals for a supported classical planet."""

    return _get_relationship_group(planet, "neutrals")


def get_planet_enemies(planet: str) -> tuple[str, ...]:
    """Return natural enemies for a supported classical planet."""

    return _get_relationship_group(planet, "enemies")


def supports_natural_relationship(planet: str) -> bool:
    """Return whether natural relationships are mapped for the planet."""

    return _normalize_supported_planet(planet) is not None


def _get_relationship_group(
    planet: str,
    group: Literal["friends", "neutrals", "enemies"],
) -> tuple[str, ...]:
    """Return a relationship group, or an empty tuple for unsupported planets."""

    planet_key = _normalize_supported_planet(planet)
    if planet_key is None:
        return ()

    return NATURAL_RELATIONSHIPS[planet_key][group]


def _normalize_supported_planet(planet: str) -> str | None:
    """Return the normalized project planet key if supported."""

    if not isinstance(planet, str):
        return None

    planet_key = planet.strip().casefold()
    if planet_key not in NATURAL_RELATIONSHIPS:
        return None

    return planet_key
