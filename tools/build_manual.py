from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/SproutCam-One-조립설명서.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
FONT='/System/Library/AssetsV2/com_apple_MobileAsset_Font8/7a0b5c0f3c1d41c4c52a33343496c9c65ad52c50.asset/AssetData/NanumGothic.ttc'
pdfmetrics.registerFont(TTFont('KR',FONT,subfontIndex=0))
pdfmetrics.registerFont(TTFont('KR-B',FONT,subfontIndex=1))

PAGE_W,PAGE_H=A4
GREEN=colors.HexColor('#B8FF2C'); ORANGE=colors.HexColor('#FF5D35'); INK=colors.HexColor('#141414'); PAPER=colors.HexColor('#F4F1E8')
styles=getSampleStyleSheet()
body=ParagraphStyle('body',fontName='KR',fontSize=9.2,leading=14,textColor=INK,spaceAfter=5)
small=ParagraphStyle('small',fontName='KR',fontSize=7.7,leading=11,textColor=colors.HexColor('#555555'))
h1=ParagraphStyle('h1',fontName='KR-B',fontSize=24,leading=29,textColor=INK,spaceAfter=12)
h2=ParagraphStyle('h2',fontName='KR-B',fontSize=15,leading=19,textColor=INK,spaceBefore=7,spaceAfter=7)
hero=ParagraphStyle('hero',fontName='KR-B',fontSize=31,leading=35,textColor=INK,alignment=TA_CENTER)

def header_footer(canvas,doc):
    canvas.saveState(); canvas.setFillColor(PAPER); canvas.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)
    canvas.setFillColor(INK); canvas.setFont('KR-B',8); canvas.drawString(18*mm,PAGE_H-12*mm,'SPROUTCAM ONE  /  BUILD KIT v0.1')
    canvas.setFont('KR',7); canvas.drawRightString(PAGE_W-18*mm,10*mm,f'{doc.page}')
    canvas.restoreState()

def p(text,style=body): return Paragraph(text,style)

story=[Spacer(1,20*mm),p('SPROUTCAM ONE',hero),p('카메라 성장 기록형 2포트 수경재배기',ParagraphStyle('sub',parent=body,fontSize=13,alignment=TA_CENTER)),Spacer(1,8*mm)]
story.append(Image(str(ROOT/'output/preview/sproutcam-one-isometric.png'),width=150*mm,height=150*mm))
story += [p('<b>직접 제작용 개발 시제품</b> - 외장 12V 어댑터, 시판 PP 물탱크, 3D 프린팅 프레임을 사용합니다.',ParagraphStyle('note',parent=body,alignment=TA_CENTER)),PageBreak()]

story += [p('1. 제품 개요',h1)]
overview=[['항목','기본 설계'],['재배 포트','50 mm 네트팟 2개'],['물탱크','외경 180 x 120 x 90-110 mm PP 용기'],['본체 크기','약 220 x 155 x 385 mm'],['카메라','XIAO ESP32-S3 Sense / OV3660 또는 호환'],['전원','KC 인증 12V 3A 외장 어댑터'],['제어','로컬 Wi-Fi 대시보드, 사진, 펌프, 조명'],['권장 작물','바질, 루꼴라, 상추, 청경채']]
t=Table(overview,colWidths=[42*mm,123*mm],repeatRows=1)
t.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'KR'),('FONT',(0,0),(-1,0),'KR-B'),('BACKGROUND',(0,0),(-1,0),GREEN),('GRID',(0,0),(-1,-1),0.5,INK),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('PADDING',(0,0),(-1,-1),7)])); story += [t,Spacer(1,7*mm)]
story += [p('설계 원칙',h2),p('물과 전자를 분리하기 위해 물탱크는 출력하지 않고 식품용 PP 용기를 사용합니다. 전자함은 최고 수위보다 80 mm 이상 높게 장착하며, 본체 내부에는 220 V가 들어가지 않습니다.'),p('카메라 AI는 성장 기록과 상태 추정을 담당합니다. 펌프 안전은 수위 스위치와 30초 하드 타임아웃이 담당하므로 영상 판단이 실패해도 계속 급수되지 않습니다.'),Spacer(1,4*mm),p('예상 부품비',h2),p('<b>필수 부품 약 11만-14만 원 + PETG 약 2만 원</b>. 공구, 배송비, 3D 출력 대행비는 제외한 1대 개발 비용입니다.'),PageBreak()]

story += [p('2. 구매 목록',h1)]
bom=[['부품','규격','수량','예상가']]
rows=[('XIAO ESP32-S3 Sense','프리솔더 권장','1','25,520'),('SHT40','I2C 3.3V','1','9,000'),('수직 플로트 스위치','PP, NO/NC','1','4,000'),('미니 수중펌프','5V, 80-120 L/h','1','7,000'),('MOSFET 모듈','2채널, 3.3V 로직','1','7,000'),('식물 LED 바','12V, 10-15W, 180-200mm','1','18,000'),('KC 어댑터','12V 3A, 5.5x2.1','1','15,000'),('DC-DC 벅','12V -> 5V 3A','1','5,000'),('실리콘 튜브','내경 4 / 외경 6mm','2m','5,000'),('네트팟','상단 외경 50mm','2','3,000'),('PP 식품용기','180 x 120 x 90-110mm','1','6,000'),('볼트/배선/커넥터','M4, JST, 열수축튜브','1식','13,000')]
bom += [list(x) for x in rows]
t=Table(bom,colWidths=[46*mm,73*mm,16*mm,28*mm],repeatRows=1)
t.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'KR'),('FONT',(0,0),(-1,0),'KR-B'),('FONTSIZE',(0,0),(-1,-1),7.8),('BACKGROUND',(0,0),(-1,0),GREEN),('GRID',(0,0),(-1,-1),0.35,INK),('ALIGN',(2,1),(-1,-1),'RIGHT'),('PADDING',(0,0),(-1,-1),5)])); story += [t,Spacer(1,5*mm),p('정확한 구매 링크는 저장소의 <b>docs/BOM.csv</b>에 있습니다. LED 바의 실제 단면이 190 x 32 x 8 mm를 넘으면 하우징 CAD 치수를 수정하십시오.',small),PageBreak()]

story += [p('3. 출력 부품',h1)]
parts=[['파일','최대 크기 mm','역할'],['tank_cradle','205.6 x 162.6 x 47','탱크 받침과 하부 마스트 소켓'],['lid_left / right','101.5 x 128 x 4','분할 탱크 덮개와 네트팟 홀'],['mast_lower','24 x 18 x 205','하부 마스트와 결합 텅'],['mast_upper','24 x 18 x 190','높이 조절 상부 마스트'],['light_housing','205 x 66.5 x 28','LED 바 하우징'],['camera_pod','46 x 45 x 24','카메라 및 USB-C 접근'],['electronics_box','96 x 64 x 34','MOSFET, 벅, 배선 수납'],['electronics_lid','96 x 64 x 5.7','전자함 압입식 덮개']]
t=Table(parts,colWidths=[48*mm,48*mm,68*mm],repeatRows=1)
t.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'KR'),('FONT',(0,0),(-1,0),'KR-B'),('FONTSIZE',(0,0),(-1,-1),7.8),('BACKGROUND',(0,0),(-1,0),GREEN),('GRID',(0,0),(-1,-1),0.35,INK),('PADDING',(0,0),(-1,-1),5)])); story += [t,Spacer(1,6*mm)]
story += [p('슬라이서 설정',h2),p('PETG / 0.20 mm 레이어 / 벽 4줄 / 상하단 5레이어 / 25% gyroid. 카메라 포드 외에는 기본적으로 서포트가 필요하지 않습니다. 처음에는 lid_left 한 장만 출력해 네트팟과 용기 치수를 확인하십시오.'),p('CAD 기준 치수는 0.8 mm 조립 여유를 포함합니다. 프린터 수축률이 큰 경우 TANK_CLEARANCE를 1.2 mm까지 늘립니다.'),PageBreak()]

story += [p('4. 조립 순서',h1)]
steps=[('01','빈 탱크를 크래들에 넣고 흔들림과 0.5-1.5 mm 간격을 확인합니다.'),('02','분할 덮개를 M4x12 볼트로 결합하고 50 mm 네트팟 두 개를 끼웁니다.'),('03','하부와 상부 마스트를 체결하고 LED-식물 간격을 200-300 mm로 맞춥니다.'),('04','LED 하우징과 카메라 포드를 설치해 렌즈가 두 포트 중앙을 향하게 합니다.'),('05','펌프와 4x6 mm 튜브를 설치하고 플로트 스위치를 흡입구보다 20 mm 높게 둡니다.'),('06','전자함을 최고 수위보다 80 mm 이상 높게 고정하고 모든 케이블에 물방울 고리를 만듭니다.'),('07','전자부품을 빼고 24시간 누수 시험 후 펌프를 10분씩 세 차례 공회전합니다.'),('08','5V 레일을 측정한 뒤 펌웨어를 올리고 대시보드에서 펌프 3초 시험을 합니다.')]
for n,txt in steps:
    box=Table([[p(n,ParagraphStyle('num',parent=h2,textColor=ORANGE)),p(txt)]],colWidths=[18*mm,145*mm])
    box.setStyle(TableStyle([('BOX',(0,0),(-1,-1),0.6,INK),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('PADDING',(0,0),(-1,-1),7)])); story += [box,Spacer(1,3*mm)]
story += [PageBreak(),p('5. 배선 및 최초 가동',h1),p('<b>12V 입력</b>은 2A 퓨즈를 거쳐 LED MOSFET으로 연결합니다. 같은 입력에서 DC-DC 벅으로 5V를 만들고 XIAO와 펌프 MOSFET에 공급합니다.'),Spacer(1,3*mm)]
wiring=[['핀','연결','주의'],['D0','플로트 스위치','INPUT_PULLUP, 반대쪽 GND'],['D1','펌프 MOSFET','펌프 직접 연결 금지'],['D2','LED MOSFET','3.3V 로직 호환'],['D4 / D5','SHT40 SDA / SCL','3.3V I2C'],['3V3','센서 전원','모터 연결 금지'],['GND','공통 접지','12V/5V 음극 공통']]
t=Table(wiring,colWidths=[30*mm,62*mm,72*mm],repeatRows=1); t.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'KR'),('FONT',(0,0),(-1,0),'KR-B'),('BACKGROUND',(0,0),(-1,0),GREEN),('GRID',(0,0),(-1,-1),0.4,INK),('PADDING',(0,0),(-1,-1),6)])); story += [t,Spacer(1,6*mm)]
story += [p('최초 가동 체크',h2),p('□ 5V 레일이 4.85-5.15V이다.<br/>□ 저수위에서 펌프 명령이 거부된다.<br/>□ 펌프 3초 명령 후 자동으로 정지한다.<br/>□ 전자함과 커넥터에 물방울이 없다.<br/>□ 카메라 화면에 두 재배 포트가 모두 보인다.<br/>□ LED 하우징을 30분 켠 뒤 손으로 만질 수 있는 온도다.'),Spacer(1,4*mm)]
warning=Table([[p('<b>즉시 전원 분리:</b> 탄 냄새, 60°C 이상의 벅 컨버터, 전자함 결로, 탱크 균열, 튜브 이탈, 펌프 소음 급증.',ParagraphStyle('warn',parent=body,textColor=colors.white))]],colWidths=[164*mm]); warning.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),ORANGE),('BOX',(0,0),(-1,-1),1,INK),('PADDING',(0,0),(-1,-1),9)])); story += [warning,Spacer(1,6*mm),p('이 문서는 개인 제작용 개발 안내입니다. 완제품 판매 전에는 전파·전기 안전, 재료 안전성, 누수 및 장기 내구성 시험이 별도로 필요합니다.',small)]

doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=18*mm,bottomMargin=16*mm,title='SproutCam One 조립설명서',author='SproutCam Project')
doc.build(story,onFirstPage=header_footer,onLaterPages=header_footer)
print(OUT)
