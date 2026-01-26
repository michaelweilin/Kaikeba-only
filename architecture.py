"""Local architecture scaffold for automation features.

Features to implement (see README):
1) Use a .bat file to traverse a folder, read file names, and open each file.
2) Copy a specified folder daily and rename it by date.
3) Automatically print a specified document.
4) Auto-fill a form based on a specified dataset.
5) Create email drafts automatically based on date.

This module defines the main layers for those capabilities:
- Configuration: runtime settings (AppConfig)
- Domain models: job definitions and execution results
- Repository layer: persistence contract for jobs
- Service layer: orchestration and adapters
- CLI: command router to exercise the architecture locally
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Protocol


@dataclass(frozen=True)
class AppConfig:
    """Application configuration values."""

    workspace: Path = Path(".")
    dataset_path: Path = Path("dataset.csv")
    templates_path: Path = Path("templates")


@dataclass(frozen=True)
class JobSpec:
    """Represents a single automation job described in README."""

    job_id: str
    name: str
    description: str


@dataclass(frozen=True)
class JobResult:
    """Represents a job execution result."""

    job_id: str
    status: str
    details: str


class JobRepository(Protocol):
    """Persistence contract for job specs."""

    def list_jobs(self) -> Iterable[JobSpec]:
        ...

    def get_job(self, job_id: str) -> Optional[JobSpec]:
        ...

    def upsert_job(self, spec: JobSpec) -> None:
        ...


class InMemoryJobRepository:
    """Simple in-memory repository for local development/testing."""

    def __init__(self) -> None:
        self._jobs: Dict[str, JobSpec] = {}

    def list_jobs(self) -> Iterable[JobSpec]:
        return list(self._jobs.values())

    def get_job(self, job_id: str) -> Optional[JobSpec]:
        return self._jobs.get(job_id)

    def upsert_job(self, spec: JobSpec) -> None:
        self._jobs[spec.job_id] = spec


@dataclass(frozen=True)
class BatchScriptPlan:
    """Plan for generating and running a .bat script."""

    folder: Path
    script_path: Path


@dataclass(frozen=True)
class FolderCopyPlan:
    """Plan for copying and renaming a folder by date."""

    source_folder: Path
    destination_root: Path
    target_date: date


@dataclass(frozen=True)
class PrintPlan:
    """Plan for printing a document."""

    document_path: Path


@dataclass(frozen=True)
class FormFillPlan:
    """Plan for auto-filling a form based on a dataset."""

    dataset_path: Path
    template_path: Path
    output_path: Path


@dataclass(frozen=True)
class EmailDraftPlan:
    """Plan for creating an email draft based on date."""

    target_date: date
    template_path: Path
    output_path: Path


class AutomationService:
    """Business logic layer that coordinates repositories and adapters."""

    def __init__(self, repository: JobRepository, config: AppConfig) -> None:
        self._repository = repository
        self._config = config

    def register_job(self, job_id: str, name: str, description: str) -> JobSpec:
        spec = JobSpec(job_id=job_id, name=name, description=description)
        self._repository.upsert_job(spec)
        return spec

    def list_jobs(self) -> List[str]:
        return [f"{job.job_id}: {job.name}" for job in self._repository.list_jobs()]

    def build_batch_script_plan(self, folder: Path, script_path: Path) -> BatchScriptPlan:
        return BatchScriptPlan(folder=folder, script_path=script_path)

    def build_folder_copy_plan(
        self, source_folder: Path, destination_root: Path, target_date: date
    ) -> FolderCopyPlan:
        return FolderCopyPlan(
            source_folder=source_folder,
            destination_root=destination_root,
            target_date=target_date,
        )

    def build_print_plan(self, document_path: Path) -> PrintPlan:
        return PrintPlan(document_path=document_path)

    def build_form_fill_plan(
        self, dataset_path: Path, template_path: Path, output_path: Path
    ) -> FormFillPlan:
        return FormFillPlan(
            dataset_path=dataset_path,
            template_path=template_path,
            output_path=output_path,
        )

    def build_email_draft_plan(
        self, target_date: date, template_path: Path, output_path: Path
    ) -> EmailDraftPlan:
        return EmailDraftPlan(
            target_date=target_date,
            template_path=template_path,
            output_path=output_path,
        )

    def execute(self, plan: object) -> JobResult:
        """Execute a plan. Replace TODOs with concrete implementations."""

        if isinstance(plan, BatchScriptPlan):
            return JobResult(
                job_id="batch",
                status="pending",
                details=(
                    "Generate .bat to iterate folder contents and open files: "
                    f"{plan.folder} -> {plan.script_path}"
                ),
            )
        if isinstance(plan, FolderCopyPlan):
            destination = plan.destination_root / plan.target_date.isoformat()
            return JobResult(
                job_id="folder_copy",
                status="pending",
                details=f"Copy {plan.source_folder} to {destination}",
            )
        if isinstance(plan, PrintPlan):
            return JobResult(
                job_id="print",
                status="pending",
                details=f"Print document {plan.document_path}",
            )
        if isinstance(plan, FormFillPlan):
            return JobResult(
                job_id="form_fill",
                status="pending",
                details=(
                    "Fill template using dataset: "
                    f"{plan.dataset_path} -> {plan.output_path}"
                ),
            )
        if isinstance(plan, EmailDraftPlan):
            return JobResult(
                job_id="email_draft",
                status="pending",
                details=(
                    "Create email draft from template: "
                    f"{plan.template_path} -> {plan.output_path}"
                ),
            )
        return JobResult(job_id="unknown", status="error", details="Unknown plan type")


def build_service(config: AppConfig) -> AutomationService:
    """Factory for the service layer."""

    repository = InMemoryJobRepository()
    return AutomationService(repository, config)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List available jobs")

    batch_parser = subparsers.add_parser("batch", help="Plan .bat traversal job")
    batch_parser.add_argument("folder")
    batch_parser.add_argument("script_path")

    copy_parser = subparsers.add_parser("copy", help="Plan daily folder copy")
    copy_parser.add_argument("source_folder")
    copy_parser.add_argument("destination_root")
    copy_parser.add_argument("target_date")

    print_parser = subparsers.add_parser("print", help="Plan document printing")
    print_parser.add_argument("document_path")

    form_parser = subparsers.add_parser("form", help="Plan form auto-fill")
    form_parser.add_argument("dataset_path")
    form_parser.add_argument("template_path")
    form_parser.add_argument("output_path")

    email_parser = subparsers.add_parser("email", help="Plan email draft creation")
    email_parser.add_argument("target_date")
    email_parser.add_argument("template_path")
    email_parser.add_argument("output_path")

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """CLI entrypoint to exercise the architecture."""

    config = AppConfig()
    service = build_service(config)

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        for summary in service.list_jobs():
            print(summary)
        return

    if args.command == "batch":
        plan = service.build_batch_script_plan(Path(args.folder), Path(args.script_path))
        result = service.execute(plan)
        print(f"{result.status}: {result.details}")
        return

    if args.command == "copy":
        plan = service.build_folder_copy_plan(
            Path(args.source_folder),
            Path(args.destination_root),
            date.fromisoformat(args.target_date),
        )
        result = service.execute(plan)
        print(f"{result.status}: {result.details}")
        return

    if args.command == "print":
        plan = service.build_print_plan(Path(args.document_path))
        result = service.execute(plan)
        print(f"{result.status}: {result.details}")
        return

    if args.command == "form":
        plan = service.build_form_fill_plan(
            Path(args.dataset_path),
            Path(args.template_path),
            Path(args.output_path),
        )
        result = service.execute(plan)
        print(f"{result.status}: {result.details}")
        return

    if args.command == "email":
        plan = service.build_email_draft_plan(
            date.fromisoformat(args.target_date),
            Path(args.template_path),
            Path(args.output_path),
        )
        result = service.execute(plan)
        print(f"{result.status}: {result.details}")
        return


if __name__ == "__main__":
    main()
