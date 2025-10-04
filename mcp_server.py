from fastmcp import FastMCP
from pathlib import Path
import sys
import os

try:
    import yaml
except Exception:
    print("[ERROR] PyYAML is required. Please `pip install -e .[mcp]`.", file=sys.stderr)
    raise

from mcp_app.tools.agent_ethan_setup import SetupTool

# Import additional tools here as needed
# from mcp_app.tools.example import ExampleTool

mcp = FastMCP("agent-ethan-guide-mcp")

# AUTO-REGISTER MARKER (do not remove): {VFMCP-AUTO-REGISTER}


@mcp.tool(name="setup")
async def setup(version: str) -> dict:
    """
    Download agent-ethan2 framework from GitHub and update rule file.
    
    Downloads the specified version of agent-ethan2, extracts it to the configured directory,
    and updates the configured rulefile with the location of the downloaded documentation and source code.
    
    Configuration is done via environment variables:
    - SETUP_RULEFILE: Path to rule file (default: "AGENTS.md")
    - SETUP_TMP_DIR: Directory for download/extraction (default: "./tmp")
    
    Args:
        version: agent-ethan2 version tag (e.g., "v0.1.0")
    
    Returns:
        Dictionary with success status, message, download_path, and rulefile_updated flag
    """
    # Get configuration from environment variables
    rulefile = os.getenv("SETUP_RULEFILE", "AGENTS.md")
    tmp_dir_path = os.getenv("SETUP_TMP_DIR", "./tmp")
    
    tool = SetupTool()
    result = await tool.run(
        {
            "version": version,
            "rulefile": rulefile,
            "tmp_dir_path": tmp_dir_path,
        }
    )
    return result

def load_run_options(path: str = None) -> dict:
    """Load run options from server config file."""
    if path is None:
        # Try current directory first, then package directory
        cwd_config = Path("configs/server.yaml")
        pkg_config = Path(__file__).parent / "configs" / "server.yaml"
        p = cwd_config if cwd_config.exists() else pkg_config
    else:
        p = Path(path)
    
    if not p.exists():
        return {"transport": "stdio"}  # 既定値
    
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    opts = data.get("run_options") or {}
    opts.setdefault("transport", "stdio")
    return opts

def main():
    """Main entry point for agent-ethan-guide-mcp server."""
    run_options = load_run_options()
    # 設定をそのまま FastMCP.run に渡す
    mcp.run(**run_options)

if __name__ == "__main__":
    main()
