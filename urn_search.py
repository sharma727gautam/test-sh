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

    if len(urn) == 25:
        search_type = "EXACT"
        pattern = urn
        operator = "="
    else:
        search_type = "PREFIX"
        pattern = urn + "%"
        operator = "LIKE"

    print(f"Search Mode: {search_type}")

    # STEP 1: Always check ORCH first (FAST single query)
    cursor.execute(f"""
        SELECT URN_CHILD
        FROM ORCH_API_LOG
        WHERE URN {operator} :urn
        AND URN_CHILD IS NOT NULL
        FETCH FIRST 1 ROWS ONLY
    """, {"urn": pattern})

    orch_row = cursor.fetchone()

    if orch_row:
        flow_type = "ORCH"
        backend_urns = [r[0] for r in cursor.execute(f"""
            SELECT DISTINCT URN_CHILD
            FROM ORCH_API_LOG
            WHERE URN {operator} :urn
            AND URN_CHILD IS NOT NULL
        """, {"urn": pattern})]
    else:
        flow_type = "NORMAL"
        backend_urns = [urn]

    print(f"Flow Type: {flow_type}")
    print(f"Backend URNs: {backend_urns}")

    # STEP 2: Common tables (always run)
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

    # STEP 3: Backend tables (based on flow)
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

        body {
            font-family: Arial;
            margin: 20px;
            background-color: #f5f5f5;
        }

        h2 {
            color: #333;
        }

        h3 {
            background-color: #333;
            color: white;
            padding: 8px;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 30px;
            background: white;
        }

        th {
            background-color: #222;
            color: white;
            padding: 8px;
        }

        td {
            border: 1px solid #ddd;
            padding: 8px;
            vertical-align: top;
            white-space: pre-wrap;
        }

        .no-records {
            color: red;
            font-weight: bold;
        }

        </style>
        </head>
        <body>
        """)
        f.write(f"<h2>URN Report: {urn}</h2>")

        for table, data in results.items():

            f.write(f"<h3>{table} ({len(data['rows'])} rows)</h3>")

            if not data["rows"]:
                f.write("<p>No Records Found</p>")
                continue

            f.write("<table border='1'>")

            f.write("<tr>")
            for c in data["columns"]:
                f.write(f"<th>{c}</th>")
            f.write("</tr>")

            for row in data["rows"]:
                f.write("<tr>")
                for v in row:
                    f.write(f"<td>{html.escape(str(pretty_print_payload(v)))}</td>")
                f.write("</tr>")

            f.write("</table>")

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