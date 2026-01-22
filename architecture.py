"""Python architecture scaffold for README feature implementation.

This module defines the main layers expected for the project:
- Configuration: runtime settings (AppConfig)
- Domain models: feature specs and results (FeatureSpec, FeatureResult)
- Repository layer: persistence contract (FeatureRepository)
- Service layer: orchestrates feature execution (FeatureService)
- CLI: small command router to exercise the architecture

Extend the TODO blocks with the concrete behavior described in README.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Protocol
import argparse


@dataclass(frozen=True)
class AppConfig:
    """Application configuration values."""

    data_store_uri: str = "memory://"
    default_feature_id: str = "core"


@dataclass(frozen=True)
class FeatureSpec:
    """Input specification for a feature described in README."""

    feature_id: str
    name: str
    description: str


@dataclass(frozen=True)
class FeatureResult:
    """Represents an execution result for a feature."""

    feature_id: str
    status: str
    details: str


class FeatureRepository(Protocol):
    """Persistence contract for feature specs."""

    def list_specs(self) -> Iterable[FeatureSpec]:
        ...

    def get_spec(self, feature_id: str) -> Optional[FeatureSpec]:
        ...

    def upsert_spec(self, spec: FeatureSpec) -> None:
        ...


class InMemoryFeatureRepository:
    """Simple in-memory repository for local development/testing."""

    def __init__(self) -> None:
        self._specs: Dict[str, FeatureSpec] = {}

    def list_specs(self) -> Iterable[FeatureSpec]:
        return list(self._specs.values())

    def get_spec(self, feature_id: str) -> Optional[FeatureSpec]:
        return self._specs.get(feature_id)

    def upsert_spec(self, spec: FeatureSpec) -> None:
        self._specs[spec.feature_id] = spec


class FeatureService:
    """Business logic layer that coordinates repository access."""

    def __init__(self, repository: FeatureRepository) -> None:
        self._repository = repository

    def list_features(self) -> List[str]:
        return [f"{spec.feature_id}: {spec.name}" for spec in self._repository.list_specs()]

    def get_feature(self, feature_id: str) -> Optional[FeatureSpec]:
        return self._repository.get_spec(feature_id)

    def register_feature(self, feature_id: str, name: str, description: str) -> FeatureSpec:
        spec = FeatureSpec(feature_id=feature_id, name=name, description=description)
        self._repository.upsert_spec(spec)
        return spec

    def execute_feature(self, feature_id: str) -> FeatureResult:
        spec = self._repository.get_spec(feature_id)
        if spec is None:
            return FeatureResult(
                feature_id=feature_id,
                status="missing",
                details="Feature spec not found. Register it first.",
            )

        # TODO: replace with the actual execution logic from README.
        return FeatureResult(
            feature_id=spec.feature_id,
            status="ok",
            details=f"Executed {spec.name}: {spec.description}",
        )


def build_service(config: AppConfig) -> FeatureService:
    """Factory for the service layer."""

    _ = config
    repository = InMemoryFeatureRepository()
    return FeatureService(repository)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Feature CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List available features")

    show_parser = subparsers.add_parser("show", help="Show feature details")
    show_parser.add_argument("feature_id")

    register_parser = subparsers.add_parser("register", help="Register a feature")
    register_parser.add_argument("feature_id")
    register_parser.add_argument("name")
    register_parser.add_argument("description")

    run_parser = subparsers.add_parser("run", help="Execute a feature")
    run_parser.add_argument("feature_id")

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """CLI entrypoint to exercise the architecture."""

    config = AppConfig()
    service = build_service(config)

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        for summary in service.list_features():
            print(summary)
        return

    if args.command == "show":
        spec = service.get_feature(args.feature_id)
        if spec is None:
            print("Feature not found")
            return
        print(f"{spec.feature_id}: {spec.name}\n{spec.description}")
        return

    if args.command == "register":
        spec = service.register_feature(args.feature_id, args.name, args.description)
        print(f"Registered {spec.feature_id}")
        return

    if args.command == "run":
        result = service.execute_feature(args.feature_id)
        print(f"{result.status}: {result.details}")
        return


if __name__ == "__main__":
    main()
