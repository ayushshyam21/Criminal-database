"""
scripts/render_diagrams.py
Renders docs/erd.mmd and docs/eerd.mmd to high-resolution PNG images
using headless Microsoft Edge or Google Chrome.
"""
import os
import subprocess
import tempfile

def find_browser():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def render_mermaid_to_png(mmd_path, png_path, browser_path):
    if not os.path.exists(mmd_path):
        print(f"Skipping {mmd_path} (file not found)")
        return False
        
    with open(mmd_path, "r", encoding="utf-8") as f:
        mermaid_code = f.read()

    # Create self-contained HTML page
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 30px;
            background-color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: inline-block;
        }}
        .mermaid {{
            background: #ffffff;
        }}
    </style>
</head>
<body>
    <pre class="mermaid">
{mermaid_code}
    </pre>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            er: {{
                useMaxWidth: false
            }}
        }});
    </script>
</body>
</html>"""

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tf:
        tf.write(html_content)
        temp_html = tf.name

    try:
        cmd = [
            browser_path,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=2",
            "--window-size=2400,1600",
            f"--screenshot={png_path}",
            f"file:///{temp_html.replace(os.sep, '/')}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if os.path.exists(png_path) and os.path.getsize(png_path) > 0:
            print(f"[OK] Rendered: {os.path.basename(png_path)} ({os.path.getsize(png_path)} bytes)")
            return True
        else:
            print(f"[WARN] Screenshot empty or missing for {png_path}: {res.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to render {mmd_path}: {e}")
        return False
    finally:
        if os.path.exists(temp_html):
            try:
                os.remove(temp_html)
            except Exception:
                pass

if __name__ == "__main__":
    browser = find_browser()
    if not browser:
        print("No compatible browser (Edge/Chrome) found for rendering.")
    else:
        print(f"Using browser: {browser}")
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        erd_mmd = os.path.join(base_dir, "docs", "erd.mmd")
        erd_png = os.path.join(base_dir, "docs", "erd.png")
        eerd_mmd = os.path.join(base_dir, "docs", "eerd.mmd")
        eerd_png = os.path.join(base_dir, "docs", "eerd.png")

        render_mermaid_to_png(erd_mmd, erd_png, browser)
        render_mermaid_to_png(eerd_mmd, eerd_png, browser)
