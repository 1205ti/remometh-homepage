"""Build the Korean page ko/index.html from the English page index.html.

index.html is the source of truth. After editing it, run:
    python3 tools/build_ko.py
The Korean page gets a Korean <title>, Korean meta tags, and static Korean
text (from the page's KO dictionary) so search engines see Korean without JS.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TITLE_KO = "리모메스 | 기체 인텔리전스"
DESC_KO = ("리모메스(REMOMETH): 위성 기체 관측을 배출원 판단 근거로. 메탄과 동반 기체를 한눈에 보는 관점. "
           "같은 관측 기록을 연간 ARD, 배출 인벤토리, 준실시간 분석으로.")


def replace_once(s, old, new):
    assert s.count(old) == 1, f"expected exactly one match: {old[:80]!r}"
    return s.replace(old, new)


def main():
    s = (ROOT / "index.html").read_text(encoding="utf-8")

    s = replace_once(s, '<html lang="en" data-lang="en">', '<html lang="ko" data-lang="ko">')
    s = replace_once(s, "<title>REMOMETH | Gas Intelligence</title>", f"<title>{TITLE_KO}</title>")
    s = re.sub(r'  <meta name="(google|naver)-site-verification"[^>]*>\n', "", s)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC_KO}">', s)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC_KO}">', s)
    s = replace_once(s, '<link rel="canonical" href="https://remometh.com/">', '<link rel="canonical" href="https://remometh.com/ko/">')
    s = replace_once(s, '<meta property="og:url" content="https://remometh.com/">', '<meta property="og:url" content="https://remometh.com/ko/">')
    s = replace_once(s, '<meta property="og:title" content="REMOMETH | Gas Intelligence">', f'<meta property="og:title" content="{TITLE_KO}">')
    s = replace_once(s, '<meta property="og:locale" content="en_US">', '<meta property="og:locale" content="ko_KR">')
    s = replace_once(s, '<meta property="og:locale:alternate" content="ko_KR">', '<meta property="og:locale:alternate" content="en_US">')

    # Pre-render Korean text into data-i18n elements. Later keys win, as in JS.
    ko_src = re.search(r"const KO=\{(.*?)\};", s, re.S).group(1)
    ko = {k: v.replace("\\'", "'") for k, v in re.findall(r"(\w+):'((?:[^'\\]|\\.)*)'", ko_src)}
    count = 0

    def fill(m):
        nonlocal count
        key = m.group(3)
        if key not in ko:
            return m.group(0)
        count += 1
        return f"<{m.group(1)}{m.group(2)}data-i18n=\"{key}\"{m.group(4)}>{ko[key]}</{m.group(1)}>"

    s = re.sub(r'<([a-z0-9]+)([^>]*?)data-i18n="([^"]+)"([^>]*)>([^<]*)</\1>', fill, s)
    s = replace_once(s, "setLang('en');", "setLang('ko');")

    out = ROOT / "ko" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(s, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}: {count} elements translated")


if __name__ == "__main__":
    main()
