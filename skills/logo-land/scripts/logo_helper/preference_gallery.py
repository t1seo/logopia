"""Publish blind, balanced PNG comparisons without changing source sessions."""

from hashlib import sha256
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory

from logo_helper.app_icon_publish import publish_gallery
from logo_helper.comparison_models import ComparisonResult
from logo_helper.models import ProjectError, Session, SessionId
from logo_helper.preference_cards import render_preference_markup
from logo_helper.preference_models import (
    PreferenceCandidate,
    PreferenceManifest,
    PreferencePair,
    PreferenceReference,
    PreferenceSelection,
    PreferenceSource,
)
from logo_helper.references import inspect_reference
from logo_helper.storage import Store, read_source, safe_path, write_new


def _candidate(
    store: Store,
    source: PreferenceSource,
    states: dict[SessionId, Session],
    image_file: str,
) -> PreferenceCandidate:
    if source.session not in states:
        states[source.session] = store.expect(source.session, source.revision)
    state = states[source.session]
    if state.revision != source.revision:
        raise ProjectError("stale_revision", "Use one current revision per source session")
    artifact = state.artifact(source.artifact)
    return PreferenceCandidate(
        source=source,
        parent_id=artifact.parent_id,
        image_file=image_file,
        sha256=artifact.sha256,
        prompt_sha256=sha256(artifact.prompt.encode("utf-8")).hexdigest(),
        brief_sha256=sha256(state.brief.model_dump_json().encode("utf-8")).hexdigest(),
        width=artifact.image.width,
        height=artifact.image.height,
    )


def _references(
    store: Store, items: tuple[PreferenceReference, ...], staging: Path
) -> tuple[PreferenceReference, ...]:
    copied: list[PreferenceReference] = []
    for number, item in enumerate(items, 1):
        if item.image_path is None:
            copied.append(item)
            continue
        data = read_source(safe_path(store.root, item.image_path))
        if sha256(data).hexdigest() != item.image_sha256:
            raise ProjectError("hash_mismatch", "Review reference differs from its expected hash")
        facts = inspect_reference(data)
        extension = "png" if facts.format == "PNG" else "jpg"
        path = f"images/reference-{number:02d}.{extension}"
        write_new(staging / path, data)
        copied.append(item.model_copy(update={"image_path": path}))
    return tuple(copied)


def render_preference_gallery(
    store: Store, selection: PreferenceSelection, output_relative: str
) -> ComparisonResult:
    """Snapshot explicit candidates; source identity is excluded from the rendered page."""
    destination = safe_path(store.root, output_relative)
    relative = destination.relative_to(store.root)
    if relative.parts[0].casefold() in {".logo-generator", ".git"}:
        raise ProjectError("reserved_output", "Gallery cannot occupy reserved project storage")
    if destination.exists():
        raise ProjectError("conflict", "Gallery destination already exists")
    rng = Random(selection.seed)  # noqa: S311 - reproducible display order, not security.
    inputs = list(selection.pairs)
    rng.shuffle(inputs)
    first_side = rng.randrange(2)
    states: dict[SessionId, Session] = {}
    snapshots: list[PreferencePair] = []
    for number, pair in enumerate(inputs, 1):
        sources = (pair.first, pair.second)
        if (number + first_side) % 2:
            sources = tuple(reversed(sources))
        snapshots.append(
            PreferencePair(
                id=f"pair-{number:02d}",
                a=_candidate(store, sources[0], states, f"images/{number:02d}-a.png"),
                b=_candidate(store, sources[1], states, f"images/{number:02d}-b.png"),
            )
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".preference-gallery-", dir=destination.parent) as temporary:
        staging = Path(temporary)
        (staging / "images").mkdir()
        (staging / "prompts").mkdir()
        references = _references(store, selection.references, staging)
        manifest = PreferenceManifest(
            shared_brief=selection.shared_brief,
            references=references,
            pairs=tuple(snapshots),
            seed=selection.seed,
            ai_review_budget=selection.ai_review_budget,
            response_limit=selection.response_limit,
        )
        for pair in snapshots:
            for candidate in (pair.a, pair.b):
                source = candidate.source
                artifact = states[source.session].artifact(source.artifact)
                data = read_source(safe_path(store.session_dir(source.session), artifact.path))
                if sha256(data).hexdigest() != candidate.sha256:
                    raise ProjectError("hash_mismatch", "Candidate bytes changed during render")
                write_new(staging / candidate.image_file, data)
        raw_manifest = manifest.model_dump_json(indent=2).encode("utf-8")
        markup = render_preference_markup(manifest, sha256(raw_manifest).hexdigest())
        write_new(staging / "manifest.json", raw_manifest)
        write_new(staging / "index.html", markup.encode("utf-8"))
        for state in states.values():
            _ = store.expect(state.id, state.revision)
        _ = safe_path(store.root, output_relative)
        publish_gallery(staging, destination)
    return ComparisonResult(
        path=relative.as_posix(),
        index_path=f"{relative.as_posix()}/index.html",
        count=len(snapshots),
    )
