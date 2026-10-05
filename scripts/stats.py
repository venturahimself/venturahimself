#!/usr/bin/env python3
"""Generate stats.svg (terminal/HUD style) from the GitHub API.

Usage: python scripts/stats.py [username]   (set GITHUB_TOKEN to avoid rate limits)
"""
import json, os, sys, urllib.request
from datetime import datetime, timezone

USER = sys.argv[1] if len(sys.argv) > 1 else "venturahimself"


def api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def ago(iso):
    s = (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds()
    for label, size in (("y", 31536000), ("mo", 2592000), ("d", 86400), ("h", 3600), ("m", 60)):
        if s >= size:
            return f"{int(s // size)}{label} ago"
    return "just now"


def render(user, repos, today=None):
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    last_push = max((r["pushed_at"] for r in repos), default=user["created_at"])
    top = sorted(own, key=lambda r: (r["stargazers_count"], r["pushed_at"]), reverse=True)[:3]

    rows = [
        ("REPOSITORIES", user["public_repos"], "cyan"),
        ("STARS", stars, "cyan"),
        ("FOLLOWERS", user["followers"], "cyan"),
        ("FOLLOWING", user["following"], "cyan"),
        ("MEMBER SINCE", user["created_at"][:4], "green"),
        ("LAST PUSH", ago(last_push), "green"),
    ]
    updated = (today or datetime.now(timezone.utc)).strftime("%Y-%m-%d")

    out = []
    a = out.append
    a('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="330" viewBox="0 0 900 330" role="img" aria-label="GitHub stats for Ventura Himself">')
    a('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#48e7ff"/><stop offset=".5" stop-color="#9d5cff"/><stop offset="1" stop-color="#ff3fc7"/></linearGradient>')
    a('<style>text{font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace}.l{fill:#6b7b90;font-size:11px;letter-spacing:2px}.v{font-size:13px;font-weight:700;letter-spacing:1px}.c{fill:#48e7ff}.gr{fill:#65ffad}.m{fill:#8190a4;font-size:12px}.t{fill:#eef7ff;font-size:13px}.b{fill:#eef7ff;font-family:Inter,"Segoe UI",system-ui,sans-serif;font-weight:900}</style></defs>')
    a('<rect x=".5" y=".5" width="899" height="329" rx="14" fill="#07080d" stroke="#8ca0be" stroke-opacity=".25"/>')

    # terminal (left)
    a('<rect x="24" y="24" width="500" height="282" rx="12" fill="#0c0f18" stroke="#8ca0be" stroke-opacity=".2"/>')
    a('<path d="M24 60h500" stroke="#8ca0be" stroke-opacity=".2"/>')
    for i in range(3):
        a(f'<circle cx="{44 + i * 14}" cy="42" r="3.5" fill="#45505f"/>')
    a('<text x="274" y="46" text-anchor="middle" class="l" style="font-size:10px;letter-spacing:1px">session://' + USER + '</text>')
    a(f'<text x="44" y="92" class="t"><tspan class="gr">$</tspan> gh api users/{USER}</text>')
    a('<text x="44" y="114" class="m">profile loaded</text>')
    y = 142
    for label, val, _ in rows[:3]:
        a(f'<text x="44" y="{y}" class="t"><tspan class="gr">[OK]</tspan> {label.lower()}: <tspan font-weight="700">{val}</tspan></text>')
        y += 22
    a(f'<text x="44" y="{y + 8}" class="m">top repositories</text>')
    y += 30
    for r in top:
        a(f'<text x="44" y="{y}" class="t"><tspan class="c">&gt;</tspan> {r["name"]} <tspan class="m">★ {r["stargazers_count"]}</tspan></text>')
        y += 20

    # HUD (right)
    a('<g stroke="#48e7ff" stroke-width="1.5" fill="none" opacity=".85"><path d="M552 44v-20h20"/><path d="M876 24h-20M876 24v20" transform="translate(0 0)"/><path d="M552 286v20h20"/><path d="M876 286v20h-20"/></g>')
    a('<text x="572" y="58" class="l">GITHUB // STATS</text>')
    a(f'<text x="572" y="118" class="b" font-size="62" letter-spacing="-3">{user["public_repos"]}</text>')
    a('<text x="572" y="138" class="l" style="font-size:9px">PUBLIC REPOSITORIES</text>')
    y = 164
    for label, val, color in rows[1:]:
        a(f'<path d="M572 {y - 15}h284" stroke="#8ca0be" stroke-opacity=".18"/>')
        a(f'<text x="572" y="{y}" class="l" style="font-size:10px">{label}</text>')
        a(f'<text x="856" y="{y}" text-anchor="end" class="v {"c" if color == "cyan" else "gr"}">{val}</text>')
        y += 28
    a(f'<text x="572" y="304" class="l" style="font-size:9px">UPDATED {updated}</text>')
    a('</svg>')
    return "\n".join(out)


def main():
    user = api(f"/users/{USER}")
    repos = api(f"/users/{USER}/repos?per_page=100")
    svg = render(user, repos)
    out = os.path.join(os.path.dirname(__file__), "..", "stats.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main()
