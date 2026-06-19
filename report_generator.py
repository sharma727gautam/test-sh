from datetime import datetime
import html
from db_search import pretty_print_payload

def is_small_payload(text):
    if text is None:
        return True

    s = str(text).strip()

    if not s:
        return True

    return len(s.split("\n")) <= 5 and len(s) <= 500

def generate_html(urn, results):

    html_parts = []

    html_parts.append("""
    <html>
    <head>
    <title>URN Report</title>
    <meta charset="UTF-8">
    <style>

    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        padding: 25px;
        background-color: #0f172a;
        color: #e2e8f0;
        font-family: "Segoe UI", Arial, sans-serif;
    }

    h2 {
        text-align: center;
        margin-bottom: 10px;
        color: #f8fafc;
    }

    .summary {
        background: #1a1f2e;
        border: 1px solid #2a3142;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 25px;
        text-align: center;
        font-size: 15px;
    }

    .section {
        background: #1a1f2e;
        border: 1px solid #2a3142;
        border-radius: 10px;
        margin-bottom: 25px;
        overflow: hidden;
        box-shadow: 0 0 15px rgba(0,0,0,0.35);
    }


    .section-header {
        background:#232b3b;
        color:#dbe2ea;
        border-bottom: 1px solid #323b4d;
        padding:14px;
        text-align:center;
        font-size:17px;
        font-weight:600;
        cursor:pointer;
    }
    .section-body{
        display:block;
    }
    .table-container {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th {
        background: #161c28;
        color: #dbe2ea;
        padding: 12px;
        text-align: left;
        border-bottom: 2px solid #334155;
        position: sticky;
        top: 0;
        z-index: 10;
    }

    td {
        padding: 10px;
        border-bottom: 1px solid #334155;
        color: #e5e7eb;
        vertical-align: top;
        white-space: nowrap;
    }

    tr:nth-child(even) {
        background-color: #273449;
    }

    tr:hover {
        background-color: #2a3142;
    }

    .no-records {
        padding: 20px;
        color: #f87171;
        font-weight: bold;
        text-align: center;
    }

    .payload {
        position: relative;
        background: #111827;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 12px;
        max-height: 350px;
        max-width: 900px;
        overflow-y: auto;
        overflow-x: auto;
        font-family: Consolas, Monaco, monospace;
        font-size: 13px;
        color: #cbd5e1;
        white-space: pre-wrap;
        word-break: break-word;
    }

    .copy-btn {
        position: absolute;
        top: 6px;
        right: 8px;
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 16px;
        color:#7c8799;
        padding: 2px;
        transition: all 0.2s ease;
    }

    .copy-btn:hover {
        color:#cbd5e1;
    }

    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #111827;
    }

    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    .top-bar{
        margin-bottom:20px;
    }

    .back-btn{
        display:inline-block;
        text-decoration:none;
        background:#2563eb;
        color:white;
        padding:10px 16px;
        border-radius:8px;
        font-weight:600;
        transition:0.2s;
    }

    .back-btn:hover{
        background:#1d4ed8;
    }

    .search-form{
        display:flex;
        gap:10px;
        align-items:center;
    }

    .search-input{
        width:450px;
        padding:12px;
        border-radius:8px;
        border:1px solid #475569;
        background:#111827;
        color:white;
        font-size:14px;
    }

    .search-input:focus{
        outline:none;
        border-color:#3b82f6;
    }

    .search-btn{
        background:#374151;
        color:white;
        border:none;
        padding:12px 18px;
        border-radius:8px;
        cursor:pointer;
        font-weight:600;
    }

    .search-btn:hover{
        background:#4b5563;
    }

    .view-btn{
        background:#374151;
        color:white;
        border:none;
        border-radius:6px;
        padding:8px 12px;
        cursor:pointer;
        font-size:13px;
    }

    .view-btn:hover{
        background:#4b5563;
    }
    .modal{
        display:none;
        position:fixed;
        z-index:99999;
        left:0;
        top:0;
        width:100%;
        height:100%;
        background:rgba(0,0,0,0.85);
    }

    .modal-content{
        background:#111827;
        width:85%;
        max-width:1200px;
        margin:40px auto;
        border-radius:12px;
        border:1px solid #334155;
        overflow:hidden;
    }

    .modal-header{
        background:#232b3b;
        border-bottom:1px solid #323b4d;
        color:white;
        padding:15px;
        display:flex;
        justify-content:space-between;
        align-items:center;
    }

    .modal-body{
        padding:20px;
        max-height:70vh;
        overflow:auto;
        white-space:pre-wrap;
        font-family:Consolas, monospace;
        color:#93c5fd;
    }

    .modal-actions{
        padding:15px;
        background:#0f172a;
        text-align:right;
    }

    .modal-btn{
        background:#2563eb;
        color:white;
        border:none;
        padding:10px 15px;
        border-radius:6px;
        cursor:pointer;
        margin-left:10px;
    }
    .inline-payload{
        font-family: Consolas, monospace;
        font-size: 12px;
        color: #93c5fd;
        margin-right: 6px;
    }

    .copy-mini{
        background: transparent;
        border: none;
        cursor: pointer;
        color: #94a3b8;
        font-size: 14px;
        padding: 2px;
    }

    .copy-mini:hover{
        color: #60a5fa;
    }
    </style>

    <script>

    function copyToClipboard(button, text) {

        navigator.clipboard.writeText(text)
        .then(() => {

            const original = button.innerHTML;
            button.innerHTML = "&#10004;";

            setTimeout(() => {
                button.innerHTML = original;
            }, 2000);

        })
        .catch(err => console.error(err));

    }
    let modalContent = "";

    function openModal(title, content){

        modalContent = content;

        document.getElementById("modalTitle").innerText = title;
        document.getElementById("modalBody").innerText = content;

        document.getElementById("payloadModal").style.display = "block";
    }

    function closeModal(){

        document.getElementById("payloadModal").style.display = "none";
    }

    function copyModalContent(button, text){

        navigator.clipboard.writeText(text).then(() => {

            const original = button.innerHTML;
            button.innerHTML = "&#10004;";

            setTimeout(() => {
                button.innerHTML = original;
            }, 1500);

        });

    }
    function miniCopy(button, text){

        navigator.clipboard.writeText(text).then(() => {

            const original = button.innerHTML;
            button.innerHTML = "&#10004;";

            setTimeout(() => {
                button.innerHTML = original;
            }, 1500);

        });

    }
    function toggleSection(id){

        const section = document.getElementById(id);

        if(section.style.display === "none"){
            section.style.display = "block";
        }
        else{
            section.style.display = "none";
        }

    }
    
    </script>

    </head>
    <body>
    """)

    html_parts.append(f"""
    <div class="top-bar">

        <form id="searchForm" action="search" method="get" class="search-form">

            <input
                type="text"
                name="urn"
                value="{urn}"
                placeholder="Enter URN"
                class="search-input"
                required
            >

            <button type="submit" class="search-btn">
                Search
            </button>

        </form>

    </div>

    <h2>RRN Finder</h2>

    <div class="summary">
        <b>URN:</b> {urn}
        <br><br>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """)

    for table, data in results.items():

        html_parts.append(f"""
        <div class="section">

        <div
            class="section-header"
            onclick="toggleSection('body_{table}')">

            ▼ {table} | Records Found: {len(data['rows'])}

        </div>

        <div
            id="body_{table}"
            class="section-body">
        """)

        if not data["rows"]:
            html_parts.append('<div class="no-records">No Records Found</div></div>')
            continue

        html_parts.append('<div class="table-container"><table>')

        html_parts.append("<tr>")
        for c in data["columns"]:
            html_parts.append(f"<th>{c}</th>")
        html_parts.append("</tr>")

        for row in data["rows"]:
            html_parts.append("<tr>")

            # for v in row:
            for col_index, v in enumerate(row):
                formatted = str(pretty_print_payload(v))
                escaped = html.escape(formatted)

                # if len(formatted) > 100:

                #     js_text = html.escape(formatted, quote=True)

                #     html_parts.append(
                #         f"<td><div class='payload'>"
                #         f"<button class='copy-btn' onclick='copyToClipboard(this, `{js_text}`)'>📋</button>"
                #         f"{escaped}"
                #         f"</div></td>"
                #     )
                # else:
                #     html_parts.append(f"<td>{escaped}</td>")
                payload_columns = [
                    "INPUT_DATA",
                    "OUTPUT_DATA",
                    "EXCEPTION",
                    "ACTUAL_ERROR"
                ]

                # column_name = data["columns"][row.index(v)]
                column_name = data["columns"][col_index]

                if column_name in payload_columns:

                    if formatted is None or str(formatted).strip() == "":
                        html_parts.append("<td class='null-value'>-</td>")

                    elif is_small_payload(formatted):

                        js_text = html.escape(formatted, quote=True)

                        html_parts.append(f"""
                        <td>
                            <span class="inline-payload">{escaped}</span>

                            <button class="copy-mini"
                                onclick="miniCopy(this, `{js_text}`)">
                                &#128203;
                            </button>
                        </td>
                        """)

                    else:

                        js_text = html.escape(formatted, quote=True)

                        html_parts.append(f"""
                        <td>
                            <button class="view-btn"
                                onclick="openModal('{column_name}', `{js_text}`)">
                                &#128196; View
                            </button>

                            <button class="copy-mini"
                                onclick="miniCopy(this, `{js_text}`)">
                                &#128203;
                            </button>
                        </td>
                        """)
                else:
                    html_parts.append(f"<td>{escaped}</td>")
            html_parts.append("</tr>")

        html_parts.append("</table></div></div></div>")

    html_parts.append("""

    <div id="payloadModal" class="modal">

        <div class="modal-content">

            <div class="modal-header">

                <span id="modalTitle">Payload Viewer</span>

                <button
                    class="modal-btn"
                    onclick="closeModal()">
                    &#10006;
                </button>

            </div>

            <div
                id="modalBody"
                class="modal-body">
            </div>

            <div class="modal-actions">

                <button
                    class="modal-btn"
                    onclick="copyModalContent(this, `{js_text}`)">
                    &#128203; Copy
                </button>

                <button
                    class="modal-btn"
                    onclick="closeModal()">
                    Close
                </button>

            </div>

        </div>

    </div>

    </body>
    </html>

    """)

    return "".join(html_parts)