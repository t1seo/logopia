"""Validate comparison hashes and budgets before an immutable sidecar-only write."""

from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from logo_helper.models import ProjectError
from logo_helper.preference_models import PreferenceManifest
from logo_helper.preference_response import (
    PreferenceRecord,
    PreferenceRecordResult,
    PreferenceResponse,
)
from logo_helper.storage import Store, read_source, safe_path, write_new


def _verify_sources(store: Store, folder: Path, manifest: PreferenceManifest) -> None:
    for pair in manifest.pairs:
        for candidate in (pair.a, pair.b):
            source = candidate.source
            state = store.expect(source.session, source.revision)
            artifact = state.artifact(source.artifact)
            hashes = (
                artifact.sha256 == candidate.sha256,
                sha256(artifact.prompt.encode("utf-8")).hexdigest() == candidate.prompt_sha256,
                sha256(state.brief.model_dump_json().encode("utf-8")).hexdigest()
                == candidate.brief_sha256,
                sha256(read_source(safe_path(folder, candidate.image_file))).hexdigest()
                == candidate.sha256,
            )
            if not all(hashes):
                raise ProjectError("hash_mismatch", "Comparison no longer matches original inputs")
            if (artifact.parent_id, artifact.image.width, artifact.image.height) != (
                candidate.parent_id,
                candidate.width,
                candidate.height,
            ):
                raise ProjectError(
                    "invalid_state", "Comparison changed source lineage or dimensions"
                )
    for reference in manifest.references:
        if reference.image_path is not None and (
            sha256(read_source(safe_path(folder, reference.image_path))).hexdigest()
            != reference.image_sha256
        ):
            raise ProjectError("hash_mismatch", "Review reference changed")


def record_preference(
    store: Store, gallery_relative: str, response: PreferenceResponse
) -> PreferenceRecordResult:
    """Record an explicit bounded observation without selecting, reviewing or exporting PNGs."""
    folder = safe_path(store.root, gallery_relative)
    if folder.relative_to(store.root).parts[0].casefold() in {".logo-generator", ".git"}:
        raise ProjectError("reserved_output", "Preference records use a standalone gallery")
    data = read_source(safe_path(folder, "manifest.json"))
    if sha256(data).hexdigest() != response.manifest_sha256:
        raise ProjectError("stale_comparison", "Response does not match this gallery manifest")
    manifest = PreferenceManifest.model_validate_json(data)
    expected = {pair.id: pair for pair in manifest.pairs}
    if set(expected) != {item.pair_id for item in response.decisions}:
        raise ProjectError(
            "invalid_review", "A response must cover each displayed pair exactly once"
        )
    for decision in response.decisions:
        pair = expected[decision.pair_id]
        if (decision.a_sha256, decision.b_sha256) != (pair.a.sha256, pair.b.sha256):
            raise ProjectError("hash_mismatch", "Response labels do not match displayed images")
    _verify_sources(store, folder, manifest)
    lock = safe_path(folder, ".preference-record.lock")
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise ProjectError("locked", "Another preference record write is active") from error
    try:
        return _write_record(store, folder, manifest, response)
    finally:
        lock.rmdir()


def _write_record(
    store: Store,
    folder: Path,
    manifest: PreferenceManifest,
    response: PreferenceResponse,
) -> PreferenceRecordResult:
    records = safe_path(folder, "preference-records")
    records.mkdir(exist_ok=True)
    existing = tuple(
        PreferenceRecord.model_validate_json(read_source(path))
        for path in sorted(records.glob("*.json"))
    )
    if any(item.response.manifest_sha256 != response.manifest_sha256 for item in existing):
        raise ProjectError("stale_comparison", "Existing responses belong to a different manifest")
    if len(existing) >= manifest.response_limit:
        raise ProjectError("review_budget", "This comparison reached its response limit")
    calls = sum(item.response.review_calls for item in existing) + response.review_calls
    if calls > manifest.ai_review_budget:
        raise ProjectError("review_budget", "This comparison reached its AI review call budget")
    digest = sha256(response.model_dump_json().encode("utf-8")).hexdigest()
    path = safe_path(records, f"{digest}.json")
    if path.exists():
        raise ProjectError("conflict", "This exact response is already recorded")
    record = PreferenceRecord(
        response_sha256=digest,
        recorded_at=datetime.now(UTC),
        status=response.status,
        response=response,
    )
    _verify_sources(store, folder, manifest)
    write_new(path, record.model_dump_json(indent=2).encode("utf-8"))
    return PreferenceRecordResult(
        path=path.relative_to(store.root).as_posix(),
        status=record.status,
        recorded_ai_review_calls=calls,
    )
