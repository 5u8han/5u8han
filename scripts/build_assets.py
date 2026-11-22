#!/usr/bin/env python3
"""Builds every SVG asset used by the profile README.

    python3 scripts/build_assets.py
    python3 scripts/build_assets.py --icons node_modules/simple-icons/icons

With --icons, real brand logos are read from a Simple Icons "icons" folder
(CC0 licensed) and embedded in the role wallpapers. Anything that is not found
falls back to a neutral line glyph, so the output is always complete.
The GitHub Action in .github/workflows/logos.yml does this for you.
"""
import argparse
import html
import math
import os
import re

FONT = ('"Avenir Next", "Segoe UI", "SF Pro Text", "Helvetica Neue", Inter, '
        '"DM Sans", "Open Sans", Arial, sans-serif')


# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(s, quote=True)


def write(folder, name, text):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        f.write(text)


def wave_path(y, amp, period, width, bottom):
    """Closed, periodic wave. Starts one period left of the canvas and runs
    past the right edge so a translateX of one period loops seamlessly."""
    half = period / 2
    x_start = -period
    n = int(math.ceil((width + 3 * period) / half))
    d = f"M{x_start:.1f},{y}"
    for i in range(n):
        x0 = x_start + i * half
        cx = x0 + half / 2
        cy = y + (-2 * amp if i % 2 == 0 else 2 * amp)
        d += f" Q{cx:.1f},{cy:.1f} {x0 + half:.1f},{y}"
    x_last = x_start + n * half
    d += f" L{x_last:.1f},{bottom} L{x_start:.1f},{bottom} Z"
    return d


def stars(points):
    out = []
    for x, y, r, delay, base in points:
        out.append(
            f'<circle class="star" cx="{x}" cy="{y}" r="{r}" fill="#f4efe3" '
            f'opacity="{base}" style="animation-delay:{delay}s"/>'
        )
    return "\n    ".join(out)


def est_width(text, size):
    """Rough text width so pills fit regardless of the viewer's font."""
    narrow = set("ijltfI.,:;'|()[]/ -!")
    wide = set("mwMW@%")
    w = 0.0
    for ch in text:
        if ch in narrow:
            w += 0.32
        elif ch in wide:
            w += 0.86
        elif ch.isupper():
            w += 0.66
        elif ch.isdigit():
            w += 0.58
        else:
            w += 0.54
    return w * size


# ------------------------------------------------------------ banner/footer
def build_banner(out):
    W, H, HORIZON, SUN_X = 1280, 320, 236, 930
    banner_stars = stars([
        (700, 34, 1.4, 0.0, .7), (760, 70, 1.1, 1.2, .55), (820, 28, 1.6, 2.1, .75),
        (884, 92, 1.2, 0.6, .5), (1010, 40, 1.5, 3.3, .7), (1090, 84, 1.1, 1.8, .55),
        (1160, 30, 1.6, 2.7, .75), (1220, 76, 1.2, 0.9, .5), (1130, 132, 1.0, 3.9, .45),
        (980, 118, 1.0, 2.4, .45), (640, 92, 1.0, 4.2, .4), (560, 26, 1.2, 1.5, .55),
        (420, 44, 1.0, 3.0, .4), (300, 22, 1.1, 0.3, .5), (1250, 126, 1.0, 2.0, .4),
    ])
    waves = [
        ("w1", 248, 3.5, 120, "#a9d3dc", .14, .30),
        ("w2", 264, 5.0, 200, "#2a5c76", .60, .22),
        ("w3", 284, 6.5, 320, "#173a52", .86, .18),
    ]
    wave_svg = "\n  ".join(
        f'<path class="wave {c}" d="{wave_path(y, a, p, W, H + 20)}" fill="{f}" '
        f'fill-opacity="{fo}" stroke="#d6ecef" stroke-opacity="{so}" stroke-width="1.2"/>'
        for c, y, a, p, f, fo, so in waves
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">Subhan Noeman, Support Engineer in Chicago</title>
  <desc id="d">A calm lake at dusk with slow, drifting waves.</desc>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#101c30"/>
      <stop offset="0.55" stop-color="#21405f"/>
      <stop offset="1" stop-color="#3a6884"/>
    </linearGradient>
    <radialGradient id="glow" cx="{SUN_X}" cy="{HORIZON}" r="470" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#f6dcb4" stop-opacity="0.88"/>
      <stop offset="0.22" stop-color="#eaa98f" stop-opacity="0.48"/>
      <stop offset="0.6" stop-color="#8a7aa6" stop-opacity="0.18"/>
      <stop offset="1" stop-color="#8a7aa6" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3b6f89"/>
      <stop offset="1" stop-color="#12273a"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#f6dcb4" stop-opacity="0.5"/>
      <stop offset="0.5" stop-color="#f0b9a0" stop-opacity="0.18"/>
      <stop offset="1" stop-color="#f0b9a0" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="streak" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#f0b9a0" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#f0b9a0" stop-opacity="0.8"/>
      <stop offset="1" stop-color="#f0b9a0" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>
  <style>
    .name {{ font: 400 60px {FONT}; fill: #f3f6f4; letter-spacing: 0.3px; }}
    .role {{ font: 500 22px {FONT}; fill: #a6d6d4; letter-spacing: 0.2px; }}
    .tag  {{ font: 400 19px {FONT}; fill: #c6d5dc; }}
    .wave {{ animation: drift linear infinite; }}
    .w1 {{ animation-name: d1; animation-duration: 26s; }}
    .w2 {{ animation-name: d2; animation-duration: 36s; animation-direction: reverse; }}
    .w3 {{ animation-name: d3; animation-duration: 48s; }}
    @keyframes d1 {{ to {{ transform: translateX(-120px); }} }}
    @keyframes d2 {{ to {{ transform: translateX(-200px); }} }}
    @keyframes d3 {{ to {{ transform: translateX(-320px); }} }}
    .star {{ animation: tw 7s ease-in-out infinite; }}
    @keyframes tw {{ 0%, 100% {{ opacity: .25; }} 50% {{ opacity: .9; }} }}
    .cloud {{ animation: float 34s ease-in-out infinite alternate; }}
    @keyframes float {{ from {{ transform: translateX(-10px); }} to {{ transform: translateX(14px); }} }}
    .glints {{ animation: shimmer 8s ease-in-out infinite; }}
    @keyframes shimmer {{ 0%, 100% {{ opacity: .7; }} 50% {{ opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .wave, .star, .cloud, .glints {{ animation: none !important; }}
    }}
  </style>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#sky)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>

    {banner_stars}

    <g class="cloud">
      <rect x="700" y="166" width="400" height="6" rx="3" fill="url(#streak)" opacity=".5"/>
      <rect x="780" y="190" width="360" height="5" rx="2.5" fill="url(#streak)" opacity=".42"/>
      <rect x="690" y="210" width="300" height="4" rx="2" fill="url(#streak)" opacity=".32"/>
    </g>

    <circle cx="{SUN_X}" cy="{HORIZON - 4}" r="104" fill="url(#halo)"/>
    <circle cx="{SUN_X}" cy="{HORIZON - 4}" r="36" fill="#f8e2bd"/>

    <rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="url(#water)"/>
    <ellipse cx="{SUN_X}" cy="258" rx="190" ry="34" fill="url(#halo)" opacity=".55"/>

    {wave_svg}

    <g class="glints" fill="#f6dcb4">
      <rect x="888" y="243" width="84" height="3" rx="1.5" opacity=".75"/>
      <rect x="898" y="252" width="64" height="3" rx="1.5" opacity=".6"/>
      <rect x="906" y="262" width="48" height="3" rx="1.5" opacity=".5"/>
      <rect x="914" y="273" width="32" height="3" rx="1.5" opacity=".4"/>
      <rect x="920" y="285" width="20" height="3" rx="1.5" opacity=".3"/>
    </g>

    <text class="name" x="62" y="124">Subhan Noeman</text>
    <text class="role" x="64" y="164">Support Engineer in Chicago</text>
    <text class="tag" x="64" y="200">I keep devices, identities and people happily connected.</text>
  </g>
</svg>
'''
    write(out, "banner.svg", svg)


def build_footer(out):
    FW, FH, FHOR = 1280, 200, 150
    footer_stars = stars([
        (140, 40, 1.3, 0.5, .6), (260, 92, 1.0, 2.2, .45), (360, 30, 1.5, 1.1, .7),
        (470, 70, 1.0, 3.4, .45), (560, 24, 1.2, 0.2, .6), (730, 28, 1.2, 2.6, .55),
        (820, 66, 1.0, 1.4, .45), (905, 30, 1.5, 3.1, .7), (1130, 38, 1.2, 0.9, .6),
        (1200, 88, 1.0, 2.0, .45), (80, 110, 1.0, 3.7, .4), (1240, 30, 1.3, 1.7, .55),
    ])
    fwaves = [
        ("w1", 156, 3.0, 110, "#a9d3dc", .12, .26),
        ("w2", 169, 4.5, 190, "#2a5c76", .62, .20),
        ("w3", 184, 6.0, 300, "#173a52", .88, .16),
    ]
    fwave_svg = "\n  ".join(
        f'<path class="wave {c}" d="{wave_path(y, a, p, FW, FH + 20)}" fill="{f}" '
        f'fill-opacity="{fo}" stroke="#d6ecef" stroke-opacity="{so}" stroke-width="1.2"/>'
        for c, y, a, p, f, fo, so in fwaves
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {FW} {FH}" width="{FW}" height="{FH}" role="img" aria-labelledby="t d">
  <title id="t">Thanks for stopping by</title>
  <desc id="d">A quiet lake at night with a crescent moon.</desc>
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0d192b"/>
      <stop offset="1" stop-color="#244260"/>
    </linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2f5b75"/>
      <stop offset="1" stop-color="#10233a"/>
    </linearGradient>
    <radialGradient id="moonglow" cx="1010" cy="54" r="90" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#f3e6c8" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#f3e6c8" stop-opacity="0"/>
    </radialGradient>
    <mask id="crescent">
      <rect x="960" y="10" width="100" height="90" fill="#fff"/>
      <circle cx="1019" cy="48" r="19" fill="#000"/>
    </mask>
    <clipPath id="card"><rect width="{FW}" height="{FH}" rx="22"/></clipPath>
  </defs>
  <style>
    .l1 {{ font: 400 30px {FONT}; fill: #eef3f1; letter-spacing: 0.3px; }}
    .l2 {{ font: 400 18px {FONT}; fill: #b7cad3; }}
    .wave {{ animation: drift linear infinite; }}
    .w1 {{ animation-name: d1; animation-duration: 28s; }}
    .w2 {{ animation-name: d2; animation-duration: 38s; animation-direction: reverse; }}
    .w3 {{ animation-name: d3; animation-duration: 50s; }}
    @keyframes d1 {{ to {{ transform: translateX(-110px); }} }}
    @keyframes d2 {{ to {{ transform: translateX(-190px); }} }}
    @keyframes d3 {{ to {{ transform: translateX(-300px); }} }}
    .star {{ animation: tw 7s ease-in-out infinite; }}
    @keyframes tw {{ 0%, 100% {{ opacity: .25; }} 50% {{ opacity: .9; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .wave, .star {{ animation: none !important; }}
    }}
  </style>

  <g clip-path="url(#card)">
    <rect width="{FW}" height="{FH}" fill="url(#sky)"/>
    {footer_stars}
    <circle cx="1010" cy="54" r="90" fill="url(#moonglow)"/>
    <circle cx="1010" cy="54" r="26" fill="#f3e6c8" mask="url(#crescent)"/>

    <rect y="{FHOR}" width="{FW}" height="{FH - FHOR}" fill="url(#water)"/>
    {fwave_svg}

    <text class="l1" x="640" y="82" text-anchor="middle">Thanks for stopping by.</text>
    <text class="l2" x="640" y="116" text-anchor="middle">Take a breath, drink some water, have a good one.</text>
  </g>
</svg>
'''
    write(out, "footer.svg", svg)


# --------------------------------------------------------------- icon system
# Neutral 24x24 line glyphs used whenever a brand logo is not available.
GLYPHS = {
    "laptop": '<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 19h20"/>',
    "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M11 18.5h2"/>',
    "server": '<rect x="3.5" y="4" width="17" height="6.5" rx="1.5"/><rect x="3.5" y="13.5" width="17" height="6.5" rx="1.5"/><path d="M7 7.25h.01M7 16.75h.01"/>',
    "cloud": '<path d="M7 18h10a4 4 0 0 0 .5-7.97A5.5 5.5 0 0 0 7 9.5 4.25 4.25 0 0 0 7 18z"/>',
    "shield": '<path d="M12 3l7 3v5.5c0 4.2-2.9 7.7-7 9.5-4.1-1.8-7-5.3-7-9.5V6l7-3z"/><path d="M9 12l2 2 4-4"/>',
    "key": '<circle cx="8" cy="12" r="3.5"/><path d="M11.5 12H21M17.5 12v3M20 12v2"/>',
    "users": '<circle cx="9" cy="8" r="3"/><path d="M3.5 19c.5-3.2 2.7-5 5.5-5s5 1.8 5.5 5"/><circle cx="17" cy="9" r="2.4"/><path d="M16 14.2c2.6-.3 4.4 1.2 4.9 4"/>',
    "network": '<circle cx="12" cy="5" r="2.2"/><circle cx="5.5" cy="18" r="2.2"/><circle cx="18.5" cy="18" r="2.2"/><path d="M12 7.2v4.3M12 11.5L6.5 16M12 11.5l5.5 4.5"/>',
    "terminal": '<rect x="3" y="4.5" width="18" height="15" rx="2"/><path d="M7 10l3 2.5-3 2.5M12.5 15.5H17"/>',
    "sliders": '<path d="M4 7h8M18 7h2M4 12h2M12 12h8M4 17h9M19 17h1"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="16" cy="17" r="2"/>',
    "database": '<ellipse cx="12" cy="6" rx="7.5" ry="3"/><path d="M4.5 6v6c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3V6M4.5 12v6c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-6"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3.5 7l8.5 6 8.5-6"/>',
    "chat": '<path d="M4 5.5h16v10H11l-4.5 3.5V15.5H4z"/>',
    "video": '<rect x="3" y="6" width="12.5" height="12" rx="2"/><path d="M15.5 10.5L21 7.5v9l-5.5-3z"/>',
    "headset": '<path d="M4.5 14v-2a7.5 7.5 0 0 1 15 0v2"/><rect x="3.5" y="13.5" width="4" height="6" rx="1.5"/><rect x="16.5" y="13.5" width="4" height="6" rx="1.5"/><path d="M18.5 19.5c0 1.4-1.6 2-4 2"/>',
    "printer": '<path d="M7 9V4h10v5"/><rect x="3.5" y="9" width="17" height="8" rx="2"/><rect x="7" y="14" width="10" height="6" rx="1"/>',
    "wifi": '<path d="M3 9.5a13 13 0 0 1 18 0M6 13a8.5 8.5 0 0 1 12 0M9 16.5a4 4 0 0 1 6 0"/><path d="M12 19.5h.01"/>',
    "package": '<path d="M12 3l8 4.2v9.6L12 21l-8-4.2V7.2L12 3z"/><path d="M4 7.2l8 4.3 8-4.3M12 11.5V21"/>',
    "chart": '<path d="M4 20V5M4 20h16"/><rect x="7.5" y="12" width="3" height="5.5" rx=".6"/><rect x="12.5" y="8" width="3" height="9.5" rx=".6"/><rect x="17.5" y="10.5" width="2" height="7" rx=".6"/>',
    "book": '<path d="M5 4.5h10a3 3 0 0 1 3 3V20H8a3 3 0 0 1-3-3V4.5z"/><path d="M8 17h10"/>',
    "checklist": '<path d="M4.5 7l1.8 1.8L9.5 5.5M4.5 14l1.8 1.8 3.2-3.3M12.5 7.5H20M12.5 14.5H20"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="9.5" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>',
    "cpu": '<rect x="6.5" y="6.5" width="11" height="11" rx="2"/><rect x="9.5" y="9.5" width="5" height="5" rx=".8"/><path d="M9 3v3.5M15 3v3.5M9 17.5V21M15 17.5V21M3 9h3.5M3 15h3.5M17.5 9H21M17.5 15H21"/>',
    "grid": '<rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/>',
    "cable": '<path d="M8 3v4M16 3v4M6 7h12v4a6 6 0 0 1-12 0V7z"/><path d="M12 17v4"/>',
    "desk-phone": '<path d="M5 10c4-3.2 10-3.2 14 0v2.5l-2.5.8-1-2c-2.2-.9-4.8-.9-7 0l-1 2L5 12.5V10z"/><rect x="5" y="14.5" width="14" height="6" rx="1.5"/>',
    "folder": '<path d="M3.5 7a2 2 0 0 1 2-2h4l2 2.5h7a2 2 0 0 1 2 2V17a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2V7z"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.5 3.5 5.3 3.5 8.5s-1 6-3.5 8.5C9.5 18 8.5 15.2 8.5 12s1-6 3.5-8.5z"/>',
}


class Logos:
    """Reads brand logo paths from a Simple Icons `icons` folder, if given."""

    def __init__(self, folder):
        self.folder = folder
        self.cache = {}
        self.used = set()

    def get(self, slug):
        if not self.folder:
            return None
        if slug in self.cache:
            return self.cache[slug]
        d = None
        path = os.path.join(self.folder, f"{slug}.svg")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                txt = f.read()
            parts = re.findall(r'<path[^>]*?\sd="([^"]+)"', txt)
            if parts:
                d = " ".join(parts)
                self.used.add(slug)
        self.cache[slug] = d
        return d


def resolve_icon(logos, glyph, slugs):
    for slug in slugs:
        d = logos.get(slug)
        if d:
            return (f"l-{slug}",
                    f'<symbol id="l-{slug}" viewBox="0 0 24 24"><path d="{d}" fill="currentColor"/></symbol>')
    return (f"g-{glyph}",
            f'<symbol id="g-{glyph}" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{GLYPHS[glyph]}</g></symbol>')


# ------------------------------------------------------------ role wallpapers
def T(label, glyph, *slugs):
    return (label, glyph, list(slugs))


# palette: three background stops, accent for the "when" line, soft tone for "where", glow colour
ROLES = [
    dict(
        file="01-tropicana", when="2025 – now",
        role=["Senior Desktop Support /", "Support Engineer"],
        where="Tropicana Brands Group",
        alt="2025 to now: Senior Desktop Support / Support Engineer at Tropicana Brands Group. The tools used in this role drift by in the background.",
        pal=dict(bg=("#14243b", "#27486b", "#5b7f9f"), when="#f2c79b", where="#bfe3e1", glow="#f2b48f"),
        rows=[
            [T("Microsoft 365", "cloud", "microsoftoffice"), T("Teams", "chat", "microsoftteams"),
             T("Outlook", "mail", "microsoftoutlook"), T("SharePoint", "folder", "microsoftsharepoint"),
             T("Intune", "laptop"), T("Surface devices", "laptop")],
            [T("Okta", "key", "okta"), T("Google Workspace", "cloud", "googleworkspace"),
             T("MFA and SSO", "shield"), T("Password resets", "lock"),
             T("Onboarding and offboarding", "users"), T("Executive support", "headset")],
            [T("Teams Rooms", "video", "microsoftteams"), T("Zoom Rooms", "video", "zoom"),
             T("AV systems", "video"), T("LAN, Wi-Fi and VPN", "wifi"),
             T("Patching and compliance", "package"), T("Windows", "grid", "windows11", "windows"),
             T("macOS", "laptop", "macos", "apple")],
        ]),
    dict(
        file="02-robinhood", when="2024 – 2025",
        role=["Support Engineer"],
        where="Robinhood",
        alt="2024 to 2025: Support Engineer at Robinhood. The tools used in this role drift by in the background.",
        pal=dict(bg=("#0e2a2b", "#1c5453", "#3c8c7c"), when="#bff0d2", where="#d8f3e8", glow="#8fe3b8"),
        rows=[
            [T("ServiceNow", "checklist", "servicenow"), T("Jira", "checklist", "jira"),
             T("Confluence", "book", "confluence"), T("Slack", "chat", "slack"),
             T("Google Workspace", "cloud", "googleworkspace"), T("Microsoft 365", "cloud", "microsoftoffice")],
            [T("Okta", "key", "okta"), T("YubiKey", "key", "yubico"), T("FIDO2 and Touch ID", "shield"),
             T("JAMF Pro", "laptop", "jamf"), T("Apple Business Manager", "laptop", "apple"),
             T("FleetDM", "server")],
            [T("Zoom Rooms", "video", "zoom"), T("macOS and iOS", "phone", "apple"),
             T("Zero-touch deployment", "package"), T("Change management", "sliders"),
             T("Log analysis", "terminal"), T("Hardware rollouts", "package")],
        ]),
    dict(
        file="03-illinois-doit", when="2024",
        role=["Helpdesk, Desktop &", "Network Specialist"],
        where="Illinois Dept. of Innovation & Technology",
        alt="2024: Helpdesk, Desktop and Network Specialist at the Illinois Department of Innovation and Technology. The tools used in this role drift by in the background.",
        pal=dict(bg=("#101f3d", "#24467a", "#4b7cb5"), when="#cfe0ff", where="#dbe8ff", glow="#8fb8ff"),
        rows=[
            [T("SCCM / MECM", "package"), T("PXE boot", "network"), T("Intune", "laptop"),
             T("AirWatch", "phone", "vmware"), T("Active Directory", "users"),
             T("Azure AD", "cloud", "microsoftazure")],
            [T("ServiceNow", "checklist", "servicenow"), T("Exchange", "mail", "microsoftexchange"),
             T("Zoom", "video", "zoom"), T("Webex", "video", "webex"),
             T("Cisco Meraki", "network", "cisco"), T("Avaya phones", "desk-phone", "avaya")],
            [T("Power BI", "chart", "powerbi"), T("SolarWinds", "chart", "solarwinds"),
             T("McAfee", "shield", "mcafee"), T("PowerShell", "terminal", "powershell"),
             T("SQL", "database"), T("ESXi and vSphere", "server", "vmware"),
             T("Citrix", "server", "citrix"), T("Zscaler", "shield", "zscaler"),
             T("OpenVPN", "lock", "openvpn")],
        ]),
    dict(
        file="04-kirkland-ellis", when="2024",
        role=["Desktop Support Analyst III"],
        where="Kirkland & Ellis LLP",
        alt="2024: Desktop Support Analyst III at Kirkland and Ellis LLP. The tools used in this role drift by in the background.",
        pal=dict(bg=("#1a1833", "#392f61", "#6a5a97"), when="#e2d6ff", where="#ece4ff", glow="#b9a3ff"),
        rows=[
            [T("Active Directory", "users"), T("Azure AD", "cloud", "microsoftazure"),
             T("SCCM", "package"), T("Intune", "laptop"), T("AirWatch", "phone", "vmware"),
             T("Windows 10", "grid", "windows11", "windows")],
            [T("Outlook", "mail", "microsoftoutlook"), T("iManage", "folder"),
             T("Microsoft 365", "cloud", "microsoftoffice"), T("VMware ESXi", "server", "vmware"),
             T("macOS", "laptop", "macos", "apple")],
            [T("Avaya CM", "desk-phone", "avaya"), T("SolarWinds", "chart", "solarwinds"),
             T("VLAN and QoS", "network"), T("iOS and Android MDM", "phone"),
             T("Secure printing", "printer"), T("White-glove support", "headset")],
        ]),
    dict(
        file="05-alter-domus", when="2023 – 2024",
        role=["Desktop, Network &", "Infrastructure Support Specialist"],
        where="Alter Domus",
        alt="2023 to 2024: Desktop, Network and Infrastructure Support Specialist at Alter Domus. The tools used in this role drift by in the background.",
        pal=dict(bg=("#0f2531", "#214f61", "#458694"), when="#c3ecee", where="#d6f3f4", glow="#7fd6dc"),
        rows=[
            [T("ServiceNow", "checklist", "servicenow"), T("Confluence", "book", "confluence"),
             T("Active Directory", "users"), T("Azure AD", "cloud", "microsoftazure"),
             T("Microsoft 365", "cloud", "microsoftoffice"), T("Google Workspace", "cloud", "googleworkspace"),
             T("Salesforce", "cloud", "salesforce"), T("DocuSign", "mail", "docusign")],
            [T("VMware ESXi", "server", "vmware"), T("SCCM", "package"),
             T("Cisco CUCM", "desk-phone", "cisco"), T("Cisco Catalyst", "network", "cisco"),
             T("Sophos Firewall", "shield", "sophos"), T("Dell, HPE, Supermicro", "server", "dell")],
            [T("Wireshark", "network", "wireshark"), T("SolarWinds", "chart", "solarwinds"),
             T("iDRAC, iLO, IPMI", "cpu"), T("AnyConnect", "lock", "cisco"),
             T("OpenVPN", "lock", "openvpn"), T("WireGuard", "lock", "wireguard"),
             T("Pulse Secure", "lock"), T("Zscaler", "shield", "zscaler"),
             T("JumpCloud", "key", "jumpcloud"), T("Hybrid migration", "cloud")],
        ]),
    dict(
        file="06-endeavour-health", when="2022 – 2023",
        role=["Desktop, Network &", "Infrastructure Support Analyst"],
        where="Endeavour Health, Swedish Hospital",
        alt="2022 to 2023: Desktop, Network and Infrastructure Support Analyst at Endeavour Health, Swedish Hospital. The tools used in this role drift by in the background.",
        pal=dict(bg=("#1b2a3d", "#3b5772", "#7f9bb0"), when="#f3cfd0", where="#f8e1e1", glow="#f0b4b8"),
        rows=[
            [T("Active Directory", "users"), T("Azure AD", "cloud", "microsoftazure"),
             T("Exchange", "mail", "microsoftexchange"), T("Group Policy", "sliders"),
             T("SSO and MFA", "shield")],
            [T("SCCM / MECM", "package"), T("PXE boot", "network"), T("BitLocker", "lock"),
             T("ESXi and vSphere", "server", "vmware"), T("Citrix XenDesktop", "server", "citrix"),
             T("XenApp", "server", "citrix")],
            [T("SolarWinds", "chart", "solarwinds"), T("iDRAC, iLO, IPMI", "cpu"),
             T("Cisco CUCM", "desk-phone", "cisco"), T("AnyConnect", "lock", "cisco"),
             T("BigFix", "package"), T("Weekly reporting", "chart")],
        ]),
    dict(
        file="07-dyopath", when="2021 – 2022",
        role=["Service Desk Analyst 3 &", "Team Lead"],
        where="DyoPath LP (MSP), remote",
        alt="2021 to 2022: Service Desk Analyst 3 and Team Lead at DyoPath LP, a managed service provider, working remotely. The tools used in this role drift by in the background.",
        pal=dict(bg=("#0d2238", "#15506f", "#3a8aa8"), when="#cdeeff", where="#dff3ff", glow="#7ccaf0"),
        rows=[
            [T("ServiceNow", "checklist", "servicenow"), T("Azure AD", "cloud", "microsoftazure"),
             T("Oracle IAM", "key", "oracle"), T("SailPoint", "key", "sailpoint"),
             T("Active Directory", "users"), T("Group Policy", "sliders")],
            [T("SCCM", "package"), T("VMware Horizon", "server", "vmware"), T("Intune", "laptop"),
             T("Exchange Online", "mail", "microsoftexchange"), T("Hybrid Exchange", "cloud"),
             T("Outlook", "mail", "microsoftoutlook")],
            [T("BitLocker", "lock"), T("Cisco AnyConnect", "lock", "cisco"),
             T("SonicWall", "shield", "sonicwall"), T("DNS and DHCP", "network"),
             T("Print servers", "printer"), T("ShadowBackup", "database"),
             T("Team leadership", "users"), T("Knowledge base", "book")],
        ]),
    dict(
        file="08-chicago-lab-services", when="2018 – now",
        role=["Desktop Support (per diem)"],
        where="Chicago Lab Services Inc.",
        alt="2018 to now: Desktop Support, per diem, at Chicago Lab Services Inc. The tools used in this role drift by in the background.",
        pal=dict(bg=("#12282a", "#225b55", "#6bb3a0"), when="#d9f6e6", where="#e6faf0", glow="#9fe3c6"),
        rows=[
            [T("Windows Server 2019", "server", "windows11", "windows"), T("Active Directory", "users"),
             T("Group Policy", "sliders"), T("3CX", "desk-phone", "3cx"),
             T("Yealink", "desk-phone"), T("SIP and fax", "desk-phone")],
            [T("pfSense", "shield", "pfsense"), T("VLANs and PoE", "network"),
             T("Cat5e and Cat6", "cable"), T("Racks and servers", "server"),
             T("Security cameras", "video")],
            [T("Drupal", "globe", "drupal"), T("SiteGround", "globe", "siteground"),
             T("McAfee", "shield", "mcafee"), T("Wolters Kluwer", "book", "wolterskluwer"),
             T("Labsoft", "database"), T("HIPAA compliance", "shield"), T("Procurement", "package")],
        ]),
]

ROLE_CSS = """
    .when { font: 500 21px @FONT@; letter-spacing: .6px; }
    .role { font: 500 34px @FONT@; fill: #f4f7f6; }
    .where { font: 500 22px @FONT@; }
    .chip { font: 500 16.5px @FONT@; fill: #eaf4f5; }
    .pill { fill: #fff; fill-opacity: .09; stroke: #fff; stroke-opacity: .22; }
    .ic { color: #eaf4f5; }
    .gl { animation: gl 22s ease-in-out infinite alternate; }
    @keyframes gl { from { transform: translateX(-50px); } to { transform: translateX(70px); } }
    @media (prefers-reduced-motion: reduce) { .a0, .a1, .a2, .gl { animation: none !important; } }
""".replace("@FONT@", FONT)


def build_role(role, logos, out):
    W, H = 1280, 250
    pal = role["pal"]
    symbols = {}
    row_defs, row_uses, row_css = [], [], []
    row_ys = [32, 102, 172]
    speeds = [22, 17, 27]          # pixels per second: slow on purpose
    phase = [0.10, 0.52, 0.80]     # where in its loop each row starts
    min_period = 1500

    for i, items in enumerate(role["rows"]):
        measured = []
        for label, glyph, slugs in items:
            icon_id, sym = resolve_icon(logos, glyph, slugs)
            symbols[icon_id] = sym
            tw = est_width(label, 16.5)
            measured.append((label, icon_id, tw, 16 + 22 + 10 + tw + 20))
        total = sum(m[3] for m in measured)
        gap = max(18.0, (min_period - total) / len(measured))
        x, parts = 0.0, []
        for label, icon_id, tw, w in measured:
            parts.append(
                f'<g transform="translate({x:.1f},0)"><rect class="pill" width="{w:.1f}" height="46" rx="23"/>'
                f'<use class="ic" href="#{icon_id}" x="16" y="12" width="22" height="22"/>'
                f'<text class="chip" x="48" y="28.5" textLength="{tw:.1f}" lengthAdjust="spacing">{esc(label)}</text></g>'
            )
            x += w + gap
        period = x
        dur = period / speeds[i]
        direction = "normal" if i % 2 == 0 else "reverse"
        row_defs.append(f'<g id="r{i}">{"".join(parts)}</g>')
        row_uses.append(
            f'<g transform="translate(0,{row_ys[i]})"><g class="a{i}"><use href="#r{i}"/>'
            f'<use href="#r{i}" x="{period:.1f}"/></g></g>'
        )
        row_css.append(
            f'@keyframes s{i} {{ to {{ transform: translateX(-{period:.1f}px); }} }} '
            f'.a{i} {{ animation: s{i} {dur:.1f}s linear infinite {direction}; animation-delay: -{dur * phase[i]:.1f}s; }}'
        )

    lines = role["role"]
    if len(lines) == 2:
        y_when, y_roles, y_where = 62, [108, 148], 196
    else:
        y_when, y_roles, y_where = 80, [124], 172
    role_text = "".join(
        f'<tspan x="64" y="{y}">{esc(t)}</tspan>' for t, y in zip(lines, y_roles)
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
  <title id="t">{esc(role["alt"])}</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{pal["bg"][0]}"/>
      <stop offset="0.55" stop-color="{pal["bg"][1]}"/>
      <stop offset="1" stop-color="{pal["bg"][2]}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{pal["glow"]}" stop-opacity=".42"/>
      <stop offset="1" stop-color="{pal["glow"]}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="scrim" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#050b14" stop-opacity=".34"/>
      <stop offset="1" stop-color="#050b14" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="fadeG" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity=".07"/>
      <stop offset=".40" stop-color="#fff" stop-opacity=".13"/>
      <stop offset=".70" stop-color="#fff" stop-opacity="1"/>
    </linearGradient>
    <mask id="fade" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <rect width="{W}" height="{H}" fill="url(#fadeG)"/>
    </mask>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
    {"".join(symbols.values())}
    {"".join(row_defs)}
  </defs>
  <style>{ROLE_CSS}
    {" ".join(row_css)}
  </style>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <ellipse class="gl" cx="1010" cy="70" rx="420" ry="210" fill="url(#glow)"/>
    <g mask="url(#fade)">
      {"".join(row_uses)}
    </g>
    <rect width="760" height="{H}" fill="url(#scrim)"/>
    <text class="when" x="64" y="{y_when}" fill="{pal["when"]}">{esc(role["when"])}</text>
    <text class="role">{role_text}</text>
    <text class="where" x="64" y="{y_where}" fill="{pal["where"]}">{esc(role["where"])}</text>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="21.5" fill="none" stroke="#fff" stroke-opacity=".10"/>
</svg>
'''
    write(out, f"{role['file']}.svg", svg)


# ------------------------------------------------------------------ roadmap
def bezier(p0, p1, p2, p3, t):
    mt = 1 - t
    x = mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0]
    y = mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]
    return x, y


def point_at_x(p0, p1, p2, p3, x_target):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if bezier(p0, p1, p2, p3, mid)[0] < x_target:
            lo = mid
        else:
            hi = mid
    return bezier(p0, p1, p2, p3, lo)


ROAD_CSS = """
    .lane { font: 600 20px @FONT@; }
    .nt { font: 600 16px @FONT@; fill: #eef3f1; }
    .nd { font: 400 13.5px @FONT@; fill: #a9bfcb; }
    .small { font: 400 13px @FONT@; fill: #8fa8b6; }
    .lake1 { font: 600 16px @FONT@; fill: #f3f6f4; }
    .lake2 { font: 400 13px @FONT@; fill: #c1d3db; }
    .dest { font: 600 15px @FONT@; fill: #fff7e6; }
    .destd { font: 400 13px @FONT@; fill: #f1dcc4; }
    .flow { stroke-dasharray: 1 16; stroke-linecap: round; animation: flow 3s linear infinite; }
    @keyframes flow { to { stroke-dashoffset: -34; } }
    .pulse { transform-box: fill-box; transform-origin: center; animation: pulse 3.6s ease-out infinite; }
    @keyframes pulse { 0% { transform: scale(.8); opacity: .75; } 100% { transform: scale(2.1); opacity: 0; } }
    .sun { animation: breathe 7s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: center; }
    @keyframes breathe { from { transform: scale(.94); opacity: .7; } to { transform: scale(1.08); opacity: 1; } }
    @media (prefers-reduced-motion: reduce) { .flow, .pulse, .sun { animation: none !important; } }
""".replace("@FONT@", FONT)


def build_roadmap(out):
    W, H = 1280, 480
    LAKE_X, LAKE_Y = 1050, 240
    DEST_X = 1218

    lanes = [
        dict(name="macOS", y=120, color="#b9c2ff", nodes=[
            (215, "macOS support", "desktop and executive"),
            (395, "JAMF Pro and ABM", "zero-touch deployment"),
            (575, "FleetDM and Okta", "compliance, MFA, YubiKey")],
            nxt=(755, "Own the Mac fleet", "baselines and patching")),
        dict(name="Windows", y=240, color="#86d8e6", nodes=[
            (215, "Active Directory", "GPO, Exchange, Azure AD"),
            (395, "SCCM, PXE, Intune", "imaging and deployment"),
            (575, "Windows Server labs", "AD, DNS, IIS (2019, 2025)")],
            nxt=(755, "Servers and hybrid ID", "Entra ID with on-prem AD")),
        dict(name="Linux", y=360, color="#f0cf95", nodes=[
            (215, "Linux fundamentals", "RHEL, CentOS, Debian"),
            (395, "Arch daily driver", "btw, I use Arch"),
            (575, "Virtualization lab", "Proxmox, KVM, LXC, ZFS")],
            nxt=(755, "Production Linux", "patching, hardening, K8s")),
    ]

    beds, flows, solids, nodes, labels = [], [], [], [], []
    for ln in lanes:
        y, c = ln["y"], ln["color"]
        if y == LAKE_Y:
            d = f"M150,{y} L946,{y}"
        else:
            d = f"M150,{y} L800,{y} C880,{y} 880,{LAKE_Y} 946,{LAKE_Y}"
        beds.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".09" stroke-width="14" stroke-linecap="round"/>')
        flows.append(f'<path class="flow" d="{d}" fill="none" stroke="{c}" stroke-opacity=".85" stroke-width="3"/>')
        solids.append(f'<path d="M150,{y} L{ln["nodes"][-1][0]},{y}" stroke="{c}" stroke-opacity=".55" stroke-width="2.5" stroke-linecap="round"/>')
        labels.append(f'<text class="lane" x="28" y="{y - 34}" fill="{c}">{ln["name"]}</text>')
        for x, title, detail in ln["nodes"]:
            nodes.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{c}" stroke="#0e1b2e" stroke-width="3"/>')
            labels.append(f'<text class="nt" x="{x}" y="{y - 34}" text-anchor="middle">{esc(title)}</text>'
                          f'<text class="nd" x="{x}" y="{y - 15}" text-anchor="middle">{esc(detail)}</text>')
        nx, ntitle, ndetail = ln["nxt"]
        ny = y
        nodes.append(f'<circle class="pulse" cx="{nx}" cy="{ny}" r="10" fill="none" stroke="{c}" stroke-width="2"/>')
        nodes.append(f'<circle cx="{nx}" cy="{ny}" r="10" fill="#0e1b2e" stroke="{c}" stroke-width="3"/>')
        labels.append(f'<text class="nt" x="{nx}" y="{ny - 34}" text-anchor="middle" fill="{c}" style="fill:{c}">{esc(ntitle)}</text>'
                      f'<text class="nd" x="{nx}" y="{ny - 15}" text-anchor="middle">{esc(ndetail)}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">The road ahead: macOS, Windows and Linux lanes flowing into hybrid and cloud, toward systems administration</title>
  <desc id="d">Three lanes show what is done so far and what comes next for macOS, Windows and Linux. They merge into hybrid and cloud architecture and then into a sunrise labeled systems administrator.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0e1b2e"/>
      <stop offset="0.6" stop-color="#18344f"/>
      <stop offset="1" stop-color="#335d7a"/>
    </linearGradient>
    <radialGradient id="dawn" cx="{DEST_X}" cy="{LAKE_Y}" r="420" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#f6dcb4" stop-opacity=".62"/>
      <stop offset=".3" stop-color="#eaa98f" stop-opacity=".28"/>
      <stop offset="1" stop-color="#eaa98f" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#f6dcb4" stop-opacity=".6"/>
      <stop offset="1" stop-color="#f6dcb4" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>
  <style>{ROAD_CSS}</style>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#dawn)"/>

    <path d="M665,62 L665,420" stroke="#fff" stroke-opacity=".22" stroke-width="1.5" stroke-dasharray="4 7"/>
    <text class="small" x="665" y="46" text-anchor="middle">today</text>

    {"".join(beds)}
    {"".join(solids)}
    {"".join(flows)}

    <ellipse cx="{LAKE_X}" cy="{LAKE_Y}" rx="108" ry="94" fill="#fff" fill-opacity=".07" stroke="#fff" stroke-opacity=".2"/>
    <text class="lake1" x="{LAKE_X}" y="{LAKE_Y - 6}" text-anchor="middle">Hybrid and cloud</text>
    <text class="lake2" x="{LAKE_X}" y="{LAKE_Y + 16}" text-anchor="middle">Azure, GCP, Cloudflare</text>
    <text class="lake2" x="{LAKE_X}" y="{LAKE_Y + 34}" text-anchor="middle">ESXi, Proxmox, Hyper-V</text>

    <path d="M{LAKE_X + 108},{LAKE_Y} L{DEST_X},{LAKE_Y}" stroke="#f6dcb4" stroke-opacity=".7" stroke-width="3" class="flow" fill="none"/>
    <circle class="sun" cx="{DEST_X}" cy="{LAKE_Y}" r="62" fill="url(#halo)"/>
    <circle cx="{DEST_X}" cy="{LAKE_Y}" r="13" fill="#f8e2bd" stroke="#fff7e6" stroke-width="2"/>
    <text class="dest" x="{DEST_X}" y="{LAKE_Y - 52}" text-anchor="middle">Systems</text>
    <text class="dest" x="{DEST_X}" y="{LAKE_Y - 34}" text-anchor="middle">administrator</text>
    <text class="destd" x="{DEST_X}" y="{LAKE_Y + 42}" text-anchor="middle">macOS, Windows</text>
    <text class="destd" x="{DEST_X}" y="{LAKE_Y + 59}" text-anchor="middle">and Linux</text>

    {"".join(nodes)}
    {"".join(labels)}

    <circle cx="36" cy="{H - 30}" r="6" fill="#cfe0ea" stroke="#0e1b2e" stroke-width="2"/>
    <text class="small" x="50" y="{H - 25.5}">where I've been</text>
    <circle cx="190" cy="{H - 30}" r="6" fill="#0e1b2e" stroke="#cfe0ea" stroke-width="2"/>
    <text class="small" x="204" y="{H - 25.5}">where I'm heading</text>
  </g>
</svg>
'''
    write(out, "roadmap.svg", svg)


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--icons", help="path to a simple-icons 'icons' folder", default=None)
    ap.add_argument("--out", help="output folder", default=None)
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = args.out or os.path.join(root, "assets")
    logos = Logos(args.icons)

    build_banner(out)
    build_footer(out)
    for role in ROLES:
        build_role(role, logos, os.path.join(out, "roles"))
    build_roadmap(out)

    if args.icons:
        wanted = sorted({s for r in ROLES for row in r["rows"] for _, _, slugs in row for s in slugs})
        missing = [s for s in wanted if s not in logos.used]
        print(f"logos used: {len(logos.used)}  not found (glyph fallback): {', '.join(missing) or 'none'}")
    print("assets written to", out)


if __name__ == "__main__":
    main()
