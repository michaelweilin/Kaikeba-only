"""Main architecture scaffold for the project.

This module provides a clean separation between:
- configuration
- domain models
- repositories (data access)
- services (business logic)
- CLI entrypoint

Fill in the feature-specific details described in README.md as you extend the app.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Protocol


@dataclass(frozen=True)
class AppConfig:
    """Application configuration values."""

    data_store_uri: str = "memory://"


@dataclass(frozen=True)
class FeatureItem:
    """Represents a single feature entity described in README."""

    item_id: str
    title: str
    description: str


class FeatureRepository(Protocol):
    """Abstraction for data access."""

    def list_items(self) -> Iterable[FeatureItem]:
        ...

    def get_item(self, item_id: str) -> Optional[FeatureItem]:
        ...

    def upsert_item(self, item: FeatureItem) -> None:
        ...


class InMemoryFeatureRepository:
    """Simple in-memory repository for local development/testing."""

    def __init__(self) -> None:
        self._items: Dict[str, FeatureItem] = {}

    def list_items(self) -> Iterable[FeatureItem]:
        return list(self._items.values())

    def get_item(self, item_id: str) -> Optional[FeatureItem]:
        return self._items.get(item_id)

    def upsert_item(self, item: FeatureItem) -> None:
        self._items[item.item_id] = item


class FeatureService:
    """Business logic layer that coordinates repository access."""

    def __init__(self, repository: FeatureRepository) -> None:
        self._repository = repository

    def list_feature_summaries(self) -> List[str]:
        return [f"{item.item_id}: {item.title}" for item in self._repository.list_items()]

    def get_feature_detail(self, item_id: str) -> Optional[FeatureItem]:
        return self._repository.get_item(item_id)

    def register_feature(self, item_id: str, title: str, description: str) -> FeatureItem:
        item = FeatureItem(item_id=item_id, title=title, description=description)
        self._repository.upsert_item(item)
        return item


def build_service(config: AppConfig) -> FeatureService:
    """Factory for the service layer."""

    _ = config
    repository = InMemoryFeatureRepository()
    return FeatureService(repository)


def main() -> None:
    """CLI entrypoint to exercise the architecture."""

    config = AppConfig()
    service = build_service(config)

    service.register_feature("core", "Core Feature", "Primary capability described in README.")

    for summary in service.list_feature_summaries():
        print(summary)


if __name__ == "__main__":
    main()
