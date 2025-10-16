# main.py — 2nd Year Quiz (Apt 8 + Reason 7 + Coding 15 • 60s/Question • Strict Mode)
# -----------------------------------------------------------------------------------
# Run:
#   pip install flask pandas openpyxl
#   python main.py
#   open http://127.0.0.1:5000

from __future__ import annotations
import os, json, random, threading
from datetime import datetime
from typing import List, Dict, Any
from functools import wraps

from flask import (
    Flask, request, redirect, url_for, session, render_template_string,
    flash, send_file
)
import pandas as pd

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("QUIZ_SECRET", "dev-secret-change-me")

# ---- Admin creds ----
ADMIN_USER = os.environ.get("QUIZ_ADMIN_USER", "surya")
ADMIN_PASS = os.environ.get("QUIZ_ADMIN_PASS", "nriit123")

# ---- local images (change if needed) ----
HEADER_IMG_PATH = r"C:\college sit\2nd year\images\header.jpg"
LOGO_IMG_PATH   = r"C:\college sit\2nd year\images\logo.jpg"

@app.route("/header-img")
def header_img():
    return send_file(HEADER_IMG_PATH) if os.path.exists(HEADER_IMG_PATH) else ("", 404)

@app.route("/logo-img")
def logo_img():
    return send_file(LOGO_IMG_PATH) if os.path.exists(LOGO_IMG_PATH) else ("", 404)

# ---- Excel ----
EXCEL_PATH = os.path.join(os.getcwd(), "quiz_data", "students.xlsx")
os.makedirs(os.path.dirname(EXCEL_PATH), exist_ok=True)
STUDENTS_SHEET = "students"
ATTEMPTS_SHEET = "attempts"
XL_LOCK = threading.Lock()

# =============================================================================
# QUESTION BANKS
# =============================================================================
APTITUDE: List[Dict[str, Any]] = [
    {"id":"APT-001","section":"Aptitude","question":"25 percent of 200 is","options":["25","50","100","75"],"answer_index":1},
    {"id":"APT-002","section":"Aptitude","question":"Simplify 6 × 7 + 8","options":["50","56","42","60"],"answer_index":0},
    {"id":"APT-003","section":"Aptitude","question":"If 10 pencils cost 40 rupees, cost of one pencil is","options":["2","3","4","5"],"answer_index":2},
    {"id":"APT-004","section":"Aptitude","question":"Average of 5, 10, 15 is","options":["5","10","15","20"],"answer_index":1},
    {"id":"APT-005","section":"Aptitude","question":"A car travels 60 km in 2 hours. Speed is","options":["20","30","40","50"],"answer_index":1},
    {"id":"APT-006","section":"Aptitude","question":"Ratio of 8 to 4 is","options":["1:2","2:1","3:1","1:3"],"answer_index":1},
    {"id":"APT-007","section":"Aptitude","question":"Simple interest on 1000 rupees at 10 percent for 2 years is","options":["100","150","200","250"],"answer_index":2},
    {"id":"APT-008","section":"Aptitude","question":"If x = 5, then 2x + 3 =","options":["10","11","12","13"],"answer_index":3},
    {"id":"APT-009","section":"Aptitude","question":"Odd number in 2, 4, 6, 9, 10 is","options":["2","4","9","10"],"answer_index":2},
    {"id":"APT-010","section":"Aptitude","question":"A bottle costs 30 and a cap 10. Cost of 3 sets is","options":["90","100","110","120"],"answer_index":3},
    {"id":"APT-011","section":"Aptitude","question":"If 3 men do work in 6 days, 6 men take","options":["2","3","4","6"],"answer_index":1},
    {"id":"APT-012","section":"Aptitude","question":"HCF of 12 and 18 is","options":["2","3","4","6"],"answer_index":3},
    {"id":"APT-013","section":"Aptitude","question":"If A = B and B = C then A =","options":["B","C","A","All equal"],"answer_index":3},
    {"id":"APT-014","section":"Aptitude","question":"Successor of 99 is","options":["98","99","100","101"],"answer_index":2},
    {"id":"APT-015","section":"Aptitude","question":"Square root of 81 is","options":["7","8","9","10"],"answer_index":2},
    {"id":"APT-016","section":"Aptitude","question":"A train travels 120 km in 3 hours. Speed is","options":["30","40","50","60"],"answer_index":1},
    {"id":"APT-017","section":"Aptitude","question":"Compound interest on 1000 at 10 percent for 2 years is","options":["200","210","220","230"],"answer_index":1},
    {"id":"APT-018","section":"Aptitude","question":"If 12 men complete work in 15 days, 6 men will take","options":["25","30","35","40"],"answer_index":1},
    {"id":"APT-019","section":"Aptitude","question":"Average of 20 numbers is 50. Sum is","options":["800","900","1000","1100"],"answer_index":2},
    {"id":"APT-020","section":"Aptitude","question":"If a:b = 2:3 and b:c = 4:5, then a:c =","options":["8:15","4:9","2:5","5:8"],"answer_index":0},
    {"id":"APT-021","section":"Aptitude","question":"Selling price 300, cost price 250. Profit percent","options":["10%","15%","20%","25%"],"answer_index":2},
    {"id":"APT-022","section":"Aptitude","question":"A can do a work in 10 days, B in 15 days. Together they take","options":["5","6","7","8"],"answer_index":1},
    {"id":"APT-023","section":"Aptitude","question":"Probability of getting head in coin toss","options":["1/4","1/3","1/2","1"],"answer_index":2},
    {"id":"APT-024","section":"Aptitude","question":"Boat upstream 10 km/h, downstream 15 km/h. Current speed","options":["2","2.5","3","4"],"answer_index":1},
    {"id":"APT-025","section":"Aptitude","question":"Area of rectangle is 60, length 10. Width","options":["5","6","7","8"],"answer_index":1},
    {"id":"APT-026","section":"Aptitude","question":"Money doubles in 8 years. Rate percent","options":["10%","12.5%","15%","20%"],"answer_index":1},
    {"id":"APT-027","section":"Aptitude","question":"5x = 20 then x =","options":["2","3","4","5"],"answer_index":2},
    {"id":"APT-028","section":"Aptitude","question":"A man walks 5 km/h for 2 hours. Distance","options":["5","10","15","20"],"answer_index":1},
    {"id":"APT-029","section":"Aptitude","question":"Radius 7 cm. Area of circle (π=22/7)","options":["44","77","154","220"],"answer_index":2},
    {"id":"APT-030","section":"Aptitude","question":"Number +20% then -10%. Net change","options":["+7%","+8%","+9%","+10%"],"answer_index":1},
    {"id":"APT-031","section":"Aptitude","question":"Two pipes fill a tank in 12 and 15 min. Together","options":["6","6.4","7","8"],"answer_index":1},
    {"id":"APT-032","section":"Aptitude","question":"Selling price 4× cost price. Profit percent","options":["100%","200%","300%","400%"],"answer_index":2},
    {"id":"APT-033","section":"Aptitude","question":"Series 2, 4, 8, 16, ?","options":["18","20","32","36"],"answer_index":2},
    {"id":"APT-034","section":"Aptitude","question":"(10 + 2)² – (10 – 2)² =","options":["32","64","96","128"],"answer_index":2},
    {"id":"APT-035","section":"Aptitude","question":"Selling price 540, loss 10%. Cost price","options":["500","550","600","650"],"answer_index":2},
    {"id":"APT-036","section":"Aptitude","question":"If x + 1/x = 2, then x² + 1/x² =","options":["2","3","4","5"],"answer_index":0},
    {"id":"APT-037","section":"Aptitude","question":"2x + 3y = 12, x – y = 1. Value of x","options":["2","3","4","5"],"answer_index":2},
    {"id":"APT-038","section":"Aptitude","question":"10000 at 10% compound interest for 2 years. Amount","options":["11000","12000","12100","12500"],"answer_index":2},
    {"id":"APT-039","section":"Aptitude","question":"A can finish in 10 days, B in 15 days. B helps 5 days. Total days","options":["7","8","9","10"],"answer_index":1},
    {"id":"APT-040","section":"Aptitude","question":"Triangle sides 3,4,5. Area","options":["6","7","8","9"],"answer_index":0},
    {"id":"APT-041","section":"Aptitude","question":"Average of first 10 natural numbers","options":["4","5","5.5","6"],"answer_index":2},
    {"id":"APT-042","section":"Aptitude","question":"Mixture milk:water 4:1. Add 5L water → 3:2. Milk","options":["10","15","20","25"],"answer_index":1},
    {"id":"APT-043","section":"Aptitude","question":"(81)^(3/4)","options":["9","27","81","243"],"answer_index":1},
    {"id":"APT-044","section":"Aptitude","question":"sinA = 3/5 then cosA =","options":["4/5","3/5","5/4","1/5"],"answer_index":0},
    {"id":"APT-045","section":"Aptitude","question":"Diff between SI and CI on 5000 at 10% for 2 years","options":["25","50","75","100"],"answer_index":0},
    {"id":"APT-046","section":"Aptitude","question":"log10 x = 2 then x =","options":["10","20","100","1000"],"answer_index":2},
    {"id":"APT-047","section":"Aptitude","question":"Trains 150m & 100m cross in 12s, opposite dir. Relative speed","options":["12.5 m/s","15 m/s","20.8 m/s","25 m/s"],"answer_index":2},
    {"id":"APT-048","section":"Aptitude","question":"x² – 5x + 6 = 0. x =","options":["1 or 2","2 or 3","3 or 4","4 or 5"],"answer_index":1},
    {"id":"APT-049","section":"Aptitude","question":"Man rows 6 km/h; current 2 km/h. Upstream 6 km time","options":["1 h","1.5 h","2 h","2.5 h"],"answer_index":2},
    {"id":"APT-050","section":"Aptitude","question":"Amount 8000 in 2 years at 10% CI. Principal","options":["6500","6600","6611","6700"],"answer_index":2},
]

REASONING: List[Dict[str, Any]] = [
    {"id":"RSN-001","section":"Reasoning","question":"Next number in the series 2, 4, 6, 8, ?","options":["9","10","11","12"],"answer_index":1},
    {"id":"RSN-002","section":"Reasoning","question":"If TOM = GNL, then CAT =","options":["XZG","ZYG","XZG","XZH"],"answer_index":0},
    {"id":"RSN-003","section":"Reasoning","question":"Which word is odd one out?","options":["Apple","Mango","Carrot","Banana"],"answer_index":2},
    {"id":"RSN-004","section":"Reasoning","question":"Find the missing letter: A, C, F, J, O, ?","options":["Q","T","U","V"],"answer_index":2},
    {"id":"RSN-005","section":"Reasoning","question":"Ravi taller than Manoj but shorter than Kiran. Who is shortest?","options":["Ravi","Manoj","Kiran","None"],"answer_index":1},
    {"id":"RSN-006","section":"Reasoning","question":"Angle between hands at 3:15 is","options":["7.5°","15°","22.5°","30°"],"answer_index":0},
    {"id":"RSN-007","section":"Reasoning","question":"If 5 → 25, 6 → 36, then 8 →","options":["48","56","64","72"],"answer_index":2},
    {"id":"RSN-008","section":"Reasoning","question":"Choose the odd pair","options":["1–3","2–4","3–6","4–8","5–11"],"answer_index":4},
    {"id":"RSN-009","section":"Reasoning","question":"Opposite direction of South-West is","options":["North-East","East","West","South-East"],"answer_index":0},
    {"id":"RSN-010","section":"Reasoning","question":"Which word cannot be made from COMPUTER?","options":["TERM","CORE","PURE","TONE"],"answer_index":3},
    {"id":"RSN-011","section":"Reasoning","question":"If P = 16, Q = 17, then S =","options":["18","19","20","21"],"answer_index":1},
    {"id":"RSN-012","section":"Reasoning","question":"A is mother of B. C is father of A. Relation of C to B","options":["Father","Grandfather","Uncle","Brother"],"answer_index":1},
    {"id":"RSN-013","section":"Reasoning","question":"Mirror image of clock showing 2:45 will show","options":["9:15","9:45","10:15","10:45"],"answer_index":0},
    {"id":"RSN-014","section":"Reasoning","question":"Arrange in logical order","options":[
        "Seed → Plant → Tree → Fruit",
        "Plant → Seed → Tree → Fruit",
        "Seed → Tree → Plant → Fruit",
        "Tree → Seed → Plant → Fruit"
    ],"answer_index":0},
    {"id":"RSN-015","section":"Reasoning","question":"If 2 = 6, 3 = 12, 4 = 20, then 5 =","options":["25","30","35","40"],"answer_index":1},
    {"id":"RSN-016","section":"Reasoning","question":"Pointing to a girl: 'She is the daughter of my grandfather’s only son.' She is","options":["Sister","Cousin","Mother","Aunt"],"answer_index":0},
    {"id":"RSN-017","section":"Reasoning","question":"In a certain code “DOG” = 4157, then “CAT” =","options":["31420","31620","31425","31525"],"answer_index":0},
    {"id":"RSN-018","section":"Reasoning","question":"Five friends P,Q,R,S,T in a line. R not next to S, S left of P. Who is in the middle?","options":["P","Q","R","S"],"answer_index":1},
    {"id":"RSN-019","section":"Reasoning","question":"If A=1, B=2, value of “ACE”","options":["7","8","9","10"],"answer_index":2},
    {"id":"RSN-020","section":"Reasoning","question":"Which is different? Circle, Triangle, Rectangle, Sphere","options":["Circle","Triangle","Rectangle","Sphere"],"answer_index":3},
    {"id":"RSN-021","section":"Reasoning","question":"If Monday = 1, then Saturday =","options":["5","6","7","8"],"answer_index":1},
    {"id":"RSN-022","section":"Reasoning","question":"Odd number out 64,125,216,343,512,100","options":["64","125","216","343","512","100"],"answer_index":5},
    {"id":"RSN-023","section":"Reasoning","question":"If A:B=2:3 and B:C=4:5 then A:C =","options":["8:15","4:9","2:5","6:10"],"answer_index":0},
    {"id":"RSN-024","section":"Reasoning","question":"Pattern PEN → OZM, then CAT →","options":["BZS","DYT","AZS","CZT"],"answer_index":0},
    {"id":"RSN-025","section":"Reasoning","question":"If KITE = 39, then BIRD =","options":["28","29","30","31"],"answer_index":2},
    {"id":"RSN-026","section":"Reasoning","question":"Rahul facing north turns right, then left, then right again. Now faces","options":["East","South","West","North"],"answer_index":1},
    {"id":"RSN-027","section":"Reasoning","question":"Next number 3, 6, 18, 72, ?","options":["144","288","360","400"],"answer_index":2},
    {"id":"RSN-028","section":"Reasoning","question":"All pens are books. No book is pencil. Some pens are not pencils?","options":["True","False","Cannot say","None"],"answer_index":0},
    {"id":"RSN-029","section":"Reasoning","question":"If 6 men = 4 women in work, ratio men:women","options":["2:3","3:2","4:3","3:4"],"answer_index":0},
    {"id":"RSN-030","section":"Reasoning","question":"Bird : Nest :: Bee :","options":["Hive","Hole","Tree","Field"],"answer_index":0},
    {"id":"RSN-031","section":"Reasoning","question":"Series 2, 3, 5, 8, 12, 17, ?","options":["21","22","23","24"],"answer_index":2},
    {"id":"RSN-032","section":"Reasoning","question":"Complete pattern A1, C3, E5, G7, ?","options":["H8","I9","J10","K11"],"answer_index":1},
    {"id":"RSN-033","section":"Reasoning","question":"Some cats are dogs; some dogs are rats. 'Some cats are rats.'","options":["True","False","Cannot be concluded","None"],"answer_index":2},
    {"id":"RSN-034","section":"Reasoning","question":"Rearrange TAECR to form a word","options":["REACT","TRACE","CARET","CREATE"],"answer_index":0},
    {"id":"RSN-035","section":"Reasoning","question":"If 5×6=30 and 6×7=42 then 8×9=","options":["64","70","72","80"],"answer_index":2},
    {"id":"RSN-036","section":"Reasoning","question":"All flowers are leaves; some leaves are roots. Some flowers are roots?","options":["True","False","Cannot be concluded","None"],"answer_index":2},
    {"id":"RSN-037","section":"Reasoning","question":"Arrange logically: Doctor, Patient, Treatment, Disease, Diagnosis","options":[
        "Disease → Patient → Diagnosis → Doctor → Treatment",
        "Patient → Disease → Doctor → Diagnosis → Treatment",
        "Disease → Diagnosis → Patient → Doctor → Treatment",
        "Doctor → Diagnosis → Patient → Treatment → Disease"
    ],"answer_index":0},
    {"id":"RSN-038","section":"Reasoning","question":"Find missing number 7, 14, 28, 56, ?, 224","options":["96","100","112","120"],"answer_index":2},
    {"id":"RSN-039","section":"Reasoning","question":"If FISH=GJTJ, then GOAT =","options":["HPBU","HQBV","IPBW","HPBW"],"answer_index":0},
    {"id":"RSN-040","section":"Reasoning","question":"If A+B: father, A–B: sister, A×B: brother. P+Q–R means","options":["P is father of R","P is brother of R","P is uncle of R","None"],"answer_index":0},
    {"id":"RSN-041","section":"Reasoning","question":"A sits 3rd left of B, C is 2nd right of A, D immediate left of B. Who between A and B?","options":["C","D","E","None"],"answer_index":1},
    {"id":"RSN-042","section":"Reasoning","question":"Series 3, 9, 27, 81, 243, ?","options":["486","729","810","900"],"answer_index":1},
    {"id":"RSN-043","section":"Reasoning","question":"Five people shake hands once each. How many handshakes?","options":["5","8","10","12"],"answer_index":2},
    {"id":"RSN-044","section":"Reasoning","question":"If A = 1 and Z = 26, value of CODE =","options":["26","27","28","30"],"answer_index":1},
    {"id":"RSN-045","section":"Reasoning","question":"If 5=12, 6=20, 7=30, then 8 =","options":["40","42","44","45"],"answer_index":1},
    {"id":"RSN-046","section":"Reasoning","question":"If it rains, match is cancelled. It did not rain. Match is","options":["Played","Cancelled","May or may not be cancelled","None"],"answer_index":2},
    {"id":"RSN-047","section":"Reasoning","question":"Six children share 10 toffees, each ≥1. Number of ways","options":["4","5","6","7"],"answer_index":1},
    {"id":"RSN-048","section":"Reasoning","question":"Facing north, turn right, then left, then left. Now facing","options":["West","South","East","North"],"answer_index":0},
    {"id":"RSN-049","section":"Reasoning","question":"All A are B, No B is C → No A is C","options":["True","False","Cannot say","None"],"answer_index":0},
    {"id":"RSN-050","section":"Reasoning","question":"Odd pair: 2:8, 3:27, 4:64, 5:100","options":["2:8","3:27","4:64","5:100"],"answer_index":3},
]

CODING: List[Dict[str, Any]] = [
    {"id":"COD-001","section":"Coding","question":"In C, which symbol ends a statement?","options":[".",";",",",":"],"answer_index":1},
    {"id":"COD-002","section":"Coding","question":"In Python, which function prints output?","options":["output()","echo()","print()","display()"],"answer_index":2},
    {"id":"COD-003","section":"Coding","question":"In Java, which keyword defines a class?","options":["def","class","structure","define"],"answer_index":1},
    {"id":"COD-004","section":"Coding","question":"C data type for decimal numbers?","options":["int","float","char","double"],"answer_index":1},
    {"id":"COD-005","section":"Coding","question":"Python is a ______ typed language.","options":["Dynamically","Statically","Manually","Structurally"],"answer_index":0},
    {"id":"COD-006","section":"Coding","question":"Output of printf(\"%d\", 5 + 3 * 2);","options":["10","11","12","13"],"answer_index":1},
    {"id":"COD-007","section":"Coding","question":"In Java, which method runs the program?","options":["start()","begin()","main()","run()"],"answer_index":2},
    {"id":"COD-008","section":"Coding","question":"Symbol for comments in Python","options":["//","/*","#","--"],"answer_index":2},
    {"id":"COD-009","section":"Coding","question":"What will 5 // 2 give in Python?","options":["2","2.5","3","3.5"],"answer_index":0},
    {"id":"COD-010","section":"Coding","question":"In C, how to read an integer?","options":["read(\"%d\", x);","scan(\"%d\", x);","scanf(\"%d\", &x);","input(x);"],"answer_index":2},
    {"id":"COD-011","section":"Coding","question":"In Java, integer division 9/2 =","options":["4","4.5","5","6"],"answer_index":0},
    {"id":"COD-012","section":"Coding","question":"In Python, len(\"code\") =","options":["3","4","5","6"],"answer_index":1},
    {"id":"COD-013","section":"Coding","question":"In C, keyword to exit loop","options":["continue","return","break","stop"],"answer_index":2},
    {"id":"COD-014","section":"Coding","question":"In Java, “==” checks","options":["Assignment","Comparison","Reference","None"],"answer_index":1},
    {"id":"COD-015","section":"Coding","question":"In Python, list index starts from","options":["0","1","-1","2"],"answer_index":0},
    {"id":"COD-016","section":"Coding","question":"C: int a=5; printf(\"%d\", ++a);","options":["4","5","6","7"],"answer_index":2},
    {"id":"COD-017","section":"Coding","question":"Java: int x=5; System.out.println(x++); prints","options":["4","5","6","7"],"answer_index":1},
    {"id":"COD-018","section":"Coding","question":"Python: for i in range(3): print(i) outputs","options":["1 2 3","0 1 2","0 1 2 3","1 2"],"answer_index":1},
    {"id":"COD-019","section":"Coding","question":"Error in: for(i=0;i<5;i++); printf(\"%d\",i);","options":["Extra semicolon","Wrong variable","Wrong syntax","Missing bracket"],"answer_index":0},
    {"id":"COD-020","section":"Coding","question":"Java keyword for inheritance","options":["implements","inherits","extends","super"],"answer_index":2},
    {"id":"COD-021","section":"Coding","question":"Python: def add(a,b): return a+b; add(2,3) =","options":["2","3","4","5"],"answer_index":3},
    {"id":"COD-022","section":"Coding","question":"In C, string ends with","options":["' '","'\\n'","'\\0'","#"],"answer_index":2},
    {"id":"COD-023","section":"Coding","question":"Java type for single character","options":["string","char","character","text"],"answer_index":1},
    {"id":"COD-024","section":"Coding","question":"Python loop continues until condition false","options":["repeat","while","for","do"],"answer_index":1},
    {"id":"COD-025","section":"Coding","question":"C: sizeof(int) usually","options":["2 bytes","4 bytes","6 bytes","8 bytes"],"answer_index":1},
    {"id":"COD-026","section":"Coding","question":"Java: int a=10,b=20; System.out.println(a>b);","options":["true","false","1","0"],"answer_index":1},
    {"id":"COD-027","section":"Coding","question":"Python: a=[1,2,3]; a.append(4); print(a)","options":["[1,2,3]","[1,2,3,4]","[4,3,2,1]","[2,3,4]"],"answer_index":1},
    {"id":"COD-028","section":"Coding","question":"C loop runs 5 times for(i=0;i<5;i++). Last i value","options":["4","5","6","7"],"answer_index":1},
    {"id":"COD-029","section":"Coding","question":"Java keyword for constant","options":["const","static","final","constant"],"answer_index":2},
    {"id":"COD-030","section":"Coding","question":"Python operator for exponent","options":["^","**","*","^^"],"answer_index":1},
    {"id":"COD-031","section":"Coding","question":"C: int x=5; x+=3; printf(\"%d\",x);","options":["5","7","8","9"],"answer_index":2},
    {"id":"COD-032","section":"Coding","question":"Java loop executes at least once","options":["for","while","do-while","until"],"answer_index":2},
    {"id":"COD-033","section":"Coding","question":"Python: bool(0) returns","options":["True","False","Error","None"],"answer_index":1},
    {"id":"COD-034","section":"Coding","question":"C: purpose of return 0 in main()","options":["End of loop","End of program","Successful execution","Error"],"answer_index":2},
    {"id":"COD-035","section":"Coding","question":"Java array index starts at","options":["0","1","-1","2"],"answer_index":0},
    {"id":"COD-036","section":"Coding","question":"C: int a=5; printf(\"%d\", a++ + ++a);","options":["10","11","12","Undefined behavior"],"answer_index":3},
    {"id":"COD-037","section":"Coding","question":"OOP concept via method overriding","options":["Inheritance","Encapsulation","Polymorphism","Abstraction"],"answer_index":2},
    {"id":"COD-038","section":"Coding","question":"Python: x=[]; def f(): x.append(1); f(); print(x)","options":["[]","[1]","[1,1]","Error"],"answer_index":1},
    {"id":"COD-039","section":"Coding","question":"In C, recursive functions call","options":["Another function","Themselves","main()","None"],"answer_index":1},
    {"id":"COD-040","section":"Coding","question":"Java access specifier restricting to same class","options":["public","private","protected","static"],"answer_index":1},
    {"id":"COD-041","section":"Coding","question":"Lambda functions in Python are","options":["Named","Anonymous","Recursive","Loops"],"answer_index":1},
    {"id":"COD-042","section":"Coding","question":"Pointer in C holds","options":["Value","Address","Character","Name"],"answer_index":1},
    {"id":"COD-043","section":"Coding","question":"Java abstract class can have","options":["Only abstract methods","Only concrete methods","Both","None"],"answer_index":2},
    {"id":"COD-044","section":"Coding","question":"Python: def f(x=[]): x.append(1); return x; print(f(), f())","options":["[1] [1]","[1] [1,1]","[1,1] [1,1]","Error"],"answer_index":1},
    {"id":"COD-045","section":"Coding","question":"C file opening mode for writing only","options":["r","w","a","rw"],"answer_index":1},
    {"id":"COD-046","section":"Coding","question":"Java exception handling uses","options":["try-catch","throw-catch","error-handling","guard"],"answer_index":0},
    {"id":"COD-047","section":"Coding","question":"Python module for random numbers","options":["randint","random","randomize","rnd"],"answer_index":1},
    {"id":"COD-048","section":"Coding","question":"C dynamic memory allocation function","options":["alloc()","malloc()","create()","calloc()"],"answer_index":1},
    {"id":"COD-049","section":"Coding","question":"In Java, interface is used for","options":["Abstraction","Overloading","Polymorphism","None"],"answer_index":0},
    {"id":"COD-050","section":"Coding","question":"Python: a=(1,2,3); a[0]=5","options":["[5,2,3]","(5,2,3)","Error","None"],"answer_index":2},
]

QUOTA = {"Aptitude": 8, "Reasoning": 7, "Coding": 15}

# ---------------------- Templates ----------------------
PHOTO_BG = "https://img.pikbest.com/origin/09/28/35/25KpIkbEsTf4R.jpg!w700wp"  # Background image URL or path

BASE_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body{margin:0;background:url('{{ photo_bg }}') center/cover fixed no-repeat;color:#f9fafb;font-family:"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
      body::after{content:"";position:fixed;inset:0;background:radial-gradient(60% 80% at 20% 10%, rgba(3,7,18,.45), transparent 60%),radial-gradient(80% 80% at 120% 120%, rgba(2,6,23,.45), transparent 60%),rgba(2,6,23,.35);pointer-events:none;z-index:0;}
      .container{max-width:980px;padding-inline:clamp(12px,3vw,24px);position:relative;z-index:1}
      h2{color:#fff;text-shadow:0 0 8px rgba(255,255,255,.55)}
      .exam-header{position:sticky;top:0;z-index:1000;display:flex;align-items:center;justify-content:space-between;padding:8px 16px;background:rgba(15,23,42,.28);backdrop-filter:blur(12px);border-bottom:1px solid rgba(147,197,253,.35);box-shadow:0 8px 30px rgba(0,0,0,.35);min-height:52px;}
      .exam-title{font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:#eaf2ff;text-shadow:0 0 10px rgba(147,197,253,.75),0 0 22px rgba(37,99,235,.45)}
      input{background:rgba(3,7,18,.35);color:#fff;border:1px solid rgba(147,197,253,.45);backdrop-filter:blur(6px);min-height:44px}
      input:focus{border-color:#93c5fd;box-shadow:0 0 0 3px rgba(96,165,250,.35);outline:none}

      /* ====== MCQ option (like your screenshots) ====== */
      .mcq-option{
        position:relative;
        display:flex; align-items:center; gap:.9rem;
        border:1px solid rgba(203,213,225,.75); /* slate-300 */
        background:rgba(2,6,23,.12);
        color:#e5e7eb; /* text-slate-200 */
        padding:.9rem 1rem; margin:.65rem 0;
        border-radius:.8rem;
        transition:background .15s, border-color .15s, box-shadow .15s, transform .04s;
        cursor:pointer; user-select:none;
      }
      .mcq-option:hover{ background:rgba(2,6,23,.20); border-color:rgba(147,197,253,.65); }
      .mcq-option:focus-within{ box-shadow:0 0 0 3px rgba(96,165,250,.35); border-color:#93c5fd; }

      .mcq-option input{
        position:absolute; inset:0; opacity:0; margin:0; cursor:pointer;
      }

      .mcq-badge{
        min-width:34px; height:34px; border-radius:50%;
        display:grid; place-items:center;
        font-weight:700;
        border:2px solid rgba(148,163,184,.9); /* slate-400 */
        color:#e5e7eb; background:transparent;
        transition:all .12s;
      }
      .mcq-text{ flex:1; line-height:1.35; }

      /* selected state */
      .mcq-option input:checked ~ .mcq-badge{
        background:#2563eb; color:#fff; border-color:#93c5fd;
        box-shadow:0 0 0 4px rgba(59,130,246,.35);
      }
      .mcq-option input:checked ~ .mcq-text{
        color:#fff;
      }
      .mcq-option input:checked ~ .mcq-badge + .mcq-text,
      .mcq-option input:checked ~ .mcq-text + .mcq-extra{
        /* keep spacing consistent if extra spans get added later */
      }
      .mcq-option input:checked ~ .mcq-text,
      .mcq-option:has(input:checked){
        background:rgba(59,130,246,.18);
        border-color:#93c5fd;
      }
      /* browsers without :has still get background via the rule above through sibling updates */

      #timer{
        background:rgba(11,19,40,.40);
        border:1px solid rgba(147,197,253,.55);
        color:#eaf2ff;font-weight:bold;padding:.3em .7em;border-radius:.5rem;
        box-shadow:0 0 10px rgba(147,197,253,.45);text-shadow:0 0 8px rgba(255,255,255,.6)
      }

      .floating-logo{position:fixed;right:20px;bottom:20px;width:76px;height:76px;border-radius:50%;display:grid;place-items:center;z-index:999;background:rgba(255,255,255,0.02);box-shadow:0 0 0 4px rgba(255,255,255,0.08) inset,0 0 24px rgba(59,130,246,0.45),0 0 48px rgba(59,130,246,0.35),0 0 84px rgba(59,130,246,0.25);backdrop-filter:blur(6px);animation:pulse 3.2s ease-in-out infinite}
      .floating-logo img{width:62px;height:62px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,.75);box-shadow:0 0 10px rgba(255,255,255,.25)}
      @keyframes pulse{0%,100%{box-shadow:0 0 0 4px rgba(255,255,255,.08) inset,0 0 22px rgba(59,130,246,.45),0 0 48px rgba(59,130,246,.30),0 0 72px rgba(59,130,246,.20)}50%{box-shadow:0 0 0 4px rgba(255,255,255,.08) inset,0 0 30px rgba(59,130,246,.65),0 0 60px rgba(59,130,246,.42),0 0 96px rgba(59,130,246,.30)}}
      @media (max-width:420px){.floating-logo{display:none}}
      ::selection{background:rgba(59,130,246,.25);}
    </style>
  </head>
  <body>
    <header class="exam-header">
      <div class="exam-title">CODING CLUB • ONLINE TEST (2nd Year)</div>
      <div id="topTimer" class="badge" style="background:transparent;border:0;">
        {% if show_timer %}<span id="mmTop">--</span>:<span id="ssTop">--</span>{% endif %}
      </div>
    </header>

    <div class="floating-logo" aria-hidden="true" title="Coding Club">
      <img src="{{ url_for('logo_img') }}" alt="Logo">
    </div>

    <div class="container py-4">
      <h2 class="mb-3">{{ header }}</h2>
      {% with messages = get_flashed_messages() %}
        {% if messages %} <div class="alert alert-warning">{{ messages[0] }}</div> {% endif %}
      {% endwith %}
      {{ body|safe }}
    </div>
  </body>
</html>
"""

# Landing with two buttons
LANDING_HTML = """
<div class="row justify-content-center">
  <div class="col-md-8">
    <div class="d-grid gap-3">
      <a class="btn btn-primary btn-lg" href="{{ url_for('admin_login') }}">Admin</a>
      <a class="btn btn-outline-light btn-lg" href="{{ url_for('student_entry') }}">Student</a>
    </div>
  </div>
</div>
"""

# Student form
FORM_HTML = """
<div class="row">
  <div class="col-lg-7">
    <form class="p-0" method="post" action="{{ url_for('start_quiz') }}">
      <div class="mb-3">
        <label class="form-label">Roll Number</label>
        <input required type="text" name="roll" class="form-control" maxlength="40"/>
      </div>
      <div class="mb-3">
        <label class="form-label">Name</label>
        <input required type="text" name="name" class="form-control" maxlength="60"/>
      </div>
      <button class="btn btn-primary" type="submit">Start Quiz</button>
      <a class="btn btn-link text-light" href="{{ url_for('home') }}">Back</a>
    </form>
  </div>
</div>
"""

# ======= QUIZ (60s/question; strict) — NOTE: we DO NOT expose correct indices in DOM =========
QUIZ_HTML = """
<form id="jeeForm" method="post" action="{{ url_for('submit_quiz') }}" class="simple-quiz" autocomplete="off">
  <input type="hidden" name="forfeit" id="forfeitField" value="">
  <div class="d-flex justify-content-end mb-2">
    <div id="timer">Time Left: <span id="mm">01</span>:<span id="ss">00</span></div>
  </div>

  {% for q in questions %}
    <div class="qwrap" id="qwrap_{{ loop.index0 }}" data-qindex="{{ loop.index0 }}" style="display:none">
      <div class="qtext">Q{{ loop.index }}. {{ q.question }}</div>
      {% for opt in q.shuffled_options %}
        <label class="mcq-option" for="{{ q.id }}_{{ loop.index0 }}">
          <input type="radio" name="ans_{{ q.id }}" id="{{ q.id }}_{{ loop.index0 }}" value="{{ loop.index0 }}">
          <span class="mcq-badge">{{ 'ABCD'[loop.index0] }}</span>
          <span class="mcq-text">{{ opt }}</span>
        </label>
      {% endfor %}
    </div>
  {% endfor %}

  <div class="d-flex justify-content-end mt-3">
    <button type="button" class="btn btn-primary" id="btnNext">Save & Next</button>
  </div>
</form>

<script>
(function(){
  // Fullscreen
  async function enterFullscreen(){
    try{
      if(document.fullscreenElement) return;
      const el = document.documentElement;
      if(el.requestFullscreen){ await el.requestFullscreen(); }
      else if(el.webkitRequestFullscreen){ await el.webkitRequestFullscreen(); }
      else if(el.msRequestFullscreen){ await el.msRequestFullscreen(); }
    }catch(e){}
  }
  document.addEventListener('DOMContentLoaded', enterFullscreen, {once:true});
  const armFS = ()=>{ enterFullscreen(); document.removeEventListener('click', armFS); document.removeEventListener('keydown', armFS); };
  document.addEventListener('click', armFS); document.addEventListener('keydown', armFS);

  // Strict anti-switch
  const form = document.getElementById('jeeForm');
  const forfeitField = document.getElementById('forfeitField');
  function forfeit(reason){ try{ forfeitField.value = reason || 'violation'; }catch(e){} try{ form.submit(); }catch(e){} }
  document.addEventListener('visibilitychange', ()=>{ if(document.hidden){ forfeit('tab_switch'); } });
  window.addEventListener('blur', ()=>{ setTimeout(()=>{ if(!document.hasFocus()){ forfeit('window_blur'); } }, 100); });
  document.addEventListener('fullscreenchange', ()=>{ if(!document.fullscreenElement){ forfeit('exit_fullscreen'); } });
  document.addEventListener('contextmenu', e => e.preventDefault());
  ['copy','cut','paste'].forEach(evt => document.addEventListener(evt, e=>e.preventDefault()));
  document.addEventListener('keydown', function(e){
    const k = e.key.toLowerCase();
    if ((e.ctrlKey && ['p','s','c','x','a','u','l'].includes(k)) || e.key === 'F11' || e.key === 'Escape'){
      e.preventDefault(); e.stopPropagation();
    }
  }, true);

  // Per-question timer
  const PER_Q_SECONDS = 60;
  let current = 0;
  const wraps = Array.from(document.querySelectorAll('.qwrap'));
  const totalQ = wraps.length;
  const btnNext = document.getElementById('btnNext');

  const mm = document.getElementById('mm');
  const ss = document.getElementById('ss');
  const mmTop = document.getElementById('mmTop');
  const ssTop = document.getElementById('ssTop');
  let left = PER_Q_SECONDS;
  let tHandle = null;

  function updateTimer(){
    const m = Math.floor(left/60), s = left%60;
    const M = String(m).padStart(2,'0'), S = String(s).padStart(2,'0');
    if(mm) mm.textContent = M; if(ss) ss.textContent = S;
    if(mmTop) mmTop.textContent = M; if(ssTop) ssTop.textContent = S;
  }
  function stopTimer(){ if(tHandle){ clearInterval(tHandle); tHandle = null; } }
  function startTimer(){
    stopTimer(); left = PER_Q_SECONDS; updateTimer();
    tHandle = setInterval(()=>{ left--; updateTimer(); if(left<=0){ nextQuestion(); } }, 1000);
  }
  function show(i){
    wraps.forEach((w,idx)=> w.style.display = (idx===i? 'block':'none'));
    current = i;
    btnNext.textContent = (current===totalQ-1? "Finish" : "Save & Next");
    startTimer();
    wraps[current].scrollIntoView({ behavior:'smooth', block:'start' });
  }
  function nextQuestion(){
    stopTimer();
    if(current < totalQ-1){ show(current+1); }
    else { form.submit(); }
  }
  btnNext.addEventListener('click', nextQuestion);

  if(totalQ){ show(0); }
})();
</script>
"""

THANK_YOU_HTML = """
<div class="d-flex align-items-center justify-content-center" style="min-height:50vh;">
  <div class="text-center">
    <h2 style="text-shadow:0 0 12px rgba(255,255,255,.5)">Thank you for your attention!</h2>
    <p class="mt-2">{{ quote }}</p>
    <p class="mt-3"><em>Redirecting to the start page in 5 seconds…</em></p>
  </div>
</div>
<script> setTimeout(()=>{ window.location.href = "{{ url_for('home') }}"; }, 5000); </script>
"""

# ---------------------- Excel helpers ----------------------
def _ensure_workbook():
    if not os.path.exists(EXCEL_PATH):
        with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
            pd.DataFrame(columns=[
                "timestamp","rollnumber","name","year","score","total","attempted","attempt_ids","forfeit_reason"
            ]).to_excel(writer, sheet_name=STUDENTS_SHEET, index=False)
            pd.DataFrame(columns=[
                "attempt_id","rollnumber","name","year","q_no","q_id","section","question",
                "options_json","correct_idx","user_choice","is_correct"
            ]).to_excel(writer, sheet_name=ATTEMPTS_SHEET, index=False)

def read_sheet(sheet: str) -> pd.DataFrame:
    _ensure_workbook()
    try:
        return pd.read_excel(EXCEL_PATH, sheet_name=sheet)
    except Exception:
        return pd.DataFrame()

def write_sheet(sheet: str, df: pd.DataFrame):
    _ensure_workbook()
    with XL_LOCK:
        all_students = read_sheet(STUDENTS_SHEET)
        all_attempts = read_sheet(ATTEMPTS_SHEET)
        if sheet == STUDENTS_SHEET:
            all_students = df
        elif sheet == ATTEMPTS_SHEET:
            all_attempts = df
        with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
            all_students.to_excel(writer, sheet_name=STUDENTS_SHEET, index=False)
            all_attempts.to_excel(writer, sheet_name=ATTEMPTS_SHEET, index=False)

def has_attempted(roll: str) -> bool:
    df = read_sheet(STUDENTS_SHEET)
    if df.empty: return False
    match = df[df["rollnumber"].astype(str).str.lower() == roll.lower()]
    if match.empty: return False
    attempted = match.iloc[-1].get("attempted", 0)
    return bool(int(attempted)) if pd.notna(attempted) else False

def save_student_start(roll: str, name: str, year: int = 2) -> None:
    students = read_sheet(STUDENTS_SHEET)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {"timestamp": ts, "rollnumber": roll.strip(), "name": name.strip(), "year": int(year),
               "score": None, "total": None, "attempted": 0, "attempt_ids": None, "forfeit_reason": None}
    students = pd.concat([students, pd.DataFrame([new_row])], ignore_index=True)
    write_sheet(STUDENTS_SHEET, students)

def finalize_student_attempt(roll: str, score: int, total: int, attempt_id: str, forfeit_reason: str | None):
    students = read_sheet(STUDENTS_SHEET)
    if students.empty: return
    mask = students["rollnumber"].astype(str).str.lower() == roll.lower()
    idxs = students[mask].index.tolist()
    if not idxs: return
    last_idx = idxs[-1]
    students.at[last_idx, "score"] = score
    students.at[last_idx, "total"] = total
    students.at[last_idx, "attempted"] = 1
    students.at[last_idx, "forfeit_reason"] = forfeit_reason
    prev = students.at[last_idx, "attempt_ids"]
    new_list = [] if pd.isna(prev) or not prev else str(prev).split(";")
    new_list.append(attempt_id)
    students.at[last_idx, "attempt_ids"] = ";".join(new_list)
    write_sheet(STUDENTS_SHEET, students)

def record_attempt_rows(attempt_id: str, roll: str, name: str, year: int, review_rows: List[Dict[str, Any]]):
    attempts = read_sheet(ATTEMPTS_SHEET)
    rows = []
    for i, r in enumerate(review_rows, start=1):
        rows.append({
            "attempt_id": attempt_id, "rollnumber": roll, "name": name, "year": year,
            "q_no": i, "q_id": r["id"], "section": r["section"], "question": r["question"],
            "options_json": json.dumps(r["options"], ensure_ascii=False),
            "correct_idx": r["correct_idx"], "user_choice": r["user_choice"],
            "is_correct": int(bool(r["is_correct"])) if r["user_choice"] is not None else 0,
        })
    attempts = pd.concat([attempts, pd.DataFrame(rows)], ignore_index=True)
    write_sheet(ATTEMPTS_SHEET, attempts)

# ---------------------- Selection helper ----------------------
def pick_random_mix() -> List[Dict[str, Any]]:
    blocks = {
        "Aptitude": random.sample(APTITUDE, QUOTA["Aptitude"]),
        "Reasoning": random.sample(REASONING, QUOTA["Reasoning"]),
        "Coding":   random.sample(CODING,   QUOTA["Coding"]),
    }
    chosen = blocks["Aptitude"] + blocks["Reasoning"] + blocks["Coding"]
    prepped = []
    for q in chosen:
        idxs = list(range(len(q["options"])))
        random.shuffle(idxs)
        shuffled = [q["options"][i] for i in idxs]
        correct_after = idxs.index(q["answer_index"])
        prepped.append({
            "id": q["id"], "section": q["section"], "question": q["question"],
            "options": q["options"],
            "shuffled_options": shuffled,
            "correct_index_after_shuffle": correct_after
        })
    return prepped

# ---------------------- Admin auth helper ----------------------
def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please log in as admin first.")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapper

# ---------------------- Routes ----------------------
@app.route("/")
def home():
    body = render_template_string(LANDING_HTML)
    return render_template_string(BASE_HTML, title="Welcome", header="Choose Portal", body=body, photo_bg=PHOTO_BG, show_timer=False)

@app.route("/student")
def student_entry():
    body = render_template_string(FORM_HTML)
    return render_template_string(BASE_HTML, title="Student", header="Enter Your Details", body=body, photo_bg=PHOTO_BG, show_timer=False)

@app.route("/start", methods=["POST"])
def start_quiz():
    roll = request.form.get("roll","").strip()
    name = request.form.get("name","").strip()
    if not roll or not name:
        flash("Please fill both Roll and Name."); return redirect(url_for("student_entry"))
    if has_attempted(roll):
        flash("You have already attempted the quiz. Only one attempt is allowed per roll number.")
        return redirect(url_for("student_entry"))

    save_student_start(roll, name, 2)
    session["student"] = {"roll": roll, "name": name, "year": 2}

    questions = pick_random_mix()
    session["quiz"] = questions
    body = render_template_string(QUIZ_HTML, student=session["student"], questions=questions)
    return render_template_string(BASE_HTML, title="Quiz", header="Answer the Questions", body=body, photo_bg=PHOTO_BG, show_timer=True)

@app.route("/submit", methods=["POST"])
def submit_quiz():
    student = session.get("student")
    questions = session.get("quiz", [])
    if not student or not questions:
        flash("Session expired or quiz not started."); return redirect(url_for("student_entry"))
    session["quiz"] = []  # prevent re-submit

    forfeit_reason = request.form.get("forfeit") or ""
    score = 0
    review = []

    if forfeit_reason:
        for q in questions:
            review.append({
                "id": q["id"], "section": q["section"], "question": q["question"],
                "options": q["shuffled_options"], "correct_idx": q["correct_index_after_shuffle"],
                "user_choice": None, "is_correct": False
            })
    else:
        for q in questions:
            correct_idx = q["correct_index_after_shuffle"]
            user_val = request.form.get(f"ans_{q['id']}")
            user_choice = int(user_val) if user_val is not None else None
            is_correct = (user_choice == correct_idx)
            if is_correct: score += 1
            review.append({
                "id": q["id"], "section": q["section"], "question": q["question"],
                "options": q["shuffled_options"], "correct_idx": correct_idx,
                "user_choice": user_choice, "is_correct": is_correct
            })

    total = len(questions)
    attempt_id = f"{student['roll']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    record_attempt_rows(attempt_id, student["roll"], student["name"], 2, review)
    finalize_student_attempt(student["roll"], 0 if forfeit_reason else score, total, attempt_id, forfeit_reason or None)

    quote = random.choice([
        "Thank you for your attention and effort!",
        "Great focus—thanks for taking the quiz!",
        "We appreciate your participation!",
        "Thanks for giving it your best shot!"
    ])
    body = render_template_string(THANK_YOU_HTML, quote=quote)
    return render_template_string(BASE_HTML, title="Done", header="Submission Received", body=body, photo_bg=PHOTO_BG, show_timer=False)

# ---------------------- Admin: login/logout/dashboard ----------------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user = request.form.get("username", "").strip()
        pw   = request.form.get("password", "").strip()
        if user == ADMIN_USER and pw == ADMIN_PASS:
            session["is_admin"] = True
            flash("Logged in as admin.")
            return redirect(url_for("admin_home"))
        flash("Invalid credentials.")
    login_form = """
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card" style="background:rgba(11,19,40,.40); border:1px solid rgba(147,197,253,.35);">
          <div class="card-body">
            <h5 class="card-title text-white mb-3">Admin Login</h5>
            <form method="post" action="{{ url_for('admin_login') }}">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input type="text" name="username" class="form-control" required autofocus>
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" name="password" class="form-control" required>
              </div>
              <button class="btn btn-primary" type="submit">Login</button>
              <a class="btn btn-link text-light" href="{{ url_for('home') }}">Back</a>
            </form>
          </div>
        </div>
      </div>
    </div>
    """
    return render_template_string(BASE_HTML, title="Admin Login", header="Admin — Login", body=render_template_string(login_form), photo_bg=PHOTO_BG, show_timer=False)

@app.route("/admin-logout")
@require_admin
def admin_logout():
    session.pop("is_admin", None)
    flash("Logged out.")
    return redirect(url_for("home"))

@app.route("/admin")
@require_admin
def admin_home():
    students = read_sheet(STUDENTS_SHEET)
    rows = []
    if not students.empty:
        students = students.fillna("")
        for _, s in students[::-1].iterrows():
            score = s.get("score","")
            total = s.get("total","")
            pct = ""
            try:
                if str(score) != "" and str(total) != "" and int(total) > 0:
                    pct = f"{(int(score)/int(total))*100:.1f}%"
            except Exception:
                pct = ""
            rows.append({
                "timestamp": s.get("timestamp",""),
                "rollnumber": str(s.get("rollnumber","")),
                "name": s.get("name",""),
                "year": s.get("year",""),
                "score": score, "total": total, "percent": pct,
                "attempted": s.get("attempted",""),
                "forfeit_reason": s.get("forfeit_reason",""),
            })

    table_html = """
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div><a class="btn btn-outline-light btn-sm" href="{{ url_for('download_excel') }}">Download Excel</a></div>
      <div><a class="btn btn-outline-danger btn-sm" href="{{ url_for('admin_logout') }}">Logout</a></div>
    </div>

    <div class="table-responsive">
      <table class="table table-dark table-striped table-hover align-middle">
        <thead>
          <tr>
            <th>Timestamp</th><th>Roll</th><th>Name</th><th>Year</th>
            <th>Score</th><th>Total</th><th>%</th><th>Attempted</th><th>Forfeit</th>
          </tr>
        </thead>
        <tbody>
        {% for r in rows %}
          <tr>
            <td>{{ r.timestamp }}</td>
            <td>{{ r.rollnumber }}</td>
            <td>{{ r.name }}</td>
            <td>{{ r.year }}</td>
            <td>{{ r.score }}</td>
            <td>{{ r.total }}</td>
            <td>{{ r.percent }}</td>
            <td>{{ r.attempted }}</td>
            <td>{{ r.forfeit_reason }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>
    """
    body = render_template_string(table_html, rows=rows)
    return render_template_string(BASE_HTML, title="Admin", header="Owner Dashboard", body=body, photo_bg=PHOTO_BG, show_timer=False)

@app.route("/download-excel")
@require_admin
def download_excel():
    if not os.path.exists(EXCEL_PATH):
        flash("No Excel file found yet.")
        return redirect(url_for("admin_home"))
    return send_file(EXCEL_PATH, as_attachment=True, download_name="students_results.xlsx")

# ===================== run =====================
if __name__ == "__main__":
    app.run(debug=True)
