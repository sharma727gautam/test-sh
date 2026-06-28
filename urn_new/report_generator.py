from datetime import datetime
import html
from pathlib import Path

from db_search import pretty_print_payload


# def is_small_payload(text):

#     if text is None:
#         return True

#     s = str(text).strip()

#     if not s:
#         return True

#     return len(s.split("\n")) <= 5 and len(s) <= 500


# def generate_html(urn, results):

#     template_path = Path("templates/report.html")

#     with open(template_path, encoding="utf-8") as f:
#         html_template = f.read()

#     html_parts = []

#     html_parts.append(f"""

#     <div class="top-bar">

#         <form id="searchForm" action="search" method="get" class="search-form">

#             <input
#                 type="text"
#                 name="urn"
#                 value="{urn}"
#                 placeholder="Enter URN"
#                 class="search-input"
#                 required
#             >

#             <button
#                 type="submit"
#                 class="search-btn">

#                 Search

#             </button>

#         </form>

#     </div>


#     <h2>RRN Finder</h2>


#     <div class="summary">

#         <b>URN:</b> {urn}

#         <br><br>

#         <b>Generated:</b>
#         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#     </div>

#     """)

#     for table, data in results.items():

#         html_parts.append(f"""

#         <div class="section">

#             <div
#                 class="section-header"
#                 onclick="toggleSection('body_{table}')">

#                 ▼ {table} | Records Found: {len(data["rows"])}

#             </div>

#             <div
#                 id="body_{table}"
#                 class="section-body">

#         """)

#         if not data["rows"]:

#             html_parts.append("""

#                 <div class="no-records">

#                     No Records Found

#                 </div>

#                 </div>

#                 </div>

#             """)

#             continue

#         html_parts.append("""

#             <div class="table-container">

#             <table>

#         """)

#         html_parts.append("<tr>")

#         for column in data["columns"]:

#             html_parts.append(f"<th>{column}</th>")

#         html_parts.append("</tr>")

#         payload_columns = [
#             "INPUT_DATA",
#             "OUTPUT_DATA",
#             "EXCEPTION",
#             "ACTUAL_ERROR"
#         ]

#         for row in data["rows"]:

#             html_parts.append("<tr>")

#             for col_index, value in enumerate(row):

#                 formatted = str(pretty_print_payload(value))

#                 escaped = html.escape(formatted)

#                 column_name = data["columns"][col_index]

#                 if column_name in payload_columns:

#                     if formatted is None or formatted.strip() == "":

#                         html_parts.append("""

#                             <td class="null-value">

#                                 -

#                             </td>

#                         """)

#                     elif is_small_payload(formatted):

#                         js_text = html.escape(formatted, quote=True)

#                         html_parts.append(f"""

#                             <td>

#                                 <span class="inline-payload">

#                                     {escaped}

#                                 </span>

#                                 <button
#                                     class="copy-mini"
#                                     onclick="miniCopy(this, `{js_text}`)">

#                                     &#128203;

#                                 </button>

#                             </td>

#                         """)

#                     else:

#                         js_text = html.escape(formatted, quote=True)

#                         html_parts.append(f"""

#                             <td>

#                                 <button
#                                     class="view-btn"
#                                     onclick="openModal('{column_name}', `{js_text}`)">

#                                     &#128196; View

#                                 </button>

#                                 <button
#                                     class="copy-mini"
#                                     onclick="miniCopy(this, `{js_text}`)">

#                                     &#128203;

#                                 </button>

#                             </td>

#                         """)

#                 else:

#                     html_parts.append(f"<td>{escaped}</td>")

#             html_parts.append("</tr>")

#         html_parts.append("""

#                 </table>

#             </div>

#         </div>

#     </div>

#         """)
        
#         html_parts.append("""

#         <div id="payloadModal" class="modal">

#             <div class="modal-content">

#                 <div class="modal-header">

#                     <span id="modalTitle">

#                         Payload Viewer

#                     </span>

#                     <button
#                         class="modal-btn"
#                         onclick="closeModal()">

#                         &#10006;

#                     </button>

#                 </div>

#                 <div
#                     id="modalBody"
#                     class="modal-body">

#                 </div>

#                 <div class="modal-actions">

#                     <button
#                         id="copyModalBtn"
#                         class="modal-btn">

#                         &#128203; Copy

#                     </button>

#                     <button
#                         class="modal-btn"
#                         onclick="closeModal()">

#                         Close

#                     </button>

#                 </div>

#             </div>

#         </div>

#         """)
#     report_html = html_template.replace(
#         "{{REPORT_CONTENT}}",
#         "".join(html_parts)
#     )

#     return report_html

def is_small_payload(text):

    if text is None:
        return True

    text = str(text).strip()

    if not text:
        return True

    return (
        len(text.splitlines()) <= 5
        and len(text) <= 500
    )


def pretty_column(name):

    return (
        name
        .replace("_", " ")
        .title()
    )

def generate_html(urn, results):

    template = Path(
        "templates/report.html"
    ).read_text(
        encoding="utf-8"
    )
    summary = f"""

    <div class="summary">

        <div>

            <span class="label">
                URN
            </span>

            <span class="value">
                {urn}
            </span>

        </div>

        <div>

            <span class="label">
                Generated
            </span>

            <span class="value">
                {datetime.now().strftime("%d %b %Y %H:%M:%S")}
            </span>

        </div>

    </div>

    """
    tabs = []

    for table, data in results.items():

        title = (
            table
            .replace("_", " ")
        )

        count = len(data["rows"])

        active = ""

        if not tabs:

            active = "active"

        tabs.append(f"""

            <button
                class="tab-button {active}"
                onclick="showTab(event, '{table}')">

                <div class="tab-title">

                    {title}

                </div>

                <div class="tab-count">

                    {count} Records

                </div>

            </button>

        """)
    sections = []

    for index, (table, data) in enumerate(results.items()):

        visible = ""

        if index != 0:

            visible = "display:none;"

        section = f"""

        <div

            id="{table}"

            class="tab-content"

            style="{visible}"

        >

        """
        if not data["rows"]:

            section += """

            <div class="no-records">

                No Records Found

            </div>

            """

            section += "</div>"

            sections.append(section)

            continue
        for record_no, row in enumerate(data["rows"], start=1):
            card_class = ""

            if "RESPONSE_STATUS" in data["columns"]:

                idx = data["columns"].index("RESPONSE_STATUS")

                status = str(row[idx]).upper()

                if status in ("SUCCESS", "0"):

                    card_class = "record-success"

                else:

                    card_class = "record-failed"
            body_style = ""

            icon = "▲"

            toggle = ""

            if len(data["rows"]) > 1:

                body_style = "display:none;"

                icon = "▼"

                toggle = "toggleRecord(this)" 
            title = f"Record {record_no}"

            if "URN" in data["columns"]:

                urn_index = data["columns"].index("URN")

                if row[urn_index]:

                    title = str(row[urn_index])


            section += f"""

            <div class="record-card {card_class}">

            <div
                class="record-header"
                onclick="{toggle}">

                    <span>

                        {title}

                    </span>

                    <span class="expand-icon">

                        {icon}

                    </span>

                </div>

                <div class="record-body" style="{body_style}">

            """
            for column, value in zip(
                data["columns"],
                row
            ):
                display_name = pretty_column(column)

                formatted = pretty_print_payload(value)

                escaped = html.escape(str(formatted))

                payload_columns = {

                    "INPUT_DATA",

                    "OUTPUT_DATA",

                    "EXCEPTION",

                    "ACTUAL_ERROR"

                }
                if column in payload_columns:
                    if is_small_payload(formatted):

                        js = html.escape(
                            str(formatted),
                            quote=True
                        )

                        section += f"""

                        <div class="field">

                            <div class="field-name">

                                {display_name}

                            </div>

                            <div class="field-value">

                                <span>

                                    {escaped}

                                </span>

                                <button
                                    class="copy-mini"
                                    onclick="miniCopy(this, `{js}`)">

                                    📋

                                </button>

                            </div>

                        </div>

                        """
                    else:

                        js = html.escape(
                            str(formatted),
                            quote=True
                        )

                        section += f"""

                        <div class="field">

                            <div class="field-name">

                                {display_name}

                            </div>

                            <div class="field-value">

                                <button
                                    class="view-btn"
                                    onclick="openModal('{display_name}', `{js}`)">

                                    View Payload

                                </button>

                                <button
                                    class="copy-mini"
                                    onclick="miniCopy(this, `{js}`)">

                                    📋

                                </button>

                            </div>

                        </div>

                        """

                else:

    
                    section += f"""

                    <div class="field">

                        <div class="field-name">

                            {display_name}

                        </div>

                        <div class="field-value {card_class}">

                            {escaped}

                        </div>

                    </div>

                    """
            section += """

                    </div>

                </div>

                """
        section += "</div>"

        sections.append(section)
    report_html = template.replace(
        "{{SUMMARY}}",
        summary
    )

    report_html = report_html.replace(
        "{{TABS}}",
        "".join(tabs)
    )

    report_html = report_html.replace(
        "{{REPORT_CONTENT}}",
        "".join(sections)
    )

    return report_html
