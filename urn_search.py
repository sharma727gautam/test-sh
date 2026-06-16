import os
import oracledb
from datetime import datetime
import html

DB_CONFIG = {
    "user": "SYSTEM",
    "password": "oracle",
    "dsn": "localhost:1521/XEPDB1"
}

TABLES = {
    "API_LOG": {
        "table": "API_LOG",
        "columns": ["URN","RESPONSE_STATUS","ERROR_CODE","URL","EXP_IP","API_NAME","EXP_BROKER","EXP_EG","REQUEST_DATE_TIME","CREATION_DATE_TIME","ACTIVITY","ACTUAL_ERROR","DB_OPERATION"]
    },
    "API_DETAILS": {
        "table": "API_DETAILS",
        "columns": ["URN","INPUT_DATA","OUTPUT_DATA","EXCEPTION"]
    },
    "ORCH_API_LOG": {
        "table": "ORCH_API_LOG",
        "columns": ["URN","URN_CHILD","URL","API_NAME"]
    },
    "ORCH_API_DETAILS": {
        "table": "ORCH_API_DETAILS",
        "columns": ["URN","INPUT_DATA","OUTPUT_DATA","EXCEPTION"]
    },
    "BACKEND_LOG": {
        "table": "BACKEND_LOG",
        "columns": ["URN","ERROR_CODE","END_POINT_URL","END_POINT_PORT","REQUEST_DATE_TIME","RESPONSE_DATE_TIME","SYS_IP","API_NAME","SYS_BROKER","SYS_EG"]
    },
    "BACKEND_DETAILS": {
        "table": "BACKEND_DETAILS",
        "columns": ["URN","EXCEPTION"]
    }
}

def search_urn(urn):

    conn = oracledb.connect(**DB_CONFIG)
    cursor = conn.cursor()

    results = {}

    urn = urn.upper()

    if urn.startswith("EIS"):

        backend_urns = [urn]

        results = {}

        common_tables = ["API_LOG", "API_DETAILS", "ORCH_API_LOG", "ORCH_API_DETAILS"]

        for name in common_tables:

            cfg = TABLES[name]

            results[name] = {
                "columns": cfg["columns"],
                "rows": []
            }

        backend_tables = ["BACKEND_LOG", "BACKEND_DETAILS"]

        for name in backend_tables:

            cfg = TABLES[name]

            cursor.execute(f"""
                SELECT {",".join(cfg["columns"])}
                FROM {cfg["table"]}
                WHERE URN = :urn
            """, {"urn": urn})

            results[name] = {
                "columns": cfg["columns"],
                "rows": cursor.fetchall()
            }

        cursor.close()
        conn.close()

        return results

    if len(urn) == 25:
        search_type = "EXACT"
        pattern = urn
        operator = "="
    else:
        search_type = "PREFIX"
        pattern = urn + "%"
        operator = "LIKE"

    print(f"Search Mode: {search_type}")

    cursor.execute(f"""
        SELECT DISTINCT URN
        FROM API_LOG
        WHERE URN {operator} :urn
    """, {"urn": pattern})

    parent_urns = [r[0] for r in cursor.fetchall()]

    if search_type == "EXACT" and not parent_urns:
        parent_urns = [urn]

    backend_urns = []

    for parent_urn in parent_urns:

        cursor.execute("""
            SELECT DISTINCT URN_CHILD
            FROM ORCH_API_LOG
            WHERE URN = :urn
            AND URN_CHILD IS NOT NULL
        """, {"urn": parent_urn})

        children = [r[0] for r in cursor.fetchall()]

        if children:
            backend_urns.extend(children)
        else:
            backend_urns.append(parent_urn)

    backend_urns = list(set(backend_urns))

    common_tables = ["API_LOG", "API_DETAILS", "ORCH_API_LOG", "ORCH_API_DETAILS"]

    for name in common_tables:

        cfg = TABLES[name]

        sql = f"""
        SELECT {",".join(cfg["columns"])}
        FROM {cfg["table"]}
        WHERE URN {operator} :urn
        """

        cursor.execute(sql, {"urn": pattern})
        rows = cursor.fetchall()

        results[name] = {
            "columns": cfg["columns"],
            "rows": rows
        }

    backend_tables = ["BACKEND_LOG", "BACKEND_DETAILS"]

    for name in backend_tables:

        cfg = TABLES[name]

        all_rows = []

        for burl in backend_urns:

            sql = f"""
            SELECT {",".join(cfg["columns"])}
            FROM {cfg["table"]}
            WHERE URN = :urn
            """

            cursor.execute(sql, {"urn": burl})
            all_rows.extend(cursor.fetchall())

        results[name] = {
            "columns": cfg["columns"],
            "rows": all_rows
        }

    cursor.close()
    conn.close()

    return results


def pretty_print_payload(value):

    if value is None:
        return "NULL"

    text = str(value).strip()

    if (text.startswith("{") and text.endswith("}")) or (text.startswith("[") and text.endswith("]")):

        formatted = ""
        indent = 0

        for char in text:

            if char in ["{", "["]:
                formatted += char + "\n"
                indent += 4
                formatted += " " * indent

            elif char in ["}", "]"]:
                formatted += "\n"
                indent -= 4
                formatted += " " * indent + char

            elif char == ",":
                formatted += char + "\n" + " " * indent

            else:
                formatted += char

        return formatted

    return text


def generate_html(urn, results):

    file = "urn_report.html"

    with open(file, "w") as f:

        f.write("""
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
            padding-top: 12px;
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
        .success {
            color: #22c55e;
            font-weight: bold;
        }

        .failed {
            color: #ef4444;
            font-weight: bold;
        }

        .null-value {
            color: #94a3b8;
            font-style: italic;
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
            .catch(err => {
                console.error(err);
            });

        }

        </script>
        </head>
        <body>
        """)

        f.write(f"""
        <h2>RRN Finder</h2>

        <div class="summary">
        <b>URN:</b> {urn}
        <br><br>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        """)

        for table, data in results.items():

            f.write(f"""
            <div class="section">
            <div class="section-header">
            {table} | Records Found: {len(data['rows'])}
            </div>
            """)

            if not data["rows"]:
                f.write('<div class="no-records">No Records Found</div></div>')
                continue

            f.write('<div class="table-container">')
            f.write("<table>")

            f.write("<tr>")
            for c in data["columns"]:
                f.write(f"<th>{c}</th>")
            f.write("</tr>")

            for row in data["rows"]:
                f.write("<tr>")
                for v in row:
                    formatted = str(pretty_print_payload(v))
                    escaped = html.escape(formatted)

                    if len(formatted) > 100:

                        js_text = html.escape(formatted, quote=True)

                        f.write(
                        f"<td><div class='payload'>"
                        f"<button class='copy-btn' onclick='copyToClipboard(this, `{js_text}`)'>📋</button>"
                        f"{escaped}"
                        f"</div></td>"
                        )
                    else:
                        f.write(f"<td>{escaped}</td>")
                f.write("</tr>")

            f.write("</table>")
            f.write("</div>")
            f.write("</div>")

        f.write("</body></html>")

    return file


def main():

    urn = input("Enter URN: ").strip()

    if not urn:
        print("URN cannot be empty")
        return

    if len(urn) < 18:
        print("URN must be at least 18 characters")
        return

    if len(urn) > 25:
        print("URN cannot be greater than 25 characters")
        return

    if not (urn.startswith("SB") or urn.startswith("EIS")):
        print("URN must start with SB or EIS")
        return

    results = search_urn(urn)

    file = generate_html(urn, results)

    print("\nReport Generated:", file)


if __name__ == "__main__":
    main()