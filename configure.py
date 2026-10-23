"""Fill in the website templates -> site_public/ (ready for GitHub Pages).

Example:
  python site/configure.py --owner "Shamim Akter" --business "Shamim Auto and Service Center" \
         --email you@gmail.com [--domain motostock.example.com] [--relay]
"""
import argparse, re, shutil, sys
from datetime import date
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--owner", required=True, help="your name or company, shown as the app provider")
p.add_argument("--email", required=True, help="support/contact email (also use it in Google Cloud)")
p.add_argument("--business", default="", help="optional business name")
p.add_argument("--app-name", default="MotoStock")
p.add_argument("--domain", default="", help="custom domain, e.g. motostock.example.com (writes the CNAME file)")
p.add_argument("--relay", action="store_true", help="mention the sign-in relay (use only if you deploy the broker)")
a = p.parse_args()
if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", a.email):
    sys.exit("That email address does not look valid.")
src, out = Path(__file__).resolve().parent, Path(__file__).resolve().parent.parent / "site_public"
if out.exists():
    shutil.rmtree(out)
out.mkdir()
values = {"{{APP_NAME}}": a.app_name, "{{OWNER}}": a.owner, "{{EMAIL}}": a.email, "{{DATE}}": date.today().strftime("%B %d, %Y").replace(" 0", " "),
          "{{YEAR}}": str(date.today().year), "{{BUSINESS_LINE}}": f" ({a.business})" if a.business else ""}
for f in src.iterdir():
    if f.name in ("configure.py",) or f.name.startswith("."):
        continue
    if f.suffix == ".html":
        text = f.read_text(encoding="utf-8")
        text = re.sub(r"<!--RELAY-->(.*?)<!--/RELAY-->", (r"\1" if a.relay else ""), text, flags=re.S)
        for k, v in values.items():
            text = text.replace(k, v)
        left = re.findall(r"\{\{[A-Z_]+\}\}", text)
        if left:
            sys.exit(f"Unfilled placeholders in {f.name}: {left}")
        (out / f.name).write_text(text, encoding="utf-8")
    else:
        shutil.copy2(f, out / f.name)
(out / ".nojekyll").write_text("")
if a.domain:
    (out / "CNAME").write_text(a.domain.strip() + "\n")
print(f"Created {out} - upload the files INSIDE this folder to your GitHub repository.")
