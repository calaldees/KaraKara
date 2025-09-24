import re
import hashlib
import base64
import logging
import shutil
import tempfile
from pathlib import Path
import typing as t

from .kktypes import TargetType
from .source import Source
from .encoders import Encoder, EncoderException


log = logging.getLogger()


class Target:
    """
    A file in the "processed" directory, with a method to figure out
    the target name (based on the hash of the source files + encoder
    settings), and a method to create that file if it doesn't exist.
    """

    def __init__(
        self,
        processed_dir: Path,
        type: TargetType,
        encoder: Encoder,
        sources: set[Source],
        variant: str | None = None,
    ) -> None:
        self.processed_dir = processed_dir
        self.type = type
        self.encoder = encoder
        self.sources = sources
        self.variant = variant

        parts = [self.encoder.salt] + [s.hash for s in self.sources]
        hasher = hashlib.sha256()
        hasher.update("".join(sorted(parts)).encode("ascii"))
        hash = re.sub("[+/=]", "_", base64.b64encode(hasher.digest()).decode("ascii"))
        self.friendly = hash[0].lower() + "/" + hash[:11] + "." + self.encoder.ext
        self.path = (
            processed_dir / hash[0].lower() / (hash[:11] + "." + self.encoder.ext)
        )
        log.debug(
            f"Filename for {self.encoder.__class__.__name__} = {self.friendly} based on {parts}"
        )

    def encode(self) -> None:
        log.info(
            f"{self.encoder.__class__.__name__}("
            f"{self.friendly!r}, "
            f"{[s.file.relative for s in self.sources]})"
        )
        with tempfile.TemporaryDirectory() as tempdir:
            temppath = Path(tempdir) / ("out." + self.encoder.ext)
            try:
                self.encoder.encode(temppath, self.sources)
                if not temppath.exists():
                    raise EncoderException(
                        "Encoder didn't return any error, but failed to create an output file"
                    )
                if temppath.stat().st_size == 0:
                    raise EncoderException(
                        "Encoder didn't return any error, but created an empty file"
                    )
                self.path.parent.mkdir(exist_ok=True)
                log.debug(f"Moving {temppath} to {self.path}")
                shutil.move(temppath.as_posix(), self.path.as_posix())
            except Exception as e:
                log.error(f"Error while encoding {self.friendly!r}: {e}")

    def __str__(self) -> str:
        source_list = [str(s) for s in self.sources]
        var = f"[{self.variant}]" if self.variant else ""
        return f"{self.type.name}{var}: {self.friendly!r} = {self.encoder.__class__.__name__}({source_list})"
