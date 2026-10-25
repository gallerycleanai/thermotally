#!/usr/bin/env python3
"""Generates the free printable food-safety log PDFs (requires: pip install reportlab).
Called by build.py; can also run alone: python3 make_pdfs.py <out_dir> <site_url_for_footer>"""
import sys, pathlib
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

INK = colors.HexColor("#0f2a24"); ACC = colors.HexColor("#0e9f6e"); LIGHT = colors.HexColor("#eef7f3"); GRID = colors.HexColor("#9fb3ac")
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=17, textColor=INK, leading=20)
SM = ParagraphStyle("sm", fontName="Helvetica", fontSize=8, textColor=INK, leading=10)
SMB = ParagraphStyle("smb", parent=SM, fontName="Helvetica-Bold")
CELL = ParagraphStyle("cell", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white, leading=9, alignment=1)

def _footer(brand, url, source):
    def draw(c, doc):
        c.saveState(); w, h = doc.pagesize
        c.setFont("Helvetica", 7); c.setFillColor(colors.HexColor("#4b5f59"))
        c.drawString(0.45*inch, 0.38*inch, f"Rules: {source}. Not legal advice; your local health department's rules apply and may be stricter.")
        c.drawString(0.45*inch, 0.26*inch, "Keep completed logs for as long as your health department requires - ask your inspector how long that is.")
        c.setFillColor(ACC); c.setFont("Helvetica-Bold", 7.5)
        c.drawRightString(w-0.45*inch, 0.26*inch, f"Free printable from {brand}" + (f" · {url}" if url else ""))
        c.restoreState()
    return draw

def _meta_row(fields):
    W = landscape(letter)[0]-0.9*inch
    t = Table([[Paragraph(f"<b>{f}:</b> " + "_"*max(8, int(W/len(fields)/4.6) - len(f)), SM) for f in fields]], colWidths=[W/len(fields)]*len(fields))
    t.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
    return t

def _rules_box(lines, width):
    t = Table([[Paragraph(" &nbsp;·&nbsp; ".join(lines), SM)]], colWidths=[width])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT),("BOX",(0,0),(-1,-1),0.6,ACC),
                           ("LEFTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    return t

def _grid(headers, widths, rows, row_h=0.27*inch, first_col=None):
    data = [[Paragraph(h, CELL) for h in headers]]
    for i in range(rows):
        r = [""]*len(headers)
        if first_col: r[0] = first_col(i)
        data.append(r)
    t = Table(data, colWidths=widths, rowHeights=[None]+[row_h]*rows, repeatRows=1)
    st = [("BACKGROUND",(0,0),(-1,0),INK),("GRID",(0,0),(-1,-1),0.5,GRID),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
          ("FONT",(0,1),(-1,-1),"Helvetica",8),("ALIGN",(0,1),(0,-1),"CENTER")]
    for i in range(1, rows+1):
        if i % 2 == 0: st.append(("BACKGROUND",(0,i),(-1,i),colors.HexColor("#f7faf9")))
    t.setStyle(TableStyle(st)); return t

def build(path, title, fields, rules, headers, widths, rows, source, brand, url, row_h=0.27*inch, first_col=None, extra=None):
    ps = landscape(letter)
    doc = SimpleDocTemplate(str(path), pagesize=ps, leftMargin=0.45*inch, rightMargin=0.45*inch, topMargin=0.4*inch, bottomMargin=0.55*inch,
                            title=title, author=brand, subject="Free printable food safety log", creator=brand)
    W = ps[0]-0.9*inch
    scale = W/sum(widths); widths = [w*scale for w in widths]
    story = [Paragraph(title, H1), Spacer(1,4), _meta_row(fields), Spacer(1,4), _rules_box(rules, W), Spacer(1,6),
             _grid(headers, widths, rows, row_h, first_col)]
    if extra: story += [Spacer(1,5), Paragraph(extra, SM)]
    doc.build(story, onFirstPage=_footer(brand, url, source), onLaterPages=_footer(brand, url, source))

FC = "FDA Food Code 2022 (same limits in the 2026 edition)"

def make_all(out, brand, url):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    made = []
    # 1 fridge / freezer
    p = out/"fridge-freezer-temperature-log.pdf"
    build(p, "Fridge & Freezer Temperature Log (monthly)", ["Business", "Unit name / location", "Month / year", "Thermometer ID"],
          ["<b>Fridge (cold holding): 41°F (5°C) or below</b> — §3-501.16(A)(2)", "<b>Freezer:</b> food must stay frozen (§3-501.11); common target 0°F (−18°C) or below",
           "Check at least twice a day (opening & closing)", "If out of range: record the action, re-check within 30 min"],
          ["Day","AM time","AM °F/°C","Initials","PM time","PM °F/°C","Initials","Corrective action (if out of range)","Re-check °F","Mgr OK"],
          [0.45,0.7,0.75,0.6,0.7,0.75,0.6,3.0,0.75,0.55], 31, f"{FC} §3-501.16, §3-501.11", brand, url, row_h=0.168*inch, first_col=lambda i: str(i+1))
    made.append(p)
    # 2 hot & cold holding
    p = out/"hot-cold-holding-temperature-log.pdf"
    build(p, "Hot & Cold Holding Temperature Log", ["Business", "Station / line", "Week of", "Thermometer ID"],
          ["<b>Hot holding: 135°F (57°C) or above</b> — §3-501.16(A)(1)", "<b>Cold holding: 41°F (5°C) or below</b> — §3-501.16(A)(2)",
           "Suggested: check every 2 hours so you can still correct", "Reheat for hot holding: 165°F (74°C) within 2 h — §3-403.11"],
          ["Date","Time","Food item","Hot / Cold","Temp °F","OK? (Y/N)","Corrective action (reheat, chill, discard)","Initials","Mgr OK"],
          [0.7,0.6,1.8,0.65,0.65,0.6,2.8,0.6,0.55], 20, f"{FC} §3-501.16, §3-403.11", brand, url, row_h=0.27*inch)
    made.append(p)
    # 3 cooling
    p = out/"food-cooling-log.pdf"
    build(p, "Food Cooling Log (2-hour / 6-hour rule)", ["Business", "Week of", "Thermometer ID"],
          ["<b>Stage 1: 135°F → 70°F (57°C → 21°C) within 2 hours</b>", "<b>Stage 2: 70°F → 41°F (21°C → 5°C) within the next 4 hours (6 h total)</b> — §3-501.14(A)",
           "Ambient-temperature ingredients: to 41°F within 4 h — §3-501.14(B)", "Missed stage 1? Reheat to 165°F and restart, or discard"],
          ["Date","Food item","Cooling method","Start time","Start °F","1 h °F","2 h time","2 h °F (≤70)","4 h °F","6 h time","6 h °F (≤41)","Action / initials"],
          [0.65,1.5,1.0,0.6,0.55,0.5,0.6,0.7,0.5,0.6,0.7,1.6], 14, f"{FC} §3-501.14, §3-501.15", brand, url, row_h=0.36*inch)
    made.append(p)
    # 4 receiving
    p = out/"receiving-log.pdf"
    build(p, "Receiving (Delivery) Log", ["Business", "Week of", "Thermometer ID"],
          ["<b>Cold TCS food: 41°F (5°C) or below</b> on arrival — §3-202.11(A)", "Exceptions (milk, shell eggs, shellstock): see §3-202.11, §3-501.14(C)",
           "<b>Frozen: received frozen</b> — §3-202.11(E)", "<b>Hot food: 135°F or above</b> — §3-202.11(D)", "Reject damaged, thawed-refrozen or unlabeled goods"],
          ["Date","Time","Supplier","Product","Temp °F","Pkg OK? (Y/N)","Use-by / lot","Accept / Reject","Reason / action","Initials"],
          [0.7,0.55,1.3,1.6,0.6,0.65,0.95,0.7,1.8,0.6], 20, f"{FC} §3-202.11, §3-202.15", brand, url, row_h=0.27*inch)
    made.append(p)
    # 5 cleaning schedule
    p = out/"kitchen-cleaning-schedule.pdf"
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    tasks = ["Food-contact surfaces & cutting boards (every 4 h in continuous use)","Prep sinks & hand sinks","Slicer / mixer / food processor (after each use)",
             "Reach-in fridge handles, gaskets & shelves (wipe)","Grill, flat-top, fryer exterior","Floors & floor drains","Trash & recycling bins emptied, lids cleaned",
             "Dish machine: check wash/rinse temp or sanitizer","Sanitizer buckets changed & concentration tested (ppm)","Restrooms","Walk-in floor & shelving (weekly)",
             "Hood filters (weekly)","Ice machine interior (monthly or per maker)","Behind/under equipment (monthly)","", ""]
    rows = len(tasks)
    build(p, "Kitchen Cleaning & Sanitizing Schedule (weekly)", ["Business", "Week of", "Sanitizer type & target ppm"],
          ["Food-contact surfaces in continuous use: clean & sanitize at least every 4 hours — §4-602.11(C)", "Test sanitizer concentration with a test kit — §4-302.14",
           "Initial each box when done; manager reviews weekly"],
          ["Task"]+days+["Notes / ppm"], [3.6]+[0.55]*7+[1.6], rows, f"{FC} §4-602.11, §4-302.14, §4-501.114", brand, url, row_h=0.285*inch,
          first_col=lambda i: Paragraph(tasks[i], SM))
    made.append(p)
    # 6 thermometer calibration
    p = out/"thermometer-calibration-log.pdf"
    build(p, "Thermometer Calibration Log", ["Business", "Month / year", "Elevation (ft)"],
          ["<b>Food probes (°F scale): accurate to ±2°F</b> — §4-203.11(B)", "<b>Air / water thermometers (°F): ±3°F</b> — §4-203.12(B)",
           "Calibrate per the manufacturer's instructions — §4-502.11(B)", "<b>Ice-point check: 32°F (0°C)</b> in a full ice-water slurry",
           "Boiling point is 212°F only at sea level; it drops about 1°F per ~500 ft of elevation", "Check weekly, after a drop, and before each shift on high-risk days"],
          ["Date","Time","Thermometer ID / type","Method (ice / boil)","Reading °F","Should read °F","Off by °F","Within limit? (Y/N)","Adjusted to °F","Action (recalibrated / replaced / removed)","Initials"],
          [0.7,0.55,1.5,0.75,0.6,0.65,0.55,0.7,0.7,2.2,0.55], 20, f"{FC} §4-203.11, §4-203.12, §4-502.11", brand, url, row_h=0.27*inch)
    made.append(p)
    # 7 sanitizer test log
    p = out/"sanitizer-test-log.pdf"
    build(p, "Sanitizer Concentration Test Log (chlorine / quat / iodine)", ["Business", "Week of", "Sanitizer product", "Label range (ppm)"],
          ["Test with a test kit or strips made for your sanitizer — §4-302.14, §4-501.116",
           "<b>Chlorine:</b> 25–49 ppm needs water ≥120°F; 50–99 ppm needs ≥100°F (pH ≤10) or ≥75°F (pH ≤8); 100 ppm needs ≥55°F — §4-501.114(A)",
           "<b>Quat:</b> ppm per the EPA label, water ≥75°F, hardness ≤500 ppm or per label — §4-501.114(C)",
           "<b>Iodine:</b> 12.5–25 ppm, water ≥68°F, pH ≤5 or per label — §4-501.114(B)",
           "Wiping-cloth buckets must be at sanitizing strength — §3-304.14(B)"],
          ["Date","Time","Where (3-comp sink / bucket / dish machine / bottle)","Sanitizer","Reading (ppm)","Water °F","In range? (Y/N)","Action (remade, re-tested ppm)","Initials","Mgr OK"],
          [0.7,0.55,2.1,0.9,0.75,0.65,0.7,2.3,0.6,0.55], 20, f"{FC} §4-302.14, §4-501.114, §4-703.11, §3-304.14", brand, url, row_h=0.27*inch)
    made.append(p)
    # 8 time as a public health control
    p = out/"time-as-a-public-health-control-log.pdf"
    build(p, "Time as a Public Health Control (TPHC) Log", ["Business", "Date", "Station", "Written procedure on file (Y/N)"],
          ["<b>4-hour rule:</b> start at ≤41°F or ≥135°F; mark the time 4 h after removal; cook &amp; serve, serve, or discard within 4 h — §3-501.19(B)",
           "<b>6-hour rule (cold food only):</b> start at ≤41°F; food may never exceed 70°F; mark removal time and the 6-h discard time — §3-501.19(C)",
           "Unmarked or over-time food must be discarded", "Written procedures required (§3-501.19(A)); some jurisdictions require approval or do not allow TPHC"],
          ["Food item","Pan / location","Start °F","Time removed","4 h or 6 h?","Discard by","Labeled? (Y/N)","6 h option: temp checks (≤70°F)","Served / discarded at (time)","Initials"],
          [1.6,1.0,0.6,0.75,0.65,0.75,0.65,2.0,1.1,0.55], 18, f"{FC} §3-501.19", brand, url, row_h=0.3*inch)
    made.append(p)
    return made

if __name__ == "__main__":
    print(make_all(sys.argv[1] if len(sys.argv) > 1 else "out", "ThermoTally", sys.argv[2] if len(sys.argv) > 2 else "thermotally.com"))
