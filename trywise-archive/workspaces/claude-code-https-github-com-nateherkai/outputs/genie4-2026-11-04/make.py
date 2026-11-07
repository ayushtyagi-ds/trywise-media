from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import textwrap
out=Path(__file__).parent
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf';reg='/System/Library/Fonts/Supplemental/Arial.ttf'
def f(n,b=True):return ImageFont.truetype(bold if b else reg,n)
white=(246,246,246);cyan=(107,217,246);gray=(182,197,206)
im=ImageOps.fit(Image.open('/Users/phoenix/.codex/generated_images/01a190a5-b799-7b70-b1de-bdf6dd48e063/exec-a541a100-13d1-457f-842b-0c225b18943d.png').convert('RGB'),(1080,1350));d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,0,1080,300),fill=(9,14,22,234));d.rectangle((0,1000,1080,1350),fill=(9,14,22,238));d.text((65,55),'TRYWISE AI  /  EXPLAINED',font=f(32),fill=cyan);d.multiline_text((65,110),'AI WORLDS\nYOU CAN STEER',font=f(84),fill=white,spacing=8);d.multiline_text((65,1060),'GOOGLE’S GENIE 4\nRESEARCH PREVIEW',font=f(54),fill=white,spacing=8);d.text((65,1250),'Announced Oct 27  •  Illustration',font=f(28,False),fill=gray);im.save(out/'01.png')
slides=[('01 / THE IDEA','A WORLD THAT\nRESPONDS','Google describes Genie 4 as a model for interactive simulation. Users can steer a scene as it unfolds, using natural-language instructions.'),('02 / WHAT IT DOES','CHANGE THE\nSCENE','Google says users can change the weather, move the camera or introduce characters. The model also generates sound, including dialogue and ambient audio.'),('03 / AVAILABILITY','NOT OPEN\nTO EVERYONE','Google announced a research preview for trusted testers. It said access for AI Ultra subscribers and early API partners was coming later. Check the latest rollout before expecting access.'),('04 / WHY IT MATTERS','CREATIVE\nPOSSIBILITIES','Google points to potential uses in games, filmmaking and training simulations. These are possibilities, not proof of reliable results. We have not tested Genie 4.')]
for i,(tag,title,body) in enumerate(slides,2):
 im=Image.new('RGB',(1080,1350),(12,20,29));d=ImageDraw.Draw(im);d.rounded_rectangle((65,65,1015,1285),radius=35,outline=(55,78,91),width=3);d.rectangle((68,69,1012,82),fill=cyan);d.text((110,130),'TRYWISE AI',font=f(30),fill=cyan);d.text((110,270),tag,font=f(29),fill=gray);d.multiline_text((110,345),title,font=f(74),fill=white,spacing=8);y=590
 for line in textwrap.wrap(body,width=32):d.text((110,y),line,font=f(42,False),fill=white);y+=65
 d.line((110,1120,970,1120),fill=(65,78,88),width=2);d.text((110,1160),'Source: Google  •  Oct 27, 2026',font=f(27,False),fill=gray);d.text((880,1200),f'{i} / 5',font=f(26),fill=cyan);im.save(out/f'{i:02}.png')
