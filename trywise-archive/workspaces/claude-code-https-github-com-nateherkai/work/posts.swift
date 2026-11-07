import AppKit
let posts: [(String,String,String,String)] = [
("01 / WELCOME", "AI, tested\nin the real world.", "I’m a software developer exploring what AI can build — and where it breaks.", "FOLLOW THE EXPERIMENTS"),
("02 / AI TIP", "Give AI a\nbetter brief.", "Try: “Act as [role]. Help me [task]. Use [context]. Return [format]. Ask if anything is unclear.”", "CHECK THE OUTPUT"),
("03 / AI NEWS", "Gemini can now\nedit files in chat.", "Google says you can create, preview and edit documents, PDFs, slides and more inside Gemini.", "SOURCE: GOOGLE · OCT 29, 2026")]
for (i,p) in posts.enumerated() {
 let image = NSImage(size:NSSize(width:1080,height:1350)); image.lockFocus()
 NSColor(calibratedRed:0.035,green:0.055,blue:0.11,alpha:1).setFill(); NSRect(x:0,y:0,width:1080,height:1350).fill()
 NSColor(calibratedRed:0.17,green:0.9,blue:0.72,alpha:1).setFill(); NSRect(x:80,y:1100,width:90,height:8).fill()
 func draw(_ s:String,_ r:NSRect,_ size:CGFloat,_ color:NSColor,_ weight:NSFont.Weight) { (s as NSString).draw(in:r,withAttributes:[.font:NSFont.systemFont(ofSize:size,weight:weight),.foregroundColor:color]) }
 let mint=NSColor(calibratedRed:0.25,green:0.9,blue:0.75,alpha:1)
 draw("TRYWISE AI",NSRect(x:80,y:1220,width:800,height:60),32,mint,.bold)
 draw(p.0,NSRect(x:80,y:1020,width:900,height:60),26,mint,.semibold)
 draw(p.1,NSRect(x:80,y:690,width:920,height:300),91,.white,.heavy)
 draw(p.2,NSRect(x:85,y:375,width:880,height:285),43,NSColor(calibratedWhite:0.82,alpha:1),.regular)
 draw(p.3,NSRect(x:85,y:135,width:900,height:60),25,mint,.bold)
 image.unlockFocus()
 let bitmap=NSBitmapImageRep(data:image.tiffRepresentation!)!; let data=bitmap.representation(using:.png,properties:[:])!
 try! data.write(to:URL(fileURLWithPath:CommandLine.arguments[1]+"/0\(i+1)-post.png"))
}
