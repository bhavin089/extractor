import csv
import json
import os
from html import escape
from pathlib import Path

from agent import process_file


ROOT = Path(__file__).resolve().parent
OUT = Path(os.environ.get("STATIC_SITE_OUT", ROOT / "site")).resolve()
SAMPLES = [
    ROOT / "sample_engineering_drawing.txt",
    ROOT / "sample_inspection_report.txt",
    ROOT / "sample_material_datasheet.txt",
]


def flatten(result):
    row = {
        "source_file": result["source_file"],
        "document_type": result["document_type"],
        "classification_confidence": result["classification_confidence"],
        "confidence_overall": result["confidence_overall"],
        "needs_review": result["needs_review"],
    }
    for key, value in result["attributes"].items():
        row[key] = value["value"]
        row[f"{key}_confidence"] = value["confidence"]
        row[f"{key}_evidence"] = value["evidence"]
    return row


def as_text(value):
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def pct(value):
    return f"{round(float(value) * 100)}%"


def confidence_bar(value):
    percent = pct(value)
    return (
        f'<div class="confidence"><span style="width:{percent}"></span></div>'
        f'<strong>{percent}</strong>'
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for sample in SAMPLES:
        result = process_file(str(sample)).to_dict()
        result["source_file"] = sample.name
        results.append(result)

    rows = [flatten(result) for result in results]
    all_fields = sorted({field for row in rows for field in row})

    (OUT / "engineering_doc_extractions.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    with (OUT / "engineering_doc_extractions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: as_text(row.get(key, "")) for key in all_fields})

    attribute_cards = []
    for result in results:
        attrs = result["attributes"]
        attr_rows = []
        for name, detail in attrs.items():
            value = as_text(detail["value"]) or "Not found"
            flag = "review" if detail["needs_review"] else "ok"
            attr_rows.append(
                "<tr>"
                f"<th>{escape(name.replace('_', ' ').title())}</th>"
                f"<td>{escape(value)}</td>"
                f"<td>{confidence_bar(detail['confidence'])}</td>"
                f"<td><span class='pill {flag}'>{'Review' if flag == 'review' else 'OK'}</span></td>"
                "</tr>"
            )
        attribute_cards.append(
            "<section class='record' data-search='"
            + escape(json.dumps(result).lower())
            + "'>"
            + "<div class='record-head'>"
            + f"<h2>{escape(result['source_file'])}</h2>"
            + f"<span class='type'>{escape(result['document_type'].replace('_', ' ').title())}</span>"
            + "</div>"
            + "<div class='record-meta'>"
            + f"<div><span>Classification</span>{confidence_bar(result['classification_confidence'])}</div>"
            + f"<div><span>Overall</span>{confidence_bar(result['confidence_overall'])}</div>"
            + f"<div><span>Status</span><strong>{'Needs review' if result['needs_review'] else 'Ready'}</strong></div>"
            + "</div>"
            + "<table><thead><tr><th>Attribute</th><th>Value</th><th>Confidence</th><th>Status</th></tr></thead>"
            + "<tbody>"
            + "".join(attr_rows)
            + "</tbody></table>"
            + "</section>"
        )

    review_count = sum(1 for result in results if result["needs_review"])
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Engineering Document Intelligence Output</title>
  <style>
    :root {{
      --ink: #172026;
      --muted: #607080;
      --line: #d9e0e7;
      --panel: #ffffff;
      --paper: #f6f8fb;
      --green: #207a4c;
      --amber: #a15c00;
      --blue: #2364aa;
      --red: #a63a3a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
    }}
    header {{
      padding: 28px clamp(18px, 4vw, 48px) 18px;
      background: #ffffff;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{ margin: 0 0 8px; font-size: clamp(26px, 4vw, 42px); letter-spacing: 0; }}
    p {{ margin: 0; color: var(--muted); line-height: 1.45; }}
    main {{ padding: 22px clamp(18px, 4vw, 48px) 44px; }}
    .toolbar {{
      display: grid;
      grid-template-columns: minmax(220px, 1fr) auto auto;
      gap: 12px;
      align-items: center;
      margin-bottom: 18px;
    }}
    input {{
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 0 12px;
      font: inherit;
      background: #fff;
    }}
    a.button {{
      min-height: 42px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0 14px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      text-decoration: none;
      white-space: nowrap;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .stat, .record {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .stat {{ padding: 16px; }}
    .stat span, .record-meta span {{ display: block; color: var(--muted); font-size: 13px; }}
    .stat strong {{ display: block; margin-top: 5px; font-size: 28px; }}
    .record {{ margin-bottom: 16px; overflow: hidden; }}
    .record-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }}
    h2 {{ margin: 0; font-size: 19px; letter-spacing: 0; }}
    .type, .pill {{
      border-radius: 999px;
      padding: 5px 9px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .type {{ background: #e9f1fb; color: var(--blue); }}
    .pill.ok {{ background: #e7f4ed; color: var(--green); }}
    .pill.review {{ background: #fff1dc; color: var(--amber); }}
    .record-meta {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      padding: 14px 18px;
      border-bottom: 1px solid var(--line);
    }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 12px 18px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ width: 22%; font-size: 13px; color: #35414d; background: #fafbfc; }}
    td {{ color: #26323c; }}
    .confidence {{
      display: inline-block;
      width: 96px;
      height: 8px;
      margin-right: 8px;
      border-radius: 999px;
      background: #e4e9ef;
      overflow: hidden;
      vertical-align: middle;
    }}
    .confidence span {{ display: block; height: 100%; background: var(--green); }}
    .hidden {{ display: none; }}
    @media (max-width: 760px) {{
      .toolbar, .stats, .record-meta {{ grid-template-columns: 1fr; }}
      .record-head {{ align-items: flex-start; flex-direction: column; }}
      table, thead, tbody, tr, th, td {{ display: block; width: 100%; }}
      thead {{ display: none; }}
      tr {{ border-bottom: 1px solid var(--line); }}
      th, td {{ border: 0; padding: 8px 14px; }}
      th {{ padding-top: 14px; }}
      td:last-child {{ padding-bottom: 14px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Engineering Document Intelligence Output</h1>
    <p>Generated from the prototype agent using the included sample engineering documents.</p>
  </header>
  <main>
    <div class="toolbar">
      <input id="search" type="search" placeholder="Search file, document type, attribute, or value">
      <a class="button" href="engineering_doc_extractions.json" download>Download JSON</a>
      <a class="button" href="engineering_doc_extractions.csv" download>Download CSV</a>
    </div>
    <section class="stats">
      <div class="stat"><span>Documents Processed</span><strong>{len(results)}</strong></div>
      <div class="stat"><span>Review Queue</span><strong>{review_count}</strong></div>
      <div class="stat"><span>Average Confidence</span><strong>{pct(sum(r['confidence_overall'] for r in results) / len(results))}</strong></div>
    </section>
    <div id="records">
      {''.join(attribute_cards)}
    </div>
  </main>
  <script>
    const search = document.getElementById('search');
    const records = [...document.querySelectorAll('.record')];
    search.addEventListener('input', () => {{
      const query = search.value.trim().toLowerCase();
      records.forEach(record => {{
        record.classList.toggle('hidden', query && !record.dataset.search.includes(query));
      }});
    }});
  </script>
</body>
</html>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
