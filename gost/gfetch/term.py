"""Terminal helpers: Windows VT enablement, size detection, escape codes.

On Windows 10+ the console needs ENABLE_VIRTUAL_TERMINAL_PROCESSING set for
ANSI escape sequences to work; in Windows Terminal it is already on. On other
platforms this module is a no-op.
"""

import os
import sys

STD_OUTPUT_HANDLE = -11
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

# Escape sequences
CLEAR_SCREEN = "\x1b[H\x1b[2J"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
RESET_ATTRS = "\x1b[0m"
SYNC_OUTPUT_ON = "\x1b[?2026h"
SYNC_OUTPUT_OFF = "\x1b[?2026l"


def enable_virtual_terminal() -> bool:
    """Turn on ANSI escape processing; returns True when available."""
    if not sys.platform.startswith("win"):
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        if mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING:
            return True
        ok = kernel32.SetConsoleMode(
            handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        )
        return bool(ok)
    except Exception:
        return False


def terminal_size() -> "tuple[int, int]":
    """Current (columns, rows); falls back to 120x40 when not a terminal."""
    try:
        size = os.get_terminal_size(sys.__stdout__.fileno())
        if size.columns > 0 and size.lines > 0:
            return size.columns, size.lines
    except (OSError, ValueError, AttributeError):
        pass
    return 120, 40


def is_tty(stream=None) -> bool:
    return (stream if stream is not None else sys.stdout).isatty()


def force_utf8(stream=None) -> None:
    """Ensure UTF-8 output even when piped through a legacy code page."""
    stream = stream if stream is not None else sys.stdout
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
