"""Fetch the Tigerair Taiwan schedule and generate the local data files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

API_URL = "https://api-cms.tigerairtw.com/api/flight-schedules/merge"
COUNTRIES = {"JP": "日本", "KR": "韓國", "TH": "泰國", "VN": "越南"}
STATIONS = {
    "TPE": "桃園",
    "TNN": "台南",
    "TSA": "台北松山",
    "RMQ": "台中",
    "KHH": "高雄",
    "NRT": "東京成田",
    "HND": "東京羽田",
    "KIX": "大阪關西",
    "NGO": "名古屋中部",
    "FUK": "福岡",
    "OKA": "沖繩那霸",
    "CTS": "札幌新千歲",
    "SDJ": "仙台",
    "KOJ": "鹿兒島",
    "KIJ": "新潟",
    "TAK": "高松",
    "KCZ": "高知",
    "MYJ": "松山",
    "ISG": "石垣",
    "AXT": "秋田",
    "FKS": "福島",
    "GMP": "首爾金浦",
    "HKD": "函館",
    "HKT": "普吉",
    "HNA": "花卷",
    "HSG": "佐賀",
    "KMI": "宮崎",
    "KMJ": "熊本",
    "KMQ": "小松",
    "OIT": "大分",
    "OKJ": "岡山",
    "YGJ": "米子",
    "PUS": "釜山",
    "ICN": "首爾仁川",
    "CJU": "濟州",
    "DMK": "曼谷廊曼",
    "DAD": "峴港",
    "SGN": "胡志明市",
    "HAN": "河內",
}
DAY_NAMES = ["日", "一", "二", "三", "四", "五", "六"]


def fetch() -> list[dict]:
    request = Request(API_URL, headers={"User-Agent": "TigerAirScheduleArchive/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)["data"]


def flatten(groups: list[dict]) -> list[dict]:
    rows = []
    for group in groups:
        for station in group["stationSchedules"]:
            for item in station["schedules"]:
                days = item["daysOfWeek"]
                day_flags = [days["sunday"], days["monday"], days["tuesday"], days["wednesday"], days["thursday"], days["friday"], days["saturday"]]
                rows.append({
                    "countryCode": group["countryCode"],
                    "country": COUNTRIES.get(group["countryCode"], group["countryCode"]),
                    "origin": item["origin"],
                    "originName": STATIONS.get(item["origin"], item["origin"]),
                    "destination": item["destination"],
                    "destinationName": STATIONS.get(item["destination"], item["destination"]),
                    "flightNumber": f'{item["carrierCode"]}{item["flightNumber"]}',
                    "departureTime": item["departureTime"][:5],
                    "arrivalTime": item["arrivalTime"][:5],
                    "overnight": bool(item.get("overnight")),
                    "days": [DAY_NAMES[i] for i, enabled in enumerate(day_flags) if enabled],
                    "operationDateSummary": item["operationDateSummary"],
                })
    return rows


def main() -> None:
    rows = flatten(fetch())
    generated_at = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    root = Path(__file__).parent
    payload = json.dumps({"generatedAt": generated_at, "source": API_URL, "flights": rows}, ensure_ascii=False, indent=2)
    (root / "flights-data.js").write_text("window.TIGERAIR_DATA = " + payload + ";\n", encoding="utf-8")

    lines = ["# 台灣虎航航班時刻表", "", f"> 資料來源：[{API_URL}]({API_URL})", f"> 擷取時間：{generated_at}", f"> 航班筆數：{len(rows)}", "", "欄位中的星期以日、一、二、三、四、五、六表示；日期為官方公告的適用日期。", ""]
    headers = ["抵達國家", "航班", "起飛地點", "抵達地點", "起飛時間", "抵達時間", "適合出發星期", "適合出發日期"]
    lines += ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        overnight = "（隔日）" if row["overnight"] else ""
        lines.append("| " + " | ".join([
            row["country"], row["flightNumber"], f'{row["originName"]}（{row["origin"]}）',
            f'{row["destinationName"]}（{row["destination"]}）', row["departureTime"],
            row["arrivalTime"] + overnight, "、".join(row["days"]), row["operationDateSummary"]
        ]) + " |")
    (root / "flight-schedule.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(rows)} flights")


if __name__ == "__main__":
    main()
