import asyncio
import io
from pathlib import Path

import pytest

from mcp_app.tools.agent_ethan_setup import SetupTool
import mcp_app.tools.agent_ethan_setup as setup_tool_module


class DummyResponse(io.BytesIO):
    def __init__(self, data: bytes):
        super().__init__(data)
        self.status = 200

    def __enter__(self):
        self.seek(0)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.close()
        return False


def _make_zip_bytes(root_name: str = "agent-ethan2-0.1.0") -> bytes:
    buffer = io.BytesIO()
    with setup_tool_module.ZipFile(buffer, "w") as zf:
        arc_path = f"{root_name}/README.md"
        zf.writestr(arc_path, "sample content")
    return buffer.getvalue()


def _patch_successful_download(monkeypatch) -> None:
    def fake_urlopen(url, timeout=30):
        return DummyResponse(_make_zip_bytes())

    monkeypatch.setattr(setup_tool_module.urlrequest, "urlopen", fake_urlopen)


def test_setup_invalid_version() -> None:
    tool = SetupTool()
    result = asyncio.run(tool.run({"version": "invalid tag!"}))
    assert result["success"] is False
    assert "invalid" in result["message"].lower()


def test_rulefile_creation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tool = SetupTool()
    _patch_successful_download(monkeypatch)

    rulefile = tmp_path / "AGENTS.md"
    downloads = tmp_path / "downloads"

    result = asyncio.run(
        tool.run(
            {
                "version": "v0.1.0",
                "rulefile": str(rulefile),
                "tmp_dir_path": str(downloads),
            }
        )
    )

    assert result["success"] is True
    assert Path(result["download_path"]).is_dir()
    expected_block = tool._build_rule_block(Path(result["download_path"]))
    assert expected_block in rulefile.read_text(encoding="utf-8")
    assert result["rulefile_updated"] is True


def test_marker_replacement(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tool = SetupTool()
    _patch_successful_download(monkeypatch)

    rulefile = tmp_path / "AGENTS.md"
    downloads = tmp_path / "downloads"

    initial_content = (
        "Header line\n"
        f"{tool._START_MARKER}\n"
        "outdated content\n"
        f"{tool._END_MARKER}\n"
        "Footer line\n"
    )
    rulefile.write_text(initial_content, encoding="utf-8")

    result = asyncio.run(
        tool.run(
            {
                "version": "v0.1.0",
                "rulefile": str(rulefile),
                "tmp_dir_path": str(downloads),
            }
        )
    )

    assert result["success"] is True
    content = rulefile.read_text(encoding="utf-8")
    assert "outdated content" not in content
    assert "Header line" in content and "Footer line" in content
    assert result["rulefile_updated"] is True


def test_download_404(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tool = SetupTool()

    def fake_urlopen(url, timeout=30):
        raise setup_tool_module.urlerror.HTTPError(url, 404, "Not Found", hdrs=None, fp=None)

    monkeypatch.setattr(setup_tool_module.urlrequest, "urlopen", fake_urlopen)

    result = asyncio.run(
        tool.run(
            {
                "version": "v9.9.9",
                "rulefile": str(tmp_path / "AGENTS.md"),
                "tmp_dir_path": str(tmp_path / "downloads"),
            }
        )
    )
    assert result["success"] is False
    assert "404" in result["message"]


def test_bad_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tool = SetupTool()
    monkeypatch.setattr(
        setup_tool_module.urlrequest,
        "urlopen",
        lambda url, timeout=30: DummyResponse(b"not-a-zip"),
    )

    result = asyncio.run(
        tool.run(
            {
                "version": "v0.1.0",
                "rulefile": str(tmp_path / "AGENTS.md"),
                "tmp_dir_path": str(tmp_path / "downloads"),
            }
        )
    )

    assert result["success"] is False
    assert "zip" in result["message"].lower()
