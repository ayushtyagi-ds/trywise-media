from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import textwrap
out=Path(__file__).parent
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
regular='/System/Library/Fonts/Supplemental/Arial.ttf'
def f(n,b=True): return ImageFont.truetype(bold if b else regular,n)
white=(246,246,246); blue=(106,194,255); soft=(180,191,202)
art=ImageOps.fit(Image.open('/Users/phoenix/.codex/generated_images/01a190a5-b799-7b70-b1de-bdf6dd48e063/exec-fdc95d98-fb58-40ba-8f03-59222a2c250a.png').convert('RGB'),(1080,1350))
d=ImageDraw.Draw(art,'RGBA');d.rectangle((0,0,1080,340),fill=(8,12,20,230));d.rectangle((0,1000,1080,1350),fill=(8,12,20,238))
d.text((65,55),'TRYWISE AI  /  NEWS',font=f(32),fill=blue)
d.multiline_text((65,115),'3 AI UPDATES\nWORTH KNOWING',font=f(74),fill=white,spacing=8)
d.multiline_text((65,1050),'GOOGLE  •  OPENAI\nANTHROPIC',font=f(54),fill=white,spacing=12)
d.text((65,1250),'News from Nov 2–3  •  Illustration',font=f(29,False),fill=soft)
art.save(out/'01.png')
slides=[
('01 / GOOGLE  •  NOV 3','AI GUIDANCE\nIN CLASSROOM','Google says teacher-led Guided Learning is rolling out globally in Google Classroom. Teachers can assign lessons that coach students through course material.'),
('02 / OPENAI  •  NOV 2','GIT FOR A\nWORLD OF AGENTS','OpenAI built Pando, a Git backend used internally to handle more parallel work. The company says it is exploring how to share the technology with users.'),
('03 / ANTHROPIC  •  NOV 2','PROVE WHICH\nMODEL RESPONDED','Anthropic released FlashProve research and code. It explores cryptographic proof that output came from a committed model. It is a research prototype, not a finished feature.'),
('SOURCES','READ THE\nORIGINALS','Google: Guided Learning in Classroom. OpenAI: Scaling Git at OpenAI. Anthropic: Progress on provable inference. Full links are in the caption.')]
for i,(tag,title,body) in enumerate(slides,2):
 im=Image.new('RGB',(1080,1350),(14,19,29));dr=ImageDraw.Draw(im)
 dr.rounded_rectangle((65,65,1015,1285),radius=35,outline=(55,75,92),width=3);dr.rectangle((68,69,1012,82),fill=blue)
 dr.text((110,130),'TRYWISE AI',font=f(30),fill=blue);dr.text((110,270),tag,font=f(29),fill=soft)
 dr.multiline_text((110,345),title,font=f(72),fill=white,spacing=8)
 y=590
 for line in textwrap.wrap(body,width=32):dr.text((110,y),line,font=f(42,False),fill=white);y+=65
 dr.line((110,1120,970,1120),fill=(65,77,90),width=2);dr.text((110,1160),'Source links in caption',font=f(28,False),fill=soft);dr.text((880,1200),f'{i} / 5',font=f(26),fill=blue)
 im.save(out/f'{i:02}.png')
