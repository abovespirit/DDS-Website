def tba_cell():
    return (
        '<td class="timetable-cell">'
        '<div class="timetable-event timetable-event--tba">'
        '<span class="event-name">TBA</span>'
        '<span class="event-time"><span>TBA</span></span>'
        '<span class="event-instructor">TBA</span>'
        '</div></td>'
    )


def empty_cell():
    return '<td class="timetable-cell empty"></td>'


def table_body():
    rows = []
    for slot in ["4 - 5", "5 - 6", "6 - 7", "7 - 8", "8 - 9"]:
        cells = "".join([tba_cell()] * 4 + [empty_cell()] * 3)
        rows.append(f'<tr><td class="time-slot">{slot}</td>{cells}</tr>')
    return "\n                            ".join(rows)


def mobile_body():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
    slots = ["4 - 5", "5 - 6", "6 - 7", "7 - 8", "8 - 9"]
    parts = []
    for day in days:
        items = "".join(
            f'<li><span class="mobile-event-name">TBA</span>'
            f'<span class="mobile-event-time">{slot}</span></li>'
            for slot in slots
        )
        parts.append(
            f'<div class="mobile-day"><h3 class="mobile-day-title">{day}</h3>'
            f'<ul class="mobile-day-list">{items}</ul></div>'
        )
    for day in ["Friday", "Saturday", "Sunday"]:
        parts.append(
            f'<div class="mobile-day mobile-day--closed">'
            f'<h3 class="mobile-day-title">{day}</h3>'
            f'<p class="mobile-day-closed">Closed</p></div>'
        )
    return "\n                    ".join(parts)


def view(view_id, active=False):
    cls = "timetable-view active" if active else "timetable-view"
    return f"""            <div class="{cls}" id="view-{view_id}">
                <div class="timetable-table-wrap">
                    <table class="timetable-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th>Monday</th>
                                <th>Tuesday</th>
                                <th>Wednesday</th>
                                <th>Thursday</th>
                                <th>Friday</th>
                                <th>Saturday</th>
                                <th>Sunday</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_body()}
                        </tbody>
                    </table>
                </div>
                <div class="timetable-mobile">
                    {mobile_body()}
                </div>
            </div>"""


if __name__ == "__main__":
    header = """            <div class="schedule-header">
                <span class="schedule-label">Schedule</span>
                <h2 class="schedule-title">Class Schedule by Age</h2>
            </div>

            <div class="timetable-filters">
                <button class="filter-btn active" data-view="preschool">Preschool</button>
                <button class="filter-btn" data-view="elementary">Elementary</button>
                <button class="filter-btn" data-view="teens">Teens</button>
            </div>

"""
    views = "\n\n".join([
        view("preschool", True),
        view("elementary"),
        view("teens"),
    ])
    print(header + views)
