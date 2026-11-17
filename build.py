"""python3 build.py -> rebuilds the animated SVGs for the GitHub profile README, in a dark and a light version.

Animations are SMIL (<animate>/<set>) plus a little CSS, which GitHub renders inside <img>.
Monospace text uses textLength, so every character is exactly CW wide whatever font the
viewer has, and the typed text, the clip and the cursor always line up.
"""

from pathlib import Path

OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

THEMES = {
    "dark": dict(bg="#040507", fg="#ffffff", text="#AEB5B8", line="#525252", soft="#1c1c1c", echo="#AEB5B8"),
    "light": dict(bg="#e4e4e4", fg="#1a1a1a", text="#3a3a3a", line="#6f6f6f", soft="#f6f6f6", echo="#6f6f6f"),
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"
DISPLAY = "Outfit, 'Arial Black', 'Helvetica Neue', Arial, sans-serif"

# the DS dot matrix, the same as on the contact and portfolio banners
DOTS = [
    (99, 115),
    (117, 115),
    (135, 115),
    (153, 115),
    (225, 115),
    (243, 115),
    (261, 115),
    (279, 115),
    (99, 133),
    (117, 133),
    (153, 133),
    (171, 133),
    (207, 133),
    (225, 133),
    (99, 151),
    (117, 151),
    (171, 151),
    (207, 151),
    (225, 151),
    (243, 151),
    (261, 151),
    (99, 169),
    (117, 169),
    (171, 169),
    (225, 169),
    (243, 169),
    (261, 169),
    (279, 169),
    (99, 187),
    (117, 187),
    (171, 187),
    (261, 187),
    (279, 187),
    (99, 205),
    (117, 205),
    (135, 205),
    (153, 205),
    (207, 205),
    (225, 205),
    (243, 205),
    (261, 205),
]



def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def mono_text(x, y, s, size, cw, fill, extra=""):
    """Monospace text forced to len(s) * cw wide."""
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
            f'textLength="{len(s) * cw:.1f}" lengthAdjust="spacingAndGlyphs" xml:space="preserve"{extra}>{esc(s)}</text>')


def discrete(attr, frames, dur, extra=""):
    """frames: list of (time_s, value) starting at 0 -> one discrete SMIL animation over dur."""
    times = ";".join(f"{t / dur:.5f}" for t, _ in frames)
    values = ";".join(str(v) for _, v in frames)
    return (f'<animate attributeName="{attr}" dur="{dur}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{times}" values="{values}"{extra}/>')


def clean(frames):
    """Sort, drop duplicate times (keep last) and make sure the list starts at 0."""
    out = {}
    for t, v in sorted(frames, key=lambda f: f[0]):
        out[round(t, 4)] = v
    items = sorted(out.items())
    if items[0][0] != 0:
        items.insert(0, (0, items[0][1]))
    return items


# ---------------------------------------------------------------- banner

PROMPT = "dias@github:~$ "
# same commands as the tab title on the sites
COMMANDS = ["hello, world", "studying...", "writing code", "sudo say hi", "ping dias"]
TYPE, DELETE, HOLD, GAP = 0.11, 0.055, 1.8, 0.45
MARQUEE = "STUDYING & WRITING CODE * NIXOS ON EVERYTHING * HOMELAB * FRONT-END * "


def banner(t):
    W, H = 1200, 400
    split = 320  # bottom of the main row, the marquee row sits under it
    cw, size = 15.6, 26
    px, py = 390, 92
    ty = 202
    tx = px + len(PROMPT) * cw

    # typing schedule
    windows, now = [], 0.0
    for cmd in COMMANDS:
        n = len(cmd)
        windows.append((now, cmd))
        now += n * TYPE + HOLD + n * DELETE + GAP
    cycle = round(now, 2)

    parts = []
    cursor_frames = [(0, tx)]
    for i, (start, cmd) in enumerate(windows):
        n = len(cmd)
        frames = [(0, 0)]
        for k in range(1, n + 1):
            frames.append((start + k * TYPE, k * cw))
        held = start + n * TYPE + HOLD
        for k in range(n - 1, -1, -1):
            frames.append((held + (n - k) * DELETE, k * cw))
        # cursor follows the same steps
        cursor_frames += [(ft, tx + w) for ft, w in frames[1:]]
        frames = clean(frames)
        parts.append(
            f'<clipPath id="cmd{i}"><rect x="{tx}" y="{py - 30}" width="0" height="42">'
            f'{discrete("width", frames, cycle)}</rect></clipPath>'
            f'<g clip-path="url(#cmd{i})">{mono_text(tx, py, cmd, size, cw, t["fg"])}</g>'
        )
    cursor_frames = clean(cursor_frames)
    cursor = (f'<rect x="{tx}" y="{py - 22}" width="{cw * 0.9:.1f}" height="28" fill="{t["text"]}">'
              f'{discrete("x", cursor_frames, cycle)}'
              f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite" calcMode="discrete"/>'
              f'</rect>')

    # dots: pop in along the diagonal, then flicker now and then (the "possessed" pictures)
    dot_css, dots = [], []
    for i, (x, y) in enumerate(DOTS):
        delay = 0.15 + ((x - 99) + (y - 115)) / 900
        flick = 3 + (i * 7919 % 97) / 97 * 9
        dots.append(f'<circle class="d" cx="{x}" cy="{y}" r="8.6" style="animation-delay:{delay:.2f}s,{flick:.2f}s"/>')
    dot_css = f"""
      .d {{ fill: {t['fg']}; transform-box: fill-box; transform-origin: center;
            animation: pop .45s cubic-bezier(.3,1.6,.5,1) both, flick 9s steps(1) infinite; }}
      @keyframes pop {{ from {{ transform: scale(0); }} to {{ transform: scale(1); }} }}
      @keyframes flick {{ 0%, 93%, 100% {{ opacity: 1; }} 94% {{ opacity: .15; }} 96% {{ opacity: 1; }} 97% {{ opacity: .3; }} }}
    """

    # big title with two sliced echoes that glitch sideways every few seconds
    title = "Dias Stas"
    tattr = f'font-family="{DISPLAY}" font-size="84" font-weight="900" letter-spacing="-2"'
    title_svg = f"""
    <clipPath id="sliceA"><rect x="380" y="142" width="700" height="20"/></clipPath>
    <clipPath id="sliceB"><rect x="380" y="176" width="700" height="14"/></clipPath>
    <text x="388" y="{ty}" {tattr} fill="{t['fg']}" class="title">{title}</text>
    <g clip-path="url(#sliceA)"><rect class="echoA" x="380" y="142" width="700" height="20" fill="{t['bg']}"/><text class="echoA" x="388" y="{ty}" {tattr} fill="{t['echo']}">{title}</text></g>
    <g clip-path="url(#sliceB)"><rect class="echoB" x="380" y="176" width="700" height="14" fill="{t['bg']}"/><text class="echoB" x="388" y="{ty}" {tattr} fill="{t['fg']}">{title}</text></g>
    """
    title_css = """
      .title { animation: rise .8s .3s cubic-bezier(.2,.8,.2,1) both; }
      @keyframes rise { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
      .echoA, .echoB { opacity: 0; }
      .echoA { animation: glitchA 5s 2s steps(1) infinite; }
      .echoB { animation: glitchB 5s 2s steps(1) infinite; }
      @keyframes glitchA { 0%, 100% { opacity: 0; transform: none; } 80% { opacity: 1; transform: translateX(14px); } 83% { opacity: 1; transform: translateX(-9px); } 86% { opacity: 1; transform: translateX(5px); } 88% { opacity: 0; transform: none; } }
      @keyframes glitchB { 0%, 100% { opacity: 0; transform: none; } 81% { opacity: 1; transform: translateX(-16px); } 84% { opacity: 1; transform: translateX(10px); } 87% { opacity: 0; transform: none; } }
    """

    # marquee row: the phrase repeated, sliding one phrase width, so the loop has no seam
    msize, mcw = 22, 13.2
    phrase_w = len(MARQUEE) * mcw
    reps = int(W * 2 / phrase_w) + 2
    my = split + (H - split) / 2 + 8
    marquee = "".join(mono_text(f"{20 + r * phrase_w:.1f}", f"{my:.1f}", MARQUEE, msize, mcw, t["fg"]) for r in range(reps))
    marquee_svg = (f'<clipPath id="mq"><rect x="1" y="{split}" width="{W - 2}" height="{H - split - 1}"/></clipPath>'
                   f'<g clip-path="url(#mq)"><g>{marquee}'
                   f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{-phrase_w:.1f} 0" '
                   f'dur="{phrase_w / 60:.2f}s" repeatCount="indefinite"/></g></g>')

    sub = [
        mono_text(390, 250, "front-end developer · belgium", 24, 14.4, t["text"]),
        mono_text(390, 286, "nixos · homelab · hand-made websites", 24, 14.4, t["text"]),
    ]
    sub_css = """
      .sub { animation: rise .7s 1s cubic-bezier(.2,.8,.2,1) both; }
    """

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Dias Stas - front-end developer, NixOS and homelab">
  <style>{dot_css}{title_css}{sub_css}</style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="{t['bg']}" stroke="{t['line']}"/>
  <line x1="0" y1="{split}" x2="{W}" y2="{split}" stroke="{t['line']}"/>
  <line x1="340" y1="40" x2="340" y2="{split - 40}" stroke="{t['line']}"/>
  <g>{''.join(dots)}</g>
  {mono_text(px, py, PROMPT, size, cw, t['text'])}
  {''.join(parts)}
  {cursor}
  {title_svg}
  <g class="sub">{''.join(sub)}</g>
  {marquee_svg}
</svg>
"""


# ---------------------------------------------------------------- terminal

SESSION = [
    ("$", "whoami"),
    (">", "dias stas — i like to make stuff, mostly for my homelab"),
    ("$", "cat stack.txt"),
    (">", "html  css  javascript  nix  linux  git"),
    ("$", "ls ~/sites"),
    ("dir", "hello/  contact/  blog/  docs/"),
    ("$", "uname -a"),
    (">", "SlashyOS 1.0 · niri · noctalia · fish · kitty"),
    ("$", "ping dias"),
    (">", "64 bytes from contact.errornoslash.be: time=0.1ms"),
]


def terminal(t):
    W = 900
    cw, size, lh = 11.4, 19, 34
    top, left = 78, 32
    H = top + len(SESSION) * lh + lh + 24
    TYPE_T, PAUSE, OUT_PAUSE, END_HOLD = 0.07, 0.35, 0.5, 6.0

    # schedule
    events, now = [], 0.9
    for kind, s in SESSION:
        if kind == "$":
            events.append((kind, s, now))
            now += len(s) * TYPE_T + PAUSE
        else:
            events.append((kind, s, now))
            now += OUT_PAUSE
    final_prompt_t = now
    cycle = round(now + END_HOLD, 2)

    lines = []
    cursor_x, cursor_y = [(0, left + 2 * cw)], [(0, top - 20)]
    for i, (kind, s, start) in enumerate(events):
        y = top + i * lh
        if kind == "$":
            x0 = left + 2 * cw
            frames = [(0, 0)] + [(start + k * TYPE_T, k * cw) for k in range(1, len(s) + 1)]
            frames = clean(frames)
            show = clean([(0, "hidden"), (start, "visible")])
            lines.append(
                f'<g visibility="hidden">{discrete("visibility", show, cycle)}'
                f'{mono_text(left, y, "$", size, cw, t["text"])}</g>'
                f'<clipPath id="t{i}"><rect x="{x0}" y="{y - 22}" width="0" height="30">{discrete("width", frames, cycle)}</rect></clipPath>'
                f'<g clip-path="url(#t{i})">{mono_text(x0, y, s, size, cw, t["fg"])}</g>'
            )
            cursor_x += [(start, x0)] + [(ft, x0 + w) for ft, w in frames[1:]]
            cursor_y += [(start, y - 18)]
        else:
            show = clean([(0, "hidden"), (start, "visible")])
            color = t["fg"] if kind == "dir" else t["text"]
            weight = ' font-weight="700"' if kind == "dir" else ""
            lines.append(f'<g visibility="hidden">{discrete("visibility", show, cycle)}'
                         f'{mono_text(left, y, s, size, cw, color, weight)}</g>')
    # last empty prompt
    fy = top + len(events) * lh
    show = clean([(0, "hidden"), (final_prompt_t, "visible")])
    lines.append(f'<g visibility="hidden">{discrete("visibility", show, cycle)}{mono_text(left, fy, "$", size, cw, t["text"])}</g>')
    cursor_x += [(final_prompt_t, left + 2 * cw)]
    cursor_y += [(final_prompt_t, fy - 18)]

    cursor = (f'<rect x="{left + 2 * cw}" y="{top - 18}" width="{cw * 0.9:.1f}" height="22" fill="{t["text"]}">'
              f'{discrete("x", clean(cursor_x), cycle)}{discrete("y", clean(cursor_y), cycle)}'
              f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite" calcMode="discrete"/>'
              f'</rect>')

    bar = 44
    title = "dias@github: ~"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="A terminal: whoami, the stack, the sites and the system Dias runs">
  <rect x="9.5" y="9.5" width="{W - 10}" height="{H - 10}" fill="{t['line']}"/>
  <rect x="0.5" y="0.5" width="{W - 10}" height="{H - 10}" fill="{t['bg']}" stroke="{t['line']}"/>
  <rect x="0.5" y="0.5" width="{W - 10}" height="{bar}" fill="{t['soft']}" stroke="{t['line']}"/>
  <g fill="none" stroke="{t['text']}" stroke-width="1.5">
    <circle cx="26" cy="{bar / 2 + .5}" r="6"/><circle cx="48" cy="{bar / 2 + .5}" r="6"/><circle cx="70" cy="{bar / 2 + .5}" r="6"/>
  </g>
  {mono_text((W - 10) / 2 - len(title) * 5.4, bar / 2 + 6, title, 17, 10.8, t['text'])}
  {''.join(lines)}
  {cursor}
</svg>
"""


for name, theme in THEMES.items():
    (OUT / f"banner-{name}.svg").write_text(banner(theme))
    (OUT / f"terminal-{name}.svg").write_text(terminal(theme))
print("ok")
