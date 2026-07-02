from pathlib import Path

root = Path(__file__).resolve().parents[1]
html = (root / "schedule.html").read_text(encoding="utf-8")
body = (root / "_schedule_body.txt").read_text(encoding="utf-8-sig").strip()
marker_start = '            <div class="schedule-header">'
marker_end = '        </div>\n    </section>'
start = html.index(marker_start)
end = html.index(marker_end, start)
new_html = html[:start] + body + "\n\n" + html[end:]
(root / "schedule.html").write_text(new_html, encoding="utf-8")
print("Updated schedule.html")
