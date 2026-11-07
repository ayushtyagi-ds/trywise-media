from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import textwrap
out=Path(__file__).parent
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf';reg='/System/Library/Fonts/Supplemental/Arial.ttf'
def f(n,b=True):return ImageFont.truetype(bold if b else reg,n)
white=(246,246,246);orange=(255,157,107);gray=(189,184,189)
im=ImageOps.fit(Image.open('/Users/phoenix/.codex/generated_images/01a190a5-b799-7b70-b1de-bdf6dd48e063/exec-f8275ae5-087d-4b1b-a1ed-4e57387829ca.png').convert('RGB'),(1080,1350));d=ImageDraw.Draw(im,'RGBA');d.rectangle((0,0,1080,310),fill=(14,10,18,238));d.rectangle((0,1000,1080,1350),fill=(14,10,18,240));d.text((65,55),'TRYWISE AI  /  NEWS',font=f(32),fill=orange);d.multiline_text((65,110),'OPENAI PLANS\nPIERRE DEAL',font=f(84),fill=white,spacing=8);d.multiline_text((65,1050),'WHAT IT MEANS\nFOR CODEX',font=f(64),fill=white,spacing=8);d.text((65,1250),'Nov 4, 2026  •  Illustration',font=f(28,False),fill=gray);im.save(out/'01.png')
slides=[('01 / THE NEWS','A DEAL FOR\nCODING TOOLS','OpenAI announced plans to acquire Pierre Computer Company, which builds developer tools and a service called Code Storage.'),('02 / ALREADY IN CODEX','YOU MAY HAVE\nUSED ITS TOOLS','OpenAI says Pierre’s Trees and Diffs libraries already help people navigate files and review changes in the Codex app.'),('03 / WHAT COMES NEXT','CODE STORAGE\nAND CODEX','OpenAI says Code Storage customers can keep using the service after closing while its features are brought into Codex. No integration date was announced.'),('04 / THE CAVEAT','THE DEAL ISN’T\nCLOSED YET','The acquisition is subject to conditions, including regulatory approvals. OpenAI says Pierre’s open-source projects will remain open source.')]
for i,(tag,title,body) in enumerate(slides,2):
 im=Image.new('RGB',(1080,1350),(20,16,24));d=ImageDraw.Draw(im);d.rounded_rectangle((65,65,1015,1285),radius=35,outline=(80,68,78),width=3);d.rectangle((68,69,1012,82),fill=orange);d.text((110,130),'TRYWISE AI',font=f(30),fill=orange);d.text((110,270),tag,font=f(29),fill=gray);d.multiline_text((110,345),title,font=f(72),fill=white,spacing=8);y=590
 for line in textwrap.wrap(body,width=32):d.text((110,y),line,font=f(42,False),fill=white);y+=65
 d.line((110,1120,970,1120),fill=(80,68,78),width=2);d.text((110,1160),'Source: OpenAI  •  Nov 4, 2026',font=f(27,False),fill=gray);d.text((880,1200),f'{i} / 5',font=f(26),fill=orange);im.save(out/f'{i:02}.png')
