"""Portable, read-only publication of explicitly requested app-icon originals."""

from hashlib import sha256
from html import escape
from pathlib import Path
from string import Template
from tempfile import TemporaryDirectory
from typing import Literal

from logo_helper.app_icon_models import AppIconIntent
from logo_helper.app_icon_publish import publish_gallery
from logo_helper.color_gallery import GalleryResult
from logo_helper.images import inspect_png
from logo_helper.model_base import Digest
from logo_helper.models import Artifact, ArtifactId, FrozenModel, ProjectError, Session, SessionId
from logo_helper.storage import Store, read_source, safe_path, write_new


class GalleryArtifact(FrozenModel):
    """Pair original and prompt hashes with that artifact's immutable icon intent."""

    artifact_id: ArtifactId
    parent_id: ArtifactId | None
    image_file: str
    prompt_file: str
    sha256: Digest
    prompt_sha256: Digest
    width: int
    height: int
    app_icon: AppIconIntent


class GalleryManifest(FrozenModel):
    """A creative gallery snapshot, independent of selection or export approval."""

    schema_version: Literal[1] = 1
    kind: Literal["app_icon_gallery"] = "app_icon_gallery"
    session_id: SessionId
    revision: int
    artifacts: tuple[GalleryArtifact, ...]
    preview_note: str = "Masks are illustrative CSS previews; original PNG bytes are unchanged."


def _snapshot(artifact: Artifact) -> GalleryArtifact:
    if artifact.app_icon is None:
        raise ProjectError("not_app_icon", f"Artifact {artifact.id} has no app-icon intent")
    return GalleryArtifact(
        artifact_id=artifact.id,
        parent_id=artifact.parent_id,
        image_file=f"images/{artifact.id}.png",
        prompt_file=f"prompts/{artifact.id}.txt",
        sha256=artifact.sha256,
        prompt_sha256=sha256(artifact.prompt.encode("utf-8")).hexdigest(),
        width=artifact.image.width,
        height=artifact.image.height,
        app_icon=artifact.app_icon,
    )


def _card(item: GalleryArtifact, number: int) -> str:
    intent = item.app_icon
    identifier = escape(item.artifact_id)
    return (
        f'<article class="icon-card" data-preset="{escape(intent.preset)}">'
        f'<div class="card-heading"><span class="number">{number:02d}</span>'
        f'<span class="preset">{escape(intent.preset.replace("_", " "))}</span></div>'
        f'<div class="preview-surface"><img src="{escape(item.image_file)}" '
        f'alt="{escape(intent.subject)}" width="{item.width}" height="{item.height}"></div>'
        f'<div class="card-body"><h2>{identifier}</h2><p class="subject">'
        f'{escape(intent.subject)}</p><p class="dimensions">{item.width} x {item.height} px'
        " · Original PNG</p><details><summary>Artwork intent</summary><dl>"
        f"<dt>Preset</dt><dd>{escape(intent.preset)}</dd>"
        f"<dt>Placement</dt><dd>{escape(intent.placement)}</dd>"
        f"<dt>Exact lettering</dt><dd>{escape(intent.text or 'None')}</dd>"
        f"<dt>Parent</dt><dd>{escape(item.parent_id or 'None')}</dd></dl>"
        f'<p class="hash">SHA-256<br>{escape(item.sha256)}</p></details>'
        f'<div class="downloads"><a href="{escape(item.image_file)}" download>'
        f'Download original<span class="sr-only"> {identifier}</span></a>'
        f'<a href="{escape(item.prompt_file)}" download>Exact prompt'
        f'<span class="sr-only"> {identifier}</span></a></div></div></article>'
    )


def _context(items: tuple[GalleryArtifact, ...]) -> str:
    peers = "".join(
        (
            f'<figure><img src="{escape(item.image_file)}" alt="Candidate {number}" '
            f'width="64" height="64"><figcaption>Candidate {number}</figcaption></figure>'
        )
        for number, item in enumerate(items, 1)
    )
    return (
        '<section class="context-section" aria-label="Balanced candidate context">'
        "<h2>Simulation · candidate peers</h2><p>All selected candidates share the same "
        "size, surrounding surface and spacing. These are diagnostic contexts, not OS "
        "renderings. The 32/48/64/128 px options are not official platform sizes.</p>"
        f'<div class="context-home">{peers}</div><div class="context-list">{peers}</div>'
        "</section>"
    )


def render_app_icon_gallery(
    store: Store,
    state: Session,
    artifact_ids: tuple[ArtifactId, ...],
    output_relative: str,
) -> GalleryResult:
    """Publish the supplied revision snapshot without writing or refreshing session state."""
    if not artifact_ids or len(set(artifact_ids)) != len(artifact_ids):
        raise ProjectError("invalid_selection", "Choose one or more distinct artifact IDs")
    artifacts = tuple(state.artifact(identifier) for identifier in artifact_ids)
    snapshots = tuple(_snapshot(artifact) for artifact in artifacts)
    destination = safe_path(store.root, output_relative)
    relative = destination.relative_to(store.root)
    if relative.parts[0].casefold() in {".logo-generator", ".git"}:
        raise ProjectError("reserved_output", "Gallery cannot occupy reserved project storage")
    if destination.exists():
        raise ProjectError("conflict", "Gallery destination already exists")
    manifest = GalleryManifest(session_id=state.id, revision=state.revision, artifacts=snapshots)
    template = Path(__file__).resolve().parents[2] / "assets/app-icon-gallery.template.html"
    markup = Template(template.read_text(encoding="utf-8")).substitute(
        brand=escape(state.brief.brand_name),
        session=escape(state.id),
        revision=state.revision,
        count=len(artifacts),
        cards="".join(_card(item, number) for number, item in enumerate(snapshots, 1)),
        context=_context(snapshots),
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".app-icon-gallery-", dir=destination.parent) as temporary:
        staging = Path(temporary)
        (staging / "images").mkdir()
        (staging / "prompts").mkdir()
        for artifact, item in zip(artifacts, snapshots, strict=True):
            data = read_source(safe_path(store.session_dir(state.id), artifact.path))
            if sha256(data).hexdigest() != artifact.sha256:
                raise ProjectError("hash_mismatch", f"Artifact {artifact.id} changed during render")
            if inspect_png(data) != artifact.image:
                raise ProjectError("invalid_state", f"Artifact {artifact.id} dimensions changed")
            write_new(staging / item.image_file, data)
            write_new(staging / item.prompt_file, artifact.prompt.encode("utf-8"))
        write_new(staging / "manifest.json", manifest.model_dump_json(indent=2).encode("utf-8"))
        write_new(staging / "index.html", markup.encode("utf-8"))
        _ = safe_path(store.root, output_relative)
        publish_gallery(staging, destination)
    return GalleryResult(relative.as_posix(), f"{relative.as_posix()}/index.html", artifact_ids)
