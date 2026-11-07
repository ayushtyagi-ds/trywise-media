from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import shutil
out = Path(__file__).parent
base = Path('/Users/phoenix/.codex/generated_images/01a190a5-b799-7b70-b1de-bdf6dd48e063')
items = [
 ('exec-d4371bed-21ce-4298-b6e8-026f3998a5fa.png','images.png','CHATGPT IMAGES\nCAN NOW MAKE GIFS','OPENAI IMAGES 2.6','Announced Nov 4  •  AI illustration'),
 ('exec-31cc950c-d60a-4421-8e49-bb9edc482ffe.png','cyber.png','OPENAI RELEASES\nA CYBERSECURITY AI','GPT-6 CYBER  /  LIMITED ACCESS','Announced Nov 5  •  AI illustration')
]
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
reg='/System/Library/Fonts/Supplemental/Arial.ttf'
for source,name,title,subtitle,foot in items:
    shutil.copy2(base/source,out/('source-'+name))
    im=ImageOps.fit(Image.open(base/source).convert('RGB'),(1080,1350))
    d=ImageDraw.Draw(im,'RGBA')
    d.rectangle((0,0,1080,310),fill=(8,14,23,225))
    d.rectangle((0,1030,1080,1350),fill=(8,14,23,238))
    d.text((58,45),'TRYWISE AI  /  NEWS',font=ImageFont.truetype(bold,30),fill=(110,221,244))
    d.multiline_text((58,110),title,font=ImageFont.truetype(bold,70),fill='white',spacing=8)
    d.text((58,1100),subtitle,font=ImageFont.truetype(bold,42),fill='white')
    d.text((58,1230),foot,font=ImageFont.truetype(reg,27),fill=(190,205,214))
    im.save(out/name)
