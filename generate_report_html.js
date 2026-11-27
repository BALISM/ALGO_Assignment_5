const fs = require('fs');
const mdText = fs.readFileSync('DAA_A4_24f-0571_Balaj_Report.md', 'utf8');

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Convert markdown to clean HTML
let htmlBody = mdText
  .replace(/^### (.*$)/gim, '<h3>$1</h3>')
  .replace(/^## (.*$)/gim, '<h2>$1</h2>')
  .replace(/^# (.*$)/gim, '<h1>$1</h1>')
  .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
  .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
  .replace(/\*(.*?)\*/gim, '<em>$1</em>')
  .replace(/```([\s\S]*?)```/gim, (m, code) => `<pre><code>${escapeHtml(code.trim())}</code></pre>`)
  .replace(/`([^`]+)`/gim, '<code>$1</code>');

// Tables
htmlBody = htmlBody.replace(/\|(.+)\|\r?\n\|[-:| ]+\|\r?\n((?:\|.+\|\r?\n?)+)/g, (match, header, rows) => {
  const ths = header.split('|').filter(c => c.trim().length > 0).map(c => `<th>${c.trim()}</th>`).join('');
  const trs = rows.trim().split(/\r?\n/).map(row => {
    const tds = row.split('|').filter(c => c.trim().length > 0).map(c => `<td>${c.trim()}</td>`).join('');
    return `<tr>${tds}</tr>`;
  }).join('');
  return `<table><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table>`;
});

// Paragraphs and breaks
const paragraphs = htmlBody.split(/\r?\n\r?\n/).map(p => {
  p = p.trim();
  if (p.startsWith('<h') || p.startsWith('<table') || p.startsWith('<pre') || p.startsWith('<ul') || p.startsWith('<ol') || p.startsWith('<blockquote') || p.startsWith('---')) {
    if (p.startsWith('---')) return '<hr/>';
    return p;
  }
  return `<p>${p.replace(/\r?\n/g, '<br/>')}</p>`;
}).join('\n');

const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>DAA Assignment 4 Report — Balaj (24f-0571)</title>
<style>
  @page { size: A4; margin: 20mm 15mm; }
  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #1e293b;
    background: #fff;
    max-width: 900px;
    margin: 0 auto;
    padding: 30px;
  }
  h1 { color: #0f172a; font-size: 1.8rem; border-bottom: 2px solid #2563eb; padding-bottom: 6px; margin-top: 24px; }
  h2 { color: #1e3a8a; font-size: 1.35rem; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-top: 20px; }
  h3 { color: #2563eb; font-size: 1.1rem; margin-top: 16px; }
  p { margin: 10px 0; text-align: justify; }
  code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.9em; color: #0f172a; }
  pre { background: #0f172a; color: #f8fafc; padding: 14px; border-radius: 6px; overflow-x: auto; font-size: 0.82rem; }
  pre code { background: none; color: inherit; padding: 0; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.88rem; }
  th, td { border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }
  th { background: #f8fafc; font-weight: 600; color: #1e293b; }
  tr:nth-child(even) { background: #f8fafc; }
  hr { border: none; border-top: 1px solid #cbd5e1; margin: 24px 0; }
  blockquote { border-left: 4px solid #2563eb; margin: 12px 0; padding-left: 12px; color: #475569; background: #f8fafc; }
  .header-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; margin-bottom: 20px; }
  @media print {
    body { padding: 0; max-width: 100%; }
    h1, h2 { page-break-after: avoid; }
    table, pre { page-break-inside: avoid; }
  }
</style>
</head>
<body>
${paragraphs}
</body>
</html>`;

fs.writeFileSync('DAA_A4_24f-0571_Balaj_Report.html', fullHtml, 'utf8');
console.log('Successfully created DAA_A4_24f-0571_Balaj_Report.html!');
