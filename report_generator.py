from datetime import datetime
import html
from db_search import pretty_print_payload

def generate_html(urn, results):

    html_parts = []

    html_parts.append("""
    <html>
    <head>
    <title>URN Report</title>
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
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 25px;
        text-align: center;
        font-size: 15px;
    }

    .section {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        margin-bottom: 25px;
        overflow: hidden;
        box-shadow: 0 0 15px rgba(0,0,0,0.35);
    }

    .section-header {
        background: #2563eb;
        color: white;
        padding: 14px;
        font-size: 17px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .table-container {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th {
        background: #111827;
        color: #f8fafc;
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
        background-color: #334155;
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
        color: #93c5fd;
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
        color: #94a3b8;
        padding: 2px;
        transition: all 0.2s ease;
    }

    .copy-btn:hover {
        color: #60a5fa;
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
        background:#2563eb;
        color:white;
        border:none;
        padding:12px 18px;
        border-radius:8px;
        cursor:pointer;
        font-weight:600;
    }

    .search-btn:hover{
        background:#1d4ed8;
    }
    </style>

    <script>

    function copyToClipboard(button, text) {

        navigator.clipboard.writeText(text)
        .then(() => {

            const original = button.innerHTML;
            button.innerHTML = "✔";

            setTimeout(() => {
                button.innerHTML = original;
            }, 2000);

        })
        .catch(err => console.error(err));

    }

    </script>

    </head>
    <body>
    """)

    html_parts.append(f"""
    <div class="top-bar">

        <form id="searchForm" action="/search" method="get" class="search-form">

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
        <div class="section-header">
        {table} | Records Found: {len(data['rows'])}
        </div>
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

            for v in row:

                formatted = str(pretty_print_payload(v))
                escaped = html.escape(formatted)

                if len(formatted) > 100:

                    js_text = html.escape(formatted, quote=True)

                    html_parts.append(
                        f"<td><div class='payload'>"
                        f"<button class='copy-btn' onclick='copyToClipboard(this, `{js_text}`)'>📋</button>"
                        f"{escaped}"
                        f"</div></td>"
                    )
                else:
                    html_parts.append(f"<td>{escaped}</td>")

            html_parts.append("</tr>")

        html_parts.append("</table></div></div>")

    html_parts.append("</body></html>")

    return "".join(html_parts)