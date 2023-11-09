from pathlib import Path
import tomli
from linkedin_summarizer.configuration.config import cfg


def read_toml(file: Path) -> dict:
    with open(file, "rb") as f:
        return tomli.load(f)


def read_prompts_toml() -> dict:
    return read_toml(cfg.project_root / "configuration" / "prompts.toml")


prompts = read_prompts_toml()
