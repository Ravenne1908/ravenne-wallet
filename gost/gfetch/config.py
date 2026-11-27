"""Configuration: config.json, environment overrides, color parsing.

Environment variables (same names as the original GhosttyFetch):
  GHOSTTY_FPS     playback speed override (float)
  GHOSTTY_COLOR   brand color override (hex, raw ANSI, or off)
  FORCE_COLOR     force colors even when output is piped
  NO_COLOR        disable all colors (https://no-color.org/)

A color value is parsed as:
  "" / omitted        -> default (bright white)
  0/off/false/none    -> disabled
  #rrggbb             -> 24-bit truecolor
  anything else       -> raw ANSI SGR content, e.g. "38;5;45"
"""

import json
import os
import sys
from dataclasses import dataclass, field

OFF_VALUES = {"0", "off", "false", "none"}

DEFAULT_FPS = 30.0
DEFAULT_COLOR = "#ffffff"
# Bright black & white palette: the brand outline pops in pure white while the
# fill shimmers through bright-black (gray) shades.
DEFAULT_GRADIENT = (
    "#e8e8e8",
    "#d9d9d9",
    "#c9c9c9",
    "#b9b9b9",
    "#a9a9a9",
    "#999999",
    "#898989",
    "#7a7a7a",
    "#6a6a6a",
    "#5b5b5b",
)


def parse_color(raw) -> "str | None":
    """Color value -> ANSI SGR code, or None when disabled."""
    if raw is None:
        return parse_color(DEFAULT_COLOR)
    value = str(raw).strip()
    if not value:
        return parse_color(DEFAULT_COLOR)
    lowered = value.lower()
    if lowered in OFF_VALUES:
        return None
    hex_part = lowered[1:] if lowered.startswith("#") else None
    if hex_part is not None and len(hex_part) == 6:
        try:
            r = int(hex_part[0:2], 16)
            g = int(hex_part[2:4], 16)
            b = int(hex_part[4:6], 16)
            return f"\x1b[38;2;{r};{g};{b}m"
        except ValueError:
            pass
    return f"\x1b[{value}m"


def _parse_bool(raw, fallback: bool) -> bool:
    if raw is None:
        return fallback
    if isinstance(raw, bool):
        return raw
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


def _script_dir() -> str:
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        return os.getcwd()


def search_dirs() -> "list[str]":
    """Directories searched for data files, in priority order."""
    dirs = [
        os.path.dirname(os.path.abspath(sys.argv[0])) or os.getcwd(),
        os.getcwd(),
        os.path.dirname(_script_dir()),
        _script_dir(),
    ]
    appdata = os.environ.get("APPDATA") or os.environ.get("XDG_CONFIG_HOME")
    if appdata:
        dirs.append(os.path.join(appdata, "ghosttyfetch"))
    else:
        home = os.path.expanduser("~/.config")
        dirs.append(os.path.join(home, "ghosttyfetch"))
    seen, unique = set(), []
    for d in dirs:
        if d and d not in seen:
            seen.add(d)
            unique.append(d)
    return unique


def find_data_file(name: str) -> "str | None":
    for directory in search_dirs():
        candidate = os.path.join(directory, name)
        if os.path.isfile(candidate):
            return candidate
    return None


@dataclass
class Prefs:
    """Fully resolved runtime preferences."""

    fps: float = DEFAULT_FPS
    brand_color: "str | None" = field(default_factory=lambda: parse_color(DEFAULT_COLOR))
    gradient_colors: tuple = DEFAULT_GRADIENT
    gradient_scroll: bool = True
    gradient_scroll_speed: float = 10.0
    animation_file: str = "animation.json"
    center: bool = True
    sync_output: bool = True
    cycles: int = 0  # 0 = loop forever
    force_color: bool = False
    no_color: bool = False

    @property
    def colors_enabled(self) -> bool:
        return not self.no_color

    def gradient_codes(self) -> "list[str | None]":
        return [parse_color(c) for c in self.gradient_colors] or [None]


def _first_int(data: dict, key: str) -> "int | None":
    raw = data.get(key)
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _first_float(data: dict, key: str) -> "float | None":
    raw = data.get(key)
    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def load_prefs(config_path: "str | None" = None, cli=None) -> Prefs:
    """Build Prefs from config.json + environment + CLI overrides."""
    data = {}
    path = config_path or find_data_file("config.json")
    if path:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
            if isinstance(loaded, dict):
                data = loaded
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ghosttyfetch: ignoring unreadable config '{path}': {exc}",
                  file=sys.stderr)

    env = os.environ
    fps = (
        _first_float({"fps": cli.fps}, "fps") if cli and cli.fps is not None else None
    )
    if fps is None and env.get("GHOSTTY_FPS"):
        fps = _first_float({"fps": env["GHOSTTY_FPS"]}, "fps")
    if fps is None:
        fps = _first_float(data, "fps")

    color_raw = None
    if cli is not None:
        color_raw = cli.color
    if color_raw is None and env.get("GHOSTTY_COLOR"):
        color_raw = env["GHOSTTY_COLOR"]
    if color_raw is None and data.get("color") is not None:
        color_raw = str(data.get("color"))
    if color_raw == "default":
        color_raw = None

    gradient_raw = data.get("white_gradient_colors")
    gradient_colors = (
        tuple(gradient_raw) if isinstance(gradient_raw, list) and gradient_raw
        else DEFAULT_GRADIENT
    )

    force = cli.force_color if cli and cli.force_color else "FORCE_COLOR" in env
    no_color = cli.no_color if cli and cli.no_color else "NO_COLOR" in env
    if not force:
        force = _parse_bool(data.get("force_color"), False)
    if not no_color:
        no_color = _parse_bool(data.get("no_color"), False)

    scroll = _parse_bool(data.get("white_gradient_scroll"), True)
    if cli is not None and cli.no_scroll:
        scroll = False

    speed = _first_float(data, "white_gradient_scroll_speed") or 10.0

    animation = data.get("animation_file") or "animation.json"
    if cli is not None and cli.animation:
        animation = cli.animation

    cycles = _first_int(data, "cycles") or 0
    if cli is not None and cli.cycles is not None:
        cycles = cli.cycles
    if cli is not None and cli.once:
        cycles = 1

    center = _parse_bool(data.get("center"), True)
    if cli is not None and cli.no_center:
        center = False

    sync = _parse_bool(data.get("sync_output"), True)

    return Prefs(
        fps=fps or DEFAULT_FPS,
        brand_color=parse_color(color_raw),
        gradient_colors=gradient_colors,
        gradient_scroll=scroll,
        gradient_scroll_speed=speed,
        animation_file=animation,
        center=center,
        sync_output=sync,
        cycles=cycles,
        force_color=bool(force),
        no_color=bool(no_color),
    )
