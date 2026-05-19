import csv
import io
import ssl
import urllib.error
import urllib.request

URL = "https://data.kcg.gov.tw/File/DirectDownload/80bbbbd3-9ee4-4244-98e9-b4c08deda91b"
OUTPUT_FILE = "kcg_data.csv"
PREVIEW_ROWS = 5


def download_file(url: str, output_path: str) -> bytes:
    print(f"Downloading data from: {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read()
    except urllib.error.URLError:
        print("下載時遇到 SSL 驗證或連線問題，改為不驗證憑證重試...")
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, context=context, timeout=30) as response:
            content = response.read()

    with open(output_path, "wb") as f:
        f.write(content)

    print(f"Saved downloaded content to: {output_path}")
    print(f"Downloaded {len(content)} bytes.")
    return content


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


def print_records(records: list[dict[str, str]], max_rows: int = PREVIEW_ROWS) -> None:
    if not records:
        print("沒有解析到任何資料。請確認下載內容是否為 CSV 格式。")
        return

    rows_to_show = min(len(records), max_rows)
    print(f"\n===== 解析資料預覽 ({rows_to_show}/{len(records)}) =====\n")

    for idx, record in enumerate(records[:rows_to_show], start=1):
        print(f"----- 資料 {idx} -----")
        for key, value in record.items():
            print(f"{key}：{value}")
        print()

    if len(records) > rows_to_show:
        print(f"... 還有 {len(records) - rows_to_show} 筆資料未顯示")


def main() -> None:
    content = download_file(URL, OUTPUT_FILE)
    records = parse_csv(content)
    print_records(records)


if __name__ == "__main__":
    main()
