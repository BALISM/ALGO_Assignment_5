const fs = require('fs');

function createPdf(lines, outputPath) {
  // Simple multi-page text PDF generator in pure Node.js
  const pageWidth = 595.28; // A4
  const pageHeight = 841.89;
  const margin = 50;
  const lineHeight = 14;
  const maxLinesPerPage = Math.floor((pageHeight - margin * 2) / lineHeight);

  // Group lines into pages
  const pages = [];
  let currentPage = [];

  for (let i = 0; i < lines.length; i++) {
    currentPage.push(lines[i]);
    if (currentPage.length >= maxLinesPerPage) {
      pages.push(currentPage);
      currentPage = [];
    }
  }
  if (currentPage.length > 0) {
    pages.push(currentPage);
  }

  const objects = [];
  function addObject(content) {
    objects.push(content);
    return objects.length;
  }

  // Obj 1: Catalog
  const catalogObjNum = addObject('<< /Type /Catalog /Pages 2 0 R >>');

  // Obj 2: Pages placeholder
  const pagesObjNum = addObject(''); 

  // Obj 3: Font
  const fontObjNum = addObject('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>');

  // Page and Content objects
  const pageObjNums = [];
  for (let p = 0; p < pages.length; p++) {
    const pageLines = pages[p];
    let streamContent = 'BT\n/F1 10 Tf\n';
    let y = pageHeight - margin;
    for (let l = 0; l < pageLines.length; l++) {
      const escaped = pageLines[l]
        .replace(/\\/g, '\\\\')
        .replace(/\(/g, '\\(')
        .replace(/\)/g, '\\)');
      streamContent += `1 0 0 1 ${margin} ${y} Tm (${escaped}) Tj\n`;
      y -= lineHeight;
    }
    streamContent += 'ET\n';

    const contentObjNum = addObject(`<< /Length ${Buffer.byteLength(streamContent, 'utf8')} >>\nstream\n${streamContent}\nendstream`);
    const pageObjNum = addObject(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pageWidth} ${pageHeight}] /Contents ${contentObjNum} 0 R /Resources << /Font << /F1 ${fontObjNum} 0 R >> >> >>`);
    pageObjNums.push(pageObjNum);
  }

  // Fill in Pages object
  const kidsStr = pageObjNums.map(n => `${n} 0 R`).join(' ');
  objects[pagesObjNum - 1] = `<< /Type /Pages /Kids [${kidsStr}] /Count ${pageObjNums.length} >>`;

  // Build PDF buffer
  let pdf = '%PDF-1.4\n';
  const xref = [0];
  for (let i = 0; i < objects.length; i++) {
    xref.push(Buffer.byteLength(pdf, 'utf8'));
    pdf += `${i + 1} 0 obj\n${objects[i]}\nendobj\n`;
  }

  const xrefOffset = Buffer.byteLength(pdf, 'utf8');
  pdf += 'xref\n';
  pdf += `0 ${objects.length + 1}\n`;
  pdf += '0000000000 65535 f \n';
  for (let i = 1; i <= objects.length; i++) {
    const offsetStr = String(xref[i]).padStart(10, '0');
    pdf += `${offsetStr} 00000 n \n`;
  }
  pdf += 'trailer\n';
  pdf += `<< /Size ${objects.length + 1} /Root ${catalogObjNum} 0 R >>\n`;
  pdf += 'startxref\n';
  pdf += `${xrefOffset}\n`;
  pdf += '%%EOF\n';

  fs.writeFileSync(outputPath, pdf, 'binary');
  console.log(`Generated ${outputPath} (${pages.length} pages)`);
}

// Read markdown and word-wrap lines for PDF
const rawText = fs.readFileSync('DAA_A4_24f-0571_Balaj_Report.md', 'utf8');
const rawLines = rawText.split(/\r?\n/);
const formattedLines = [];

for (let line of rawLines) {
  // wrap long lines at ~85 chars
  while (line.length > 85) {
    let splitIdx = line.lastIndexOf(' ', 85);
    if (splitIdx === -1) splitIdx = 85;
    formattedLines.push(line.slice(0, splitIdx));
    line = line.slice(splitIdx).trim();
  }
  formattedLines.push(line);
}

createPdf(formattedLines, 'DAA_A4_24f-0571_Balaj_Report.pdf');
