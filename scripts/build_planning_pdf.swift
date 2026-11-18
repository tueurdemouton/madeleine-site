import AppKit
import CoreText
import PDFKit

struct Day: Decodable {
    let day: String
    let title: String
    let description: String
}

let days = try JSONDecoder().decode([Day].self, from: FileHandle.standardInput.readDataToEndOfFile())
let output = URL(fileURLWithPath: CommandLine.arguments[1])
var page = CGRect(x: 0, y: 0, width: 595.28, height: 841.89)
let metadata = [kCGPDFContextTitle: "Une semaine, tous les goûts — Madeleine de Goût", kCGPDFContextAuthor: "Madeleine de Goût"] as CFDictionary
let context = CGContext(output as CFURL, mediaBox: &page, metadata)!
let violet = NSColor(srgbRed: 0.40, green: 0.31, blue: 0.58, alpha: 1)
let ink = NSColor(srgbRed: 0.23, green: 0.23, blue: 0.36, alpha: 1)
let muted = NSColor(srgbRed: 0.39, green: 0.35, blue: 0.31, alpha: 1)

func text(_ string: String, x: CGFloat, y: CGFloat, width: CGFloat, height: CGFloat, size: CGFloat, bold: Bool = false, color: NSColor = ink) {
    let font = NSFont(name: bold ? "AvenirNext-DemiBold" : "AvenirNext-Regular", size: size) ?? NSFont.systemFont(ofSize: size)
    let paragraph = NSMutableParagraphStyle()
    paragraph.lineSpacing = 2
    let attributed = NSAttributedString(string: string, attributes: [.font: font, .foregroundColor: color, .paragraphStyle: paragraph])
    let framesetter = CTFramesetterCreateWithAttributedString(attributed)
    let path = CGPath(rect: CGRect(x: x, y: page.height - y - height, width: width, height: height), transform: nil)
    CTFrameDraw(CTFramesetterCreateFrame(framesetter, CFRange(location: 0, length: 0), path, nil), context)
}

context.beginPDFPage(nil)
text("MADELEINE DE GOÛT", x: 40, y: 32, width: 515, height: 18, size: 10, bold: true, color: violet)
text("Une semaine, tous les goûts.", x: 40, y: 56, width: 515, height: 38, size: 25, bold: true)
text("Un exemple pour organiser les dîners de votre famille.", x: 40, y: 99, width: 515, height: 20, size: 11, color: muted)
text("Plats indicatifs : adaptez les recettes, les quantités et les contraintes à votre foyer.", x: 40, y: 119, width: 515, height: 20, size: 9, color: muted)

for (index, day) in days.enumerated() {
    let y = CGFloat(151 + index * 73)
    context.setFillColor((index % 2 == 0 ? NSColor(srgbRed: 0.98, green: 0.96, blue: 0.93, alpha: 1) : NSColor.white).cgColor)
    context.fill(CGRect(x: 40, y: page.height - y - 70, width: 515, height: 70))
    text(day.day, x: 50, y: y + 10, width: 72, height: 20, size: 10, bold: true, color: violet)
    text(day.title, x: 127, y: y + 9, width: 418, height: 20, size: 10.5, bold: true)
    text(day.description, x: 127, y: y + 30, width: 413, height: 35, size: 9, color: muted)
}

text("À NOTER POUR MA SEMAINE", x: 40, y: 681, width: 515, height: 18, size: 9, bold: true, color: violet)
text("Présences et soirs pressés : ..................................................................................................", x: 40, y: 704, width: 515, height: 20, size: 10)
text("Mes adaptations : ...................................................................................................................", x: 40, y: 729, width: 515, height: 20, size: 10)
text("Mon repas de secours : .........................................................................................................", x: 40, y: 754, width: 515, height: 20, size: 10)
text("Le guide complet et l’application : madeleine-de-gout.com/guides/", x: 40, y: 803, width: 515, height: 18, size: 9, color: violet)
context.setURL(URL(string: "https://madeleine-de-gout.com/guides/organiser-repas-famille-gouts-differents/")! as CFURL, for: CGRect(x: 40, y: 20, width: 515, height: 20))
context.endPDFPage()
context.closePDF()

let pdf = PDFDocument(url: output)!
let content = pdf.string ?? ""
guard pdf.pageCount == 1, days.allSatisfy({ content.contains($0.day) && content.contains($0.title) }) else {
    fatalError("Le PDF doit tenir sur une page et contenir les sept jours.")
}
print("PDF A4 généré : une page, sept jours vérifiés.")
