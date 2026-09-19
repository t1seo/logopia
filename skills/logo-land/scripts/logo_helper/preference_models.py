"""Strict blind-comparison inputs and immutable, hash-bound source snapshots."""

from typing import Annotated, Literal, Self

from pydantic import Field, HttpUrl, model_validator

from logo_helper.model_base import ArtifactId, Digest, FrozenModel, ProjectError, SessionId, Text

type EvidenceText = Annotated[str, Field(min_length=1, max_length=2000, pattern=r"\S")]


class PreferenceSource(FrozenModel):
    """An explicit saved source revision, never an inferred latest candidate."""

    session: Annotated[SessionId, Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")]
    revision: Annotated[int, Field(ge=0)]
    artifact: Annotated[ArtifactId, Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")]


class PreferencePairInput(FrozenModel):
    """Two candidates before seeded order balancing assigns blind A/B labels."""

    first: PreferenceSource
    second: PreferenceSource

    @model_validator(mode="after")
    def distinct_sources(self) -> Self:
        if (self.first.session, self.first.artifact) == (self.second.session, self.second.artifact):
            raise ProjectError("invalid_pair", "A pair requires two distinct candidate sources")
        return self


class PreferenceReference(FrozenModel):
    """Only task-relevant visual evidence; local images are opt-in private copies."""

    label: EvidenceText
    source_url: HttpUrl
    role: Literal["positive", "negative"]
    observations: EvidenceText
    verification: Literal["image_observed", "unverified"]
    image_sha256: Digest | None = None
    image_path: str | None = None

    @model_validator(mode="after")
    def evidence_binding(self) -> Self:
        if (self.verification == "image_observed" or self.image_path is not None) and (
            self.image_sha256 is None
        ):
            raise ProjectError("invalid_reference", "Observed/local reference needs an image hash")
        return self


class PreferenceSelection(FrozenModel):
    """Bounded local comparison; these budgets do not invoke external review tools."""

    shared_brief: Text
    pairs: Annotated[tuple[PreferencePairInput, ...], Field(min_length=1, max_length=12)]
    references: Annotated[tuple[PreferenceReference, ...], Field(max_length=8)] = ()
    seed: Annotated[int, Field(ge=0, le=2**32 - 1)] = 0
    ai_review_budget: Annotated[int, Field(ge=0, le=12)] = 3
    response_limit: Annotated[int, Field(ge=1, le=24)] = 12

    @model_validator(mode="after")
    def unique_pairs(self) -> Self:
        identities = {
            frozenset(
                (
                    (pair.first.session, pair.first.artifact),
                    (pair.second.session, pair.second.artifact),
                )
            )
            for pair in self.pairs
        }
        if len(identities) != len(self.pairs):
            raise ProjectError("invalid_pair", "Do not repeat a candidate pair")
        return self


class PreferenceCandidate(FrozenModel):
    """Blind filename paired with private provenance and verified original bytes."""

    source: PreferenceSource
    parent_id: ArtifactId | None
    image_file: str
    sha256: Digest
    prompt_sha256: Digest
    brief_sha256: Digest
    width: Annotated[int, Field(gt=0)]
    height: Annotated[int, Field(gt=0)]


class PreferencePair(FrozenModel):
    """Displayed order is immutable for every response tied to the manifest hash."""

    id: Annotated[str, Field(pattern=r"^pair-[0-9]{2}$")]
    a: PreferenceCandidate
    b: PreferenceCandidate


class PreferenceManifest(FrozenModel):
    """Unlinked organizer mapping; never a QA or selection record."""

    schema_version: Literal[1] = 1
    kind: Literal["preference_gallery"] = "preference_gallery"
    shared_brief: Text
    references: tuple[PreferenceReference, ...]
    pairs: tuple[PreferencePair, ...]
    seed: int
    ai_review_budget: Annotated[int, Field(ge=0, le=12)]
    response_limit: Annotated[int, Field(ge=1, le=24)]
    preview_note: str = (
        "Diagnostic CSS simulation at 32/48/64/128 CSS px, light/dark surfaces, equal-size "
        "candidate peers. Not OS rendering, official platform sizes or store verification."
    )
