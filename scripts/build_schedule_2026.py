#!/usr/bin/env python3
"""Rebuild schedule.html timetable from 2026-27 class schedule flyer."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# day -> list of (start_hour_bucket, name, time_label, ages, notes)
# bucket is used for row placement (hour the class starts, or morning bucket)

PRESCHOOL = {
    "Monday": [
        (16, "Tutu Cute", "4:00 – 4:30 PM", "Ages 3–4", ""),
        (16, "Ballet / Tap", "4:40 – 5:10 PM", "Ages 4–5", ""),
        (17, "Hip Hop", "5:10 – 5:40 PM", "Ages 4–5", ""),
    ],
    "Tuesday": [
        (10, "Dance With Me", "10:00 – 10:30 AM", "Ages 18 mo – 3", ""),
        (10, "Watch Me Dance", "10:35 – 11:20 AM", "Ages 18 mo – 3", ""),
        (11, "Tutu Cute", "11:30 AM – 12:00 PM", "Ages 3–4", ""),
    ],
    "Wednesday": [],
    "Thursday": [],
    "Friday": [
        (17, "Sensory Steps", "5:00 – 5:30 PM", "Sensory-friendly", "New"),
        (17, "Creative Dance", "5:45 – 6:15 PM", "Ages 3–5", ""),
    ],
    "Saturday": [],
    "Sunday": [],
}

ELEMENTARY = {
    "Monday": [
        (17, "Ballet", "5:45 – 6:30 PM", "Ages 8–11", ""),
        (18, "Hip Hop", "6:30 – 7:00 PM", "Ages 8–11", ""),
        (19, "Jazz", "7:00 – 7:45 PM", "Ages 8–11", ""),
        (19, "Acro 1 / 2", "7:45 – 8:30 PM", "Ages 8–11", "**"),
    ],
    "Tuesday": [],
    "Wednesday": [
        (16, "Ballet 2", "4:30 – 5:00 PM", "Ages 5–6", "*"),
        (16, "Ballet", "4:30 – 5:00 PM", "Ages 6–7", ""),
        (17, "Jazz / Tap 2", "5:00 – 5:30 PM", "Ages 5–6", "*"),
        (17, "Jazz / Tap", "5:00 – 5:30 PM", "Ages 6–7", ""),
        (17, "Ballet / Jazz", "5:30 – 6:30 PM", "Ages 6–7", ""),
        (18, "Tap", "6:30 – 7:00 PM", "Ages 8–11", "*"),
        (19, "Jazz 2", "7:00 – 7:45 PM", "Ages 8–11", "*"),
    ],
    "Thursday": [],
    "Friday": [
        (18, "Jazz / Hip Hop", "6:15 – 7:00 PM", "Ages 6–8", ""),
        (19, "Beginner Acro", "7:00 – 7:30 PM", "Ages 6+", "**"),
        (19, "Musical Theater", "7:30 – 8:00 PM", "Ages 6+", ""),
    ],
    "Saturday": [],
    "Sunday": [],
}

TEENS = {
    "Monday": [],
    "Tuesday": [
        (19, "Int / Adv Tap", "7:45 – 8:15 PM", "Ages 12–18", "*"),
        (20, "Adv Acro", "8:15 – 9:15 PM", "Ages 12–18", "**"),
    ],
    "Wednesday": [],
    "Thursday": [
        (17, "Ballet", "5:00 – 6:00 PM", "Ages 12–18", "*"),
        (18, "Jazz", "6:00 – 7:00 PM", "Ages 12–18", "*"),
        (19, "Hip Hop", "7:00 – 7:30 PM", "Ages 12–18", ""),
    ],
    "Friday": [],
    "Saturday": [],
    "Sunday": [],
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def event_html(name, time_label, ages, note=""):
    display = f"{name} {note}".strip() if note in ("*", "**") else (
        f"{name} ({note})" if note else name
    )
    return (
        f'<div class="timetable-event">'
        f'<span class="event-name">{display}</span>'
        f'<span class="event-time"><span>{time_label}</span></span>'
        f'<span class="event-instructor">{ages}</span>'
        f"</div>"
    )


def cell_html(events):
    if not events:
        return '<td class="timetable-cell empty"></td>'
    inner = "".join(event_html(*e[1:]) for e in events)
    return f'<td class="timetable-cell">{inner}</td>'


def slots_for(schedule: dict) -> list[int]:
    hours = sorted({e[0] for day in schedule.values() for e in day})
    if not hours:
        return [16, 17, 18, 19, 20]
    # Only show hour rows that have at least one class
    return hours


def label_for_hour(h: int) -> str:
    end = h + 1

    def fmt(x):
        if x == 0 or x == 24:
            return "12"
        if x == 12:
            return "12"
        if x > 12:
            return str(x - 12)
        return str(x)

    if h < 11:
        return f"{fmt(h)} – {fmt(end)} AM"
    if h == 11:
        return "11 AM – 12 PM"
    return f"{fmt(h)} – {fmt(end)} PM"


def table_html(schedule: dict) -> str:
    slots = slots_for(schedule)
    rows = []
    for hour in slots:
        cells = []
        for day in DAYS:
            events = [e for e in schedule[day] if e[0] == hour]
            cells.append(cell_html(events))
        rows.append(
            f'<tr><td class="time-slot">{label_for_hour(hour)}</td>{"".join(cells)}</tr>'
        )
    body = "\n                            ".join(rows)
    heads = "".join(f"<th>{d}</th>" for d in DAYS)
    return f"""                <div class="timetable-table-wrap">
                    <table class="timetable-table">
                        <thead>
                            <tr>
                                <th></th>
                                {heads}
                            </tr>
                        </thead>
                        <tbody>
                            {body}
                        </tbody>
                    </table>
                </div>"""


def mobile_html(schedule: dict) -> str:
    parts = []
    for day in DAYS:
        events = schedule[day]
        if not events:
            parts.append(
                f'<div class="mobile-day mobile-day--closed">'
                f'<h3 class="mobile-day-title">{day}</h3>'
                f'<p class="mobile-day-closed">No classes</p></div>'
            )
            continue
        items = "".join(
            f'<li><span class="mobile-event-name">{name}</span>'
            f'<span class="mobile-event-meta">{time} · {ages}</span></li>'
            for _, name, time, ages, note in events
        )
        parts.append(
            f'<div class="mobile-day"><h3 class="mobile-day-title">{day}</h3>'
            f'<ul class="mobile-day-list">{items}</ul></div>'
        )
    return '<div class="timetable-mobile">\n                    ' + "\n                    ".join(parts) + "\n                </div>"


def view_html(view_id: str, schedule: dict, active: bool = False) -> str:
    cls = "timetable-view active" if active else "timetable-view"
    return (
        f'            <div class="{cls}" id="view-{view_id}">\n'
        f"{table_html(schedule)}\n"
        f"{mobile_html(schedule)}\n"
        f"            </div>"
    )


def main() -> None:
    body = f"""            <div class="schedule-header">
                <span class="schedule-label">2026 – 2027</span>
                <h2 class="schedule-title">Class Schedule by Age</h2>
            </div>

            <div class="schedule-flyer framed-image framed-image--photo">
                <img src="images/schedule/class-schedule-2026-27.png" alt="DDS Dance Dimensions 2026-2027 Class Schedule">
            </div>

            <div class="timetable-filters">
                <button class="filter-btn active" data-view="preschool">Preschool</button>
                <button class="filter-btn" data-view="elementary">Elementary</button>
                <button class="filter-btn" data-view="teens">Teens</button>
            </div>

{view_html("preschool", PRESCHOOL, active=True)}

{view_html("elementary", ELEMENTARY)}

{view_html("teens", TEENS)}

            <div class="schedule-notes">
                <p><strong>*</strong> Level 2 or Int/Advanced classes need teacher / placement approval.</p>
                <p><strong>**</strong> All Acro classes require a ballet or jazz class as well as teacher / placement approval. Acro placement is based on skill set, not age.</p>
                <p>All classes have dress code requirements — see our <a href="dress-code.html">Dress Code</a> page.</p>
                <p class="schedule-tuition"><strong>Tuition:</strong> $60/mo (30 min) · $75/mo (45 min) · $95/mo (1 hr) · Annual registration $45/dancer or $65/family</p>
            </div>
"""

    html_path = ROOT / "schedule.html"
    html = html_path.read_text(encoding="utf-8")
    start = html.index('            <div class="schedule-header">')
    end = html.index("        </div>\n    </section>", start)
    new_html = html[:start] + body + "\n" + html[end:]
    html_path.write_text(new_html, encoding="utf-8")
    print("Updated schedule.html")


if __name__ == "__main__":
    main()
