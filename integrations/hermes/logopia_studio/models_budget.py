"""Reserved upper bounds count uncertain attempts and both LLM calls per role pair."""

from .models_base import FrozenModel, Revision


class CallBudget(FrozenModel):
    """Reservations are not an assertion of exact provider billing or completion."""

    initial_images_reserved: Revision
    initial_image_limit: Revision
    edit_images_reserved: Revision
    edit_image_limit: Revision
    planning_llm_calls_reserved: Revision
    review_llm_calls_reserved: Revision
    review_llm_call_limit: Revision
    explicit_review_recoveries: Revision
