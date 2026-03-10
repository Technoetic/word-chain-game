"""HTML Bundler - Inlines JS and CSS into a single index.html"""
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
SRC_HTML = os.path.join(SRC_DIR, "index.html")
DIST_HTML = os.path.join(DIST_DIR, "index.html")


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def bundle():
    if not os.path.exists(SRC_HTML):
        print("src/index.html not found, skipping")
        return

    os.makedirs(DIST_DIR, exist_ok=True)
    html = read_file(SRC_HTML)

    # Inline CSS: <link rel="stylesheet" href="..."> -> <style>...</style>
    def replace_css(match):
        href = match.group(1)
        css_path = os.path.join(SRC_DIR, href)
        if os.path.exists(css_path):
            css = read_file(css_path)
            print(f"  CSS inline: {href}")
            return f"<style>\n{css}\n</style>"
        return match.group(0)

    html = re.sub(
        r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\'][^>]*/?>',
        replace_css,
        html,
    )

    # Inline JS: <script src="...js"></script> -> <script>...</script>
    def replace_js(match):
        src = match.group(1)
        js_path = os.path.join(SRC_DIR, src)
        if os.path.exists(js_path):
            js = read_file(js_path)
            print(f"  JS inline: {src}")
            return f"<script>\n{js}\n</script>"
        return match.group(0)

    html = re.sub(
        r'<script[^>]+src=["\']([^"\']+\.js)["\'][^>]*></script>',
        replace_js,
        html,
    )

    with open(DIST_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Bundle complete: {DIST_HTML}")


if __name__ == "__main__":
    bundle()
