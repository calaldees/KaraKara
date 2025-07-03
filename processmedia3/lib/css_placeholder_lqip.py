"""
Attempt to implement css-only placeholder gradients
https://leanrada.com/notes/css-only-lqip/
"""

import math
from collections.abc import Sequence
from typing import Annotated, NamedTuple, Self
from annotated_types import Len

type bytesRGBColor = Annotated[bytes, Len(min_length=3, max_length=3)]
type bytesRGBAColor = Annotated[bytes, Len(min_length=4, max_length=4)]


class RGBColor(NamedTuple):
    r: float # values between 0 and 1
    g: float
    b: float

    @classmethod
    def fromBytes(cls, rgb: bytesRGBColor | bytesRGBAColor) -> Self:
        return cls(*map(lambda x: x/255, rgb))

    @property
    def bytes(self) -> bytes:
        return bytes(map(lambda x: min(max(0,int(x*255)),255), self))
    @property
    def rgb255(self) -> Sequence[int]:
        return tuple(map(int, self.bytes))

class RGBAColor(RGBColor):
    a: float


class OKLabColor(NamedTuple):
    # https://github.com/Kalabasa/leanrada.com/blob/fb0dea1db046fa083356824129b2e30f67495df0/main/scripts/update/lib/color/convert.mjs#L4
    L: float
    a: float
    b: float

    @staticmethod
    def gamma(x: float) -> float:
        return 1.055 * pow(x, 1 / 2.4) - 0.055 if x >= 0.0031308 else 12.92 * x
    @staticmethod
    def gamma_inv(x: float) -> float:
        return pow((x + 0.055) / 1.055, 2.4) if x >= 0.04045 else x / 12.92

    @classmethod
    def rgbToOkLab(cls, rgb: RGBColor) -> Self:
        r = cls.gamma_inv(rgb.r)
        g = cls.gamma_inv(rgb.g)
        b = cls.gamma_inv(rgb.b)
        l = math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
        m = math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
        s = math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
        return cls(
            L= l * +0.2104542553 + m * +0.793617785 + s * -0.0040720468,
            a= l * +1.9779984951 + m * -2.428592205 + s * +0.4505937099,
            b= l * +0.0259040371 + m * +0.7827717662 + s * -0.808675766,
        )

    def oklabToRGB(self) -> RGBColor:
        l = (self.L + 0.3963377774 * self.a + 0.2158037573 * self.b) ** 3
        m = (self.L - 0.1055613458 * self.a - 0.0638541728 * self.b) ** 3
        s = (self.L - 0.0894841775 * self.a - 1.291485548 * self.b) ** 3
        return RGBColor(
            r = self.gamma(+4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
            g = self.gamma(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
            b = self.gamma(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
        )

    @property
    def bytes(self) -> bytes:
        return bytes(map(lambda x: min(max(0,int(x*255)),255), self))

    @property
    def css(self) -> str:
        return f'oklab({self.L:.5f} {self.a:.5f} {self.b:.5f})'


class OKLabColorCompressed(OKLabColor):

    class ScaledComponent(NamedTuple):
        chroma: float
        scaledA: float
        scaledB: float
        @classmethod
        def fromOKLab(cls, oklab: OKLabColor) -> Self:
            chroma = math.hypot(oklab.a, oklab.b)
            return cls(
                chroma = chroma,
                scaledA = cls.scaleComponentForDiff(oklab.a, chroma),
                scaledB = cls.scaleComponentForDiff(oklab.b, chroma),
            )
        @staticmethod
        def scaleComponentForDiff(x: float, chroma: float):
            """
            Scales a or b of Oklab to move away from the center
            so that euclidean comparison won't be biased to the center
            """
            return x / (1e-6 + math.pow(chroma, 0.5))


    @classmethod
    def fromSingleCompressedByte(cls, i: int):
        assert i>=0 and i<=255
        return cls(
            L = (((i & 0b11000000)>>6) / 0b11) * 0.6 + 0.20,
            a = (((i & 0b00111000)>>3) / 0b1000) * 0.7 - 0.35,
            b = ((((i & 0b00000111)>>0)+1) / 0b1000) * 0.7 - 0.35,
        )

    @property
    def toSingleCompressedByte(self) -> int:
        """
        find the best bit configuration that would produce a color closest to target
        https://github.com/Kalabasa/leanrada.com/blob/7b6739c7c30c66c771fcbc9e1dc8942e628c5024/main/scripts/update/lqip.mjs#L172-L203
        """
        target_scaled = self.ScaledComponent.fromOKLab(self)
        bestSingleCompressedByte = 0
        bestDifference = math.inf

        for i in range(0, 255):
            possible_oklab = self.fromSingleCompressedByte(i)
            possible_scaled = self.ScaledComponent.fromOKLab(possible_oklab)

            difference = math.hypot(
                possible_oklab.L - self.L,
                possible_scaled.scaledA - target_scaled.scaledA,
                possible_scaled.scaledA - target_scaled.scaledA,
            )

            print(possible_oklab)
            if (difference < bestDifference):
                bestDifference = difference
                bestSingleCompressedByte = i
        #breakpoint()
        # Question: Are negative values for a and b ok in oklab color space?
        return bestSingleCompressedByte


# ------------------------------------------------------------------------------


from pathlib import Path
import io
import itertools

from PIL import Image
import modern_colorthief  # type: ignore[import-untyped]

def css_lqip(path_image: Path) -> int:
    """
    https://leanrada.com/notes/css-only-lqip/
    https://github.com/Kalabasa/leanrada.com/blob/7b6739c7c30c66c771fcbc9e1dc8942e628c5024/main/scripts/update/lqip.mjs#L118-L159
    """
    # Derive image dominant color
    image_bytes = io.BytesIO()
    img = Image.open(path_image, mode="r")
    img.save(image_bytes, format="PNG")
    oklab_dominant = OKLabColor.rgbToOkLab(RGBColor.fromBytes(modern_colorthief.get_color(image_bytes)))

    # Separate image into 6 segments
    oklab_segments = tuple(map(OKLabColor.rgbToOkLab, map(
        RGBColor.fromBytes,  # type: ignore[arg-type]
        itertools.batched(
            img.resize((3,2)).convert('RGB').tobytes(encoder_name='raw'),  # type: ignore[arg-type]
            n=3
        )
    )))

    # Calculate luminance diff for each segment compared to dominant luminance
    def clamp(value:float, _min=0.0, _max=1.0) -> float:
        return min(_max, max(_min, value))
    luminance_diff = tuple(
        clamp(0.5 + oklab_segment.L - oklab_dominant.L)
        for oklab_segment in oklab_segments
    )

    # Bit-pack 20bits into 9 digit int
    (ca, cb, cc, cd, ce, cf) = (round(ld * 0b11) for ld in luminance_diff)
    lqip = (
        -(2 ** 19) +
        ((ca & 0b11) << 18) +
        ((cb & 0b11) << 16) +
        ((cc & 0b11) << 14) +
        ((cd & 0b11) << 12) +
        ((ce & 0b11) << 10) +
        ((cf & 0b11) << 8) +
        OKLabColorCompressed(*oklab_dominant).toSingleCompressedByte
    )
    if lqip < -999_999 or lqip > 999_999:
        raise Exception()
    #breakpoint()
    return lqip

if __name__ == "__main__":
    #lqip = css_lqip(Path('/media/processed/6/6imQNaMPILo.avif'))
    lqip = css_lqip(Path('/media/processed/y/ynd7REZ5cJS.avif'))
    #lqip = css_lqip(Path('/media/processed/g/gWLr1JiSOVZ.avif'))
    print(lqip)