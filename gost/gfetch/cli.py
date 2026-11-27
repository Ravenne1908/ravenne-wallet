"""Command line interface and playback loop."""

import argparse
import os
import sys
import time

from . import __version__, frames, term
from .config import find_data_file, load_prefs, parse_color


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ghosttyfetch",
        description="Animated Ghostty logo splash for your terminal "
                    "(Windows port of GhosttyFetch).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--animation", metavar="FILE",
        help="animation data file (default: animation.json next to the script; "
             "ship ansi.json for the compact half-block variant)",
    )
    parser.add_argument("--config", metavar="FILE", help="custom config.json path")
    parser.add_argument("--fps", type=float, help="playback speed in frames per second")
    parser.add_argument(
        "--color", metavar="COLOR",
        help="brand color: #rrggbb hex, raw ANSI like 38;5;45, or 'off'",
    )
    parser.add_argument("--force-color", action="store_true",
                        help="force colors even when output is piped")
    parser.add_argument("--no-color", action="store_true", help="disable all colors")
    parser.add_argument("--no-center", action="store_true",
                        help="draw the logo from the left edge instead of centered")
    parser.add_argument("--no-scroll", action="store_true",
                        help="freeze the gradient instead of scrolling it")
    parser.add_argument("--once", action="store_true",
                        help="play a single cycle then exit")
    parser.add_argument("--cycles", type=int, metavar="N",
                        help="number of cycles to play (0 = loop forever, default)")
    parser.add_argument(
        "--frame", type=int, metavar="N",
        help="non-interactive mode: render this single frame index to stdout "
             "and exit (useful for previews and scripting)",
    )
    return parser


def _layout(cols: int, rows: int, src_w: int, src_h: int):
    """Destination art size that fits the terminal and keeps the aspect ratio."""
    reserved = 3
    art_h = rows - reserved if rows > reserved + 10 else max(10, rows - reserved)
    art_w = cols
    if src_h > 0:
        art_w = min(art_w, (art_h * src_w) // src_h)
    return max(1, art_w), max(1, art_h)


def _find_animation(cli) -> str:
    candidates = []
    if cli.animation:
        candidates.append(cli.animation)
    for name in (getattr(cli, "animation_file_hint", None), "animation.json"):
        if name:
            found = find_data_file(name)
            if found:
                candidates.append(found)
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    searched = [c for c in candidates if c] or ["animation.json"]
    raise SystemExit(
        "ghosttyfetch: animation file not found. Tried: "
        + ", ".join(searched)
        + " — keep animation.json next to ghosttyfetch.py or pass --animation FILE."
    )


def _render_single(prefs, scaler, renderer, cache, frame_index, pad):
    scroll = 0
    return renderer.render(cache.get(frame_index), scroll, pad)


def main(argv=None) -> int:
    parser = build_parser()
    cli = parser.parse_args(argv)

    term.force_utf8()
    is_tty = term.is_tty()
    if is_tty and not term.enable_virtual_terminal():
        print(
            "ghosttyfetch: warning: ANSI escape codes are not enabled for this "
            "console. Use Windows Terminal (recommended) or a Windows 10+ "
            "console host.",
            file=sys.stderr,
        )

    # Prefs need the animation choice from config.json, so peek at it first.
    hint = None
    if not cli.animation and cli.config is None:
        try:
            import json

            path = find_data_file("config.json")
            if path:
                with open(path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                if isinstance(data, dict) and data.get("animation_file"):
                    hint = str(data["animation_file"])
        except (OSError, json.JSONDecodeError):
            hint = None
    cli.animation_file_hint = hint

    prefs = load_prefs(cli.config, cli)
    animation_path = _find_animation(cli)
    raw_frames, src_w, src_h = frames.load_animation(animation_path)
    frame_count = len(raw_frames)

    cols, rows = term.terminal_size()
    art_w, art_h = _layout(cols, rows, src_w, src_h)
    scaler = frames.Scaler(src_w, src_h, art_w, art_h)
    cache = frames.FrameCache(raw_frames, scaler)

    colors_on = prefs.colors_enabled and (is_tty or prefs.force_color)
    renderer = frames.Renderer(
        prefs.brand_color,
        [parse_color(c) for c in prefs.gradient_colors],
        colors_on,
    )
    pad = (cols - art_w) // 2 if prefs.center else 0

    # Non-interactive: render one frame to stdout (or a pipe) and exit.
    if not is_tty or cli.frame is not None:
        index = cli.frame if cli.frame is not None else frame_count // 2
        index = max(0, min(index, frame_count - 1))
        sys.stdout.write(_render_single(prefs, scaler, renderer, cache, index, pad))
        return 0

    # Interactive playback loop.
    total_target = None if prefs.cycles <= 0 else prefs.cycles * frame_count
    frame_dur = 1.0 / prefs.fps
    scroll_speed = (
        prefs.gradient_scroll_speed
        if (prefs.gradient_scroll and renderer.gradient_active)
        else 0.0
    )
    sync_wrap = (
        (term.SYNC_OUTPUT_ON, term.SYNC_OUTPUT_OFF) if prefs.sync_output else ("", "")
    )

    start = time.monotonic()
    next_deadline = start
    out = sys.stdout
    art_bottom = art_h

    try:
        out.write(term.HIDE_CURSOR)
        while True:
            now = time.monotonic()
            elapsed = now - start
            played = int(elapsed * prefs.fps)

            if total_target is not None and played >= total_target:
                break

            index = played % frame_count
            scroll = int(elapsed * scroll_speed) if scroll_speed > 0 else 0
            rendered = renderer.render(cache.get(index), scroll, pad)
            out.write(sync_wrap[0] + term.CLEAR_SCREEN + rendered + sync_wrap[1])
            out.flush()

            new_cols, new_rows = term.terminal_size()
            if (new_cols, new_rows) != (cols, rows):
                cols, rows = new_cols, new_rows
                art_w, art_h = _layout(cols, rows, src_w, src_h)
                scaler = frames.Scaler(src_w, src_h, art_w, art_h)
                cache.resize(scaler)
                pad = (cols - art_w) // 2 if prefs.center else 0
                art_bottom = art_h

            next_deadline += frame_dur
            delay = next_deadline - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            else:
                # Rendering fell behind (first cycle scales frames): resynchronize
                # instead of bursting several frames at once.
                next_deadline = time.monotonic()
    except KeyboardInterrupt:
        pass
    finally:
        if is_tty:
            out.write(term.SHOW_CURSOR + term.RESET_ATTRS + "\n")
            out.flush()
    return 0
