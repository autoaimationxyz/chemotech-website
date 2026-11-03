#!/usr/bin/env python3
"""Parse the Product Master List (pdftotext -layout output) into JSON.

Usage:
  pdftotext -layout Chemotech_Product_Master_List.pdf master.txt
  python3 tools/parse_master_list.py master.txt tools/products.json
"""
import json, re, sys

MAKES_COL = 59  # character column where the MAKES column starts

src, dst = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().replace("\f", "\n").split("\n")

# Summary table: main makes per product (columns at fixed positions)
main_makes, last = {}, None
for l in lines:
    if "Products, Variants & Makes" in l:
        break
    m = re.match(r"^ (\d{2}) {3,}(.+?) {2,}(.+?) {2,}(\d+)\s*$", l)
    if m:
        last = int(m.group(1)); main_makes[last] = m.group(3).strip()
    elif last and l.startswith(" " * 50) and l.strip() and not re.search(r"\d+$", l.strip()):
        main_makes[last] += " " + l.strip()
main_makes = {k: [x.strip() for x in v.split("·") if x.strip()] for k, v in main_makes.items()}

# Only the detailed section (after the summary table)
start = next(i for i, l in enumerate(lines) if l.strip().startswith("Products, Variants & Makes"))
lines = lines[start + 1:]

products, cur, mode = [], None, None
row = None


def flush_row():
    global row
    if row and cur is not None:
        v = re.sub(r"(\w)- (\w)", r"\1-\2", re.sub(r"\s+", " ", row["v"]).strip())
        m = re.sub(r"\s+", " ", row["m"]).strip()
        cur["variants"].append({"name": "" if v == "—" else v, "makes": [x.strip() for x in m.split(",") if x.strip()]})
    row = None


for raw in lines:
    s = raw.rstrip()
    if not s.strip():
        continue
    if "Product Master List" in s and "Page" in s:
        continue
    hm = re.match(r"^(\d{2})\. (.+)$", s.strip())
    if hm and not s.startswith(" "):
        flush_row()
        cur = {"no": int(hm.group(1)), "name": hm.group(2).strip(), "desc": "", "variants": [], "note": ""}
        products.append(cur)
        mode = "desc"
        continue
    if cur is None:
        continue
    if s.strip().startswith("VARIANT / TYPE"):
        mode = "rows"
        continue
    if mode == "desc":
        cur["desc"] = (cur["desc"] + " " + s.strip()).strip()
        continue
    # note paragraph (e.g. DG sets)
    if "We are a leading supplier" in s or mode == "note":
        flush_row()
        cur["note"] = (cur["note"] + " " + s.strip()).strip()
        mode = "note" if not s.strip().endswith(".") else "rows"
        continue
    left = s[:MAKES_COL].strip()
    right = s[MAKES_COL:].strip() if len(s) > MAKES_COL else ""
    if row is None:
        row = {"v": left, "m": right}
    elif not left:                       # makes wrapped
        row["m"] += " " + right
    elif not right:                      # variant name wrapped
        row["v"] += " " + left
    elif row["m"].rstrip().endswith(","):  # both columns wrapped together
        row["v"] += " " + left
        row["m"] += " " + right
    else:
        flush_row()
        row = {"v": left, "m": right}
flush_row()

# Clean the DG note prefix
for p in products:
    p["note"] = re.sub(r"^Diesel Generator Sets:\s*", "", p["note"])

for p in products:
    p["main_makes"] = main_makes.get(p["no"], [])
nv = sum(len(p["variants"]) for p in products)
print(len(products), "products,", nv, "variants")
assert len(products) == 56, len(products)
json.dump(products, open(dst, "w"), ensure_ascii=False, indent=1)
