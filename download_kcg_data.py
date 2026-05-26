import csv
import io
import ssl
import urllib.error
import urllib.request

from flask import Flask, render_template_string

URL = "https://data.ntpc.gov.tw/api/datasets/781b822e-214a-4b9a-b4db-32c9f4626d98/csv/file"

app = Flask(__name__)


def download_file(url: str) -> bytes:
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    except urllib.error.URLError:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, context=context, timeout=30) as response:
            return response.read()


def decode_text(content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("utf-8", errors="replace")


def parse_csv(content: bytes) -> list[dict[str, str]]:
    text = decode_text(content)
    text_io = io.StringIO(text)
    reader = csv.DictReader(text_io)
    return list(reader)


HTML_TEMPLATE = """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>新北市政府開放資料</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; color: #212529; }
    h1, h2 { color: #0d6efd; }
    .summary { margin-bottom: 16px; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
    th, td { border: 1px solid #dee2e6; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #e9ecef; }
    tr:nth-child(even) { background: #ffffff; }
    tr:nth-child(odd) { background: #f1f3f5; }
    .container { max-width: 100%; overflow-x: auto; }
    .footer { margin-top: 20px; font-size: 0.9rem; color: #495057; }
  </style>
</head>
<body>
  <h1>新北市政府資料集</h1>
  <p class="summary">從資料來源下載並解析 CSV，總筆數：{{ total }}。</p>
  {% if header_fields %}
  <div class="container">
    <table>
      <thead>
        <tr>
          {% for field in header_fields %}
          <th>{{ field }}</th>
          {% endfor %}
        </tr>
      </thead>
      <tbody>
        {% for row in rows %}
        <tr>
          {% for field in header_fields %}
          <td>{{ row[field] }}</td>
          {% endfor %}
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% else %}
  <p>找不到任何可用的資料欄位。請確認資料來源是否正確。</p>
  {% endif %}
  <div class="footer">資料來源：{{ url }}</div>
</body>
</html>
"""


@app.route("/")
def index():
    content = download_file(URL)
    records = parse_csv(content)
    header_fields = list(records[0].keys()) if records else []
    return render_template_string(
        HTML_TEMPLATE,
        total=len(records),
        rows=records,
        header_fields=header_fields,
        url=URL,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
