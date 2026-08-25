"""Build the printable HOME 12 / PRO 48 product fabrication manual."""

from pathlib import Path
import csv
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon, Circle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "SproutCam-HOME12-PRO48-제품제작서-v0.1.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

FONT = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/7a0b5c0f3c1d41c4c52a33343496c9c65ad52c50.asset/AssetData/NanumGothic.ttc"
pdfmetrics.registerFont(TTFont("KR", FONT, subfontIndex=0))
pdfmetrics.registerFont(TTFont("KR-B", FONT, subfontIndex=1))

PAGE_W, PAGE_H = A4
INK = colors.HexColor("#151817")
MUTED = colors.HexColor("#66706B")
PAPER = colors.HexColor("#F5F2E9")
GREEN = colors.HexColor("#B9F53D")
DARK_GREEN = colors.HexColor("#184D3B")
ORANGE = colors.HexColor("#FF6534")
MIST = colors.HexColor("#DDE9E4")
WHITE = colors.white

styles = getSampleStyleSheet()
body = ParagraphStyle("body", fontName="KR", fontSize=8.8, leading=13.2, textColor=INK, spaceAfter=4)
small = ParagraphStyle("small", fontName="KR", fontSize=7.1, leading=10.2, textColor=MUTED, spaceAfter=3)
h1 = ParagraphStyle("h1", fontName="KR-B", fontSize=22, leading=27, textColor=INK, spaceAfter=8)
h2 = ParagraphStyle("h2", fontName="KR-B", fontSize=13, leading=17, textColor=INK, spaceBefore=5, spaceAfter=5)
h3 = ParagraphStyle("h3", fontName="KR-B", fontSize=9.5, leading=13, textColor=DARK_GREEN, spaceAfter=3)
hero = ParagraphStyle("hero", fontName="KR-B", fontSize=29, leading=34, textColor=INK, alignment=TA_CENTER)
center = ParagraphStyle("center", parent=body, alignment=TA_CENTER)
white_body = ParagraphStyle("white", parent=body, textColor=WHITE)


def p(text, style=body):
    return Paragraph(text, style)


def money(value):
    return f"{int(value):,}원"


def read_bom(filename):
    with (ROOT / "docs" / filename).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


HOME = read_bom("HOME12_BOM.csv")
PRO = read_bom("PRO48_BOM.csv")


def page_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(INK)
    canvas.setFont("KR-B", 7.5)
    canvas.drawString(16 * mm, PAGE_H - 10 * mm, "SPROUTCAM PRODUCT BUILD BOOK  /  v0.1")
    canvas.setFont("KR", 7)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(PAGE_W - 16 * mm, 9 * mm, f"{doc.page}")
    canvas.restoreState()


def table(data, widths, header=True, font=7.3, aligns=None):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("FONT", (0, 0), (-1, -1), "KR"),
        ("FONTSIZE", (0, 0), (-1, -1), font),
        ("LEADING", (0, 0), (-1, -1), font + 3.2),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9FA8A3")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.extend([
            ("FONT", (0, 0), (-1, 0), "KR-B"),
            ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ])
    for col, align in (aligns or {}).items():
        commands.append(("ALIGN", (col, 1 if header else 0), (col, -1), align))
    t.setStyle(TableStyle(commands))
    return t


def callout(title, text, color=DARK_GREEN):
    content = [[p(title, ParagraphStyle("coh", parent=h3, textColor=WHITE)), p(text, white_body)]]
    t = Table(content, colWidths=[35 * mm, 128 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def dimension_diagram(model):
    d = Drawing(470, 270)
    d.add(Rect(0, 0, 470, 270, rx=12, ry=12, fillColor=MIST, strokeColor=None))
    if model == "HOME":
        x, y, w, h = 55, 35, 235, 205
        d.add(Rect(x, y, w, h, fillColor=colors.Color(1, 1, 1, 0.65), strokeColor=INK, strokeWidth=2))
        for px in (x + 10, x + w - 10):
            d.add(Line(px, y, px, y + h, strokeColor=INK, strokeWidth=4))
        d.add(Rect(x + 13, y + 48, w - 26, 13, fillColor=colors.HexColor("#BFD7D0"), strokeColor=INK))
        d.add(Rect(x + 13, y + 165, w - 26, 8, fillColor=colors.HexColor("#FFD45C"), strokeColor=INK))
        for row in range(3):
            for col in range(4):
                cx = x + 42 + col * 51
                cy = y + 75 + row * 29
                d.add(Circle(cx, cy, 10, fillColor=colors.HexColor("#4E985A"), strokeColor=DARK_GREEN))
        d.add(Rect(x + 78, y + 8, 78, 30, fillColor=colors.HexColor("#C7CBC8"), strokeColor=INK))
        d.add(String(320, 205, "외형 560 W x 400 D x 600 H", fontName="KR-B", fontSize=11, fillColor=INK))
        d.add(String(320, 180, "재배 12포트 / 4 x 3", fontName="KR", fontSize=9, fillColor=INK))
        d.add(String(320, 160, "식물-LED 250-330 mm", fontName="KR", fontSize=9, fillColor=INK))
        d.add(String(320, 140, "서비스실 높이 130 mm", fontName="KR", fontSize=9, fillColor=INK))
        d.add(String(320, 120, "트레이 520 x 340 x 50", fontName="KR", fontSize=9, fillColor=INK))
        d.add(String(320, 80, "본체 내부는 24V / 5V DC", fontName="KR-B", fontSize=9, fillColor=DARK_GREEN))
        d.add(String(320, 58, "권장 설치: 실내 20-28 C", fontName="KR", fontSize=9, fillColor=INK))
    else:
        x, y, w, h = 70, 20, 110, 230
        d.add(Rect(x, y, w, h, fillColor=colors.Color(1, 1, 1, 0.65), strokeColor=INK, strokeWidth=2))
        for px in (x + 8, x + w - 8):
            d.add(Line(px, y, px, y + h, strokeColor=INK, strokeWidth=5))
        for base in (62, 150):
            d.add(Rect(x + 10, base, w - 20, 8, fillColor=colors.HexColor("#BFD7D0"), strokeColor=INK))
            d.add(Rect(x + 10, base + 69, w - 20, 6, fillColor=colors.HexColor("#FFD45C"), strokeColor=INK))
            for row in range(2):
                for col in range(6):
                    d.add(Circle(x + 20 + col * 14, base + 18 + row * 15, 4.5, fillColor=colors.HexColor("#4E985A"), strokeColor=DARK_GREEN))
        d.add(Rect(x + 22, y + 8, 66, 25, fillColor=colors.HexColor("#C7CBC8"), strokeColor=INK))
        d.add(String(225, 210, "외형 680 W x 560 D x 1700 H", fontName="KR-B", fontSize=11, fillColor=INK))
        d.add(String(225, 184, "2개 독립 구역 x 24포트", fontName="KR", fontSize=9, fillColor=INK))
        d.add(String(225, 164, "구역별 LED 80 W", fontName="KR", fontSize=9, fillColor=INK))
        d.add(String(225, 144, "구역별 카메라·센서·가습", fontName="KR", fontSize=9, fillColor=INK))
        d.add(String(225, 124, "트레이 610 x 470 x 40", fontName="KR", fontSize=9, fillColor=INK))
        d.add(String(225, 104, "서비스실 높이 280 mm", fontName="KR", fontSize=9, fillColor=INK))
        d.add(String(225, 70, "구역당 24V 150 W 어댑터", fontName="KR-B", fontSize=9, fillColor=DARK_GREEN))
        d.add(String(225, 48, "브레이크 캐스터 4개", fontName="KR", fontSize=9, fillColor=INK))
    return d


def wiring_diagram(model):
    d = Drawing(470, 205)
    d.add(Rect(0, 0, 470, 205, rx=12, ry=12, fillColor=MIST, strokeColor=None))
    boxes = [
        (16, 134, 92, 45, "KC 외장 어댑터", "24V DC"),
        (136, 134, 92, 45, "퓨즈 분기", "메인 + 부하별"),
        (256, 134, 92, 45, "MOSFET", "LED·팬·가습"),
        (376, 134, 78, 45, "부하", "24V"),
        (136, 42, 92, 45, "DC-DC", "24V -> 5V"),
        (256, 42, 92, 45, "XIAO S3", "카메라·로직"),
        (376, 42, 78, 45, "센서", "SHT40·누수"),
    ]
    for x, y, w, h, title, sub in boxes:
        d.add(Rect(x, y, w, h, rx=6, ry=6, fillColor=WHITE, strokeColor=INK, strokeWidth=1.2))
        d.add(String(x + w / 2, y + 27, title, textAnchor="middle", fontName="KR-B", fontSize=8, fillColor=INK))
        d.add(String(x + w / 2, y + 12, sub, textAnchor="middle", fontName="KR", fontSize=6.8, fillColor=MUTED))
    def arrow(x1, y1, x2, y2, color=ORANGE):
        d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=2))
        d.add(Polygon([x2, y2, x2 - 7, y2 + 4, x2 - 7, y2 - 4], fillColor=color, strokeColor=None))
    arrow(108, 156, 136, 156)
    arrow(228, 156, 256, 156)
    arrow(348, 156, 376, 156)
    d.add(Line(182, 134, 182, 87, strokeColor=ORANGE, strokeWidth=2))
    d.add(Polygon([182, 87, 178, 94, 186, 94], fillColor=ORANGE, strokeColor=None))
    arrow(228, 64, 256, 64)
    arrow(348, 64, 376, 64, DARK_GREEN)
    d.add(String(16, 12, "젖은 구역과 서비스실 사이의 관통부는 케이블 글랜드와 드립 루프로 마감", fontName="KR-B", fontSize=7.5, fillColor=DARK_GREEN))
    if model == "PRO":
        d.add(String(16, 188, "이 회로를 ZONE A와 ZONE B에 각각 1세트 적용", fontName="KR-B", fontSize=8.5, fillColor=ORANGE))
    return d


def bom_summary(rows):
    groups = {}
    for row in rows:
        if row["category"] == "TOTAL":
            continue
        groups.setdefault(row["category"], [0, 0])
        groups[row["category"]][0] += int(row["prototype_subtotal_krw"] or 0)
        groups[row["category"]][1] += int(row["target_50unit_subtotal_krw"] or 0)
    return [["구분", "시제품 1대", "50대 목표/대"]] + [[k, money(v[0]), money(v[1])] for k, v in groups.items()]


def bom_detail(rows, start, end):
    data = [["부품", "규격", "수량", "시제품 소계"]]
    clean = [r for r in rows if r["category"] != "TOTAL"][start:end]
    for r in clean:
        data.append([r["item"], r["specification"], r["qty"], money(r["prototype_subtotal_krw"])])
    return data


story = []

# Cover
story += [Spacer(1, 16 * mm), p("SPROUTCAM", hero), p("HOME 12 + PRO 48", ParagraphStyle("subhero", parent=hero, fontSize=19, leading=25, textColor=DARK_GREEN)), p("제품 제작서 / 견적서 / 조립 검사서 v0.1", center), Spacer(1, 7 * mm)]
concept = ROOT / "output" / "concepts" / "home-vs-pro-clean-v1.png"
story.append(Image(str(concept), width=170 * mm, height=106.25 * mm))
story += [Spacer(1, 5 * mm), callout("설계 결론", "광원은 위, 식물은 아래입니다. 고가 식물의 병 전파를 막기 위해 공용 순환수조 대신 개별 화분과 탈착식 방수 트레이를 사용합니다."), Spacer(1, 8 * mm), p("작성 기준일 2026-08-25  |  치수 단위 mm  |  금액 VAT 포함 소매 추정", small), PageBreak()]

# Executive cost page
story += [p("0. 먼저 보는 결론", h1), p("직접 한 대를 만드는 예산과 판매용 50대 생산의 제조원가는 다릅니다. 아래 금액은 현재 설계를 실제로 구매 가능한 부품으로 조립하기 위한 기준선입니다.")]
cost = [
    ["모델", "소매 시제품", "50대 목표 제조원가", "권장 시험 판매가"],
    ["HOME 12", "568,430원", "399,100원/대", "799,000-899,000원"],
    ["PRO 48", "1,419,240원", "971,000원/대", "1,890,000-2,190,000원"],
]
story += [table(cost, [33 * mm, 40 * mm, 48 * mm, 45 * mm], font=8), Spacer(1, 6 * mm)]
story += [callout("원가에 포함", "본체 구조, 패널, 트레이, 화분, LED, 카메라 제어기, 센서, 팬, 가습, 외장 전원, 소모품, 소매 배송. 50대 목표에는 조립·검사, 포장, 보증충당도 포함."), Spacer(1, 4 * mm)]
story += [callout("원가에 제외", "3D 프린터와 공구, 앱·서버 개발, 금형, KC·EMC·방수 시험, 창고, 반품 물류, 판매 수수료, 마케팅, 부가세 환급 효과.", ORANGE), Spacer(1, 6 * mm)]
story += [p("제품 역할 분리", h2)]
roles = [
    ["제품이 제어", "설치 공간이 담당", "이번 버전에서 제외"],
    ["광주기·광량\n습도·환기\n성장 촬영·기록\n누수 감지", "실내 온도 20-28 C\n급배수 접근\n안정적인 Wi-Fi\n주기적 물 보충", "냉난방\n자동 영양액 배합\n병해충 완전 진단\n판매 등급 자동 판정"],
]
story += [table(roles, [55 * mm, 55 * mm, 55 * mm], font=8), Spacer(1, 6 * mm), p("핵심 판단: HOME은 개인 수집가의 발근·순화·성장 기록 장비이고, PRO는 소형 농가나 식물 판매자의 2구역 생산 장비입니다. 단순 채소 재배기보다 고가 삽수·유묘의 생존률과 기록성을 파는 편이 가격 방어가 쉽습니다."), PageBreak()]

# Safety and architecture
story += [p("1. 시스템 구조와 안전 경계", h1), p("판매 가능한 제품으로 발전시키려면 처음부터 물과 전원의 경계를 명확히 해야 합니다. 본체 안에는 SELV 저전압 DC만 넣고 220V 변환은 KC 인증 외장 어댑터에서 끝냅니다."), wiring_diagram("HOME"), Spacer(1, 5 * mm)]
safety = [
    ["항목", "제작 기준", "불합격 조건"],
    ["전원", "외장 24V 어댑터, 본체 입구 퓨즈", "본체 내부 220V 배선"],
    ["물", "트레이·가습수조 독립, 드립 루프", "전자함 위쪽 호스 연결"],
    ["전자함", "서비스실 상단, IP54 이상 목표", "바닥 최저점에 장착"],
    ["가습", "저수위 보호, 최대 연속 15분", "무수 상태 발진 가능"],
    ["열", "LED 알루미늄 방열판, 팬 정지 감지", "30분 후 표면 60 C 초과"],
    ["소프트웨어", "로컬 타임아웃 우선", "클라우드 장애 시 계속 켜짐"],
]
story += [table(safety, [28 * mm, 75 * mm, 62 * mm], font=7.5), Spacer(1, 5 * mm), callout("작업 전", "누전차단기가 있는 콘센트를 사용하고, 빈 캐비닛 누수 시험 24시간을 통과하기 전에는 전자부품을 설치하지 않습니다.", ORANGE), PageBreak()]

# HOME dimension and cut list
story += [p("2. HOME 12 기구 설계", h1), dimension_diagram("HOME"), Spacer(1, 4 * mm)]
home_cut = [
    ["재료", "절단 치수", "수량", "용도"],
    ["2020 프로파일", "560", "4", "상·하 폭"],
    ["2020 프로파일", "400", "4", "상·하 깊이"],
    ["2020 프로파일", "600", "4", "기둥"],
    ["2020 프로파일", "520", "4", "LED·트레이 레일"],
    ["2020 프로파일", "360", "2", "서비스 선반"],
    ["3T 투명 PC", "560x400 / 400x600x2 / 560x600 / 520x450", "5", "상·좌우·후면·도어"],
    ["3T ABS/ACP", "520x360", "1", "젖음·건조 분리판"],
]
story += [table(home_cut, [38 * mm, 56 * mm, 18 * mm, 53 * mm], font=7.4), Spacer(1, 4 * mm)]
story += [p("배치 기준", h2), p("트레이 바닥은 서비스실 위 148 mm, 화분 상단은 약 235 mm, LED 방열판은 520 mm에 둡니다. 키가 작은 삽수는 LED 레일을 60 mm 아래로 이동합니다. 카메라는 전면 상단 모서리에서 중앙을 향해 30도로 내려다보게 설치합니다."), PageBreak()]

# HOME BOM
story += [p("3. HOME 12 구매 목록과 원가", h1), table(bom_summary(HOME), [60 * mm, 48 * mm, 55 * mm], font=7.4, aligns={1: "RIGHT", 2: "RIGHT"}), Spacer(1, 5 * mm)]
story += [p("상세 BOM 1/2", h2), table(bom_detail(HOME, 0, 12), [44 * mm, 73 * mm, 14 * mm, 32 * mm], font=6.5, aligns={2: "RIGHT", 3: "RIGHT"}), PageBreak()]
story += [p("3. HOME 12 구매 목록과 원가", h1), p("상세 BOM 2/2", h2), table(bom_detail(HOME, 12, 30), [44 * mm, 73 * mm, 14 * mm, 32 * mm], font=6.5, aligns={2: "RIGHT", 3: "RIGHT"}), Spacer(1, 5 * mm), callout("구매 순서", "먼저 프로파일·트레이·화분·LED 실물 치수를 확정한 뒤 패널 재단과 3D 출력을 주문합니다. 트레이와 LED를 나중에 바꾸면 고정구를 다시 출력하게 됩니다."), PageBreak()]

# HOME assembly
story += [p("4. HOME 12 조립 순서", h1)]
home_steps = [
    ("01", "하부 사각 프레임과 4개 기둥을 손조임으로 조립합니다. 대각선 길이 차가 2 mm 이내인지 확인한 뒤 체결합니다."),
    ("02", "높이 130 mm에 서비스 선반 레일을 설치하고 ABS/ACP 분리판 둘레를 중성 실리콘으로 밀봉합니다."),
    ("03", "트레이 레일과 3D 출력 코너 스토퍼 4개를 설치합니다. 트레이는 앞쪽으로 완전히 빠져야 합니다."),
    ("04", "상·후·측면 PC 패널을 장착하고 전면 도어 간극 3 mm를 확보합니다. 환기 팬은 후면 상단 배기로 둡니다."),
    ("05", "LED 두 줄을 알루미늄 레일과 출력 클립으로 고정합니다. 방열판과 PC 상판 사이 간격은 20 mm 이상입니다."),
    ("06", "카메라 브래킷, SHT40 가드, 케이블 클립을 장착합니다. 센서는 미스트 직분사와 LED 열원에서 120 mm 이상 떨어뜨립니다."),
    ("07", "가습수조와 덕트를 서비스실 왼쪽, 전자함을 오른쪽에 배치합니다. 모든 호스 연결부는 전자함보다 낮게 둡니다."),
    ("08", "24시간 누수 시험 후 배선하고 5V 레일, 팬 방향, 저수위 차단, 누수 경보, 카메라 화각을 순서대로 검사합니다."),
]
for num, text in home_steps:
    t = Table([[p(num, ParagraphStyle("stepn", parent=h2, textColor=ORANGE)), p(text)]], colWidths=[18 * mm, 145 * mm])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9FA8A3")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("PADDING", (0, 0), (-1, -1), 6)]))
    story += [t, Spacer(1, 2.5 * mm)]
story += [PageBreak()]

# HOME electrical
story += [p("5. HOME 12 배선과 전력", h1), wiring_diagram("HOME"), Spacer(1, 4 * mm)]
home_power = [
    ["부하", "정격", "예상 최대", "퓨즈"],
    ["LED 2개", "24V", "60 W / 2.5 A", "3 A"],
    ["미스트", "24V", "24 W / 1.0 A", "1.5 A"],
    ["팬 2개", "24V 또는 12V", "6 W / 0.25 A", "1 A"],
    ["제어·카메라", "5V", "5 W / 1.0 A", "벅 입력 1 A"],
    ["합계", "24V", "약 95 W / 4.0 A", "메인 5 A"],
]
story += [table(home_power, [42 * mm, 44 * mm, 48 * mm, 29 * mm], font=7.5), Spacer(1, 4 * mm)]
pins = [
    ["기능", "연결", "제어 규칙"],
    ["SHT40", "I2C SDA/SCL", "30초 평균, 결로 방지"],
    ["LED", "MOSFET CH1", "기본 12시간, PWM 선택"],
    ["배기 팬", "MOSFET CH2", "습도 상한 또는 주기 환기"],
    ["미스트", "MOSFET CH3", "최대 15분, 5분 휴지"],
    ["누수", "디지털 입력", "감지 즉시 모든 부하 OFF"],
]
story += [table(pins, [40 * mm, 52 * mm, 71 * mm], font=7.4), Spacer(1, 4 * mm), p("HOME 피크 부하는 95 W이므로 24V 5A 120 W 어댑터에 약 20% 여유가 남습니다. LED나 미스트 모듈을 상향하면 어댑터와 메인 퓨즈를 다시 계산해야 합니다.", small), PageBreak()]

# PRO dimension
story += [p("6. PRO 48 기구 설계", h1), dimension_diagram("PRO"), Spacer(1, 4 * mm)]
pro_cut = [
    ["재료", "절단 치수", "수량", "용도"],
    ["3030 프로파일", "1700", "4", "기둥"],
    ["3030 프로파일", "680", "8", "상·하·구역 폭"],
    ["3030 프로파일", "560", "12", "상·하·구역 깊이"],
    ["4T 투명 PC", "680x560 / 560x1700x2 / 680x1700", "4", "상·좌우·후면"],
    ["4T 투명 PC", "640x600x2 / 640x250", "3", "구역·서비스 도어"],
    ["4T ABS/ACP", "620x500", "3", "구역 바닥·분리판"],
]
story += [table(pro_cut, [38 * mm, 64 * mm, 18 * mm, 45 * mm], font=7.2), Spacer(1, 5 * mm)]
story += [callout("독립 2구역", "ZONE A와 B는 어댑터, 제어기, 센서, 팬, 가습수조를 따로 둡니다. 한 구역 고장이나 병 발생이 다른 구역으로 번지는 것을 줄이고 서로 다른 순화 레시피를 운전할 수 있습니다."), PageBreak()]

# PRO BOM pages
story += [p("7. PRO 48 구매 목록과 원가", h1), table(bom_summary(PRO), [60 * mm, 48 * mm, 55 * mm], font=7.4, aligns={1: "RIGHT", 2: "RIGHT"}), Spacer(1, 5 * mm), p("상세 BOM 1/2", h2), table(bom_detail(PRO, 0, 12), [44 * mm, 73 * mm, 14 * mm, 32 * mm], font=6.5, aligns={2: "RIGHT", 3: "RIGHT"}), PageBreak()]
story += [p("7. PRO 48 구매 목록과 원가", h1), p("상세 BOM 2/2", h2), table(bom_detail(PRO, 12, 30), [44 * mm, 73 * mm, 14 * mm, 32 * mm], font=6.5, aligns={2: "RIGHT", 3: "RIGHT"}), Spacer(1, 4 * mm), callout("큰 원가 3개", "외장·프레임 약 54.7만원, 광원 17.6만원, 배송·조립 준비 약 9만원이 시제품 가격을 끌어올립니다. 실제 양산에서는 패널 네스팅과 프로파일 일괄 절단이 가장 먼저 절감할 부분입니다."), PageBreak()]

# PRO assembly
story += [p("8. PRO 48 조립 순서", h1)]
pro_steps = [
    ("01", "캐스터가 달린 하부 3030 프레임을 조립하고 수평계를 사용합니다. 두 대각선 차이는 3 mm 이내로 맞춥니다."),
    ("02", "기둥 4개와 상부 프레임을 세운 뒤 벽 고정용 전도 방지 스트랩 위치를 확보합니다."),
    ("03", "높이 280, 930, 1610 mm에 구역 레일을 설치하고 ABS/ACP 분리판 둘레를 실링합니다."),
    ("04", "각 구역 트레이 레일과 스토퍼를 설치합니다. 24개 화분을 넣은 상태에서도 한 손으로 트레이가 빠져야 합니다."),
    ("05", "구역당 LED 2줄, 배기 팬 2개, 카메라 1개, SHT40 1개를 설치합니다. 두 구역의 하네스 색을 다르게 합니다."),
    ("06", "서비스실을 좌측 가습수조 A/B, 중앙 전원 입구, 우측 전자함 A/B로 구획합니다. 물통은 별도 누수받이에 둡니다."),
    ("07", "패널과 도어를 설치하고 각 구역의 문을 닫았을 때 2-5 mm 흡기 간극을 남깁니다."),
    ("08", "구역별 24시간 누수 시험, 4시간 열 시험, 정전 복구, 네트워크 단절, 누수 센서 강제 작동 시험을 합니다."),
]
for num, text in pro_steps:
    t = Table([[p(num, ParagraphStyle("stepnp", parent=h2, textColor=ORANGE)), p(text)]], colWidths=[18 * mm, 145 * mm])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9FA8A3")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("PADDING", (0, 0), (-1, -1), 6)]))
    story += [t, Spacer(1, 2.5 * mm)]
story += [PageBreak()]

# PRO electrical
story += [p("9. PRO 48 배선과 전력", h1), wiring_diagram("PRO"), Spacer(1, 4 * mm)]
pro_power = [
    ["구역당 부하", "정격", "예상 최대", "퓨즈"],
    ["LED 2개", "24V", "80 W / 3.33 A", "4 A"],
    ["미스트", "24V", "24 W / 1.0 A", "1.5 A"],
    ["팬 2개", "24V 또는 12V", "10 W / 0.42 A", "1 A"],
    ["제어·카메라", "5V", "5 W / 1.0 A", "벅 입력 1 A"],
    ["합계", "24V", "약 119 W / 5.0 A", "메인 6.3 A"],
]
story += [table(pro_power, [42 * mm, 44 * mm, 48 * mm, 29 * mm], font=7.5), Spacer(1, 4 * mm)]
story += [p("구역마다 24V 150 W 이상 외장 어댑터를 사용합니다. 120 W 어댑터는 정격과 피크가 너무 가까워 제외했습니다. 두 구역의 DC 음극을 합치지 않아도 되며, 통신은 Wi-Fi로 묶는 편이 고장 격리에 유리합니다."), Spacer(1, 3 * mm), callout("전도 방지", "PRO 48은 높이 1700 mm입니다. 브레이크 캐스터만으로는 부족하므로 사용 중에는 상단을 벽체 또는 고정 구조물에 스트랩으로 연결하십시오.", ORANGE), PageBreak()]

# Printed parts
story += [p("10. 3D 출력 고정구", h1), p("캐비닛 전체를 출력하지 않습니다. 크고 물을 받는 부품은 프로파일·판재·시판 트레이로 만들고, 치수 적응이 필요한 작은 고정구만 PETG로 출력합니다.")]
fixtures = [
    ["파일", "HOME", "PRO", "권장 수량", "역할"],
    ["led_clip_2020 / 3030", "2020", "3030", "8 / 16", "LED 레일 고정"],
    ["camera_bracket_*_30deg", "2020", "3030", "1 / 2", "카메라 30도 설치"],
    ["sht40_sensor_guard", "공용", "공용", "1 / 2", "센서 비말 보호"],
    ["cable_clip_2020 / 3030", "2020", "3030", "12 / 24", "하네스 정리"],
    ["tray_corner_2020 / 3030", "2020", "3030", "4 / 8", "트레이 위치 반복"],
]
story += [table(fixtures, [55 * mm, 23 * mm, 23 * mm, 27 * mm, 37 * mm], font=7.2), Spacer(1, 6 * mm)]
settings = [
    ["설정", "권장값", "이유"],
    ["재료", "PETG", "습기·열에 PLA보다 안정"],
    ["노즐/레이어", "0.4 / 0.20 mm", "치수와 시간 균형"],
    ["벽/상하단", "4줄 / 5레이어", "클립 파손 억제"],
    ["인필", "30% gyroid", "충격 방향 분산"],
    ["공차", "프로파일 +0.8 mm", "프린터 편차 흡수"],
    ["볼트", "M4 관통 + T너트", "스냅만으로 하중 지지 금지"],
]
story += [table(settings, [42 * mm, 48 * mm, 75 * mm], font=7.5), Spacer(1, 5 * mm), p("STL은 output/stl/home-pro, 수정 가능한 STEP은 output/step/home-pro에 생성됩니다. 첫 출력은 케이블 클립 1개로 프로파일 맞춤을 확인한 후 진행합니다.", small), PageBreak()]

# QA
story += [p("11. 완성품 검사와 최초 가동", h1)]
qa = [
    ["시험", "방법", "합격 기준"],
    ["프레임", "대각선·수평·도어 반복", "흔들림 없음, 간극 일정"],
    ["누수", "트레이·가습수조 만수 24시간", "바닥·관통부 물방울 0"],
    ["절연 경계", "어댑터 분리 후 내부 확인", "220V 부품 0개"],
    ["5V 레일", "카메라 스트리밍 중 측정", "4.85-5.15V"],
    ["열", "모든 부하 4시간", "LED 60 C 이하, 커넥터 변색 0"],
    ["누수 차단", "센서에 물 3 ml", "5초 안에 모든 부하 OFF"],
    ["저수위", "가습수조 비우기", "미스트 기동 거부"],
    ["통신 장애", "Wi-Fi 30분 차단", "예약·안전 타임아웃 유지"],
    ["정전 복구", "전원 5회 반복", "미스트 OFF로 안전 부팅"],
    ["카메라", "빈칸 없이 전체 포트 확인", "HOME 12 / PRO 각 24포트 식별"],
]
story += [table(qa, [34 * mm, 68 * mm, 63 * mm], font=7.3), Spacer(1, 6 * mm)]
story += [p("가동 레시피 초안", h2)]
recipe = [
    ["단계", "기간", "습도", "광주기", "환기"],
    ["발근", "1-7일", "85-92%", "12h / 약광", "10분마다 1분"],
    ["순화", "8-14일", "하루 3%p 감소", "12-14h", "5분마다 1분"],
    ["성장", "15일 이후", "60-75%", "14h", "습도 상한 연동"],
]
story += [table(recipe, [32 * mm, 30 * mm, 45 * mm, 34 * mm, 24 * mm], font=7.3), Spacer(1, 4 * mm), p("식물 종과 기질에 따라 레시피 검증이 필요합니다. 고습 환경은 곰팡이 위험을 키우므로 상대습도만이 아니라 잎 표면 결로와 공기 흐름을 함께 관찰하십시오.", small), PageBreak()]

# Business/cost interpretation
story += [p("12. 원가를 판매가로 바꾸는 법", h1)]
economics = [
    ["항목", "HOME 12", "PRO 48"],
    ["시제품 BOM", "568,430원", "1,419,240원"],
    ["50대 목표 제조원가", "399,100원", "971,000원"],
    ["시험 판매가", "799,000-899,000원", "1,890,000-2,190,000원"],
    ["원가율", "44-50%", "44-51%"],
    ["예상 월 전력", "약 30-45 kWh", "약 80-120 kWh"],
    ["주요 고객", "고가 관엽 수집가·삽수 판매자", "소형 농가·판매점·육묘 작업자"],
]
story += [table(economics, [48 * mm, 57 * mm, 60 * mm], font=7.6), Spacer(1, 6 * mm)]
story += [p("사업성 검증 순서", h2)]
validation = [
    ["1", "HOME 12 한 대를 먼저 만들고 30일 순화 로그를 공개합니다."],
    ["2", "고가 식물 12개 중 생존률, 작업시간, 사진 기록 가치를 측정합니다."],
    ["3", "예약금 10만원을 받는 유료 선주문 10건이 생기기 전에는 PRO 금형을 만들지 않습니다."],
    ["4", "첫 10대는 프로파일 조립품으로 판매해 고장 데이터를 모읍니다."],
    ["5", "50대 주문이 보이면 패널 네스팅, 하네스 외주, 판금 서비스실부터 양산화합니다."],
]
story += [table(validation, [12 * mm, 153 * mm], header=False, font=8), Spacer(1, 6 * mm)]
story += [callout("돈이 되는 조건", "기계 자체보다 '고가 삽수 12개를 한 번에 순화하면서 실패 원인을 사진과 환경 로그로 남긴다'는 결과를 팔아야 합니다. 월 구독은 원격 알림, 타임랩스 보관, 재배 레시피 공유가 실제로 반복 사용될 때만 붙입니다."), PageBreak()]

# Sources and revision checklist
story += [p("13. 가격 근거와 제작 전 확인", h1), p("가격은 2026-08-25 국내 소매 구매를 가정한 예산입니다. 판매처·절단비·배송지에 따라 달라질 수 있으며, 특정 판매자의 공식 견적이 아닌 시장가 기반 설계 예산입니다.")]
sources = [
    ["항목", "확인값", "근거"],
    ["XIAO ESP32-S3 Sense", "VAT 포함 25,520원", "디바이스마트 상품 페이지"],
    ["24V 5A 어댑터", "약 29,910원부터", "다나와 24V 5A 검색 결과"],
    ["2020 프로파일", "200-800 mm 소매 비교가 존재", "다나와 2020 프로파일 비교"],
    ["나머지 부품", "샘플 구매 예산", "국내 쇼핑몰 1-3개 견적 후 확정"],
]
story += [table(sources, [45 * mm, 45 * mm, 75 * mm], font=7.5), Spacer(1, 5 * mm)]
story += [p("원문 링크", h2), p("XIAO: https://www.devicemart.co.kr/goods/view?no=14991199", small), p("24V 5A 어댑터: https://search.danawa.com/mobile/dsearch.php?keyword=24v+5a+adapter", small), p("2020 프로파일: https://prod.danawa.com/info/?pcode=20334098", small), Spacer(1, 5 * mm)]
check = [
    ["제작 전 실측", "확인"],
    ["구매 트레이 외경과 레일 간격", "□"],
    ["화분 상단 외경과 4x3 / 6x4 피치", "□"],
    ["LED 실제 길이·폭·발열·입력전압", "□"],
    ["어댑터 KC 인증번호와 출력 커넥터", "□"],
    ["팬 방향·전압과 최대 전류", "□"],
    ["미스트 모듈 저수위 보호 동작", "□"],
    ["패널 도어 간극과 힌지 홀 위치", "□"],
    ["벽체 전도 방지 고정점(PRO)", "□"],
]
story += [table(check, [142 * mm, 23 * mm], font=7.5, aligns={1: "CENTER"}), Spacer(1, 5 * mm), p("본 문서는 개발 시제품 제작서입니다. 실제 판매 전에는 전파·전기·재료·내구·표시 의무에 대해 시험기관과 별도로 검토해야 합니다.", small)]

doc = SimpleDocTemplate(
    str(OUT), pagesize=A4,
    leftMargin=16 * mm, rightMargin=16 * mm,
    topMargin=16 * mm, bottomMargin=15 * mm,
    title="SproutCam HOME 12 + PRO 48 제품 제작서 v0.1",
    author="SproutCam Project",
    subject="Smart plant cabinet fabrication manual and cost model",
)
doc.build(story, onFirstPage=page_bg, onLaterPages=page_bg)
print(OUT)
