"""Measure alpha outside Android's conservative 66/108 circle without editing input."""

from io import BytesIO
from math import ceil, floor, sqrt

from PIL import Image, ImageChops, ImageDraw

from logo_helper.asset_models import (
    ANDROID_LAYER_DP,
    ANDROID_SAFE_DIAMETER_DP,
    SafeZoneEvidence,
)


def android_safe_zone(data: bytes) -> SafeZoneEvidence:
    """Count visible pixel centers outside the guide; identity and importance remain unknown."""
    radius = ANDROID_SAFE_DIAMETER_DP / ANDROID_LAYER_DP / 2
    with (
        Image.open(BytesIO(data)) as source,
        source.convert("RGBA") as rgba,
        rgba.getchannel("A") as alpha,
        Image.new("L", rgba.size, 255) as outside,
    ):
        drawing = ImageDraw.Draw(outside)
        for y in range(rgba.height):
            vertical = (y + 0.5) / rgba.height - 0.5
            if abs(vertical) <= radius:
                half_width = sqrt(radius**2 - vertical**2)
                left = ceil((0.5 - half_width) * rgba.width - 0.5)
                right = floor((0.5 + half_width) * rgba.width - 0.5)
                if left <= right:
                    drawing.line((left, y, right, y), fill=0)
        with ImageChops.multiply(alpha, outside) as clipped:
            count = sum(clipped.histogram()[1:])
    return SafeZoneEvidence(visible_pixels_outside=count)
