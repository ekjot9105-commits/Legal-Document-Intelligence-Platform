export type BriefDocument = { filename: string; classification: string; risk: string }
export type BriefClause = { title: string; simple: string; citation: string }

/** Create a plain, printable PDF from already-grounded document findings. */
export async function downloadLawyerBrief(document: BriefDocument, clauses: BriefClause[]): Promise<void> {
  const { jsPDF } = await import('jspdf')
  const pdf = new jsPDF({ unit: 'pt', format: 'a4' })
  const margin = 44
  const width = 507
  let y = 54
  pdf.setFont('helvetica', 'bold')
  pdf.setFontSize(20)
  pdf.text('LEXORA DOCUMENT BRIEF', margin, y)
  y += 30
  pdf.setFont('helvetica', 'normal')
  pdf.setFontSize(10)
  pdf.text(document.filename, margin, y)
  y += 16
  pdf.text(`Classification: ${document.classification}`, margin, y)
  y += 16
  pdf.text(`Attention level: ${document.risk}`, margin, y)
  y += 30
  pdf.setFont('helvetica', 'bold')
  pdf.setFontSize(13)
  pdf.text('Key clauses', margin, y)
  y += 22
  pdf.setFont('helvetica', 'normal')
  pdf.setFontSize(10)

  clauses.forEach((clause) => {
    const lines = pdf.splitTextToSize(`${clause.title}: ${clause.simple} (${clause.citation})`, width)
    if (y + lines.length * 14 > 760) {
      pdf.addPage()
      y = 54
    }
    pdf.text(lines, margin, y)
    y += lines.length * 14 + 10
  })

  y += 10
  pdf.setFont('helvetica', 'italic')
  pdf.setFontSize(9)
  pdf.text('This tool provides legal information and document assistance, not legal advice.', margin, y)
  pdf.save(`${document.filename.replace(/\.[^.]+$/, '')}-brief.pdf`)
}
