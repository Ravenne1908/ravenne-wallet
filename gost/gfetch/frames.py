"""Frame loading, parsing, scaling and gradient rendering.

The animation assets are plain JSON: a list of frames where each frame is a
string of lines joined by '\\n'. Characters wrapped in <span class="b">...</span>
are "brand" glyphs (the Ghostty outline) and receive the brand color; every
other glyph receives the per-line gradient color.

The resampler is a port of the voting scaler from the original GhosttyFetch
(Zig, MIT): when shrinking, each destination cell keeps the dominant glyph
over the source cells it covers (majority vote, brand flag included); when
growing, nearest-neighbor sampling is used.
"""

import json

SPAN_OPEN = '<span class="b">'
SPAN_CLOSE = "</span>"
RESET = "\x1b[0m"


def load_animation(path: str):
    """Read an animation JSON file -> (raw_frames, src_width, src_height)."""
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    raw = [
        "\n".join(frame) if isinstance(frame, list) else str(frame)
        for frame in data["frames"]
    ]
    if not raw:
        raise ValueError(f"no frames found in {path}")
    src_h = int(data.get("lines_per_frame") or raw[0].count("\n") + 1)
    if src_h <= 0:
        src_h = 1
    src_w = int(data.get("max_width") or max(len(parse_line(l)[0]) for l in raw[0].split("\n")))
    if src_w <= 0:
        src_w = 1
    return raw, src_w, src_h


def parse_line(line: str):
    """Markup line -> (plain text, brand mask with one bool per character)."""
    if SPAN_OPEN not in line:
        return line, [False] * len(line)
    plain, mask, branded = [], [], False
    i, n = 0, len(line)
    while i < n:
        if line.startswith(SPAN_OPEN, i):
            branded = True
            i += len(SPAN_OPEN)
            continue
        if line.startswith(SPAN_CLOSE, i):
            branded = False
            i += len(SPAN_CLOSE)
            continue
        plain.append(line[i])
        mask.append(branded)
        i += 1
    return "".join(plain), mask


def _sample_map(src: int, dst: int):
    """For each destination index, the tuple of source indices it covers."""
    if dst <= 0:
        return ()
    if src <= 0:
        return tuple(() for _ in range(dst))
    if src == dst:
        return tuple((i,) for i in range(dst))
    if src > dst:
        out = []
        for i in range(dst):
            start = (i * src) // dst
            end = ((i + 1) * src + dst - 1) // dst
            if end <= start:
                end = start + 1
            if end > src:
                end = src
            out.append(tuple(range(start, end)))
        return tuple(out)
    if src == 1:
        return tuple((0,) for _ in range(dst))
    step = (src - 1) / (dst - 1)
    return tuple((min(int(i * step), src - 1),) for i in range(dst))


def _finalize(plain: str, mask):
    """Compress (plain, mask) into ordered color segments for rendering."""
    segments = []
    has_art = False
    n = len(plain)
    i = 0
    while i < n:
        branded = mask[i]
        j = i + 1
        while j < n and mask[j] == branded:
            j += 1
        text = plain[i:j]
        if not has_art and text.strip(" \t\r"):
            has_art = True
        segments.append((text, branded))
        i = j
    return segments, n, has_art


class Scaler:
    """Precomputed index maps for one source -> destination size conversion."""

    def __init__(self, src_w: int, src_h: int, dst_w: int, dst_h: int):
        self.src_w, self.src_h = src_w, src_h
        self.dst_w, self.dst_h = dst_w, dst_h
        self.identity = src_w == dst_w and src_h == dst_h
        self._cols = _sample_map(src_w, dst_w)
        self._rows = _sample_map(src_h, dst_h)

    def scale_frame(self, raw_frame: str):
        """Raw markup frame -> list of scaled lines [(segments, width, has_art)]."""
        src = self._parse_normalized(raw_frame)
        if self.identity:
            return [_finalize(plain, mask) for plain, mask in src]
        lines = []
        for rows in self._rows:
            if len(rows) == 1:
                plain, mask = src[rows[0]]
                lines.append(self._scale_row(plain, mask))
            else:
                lines.append(self._blend_rows(src, rows))
        return lines

    def _parse_normalized(self, raw_frame: str):
        """Parse a raw frame into exactly src_h lines of src_w characters."""
        width, height = self.src_w, self.src_h
        src = []
        for line in raw_frame.split("\n")[:height]:
            plain, mask = parse_line(line)
            pad = width - len(plain)
            if pad > 0:
                plain += " " * pad
                mask += [False] * pad
            src.append((plain, mask))
        while len(src) < height:
            src.append((" " * width, [False] * width))
        return src

    def _scale_row(self, plain: str, mask):
        """Horizontal resample of a single source row."""
        if self.dst_w == len(plain):
            return _finalize(plain, mask)
        chars, brands = [], []
        for cols in self._cols:
            if len(cols) == 1:
                chars.append(plain[cols[0]])
                brands.append(mask[cols[0]])
            else:
                char, branded = _vote([(plain, mask, c) for c in cols])
                chars.append(char)
                brands.append(branded)
        return _finalize("".join(chars), brands)

    def _blend_rows(self, src, rows):
        """Vote across the block of source rows/columns covering one output row."""
        chars, brands = [], []
        for cols in self._cols:
            cells = [(src[r][0], src[r][1], c) for r in rows for c in cols]
            char, branded = _vote(cells)
            chars.append(char)
            brands.append(branded)
        return _finalize("".join(chars), brands)


def _vote(cells):
    """Dominant glyph + brand majority over the source cells an output covers."""
    counts = {}
    brand_votes = 0
    for plain, mask, col in cells:
        try:
            char = plain[col]
            branded = mask[col]
        except IndexError:
            continue
        counts[char] = counts.get(char, 0) + 1
        if branded:
            brand_votes += 1
    if not counts:
        return " ", False
    # max() keeps the first-encountered glyph on ties, matching the original.
    best = max(counts, key=counts.get)
    total = sum(counts.values())
    return best, brand_votes * 2 >= total


class FrameCache:
    """Lazily parsed and scaled frames, invalidated when the terminal resizes."""

    def __init__(self, raw_frames, scaler: Scaler):
        self.raw = raw_frames
        self.scaler = scaler
        self._cache = {}

    def get(self, frame_index: int):
        scaled = self._cache.get(frame_index)
        if scaled is None:
            scaled = self.scaler.scale_frame(self.raw[frame_index])
            self._cache[frame_index] = scaled
        return scaled

    def resize(self, scaler: Scaler) -> None:
        if (scaler.dst_w, scaler.dst_h) == (self.scaler.dst_w, self.scaler.dst_h):
            self.scaler = scaler
            return
        self.scaler = scaler
        self._cache.clear()


class Renderer:
    """Applies the brand color and the scrolling gradient to scaled frames."""

    def __init__(self, brand_color, gradient_codes, enabled: bool):
        self.brand = brand_color if enabled else None
        self.gradient = [c for c in gradient_codes if c] if enabled else []
        self.enabled = enabled

    @property
    def gradient_active(self) -> bool:
        return bool(self.gradient)

    def render(self, scaled_lines, scroll_step: int, pad_left: int) -> str:
        """One scaled frame -> a full ANSI string ready to write to the terminal."""
        has_spans = any(seg[1] for line in scaled_lines for seg in line[0])

        start, end = -1, -1
        for i, (_, _, has_art) in enumerate(scaled_lines):
            if has_art:
                if start < 0:
                    start = i
                end = i
        art_height = (end - start + 1) if start >= 0 else 0

        gradient = self.gradient
        pad = " " * pad_left if pad_left > 0 else ""
        out = []

        for line_idx, (segments, _, _) in enumerate(scaled_lines):
            base = None
            if gradient and start <= line_idx <= end:
                if len(gradient) == 1 or art_height <= 1:
                    base = gradient[0]
                else:
                    relative = line_idx - start
                    step = scroll_step % art_height if scroll_step else 0
                    shifted = (relative + art_height - step) % art_height
                    index = shifted * (len(gradient) - 1) // (art_height - 1)
                    base = gradient[index]
            elif not gradient and self.brand and not has_spans:
                base = self.brand

            parts = []
            if pad:
                parts.append(pad)
            active = None
            for text, branded in segments:
                code = None
                if self.enabled:
                    if branded:
                        code = self.brand or base
                    else:
                        code = base
                if code != active:
                    parts.append(code if code else RESET)
                    active = code
                parts.append(text)
            if active is not None:
                parts.append(RESET)
            parts.append("\n")
            out.append("".join(parts))
        return "".join(out)
