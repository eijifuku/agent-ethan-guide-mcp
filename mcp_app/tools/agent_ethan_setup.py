import re
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from urllib import error as urlerror
from urllib import request as urlrequest
from zipfile import BadZipFile, ZipFile


class SetupTool:
    """Download agent-ethan2 archive and update rule guidance."""

    name = "setup"
    description = "Download agent-ethan2 and update rule guidance."  # noqa: D401

    _START_MARKER = "<!-- AGENT-ETHAN2-GUIDE-START -->"
    _END_MARKER = "<!-- AGENT-ETHAN2-GUIDE-END -->"
    _TAG_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")

    async def run(self, inp: Dict[str, Any]) -> Dict[str, Any]:
        return self._run_sync(inp)

    def _run_sync(self, inp: Dict[str, Any]) -> Dict[str, Any]:
        version = inp.get("version")
        rulefile = inp.get("rulefile", "AGENTS.md")
        tmp_dir_path = inp.get("tmp_dir_path", "./tmp")

        validation_error = self._validate_inputs(version, rulefile, tmp_dir_path)
        if validation_error:
            return validation_error

        version_str = version.strip()
        tmp_dir = Path(tmp_dir_path).expanduser()
        try:
            tmp_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return self._error(f"Failed to prepare tmp_dir_path: {exc}")

        rulefile_path = Path(rulefile).expanduser()
        try:
            rulefile_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return self._error(f"Failed to prepare rulefile directory: {exc}")

        archive_path = tmp_dir / f"agent-ethan2-{version_str}.zip"
        download_result = self._download_archive(version_str, archive_path)
        if download_result is not None:
            return download_result

        try:
            download_dir = self._extract_archive(archive_path, tmp_dir)
        except BadZipFile:
            archive_path.unlink(missing_ok=True)
            return self._error("Downloaded archive is not a valid zip file.")
        except OSError as exc:
            archive_path.unlink(missing_ok=True)
            return self._error(f"Failed to extract archive: {exc}")

        archive_path.unlink(missing_ok=True)
        if download_dir is None:
            return self._error("Could not determine extracted archive directory.")

        try:
            rulefile_updated = self._update_rulefile(rulefile_path, download_dir)
        except OSError as exc:
            return self._error(str(exc))
        message = f"Successfully set up agent-ethan2 {version_str}"
        return {
            "success": True,
            "message": message,
            "download_path": download_dir.as_posix(),
            "rulefile_updated": rulefile_updated,
        }

    def _validate_inputs(self, version: Any, rulefile: Any, tmp_dir_path: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(version, str) or not version.strip():
            return self._error("Parameter 'version' is required and must be a non-empty string.")
        if not self._TAG_PATTERN.match(version.strip()):
            return self._error("Parameter 'version' contains invalid characters.")
        if not isinstance(rulefile, str) or not rulefile.strip():
            return self._error("Parameter 'rulefile' must be a non-empty string path.")
        if not isinstance(tmp_dir_path, str) or not tmp_dir_path.strip():
            return self._error("Parameter 'tmp_dir_path' must be a non-empty string path.")
        return None

    def _download_archive(self, version: str, archive_path: Path) -> Optional[Dict[str, Any]]:
        url = f"https://github.com/eijifuku/agent-ethan2/archive/refs/tags/{version}.zip"
        try:
            with urlrequest.urlopen(url, timeout=30) as response:
                with archive_path.open("wb") as fp:
                    shutil.copyfileobj(response, fp)
        except urlerror.HTTPError as exc:
            if exc.code == 404:
                return self._error(f"Version '{version}' was not found (HTTP 404).")
            return self._error(f"HTTP error while downloading archive: {exc}")
        except urlerror.URLError as exc:
            return self._error(f"Network error while downloading archive: {exc}")
        except OSError as exc:
            return self._error(f"Failed to write archive to disk: {exc}")
        return None

    def _extract_archive(self, archive_path: Path, destination: Path) -> Optional[Path]:
        with ZipFile(archive_path, "r") as zip_file:
            root_dir_name = self._top_level_dir(zip_file)
            zip_file.extractall(destination)
        if root_dir_name is None:
            return None
        download_dir = destination / root_dir_name
        if not download_dir.exists():
            return None
        return download_dir

    def _top_level_dir(self, zip_file: ZipFile) -> Optional[str]:
        root_names = set()
        for name in zip_file.namelist():
            stripped = name.strip()
            if not stripped:
                continue
            parts = stripped.split("/")
            if parts:
                root_names.add(parts[0])
        if len(root_names) == 1:
            return next(iter(root_names))
        return None

    def _update_rulefile(self, rulefile_path: Path, download_dir: Path) -> bool:
        existing_text = ""
        if rulefile_path.exists():
            try:
                existing_text = rulefile_path.read_text(encoding="utf-8")
            except OSError as exc:
                raise OSError(f"Failed to read rulefile: {exc}") from exc

        block = self._build_rule_block(download_dir)
        if self._START_MARKER in existing_text and self._END_MARKER in existing_text:
            start_index = existing_text.index(self._START_MARKER)
            end_index = existing_text.index(self._END_MARKER, start_index) + len(self._END_MARKER)
            new_text = existing_text[:start_index] + block + existing_text[end_index:]
        else:
            separator = "\n" if existing_text and not existing_text.endswith("\n") else ""
            new_text = f"{existing_text}{separator}{block}"

        if new_text == existing_text:
            return False

        try:
            rulefile_path.write_text(new_text, encoding="utf-8")
        except OSError as exc:
            raise OSError(f"Failed to write rulefile: {exc}") from exc
        return True

    def _build_rule_block(self, download_dir: Path) -> str:
        display_path = download_dir.as_posix()
        if not display_path.endswith("/"):
            display_path = f"{display_path}/"
        lines = [
            self._START_MARKER,
            "agent-ethan2のドキュメントとソースコードは下記にあります。",
            "実装に必要な情報はここから入手してください。",
            "",
            display_path,
            self._END_MARKER,
            "",
        ]
        return "\n".join(lines)

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "success": False,
            "message": message,
            "download_path": "",
            "rulefile_updated": False,
        }
