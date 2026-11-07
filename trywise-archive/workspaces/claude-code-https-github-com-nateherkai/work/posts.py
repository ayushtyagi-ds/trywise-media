import sys,textwrap
sys.path.insert(0,'work/pylibs')
from PIL import Image,ImageDraw,ImageFont
font='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
regular='/System/Library/Fonts/Supplemental/Arial.ttf'
posts=[('01 / WELCOME','AI, tested\nin the real world.','I’m a software developer exploring what AI can build — and where it breaks.','FOLLOW THE EXPERIMENTS'),('02 / AI TIP','Give AI a\nbetter brief.','Try: “Act as [role]. Help me [task]. Use [context]. Return [format]. Ask if anything is unclear.”','CHECK THE OUTPUT'),('03 / AI NEWS','Gemini can now\nedit files in chat.','Google says you can create, preview and edit documents, PDFs, slides and more inside Gemini.','SOURCE: GOOGLE · OCT 29, 2026')]
for i,(label,title,body,foot) in enumerate(posts,1):
 im=Image.new('RGB',(1080,1350),'#090f1c');d=ImageDraw.Draw(im); mint='#57eac1'
 d.text((80,95),'TRYWISE AI',font=ImageFont.truetype(font,36),fill=mint)
 d.rounded_rectangle((80,220,180,227),3,fill=mint)
 d.text((80,270),label,font=ImageFont.truetype(font,28),fill=mint)
 d.multiline_text((75,365),title,font=ImageFont.truetype(font,90),fill='white',spacing=12)
 d.multiline_text((82,685),'\n'.join(textwrap.wrap(body,35)),font=ImageFont.truetype(regular,43),fill='#d3dbe4',spacing=14)
 d.line((80,1160,1000,1160),fill='#294158',width=2)
 d.text((80,1205),foot,font=ImageFont.truetype(font,26),fill=mint)
 im.save(f'outputs/0{i}-post.png')
