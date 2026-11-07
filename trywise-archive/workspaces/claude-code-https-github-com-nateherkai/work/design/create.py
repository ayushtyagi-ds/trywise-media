import sys, os
sys.path.insert(0,'work/pylibs')
from PIL import Image,ImageDraw,ImageFont
P='outputs/trywise-sample/'
W,H=1080,1350
navy='#121a36'; muted='#687289'; paper='#f6f4ec'; lime='#d6f25b'; coral='#ff805f'; white='#ffffff'; line='#dadddf'; lavender='#bcb2fd'
B='/System/Library/Fonts/Supplemental/Arial Bold.ttf'; R='/System/Library/Fonts/Supplemental/Arial.ttf'; I='/System/Library/Fonts/Supplemental/Georgia Italic.ttf'
F=lambda n,b=False:ImageFont.truetype(B if b else R,n)
def text(d,xy,s,size,color=navy,b=False,spacing=8): d.multiline_text(xy,s,font=F(size,b),fill=color,spacing=spacing,stroke_width=0)
def rect(d,box,fill,r=24,outline=None,w=1): d.rounded_rectangle(box,r,fill=fill,outline=outline,width=w)
def base(n,tag,background=paper):
 im=Image.new('RGB',(W,H),background); d=ImageDraw.Draw(im)
 color=paper if background==navy else navy
 text(d,(66,58),'TRYWISE',30,color,True); text(d,(224,58),'AI',30,coral,True)
 text(d,(756,63),tag,22,color,True)
 d.line((66,115,1014,115),fill='#4d5570' if background==navy else '#d4d9d7',width=2)
 d.line((66,1260,1014,1260),fill='#4d5570' if background==navy else '#d4d9d7',width=2)
 text(d,(66,1280),'PRACTICAL AI  /  MEETING NOTES',20,color,True); text(d,(952,1277),f'0{n}',24,color,True)
 return im,d
def save(im,n): im.save(P+f'{n:02}.png', optimize=True)
# cover
im,d=base(1,'THE AI PLAYBOOK',navy)
text(d,(65,168),'TURN MESSY',75,paper,True);text(d,(65,257),'MEETING NOTES',75,paper,True)
text(d,(65,355),'INTO',75,paper,True);text(d,(65,445),'ACTION ITEMS.',75,lime,True)
text(d,(68,565),'One simple prompt. A clearer next step.',34,'#bec5d8')
# original miniature graphical paper sheet and checklist
rect(d,(92,680,765,1122),'#e9e8df',27); rect(d,(127,724,730,1081),white,14)
text(d,(165,754),'MEETING NOTES',24,muted,True)
for y,width in [(824,480),(872,405),(920,455)]: d.rounded_rectangle((165,y,165+width,y+12),6,fill='#d9dee4')
rect(d,(500,847,967,1168),lime,24)
text(d,(535,877),'ACTION LIST',26,navy,True)
for y,label in [(935,'Task'),(1000,'Owner'),(1065,'Due date')]:
 rect(d,(538,y,567,y+29),navy,7); text(d,(589,y-5),label,31,navy,True)
text(d,(809,1220),'SWIPE  →',22,paper,True)
save(im,1)
# messy notes
im,d=base(2,'01 / THE INPUT')
text(d,(67,159),'Start with notes,',61,navy,True);text(d,(67,232),'not a perfect brief.',61,navy,True)
text(d,(70,329),'Example: a team meeting about a launch.',31,muted)
rect(d,(69,417,1011,925),white,22,outline=line,w=2)
rect(d,(101,452,300,497),navy,10);text(d,(121,461),'SAMPLE NOTES',20,white,True)
text(d,(116,560),'• Priya will send the draft Friday.\n\n• The team needs to review the\n  budget. No owner chosen yet.\n\n• Check launch timeline next week.',36,navy,False,8)
rect(d,(70,1005,1010,1163),'#e5e8fd',20)
text(d,(100,1035),'THE PROBLEM',21,'#6258a4',True);text(d,(100,1074),'Tasks, owners and dates are mixed together.',30,navy,True)
save(im,2)
# prompt
im,d=base(3,'02 / COPY THE PROMPT',navy)
text(d,(66,160),'Give the AI',63,paper,True);text(d,(66,237),'clear rules.',63,lime,True)
text(d,(68,334),'Paste your notes after this prompt:',32,'#c4ccdd')
rect(d,(68,415,1012,1003),'#f7f5ec',25)
text(d,(105,454),'PROMPT',23,'#807a73',True)
text(d,(105,515),'Turn these notes into a table with:\n\nTask | Owner | Due date\n\nUse only information in the notes.\nIf an owner or date is missing,\nwrite “Not specified.”\nDo not invent details.\n\nNotes: [paste here]',35,navy,False,5)
text(d,(69,1070),'TIP  /  Use fictional or non-sensitive notes.',27,'#ced4e0')
save(im,3)
# example
im,d=base(4,'03 / THE OUTPUT')
text(d,(67,158),'A useful result',63,navy,True);text(d,(67,235),'looks like this.',63,navy,True)
text(d,(70,331),'Illustrative example based on slide 2.',30,muted)
rect(d,(67,416,1013,967),white,20,outline=line,w=2)
rect(d,(67,416,1013,493),navy,18)
text(d,(94,438),'TASK',22,white,True);text(d,(579,438),'OWNER',22,white,True);text(d,(824,438),'DUE',22,white,True)
for y in [642,796]:d.line((93,y,989,y),fill=line,width=2)
for y,task,owner,due in [(528,'Send draft','Priya','Friday'),(684,'Review budget','Not specified','Not specified'),(837,'Check launch\ntimeline','Not specified','Next week')]:
 text(d,(94,y),task,29,navy,True);text(d,(579,y),owner,24,navy);text(d,(823,y),due,24,navy)
rect(d,(70,1031,1010,1165),'#e9edcf',20);text(d,(101,1063),'Missing details stay missing.',31,navy,True)
save(im,4)
# close
im,d=base(5,'04 / FINAL CHECK')
text(d,(68,158),'Before you',67,navy,True);text(d,(68,240),'share the list...',67,navy,True)
for y,num,title,sub,col in [(410,'01','Check the owners','Did the notes actually name them?',lime),(620,'02','Confirm the dates','“Friday” may need a calendar date.',lavender),(830,'03','Ask for missing details','Don’t turn a guess into a deadline.',coral)]:
 rect(d,(70,y,170,y+100),col,22);text(d,(92,y+26),num,37,navy,True)
 text(d,(202,y+4),title,40,navy,True);text(d,(202,y+58),sub,29,muted)
rect(d,(70,1061,1010,1172),navy,20);text(d,(104,1095),'SAVE FOR YOUR NEXT MEETING',27,white,True)
save(im,5)
