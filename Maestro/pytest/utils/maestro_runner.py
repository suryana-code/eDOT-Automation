import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RECORDINGS_DIR = PROJECT_ROOT / "recordings"
DEFAULT_VIDEO_CRF = "23"


MAESTRO_ENV_KEYS = [
    "APP_ID",
    "COMPANY_ID",
    "USER_NAME",
    "PASSWORD",
    "OUTLET_NAME",
    "PHONE",
    "EMAIL",
    "CONTACT_PERSON",
    "CHANNEL",
    "OUTLET_TYPE",
    "ADDRESS_TYPE",
    "ADDRESS",
    "PROVINCE",
    "CITY",
    "DISTRICT",
    "SUBDISTRICT",
    "KTP",
    "MAESTRO_EVIDENCE_RUN_ID",
]


@dataclass
class MaestroExecution:
    result: subprocess.CompletedProcess
    evidence_dir: Path
    output_path: Path
    recordings: list["MaestroRecording"]


@dataclass
class MaestroRecording:
    name: str
    original_video_path: Path | None
    attached_video_path: Path | None
    original_video_metadata: tuple[int, int] | None
    attached_video_metadata: tuple[int, int] | None


def run_maestro(env):
    """
    Menjalankan flow utama Maestro dan meneruskan
    environment variable yang dibutuhkan ke Maestro.
    """

    run_id = uuid4().hex

    evidence_dir = RECORDINGS_DIR / run_id
    evidence_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    execution_env = env.copy()
    execution_env["MAESTRO_EVIDENCE_RUN_ID"] = run_id

    command = [
        "maestro",
        "test",
        "-p",
        "android",
    ]

    for key in MAESTRO_ENV_KEYS:
        value = execution_env.get(key)

        if value is not None:
            command.extend([
                "-e",
                f"{key}={value}",
            ])

    command.append(
        str(PROJECT_ROOT / "flows" / "main.yaml")
    )

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=execution_env,
            cwd=PROJECT_ROOT,
        )

    except OSError as error:
        result = subprocess.CompletedProcess(
            args=command,
            returncode=127,
            stdout="",
            stderr=str(error),
        )

    output_path = (
        evidence_dir / "maestro-execution-output.txt"
    )

    output_path.write_text(
        "Command: "
        + " ".join(
            command[:4]
            + ["<environment variables>"]
            + command[-1:]
        )
        + "\n\n--- stdout ---\n"
        + result.stdout
        + "\n\n--- stderr ---\n"
        + result.stderr,
        encoding="utf-8",
    )

    return MaestroExecution(
        result=result,
        evidence_dir=evidence_dir,
        output_path=output_path,
        recordings=[
            _prepare_recording(
                evidence_dir,
                "Maestro execution",
                "maestro-execution",
            ),
        ],
    )


def _prepare_recording(
    evidence_dir: Path,
    name: str,
    stem: str,
) -> MaestroRecording:

    original_video_path = (
        evidence_dir / f"{stem}.mp4"
    )

    if not original_video_path.is_file():
        return MaestroRecording(
            name=name,
            original_video_path=None,
            attached_video_path=None,
            original_video_metadata=None,
            attached_video_metadata=None,
        )

    original_video_metadata = _video_metadata(
        original_video_path
    )

    attached_video_path = original_video_path
    attached_video_metadata = original_video_metadata

    if original_video_metadata:

        compressed_video_path = (
            evidence_dir
            / f"{stem}-compressed.mp4"
        )

        if _compress_video(
            original_video_path,
            compressed_video_path,
        ):

            compressed_metadata = _video_metadata(
                compressed_video_path
            )

            try:
                if (
                    compressed_metadata
                    == original_video_metadata
                    and compressed_video_path.stat().st_size
                    < original_video_path.stat().st_size
                ):
                    attached_video_path = (
                        compressed_video_path
                    )

                    attached_video_metadata = (
                        compressed_metadata
                    )

            except OSError:
                pass

    return MaestroRecording(
        name=name,
        original_video_path=original_video_path,
        attached_video_path=attached_video_path,
        original_video_metadata=original_video_metadata,
        attached_video_metadata=attached_video_metadata,
    )


def _video_metadata(
    video_path: Path | None,
) -> tuple[int, int] | None:

    """
    Mengembalikan dimensi video jika ffprobe
    dapat membaca file MP4.
    """

    if not video_path:
        return None

    if not shutil.which("ffprobe"):
        return None

    try:
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "json",
                str(video_path),
            ],
            capture_output=True,
            text=True,
        )

    except OSError:
        return None

    if probe.returncode != 0:
        return None

    try:
        stream = json.loads(
            probe.stdout
        )["streams"][0]

        return (
            int(stream["width"]),
            int(stream["height"]),
        )

    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        return None


def _compress_video(
    original_video_path: Path,
    compressed_video_path: Path,
) -> bool:

    """
    Mengompresi video menggunakan H.264
    tanpa mengubah resolusi video.
    """

    if not shutil.which("ffmpeg"):
        return False

    if not shutil.which("ffprobe"):
        return False

    try:
        compression = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(original_video_path),
                "-map",
                "0:v:0",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                os.getenv(
                    "MAESTRO_VIDEO_CRF",
                    DEFAULT_VIDEO_CRF,
                ),
                "-an",
                "-movflags",
                "+faststart",
                str(compressed_video_path),
            ],
            capture_output=True,
            text=True,
        )

    except OSError:
        return False

    return (
        compression.returncode == 0
        and compressed_video_path.is_file()
    )