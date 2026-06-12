import os
import oracledb
from datetime import datetime
import html

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "dsn": os.getenv("DB_DSN")
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
    pattern = f"%{urn}%"

    print("\n==============================")
    print("Starting URN Search Process")
    print("==============================\n")

    for name, cfg in TABLES.items():

        sql = f"""
        SELECT {",".join(cfg["columns"])}
        FROM {cfg["table"]}
        WHERE URN LIKE :urn
        """

        print(f"Running query on table: {cfg['table']}")
        print(f"Query: {sql.strip()}")
        print(f"With URN LIKE: {pattern}")

        cursor.execute(sql, {"urn": pattern})
        rows = cursor.fetchall()

        results[name] = {
            "columns": cfg["columns"],
            "rows": rows
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

    results = search_urn(urn)

    file = generate_html(urn, results)

    print("\nReport Generated:", file)

if __name__ == "__main__":
    main()