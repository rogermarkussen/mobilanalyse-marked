from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
INDEX = DIST / "index.html"
MENU_JS = DIST / "assets" / "export-menu.js"


def main() -> None:
    MENU_JS.write_text(
        """
document.addEventListener("click", (event) => {
  document.querySelectorAll("details.export-menu[open]").forEach((menu) => {
    if (!menu.contains(event.target)) {
      menu.removeAttribute("open");
    }
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    document.querySelectorAll("details.export-menu[open]").forEach((menu) => {
      menu.removeAttribute("open");
    });
  }
});
""".strip()
        + "\n",
        encoding="utf-8",
    )

    html = INDEX.read_text(encoding="utf-8")
    script_tag = '<script src="assets/export-menu.js" defer></script>'
    if script_tag in html:
        return
    if "</body>" not in html:
        raise RuntimeError("Could not find </body> in dist/index.html")
    INDEX.write_text(html.replace("</body>", f"{script_tag}\n</body>"), encoding="utf-8")


if __name__ == "__main__":
    main()
