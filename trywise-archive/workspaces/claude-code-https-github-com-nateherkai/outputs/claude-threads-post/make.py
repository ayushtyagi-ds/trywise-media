from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import textwrap

out = Path(__file__).parent
font = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
regular = '/System/Library/Fonts/Supplemental/Arial.ttf'
def f(size, bold=True): return ImageFont.truetype(font if bold else regular, size)
white=(247,243,237); orange=(255,135,99); muted=(187,180,178)
art=Image.open('/Users/phoenix/.codex/generated_images/01a190a5-b799-7b70-b1de-bdf6dd48e063/exec-7e09ae48-116f-4439-9d75-5fca8b9d70d8.png').convert('RGB')
art=ImageOps.fit(art,(1080,1350))
img=art.copy(); d=ImageDraw.Draw(img,'RGBA'); d.rectangle((0,0,1080,310),fill=(12,12,18,225));d.rectangle((0,920,1080,1350),fill=(12,12,18,237));
d.text((70,65),'TRYWISE AI  /  NEWS',font=f(32),fill=orange)
d.multiline_text((70,110),'CLAUDE API\nGETS THREADS',font=f(88),fill=white,spacing=4)
d.multiline_text((70,990),'LESS RESENDING.\nONE BIG CATCH.',font=f(66),fill=white,spacing=10)
d.text((70,1255),'Illustration  •  Nov 2, 2026 announcement',font=f(25,False),fill=muted)
img.save(out/'01.png')
slides=[
('01 / WHAT CHANGED','SEND THE CHAT\nONCE','Anthropic launched message threads in public beta for its Messages API. After the first request, an app can send new messages and the previous response ID.'),
('02 / WHY IT MATTERS','SMALLER\nREQUESTS','Long agent conversations can avoid uploading the entire history on every turn. Anthropic says this can reduce time to the first token.'),
('03 / THE CATCH','5 MINUTES.','A thread expires 5 minutes after its last request. Your app must keep the conversation and be ready to resend it if the thread expires.'),
('04 / BEFORE YOU BUILD','NOT A TOKEN\nDISCOUNT','Claude still reads the full conversation, so token usage stays the same. Standard API rates apply. This is an API feature; it is not a new memory setting in the Claude chat app.')]
for idx,(tag,title,body) in enumerate(slides,2):
 im=Image.new('RGB',(1080,1350),(17,18,24)); dr=ImageDraw.Draw(im)
 dr.rounded_rectangle((65,65,1015,1285),radius=35,outline=(70,66,68),width=3)
 dr.rectangle((68,69,1012,82),fill=orange)
 dr.text((110,130),'TRYWISE AI',font=f(30),fill=orange)
 dr.text((110,270),tag,font=f(29),fill=muted)
 dr.multiline_text((110,335),title,font=f(74),fill=white,spacing=6)
 y=590
 for line in textwrap.wrap(body,width=32):
  dr.text((110,y),line,font=f(42,False),fill=white); y+=65
 dr.line((110,1120,970,1120),fill=(80,75,75),width=2)
 dr.text((110,1160),'Source: claude.com  •  Nov 2, 2026',font=f(27,False),fill=muted)
 dr.text((880,1200),f'{idx} / 5',font=f(26),fill=orange)
 im.save(out/f'{idx:02}.png')
