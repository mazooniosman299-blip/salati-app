"""Compatibility entry for the corrected playback/on-off-only blue scope."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("audio-control-colors.py")),run_name="__main__")
