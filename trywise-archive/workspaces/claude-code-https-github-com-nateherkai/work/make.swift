import AVFoundation
import AppKit
import CoreVideo
let out = URL(fileURLWithPath: CommandLine.arguments[1])
let audio = AVURLAsset(url: URL(fileURLWithPath: CommandLine.arguments[2]))
let duration = CMTimeGetSeconds(audio.duration)
let temp = URL(fileURLWithPath: NSTemporaryDirectory()).appendingPathComponent("trywise-video.mov")
try? FileManager.default.removeItem(at: temp)
let writer = try AVAssetWriter(outputURL: temp, fileType: .mov)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: 720, AVVideoHeightKey: 1280])
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB, kCVPixelBufferWidthKey as String: 720, kCVPixelBufferHeightKey as String: 1280])
writer.add(input); writer.startWriting(); writer.startSession(atSourceTime: .zero)
let phrases = ["WHAT CAN AI\nREALLY BUILD?", "I’M A SOFTWARE\nDEVELOPER", "WELCOME TO\nTRYWISE AI", "REAL PROJECTS.\nREAL TESTS.", "WHAT WORKS?\nWHAT BREAKS?", "NO HYPE.\nJUST HONEST\nEXPERIMENTS.", "FOLLOW ALONG\n@TRYWISEAI"]
for i in 0..<Int(ceil(duration * 15)) {
 while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.01) }
 var pixel: CVPixelBuffer?; CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &pixel)
 let p = pixel!; CVPixelBufferLockBaseAddress(p, [])
 let context = CGContext(data: CVPixelBufferGetBaseAddress(p), width: 720, height: 1280, bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(p), space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
 context.setFillColor(CGColor(red: 0.025, green: 0.04, blue: 0.09, alpha: 1)); context.fill(CGRect(x: 0, y: 0, width: 720, height: 1280))
 let ns = NSGraphicsContext(cgContext: context, flipped: false); NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
 let idx = min(phrases.count-1, Int(Double(i) / (duration * 15) * Double(phrases.count)))
 let para = NSMutableParagraphStyle(); para.alignment = .center
 let attrs: [NSAttributedString.Key: Any] = [.font: NSFont.systemFont(ofSize: 64, weight: .heavy), .foregroundColor: NSColor.white, .paragraphStyle: para]
 phrases[idx].draw(in: CGRect(x: 45, y: 480, width: 630, height: 320), withAttributes: attrs)
 let small: [NSAttributedString.Key: Any] = [.font: NSFont.systemFont(ofSize: 25, weight: .semibold), .foregroundColor: NSColor.systemTeal, .paragraphStyle: para]
 "TRYWISE AI  /  BUILD • TEST • LEARN".draw(in: CGRect(x: 30, y: 180, width: 660, height: 50), withAttributes: small)
 NSGraphicsContext.restoreGraphicsState(); CVPixelBufferUnlockBaseAddress(p, [])
 adaptor.append(p, withPresentationTime: CMTime(value: Int64(i), timescale: 15))
}
input.markAsFinished(); let sem = DispatchSemaphore(value: 0); writer.finishWriting { sem.signal() }; sem.wait()
let composition = AVMutableComposition(); let video = AVURLAsset(url: temp)
let v = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)!
try v.insertTimeRange(CMTimeRange(start: .zero, duration: audio.duration), of: video.tracks(withMediaType: .video)[0], at: .zero)
let a = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)!
try a.insertTimeRange(CMTimeRange(start: .zero, duration: audio.duration), of: audio.tracks(withMediaType: .audio)[0], at: .zero)
try? FileManager.default.removeItem(at: out)
let exporter = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality)!; exporter.outputURL = out; exporter.outputFileType = .mp4
let done = DispatchSemaphore(value: 0); exporter.exportAsynchronously { done.signal() }; done.wait()
if exporter.status != .completed { fatalError("Export failed: \(String(describing: exporter.error))") }
