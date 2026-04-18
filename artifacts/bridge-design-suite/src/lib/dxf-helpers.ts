// ─────────────────────────────────────────────
// DXF HELPERS — IRC Standard Bridge Drawing Library
// Based on real Rajasthan PWD bridge drawings (Kherwara, Devka, Malwasa, Bengu)
// IRC SP-13 / IRC:6 / IRC:112 / IRC:78
// 

export function sec(name: string, content: string[]): string {
  return `  0\nSECTION\n  2\n${name}\n${content.join("")}  0\nENDSEC\n`;
}

export function varDxf(name: string, value: string | number | number[]): string {
  let s = `  9\n${name}\n`;
  if (Array.isArray(value)) {
    s += ` 10\n${value[0]}\n 20\n${value[1]}\n 30\n${value[2] ?? 0}\n`;
  } else if (typeof value === "number") {
    s += ` 40\n${value}\n`;
  } else {
    s += `  1\n${value}\n`;
  }
  return s;
}

export function tbl(name: string, entries: string[]): string {
  return `  0\nTABLE\n  2\n${name}\n 70\n${entries.length}\n${entries.join("")}  0\nENDTAB\n`;
}

export function ltype(name: string, desc: string, pattern: number[]): string {
  return `  0\nLTYPE\n  2\n${name}\n 70\n0\n 40\n1.0\n  3\n${desc}\n 72\n65\n 73\n${pattern.length}\n${pattern.map(p => ` 40\n${p}\n`).join("")}`;
}

export function layer(name: string, color: number, lt: string): string {
  return `  0\nLAYER\n  2\n${name}\n 70\n0\n 62\n${color}\n  6\n${lt}\n`;
}

export function txt(x: number, y: number, text: string, height: number, layerName: string, angle = 0): string {
  return `  0\nTEXT\n  8\n${layerName}\n 10\n${x.toFixed(4)}\n 20\n${y.toFixed(4)}\n 30\n0\n 40\n${height}\n  1\n${text}\n 50\n${angle}\n 72\n1\n 11\n${x.toFixed(4)}\n 21\n${y.toFixed(4)}\n 31\n0\n`;
}

export function txtL(x: number, y: number, text: string, height: number, layerName: string): string {
  return `  0\nTEXT\n  8\n${layerName}\n 10\n${x.toFixed(4)}\n 20\n${y.toFixed(4)}\n 30\n0\n 40\n${height}\n  1\n${text}\n 72\n0\n 11\n${x.toFixed(4)}\n 21\n${y.toFixed(4)}\n 31\n0\n`;
}

export function poly(points: number[][], layerName: string, lt = "CONTINUOUS"): string {
  let s = `  0\nLWPOLYLINE\n  8\n${layerName}\n  6\n${lt}\n 90\n${points.length}\n 70\n0\n`;
  for (const [x, y] of points) s += ` 10\n${x.toFixed(4)}\n 20\n${y.toFixed(4)}\n`;
  return s;
}

export function closedPoly(points: number[][], layerName: string, lt = "CONTINUOUS"): string {
  let s = `  0\nLWPOLYLINE\n  8\n${layerName}\n  6\n${lt}\n 90\n${points.length}\n 70\n1\n`;
  for (const [x, y] of points) s += ` 10\n${x.toFixed(4)}\n 20\n${y.toFixed(4)}\n`;
  return s;
}

export function ln(x1: number, y1: number, x2: number, y2: number, layerName: string, lt = "CONTINUOUS"): string {
  return `  0\nLINE\n  8\n${layerName}\n  6\n${lt}\n 10\n${x1.toFixed(4)}\n 20\n${y1.toFixed(4)}\n 30\n0\n 11\n${x2.toFixed(4)}\n 21\n${y2.toFixed(4)}\n 31\n0\n`;
}

export function circle(cx: number, cy: number, r: number, layerName: string): string {
  return `  0\nCIRCLE\n  8\n${layerName}\n 10\n${cx.toFixed(4)}\n 20\n${cy.toFixed(4)}\n 30\n0\n 40\n${r.toFixed(4)}\n`;
}

export function arc(cx: number, cy: number, r: number, startAngle: number, endAngle: number, layerName: string): string {
  return `  0\nARC\n  8\n${layerName}\n 10\n${cx.toFixed(4)}\n 20\n${cy.toFixed(4)}\n 30\n0\n 40\n${r.toFixed(4)}\n 50\n${startAngle}\n 51\n${endAngle}\n`;
}

export function dimH(x1: number, y: number, x2: number, dimY: number, layerName: string, label?: string): string[] {
  const e: string[] = [];
  const mid = (x1 + x2) / 2;
  const dist = Math.abs(x2 - x1);
  const lbl = label ?? (dist >= 1 ? `${dist.toFixed(2)}m` : `${(dist * 1000).toFixed(0)}`);
  e.push(ln(x1, y, x1, dimY + 0.15, layerName));
  e.push(ln(x2, y, x2, dimY + 0.15, layerName));
  e.push(ln(x1, dimY, x2, dimY, layerName));
  e.push(ln(x1, dimY - 0.12, x1 + 0.18, dimY, layerName));
  e.push(ln(x2, dimY - 0.12, x2 - 0.18, dimY, layerName));
  e.push(txt(mid, dimY + 0.08, lbl, 0.28, layerName));
  return e;
}

export function dimV(x: number, y1: number, y2: number, dimX: number, layerName: string, label?: string): string[] {
  const e: string[] = [];
  const mid = (y1 + y2) / 2;
  const dist = Math.abs(y2 - y1);
  const lbl = label ?? (dist >= 1 ? `${dist.toFixed(2)}m` : `${(dist * 1000).toFixed(0)}`);
  e.push(ln(x, y1, dimX + 0.15, y1, layerName));
  e.push(ln(x, y2, dimX + 0.15, y2, layerName));
  e.push(ln(dimX, y1, dimX, y2, layerName));
  e.push(ln(dimX - 0.12, y1, dimX, y1 + 0.18, layerName));
  e.push(ln(dimX - 0.12, y2, dimX, y2 - 0.18, layerName));
  e.push(txt(dimX + 0.12, mid, lbl, 0.28, layerName, 90));
  return e;
}

export function rlMarker(x: number, y: number, rl: number, label: string, layerName: string): string[] {
  const e: string[] = [];
  e.push(ln(x - 0.5, y, x + 3.5, y, layerName, "DASHED"));
  e.push(ln(x, y, x - 0.3, y + 0.2, layerName));
  e.push(ln(x, y, x - 0.3, y - 0.2, layerName));
  e.push(txtL(x + 0.15, y + 0.08, `${label} = ${rl.toFixed(3)} M`, 0.25, layerName));
  return e;
}

export function hatchLines(x1: number, y1: number, x2: number, y2: number, spacing: number, layerName: string): string[] {
  const e: string[] = [];
  const w = x2 - x1, h = y2 - y1;
  const diag = w + h;
  for (let d = 0; d <= diag; d += spacing) {
    const ax = x1 + Math.min(d, w);
    const ay = y1 + Math.max(0, d - w);
    const bx = x1 + Math.max(0, d - h);
    const by = y1 + Math.min(d, h);
    if (ax !== bx || ay !== by) e.push(ln(ax, ay, bx, by, layerName));
  }
  return e;
}

export function northArrow(x: number, y: number, layerName: string): string[] {
  const e: string[] = [];
  e.push(circle(x, y, 0.6, layerName));
  e.push(ln(x, y - 0.55, x, y + 0.55, layerName));
  e.push(ln(x, y + 0.55, x - 0.2, y + 0.1, layerName));
  e.push(ln(x, y + 0.55, x + 0.2, y + 0.1, layerName));
  e.push(txt(x, y + 0.7, "N", 0.35, layerName));
  return e;
}

export function scaleBar(x: number, y: number, scaleM: number, layerName: string): string[] {
  const e: string[] = [];
  e.push(ln(x, y, x + scaleM, y, layerName));
  e.push(ln(x, y - 0.1, x, y + 0.1, layerName));
  e.push(ln(x + scaleM / 2, y - 0.08, x + scaleM / 2, y + 0.08, layerName));
  e.push(ln(x + scaleM, y - 0.1, x + scaleM, y + 0.1, layerName));
  e.push(txt(x, y - 0.25, "0", 0.2, layerName));
  e.push(txt(x + scaleM / 2, y - 0.25, `${(scaleM / 2).toFixed(0)}m`, 0.2, layerName));
  e.push(txt(x + scaleM, y - 0.25, `${scaleM.toFixed(0)}m`, 0.2, layerName));
  return e;
}

export interface TitleBlockData {
  projectName: string;
  drawingTitle: string;
  drawingNo: string;
  scale: string;
  designedBy?: string;
  checkedBy?: string;
  approvedBy?: string;
  date?: string;
  sheetNo?: string;
  totalSheets?: string;
  client?: string;
  location?: string;
}

export function ircTitleBlock(x: number, y: number, data: TitleBlockData): string[] {
  const e: string[] = [];
  const W = 28, H = 10;
  const date = data.date ?? new Date().toLocaleDateString("en-IN");

  e.push(closedPoly([[x, y], [x + W, y], [x + W, y + H], [x, y + H]], "TITLEBLOCK"));
  e.push(closedPoly([[x + 0.12, y + 0.12], [x + W - 0.12, y + 0.12], [x + W - 0.12, y + H - 0.12], [x + 0.12, y + H - 0.12]], "TITLEBLOCK"));

  e.push(ln(x, y + H - 1.8, x + W, y + H - 1.8, "TITLEBLOCK"));
  e.push(txt(x + W / 2, y + H - 1.15, data.projectName.toUpperCase(), 0.55, "TITLEBLOCK"));
  e.push(txt(x + W / 2, y + H - 1.62, `LOCATION: ${(data.location || "").toUpperCase()}`, 0.28, "TITLEBLOCK"));

  e.push(ln(x, y + H - 3.4, x + W, y + H - 3.4, "TITLEBLOCK"));
  e.push(txt(x + W / 2, y + H - 2.45, data.drawingTitle.toUpperCase(), 0.50, "TITLEBLOCK"));
  e.push(txt(x + W / 2, y + H - 3.1, "DESIGN AS PER IRC SP-13:2004 / IRC:6-2017 / IRC:112-2020 / IRC:78-2014", 0.24, "TITLEBLOCK"));

  const col1 = x + W * 0.33, col2 = x + W * 0.66;
  e.push(ln(col1, y, col1, y + H - 3.4, "TITLEBLOCK"));
  e.push(ln(col2, y, col2, y + H - 3.4, "TITLEBLOCK"));

  for (const ry of [y + 7.0, y + 5.8, y + 4.6, y + 3.4, y + 2.2, y + 1.2]) {
    e.push(ln(x, ry, x + W, ry, "TITLEBLOCK"));
  }

  e.push(txtL(x + 0.2, y + 7.2, "DRAWING NO.", 0.22, "TITLEBLOCK"));
  e.push(txt(x + W * 0.165, y + 6.45, data.drawingNo, 0.38, "TITLEBLOCK"));
  e.push(txtL(x + 0.2, y + 6.0, "SCALE", 0.22, "TITLEBLOCK"));
  e.push(txt(x + W * 0.165, y + 5.3, data.scale, 0.30, "TITLEBLOCK"));
  e.push(txtL(x + 0.2, y + 4.8, "DATE", 0.22, "TITLEBLOCK"));
  e.push(txtL(x + 0.2, y + 4.2, date, 0.28, "TITLEBLOCK"));
  e.push(txtL(x + 0.2, y + 3.6, "SHEET NO.", 0.22, "TITLEBLOCK"));
  e.push(txt(x + W * 0.165, y + 2.9, `${data.sheetNo || "1"} OF ${data.totalSheets || "1"}`, 0.28, "TITLEBLOCK"));

  e.push(txtL(col1 + 0.2, y + 7.2, "DESIGNED BY", 0.22, "TITLEBLOCK"));
  e.push(txtL(col1 + 0.2, y + 6.5, data.designedBy || "", 0.28, "TITLEBLOCK"));
  e.push(txtL(col1 + 0.2, y + 6.0, "CHECKED BY", 0.22, "TITLEBLOCK"));
  e.push(txtL(col1 + 0.2, y + 5.3, data.checkedBy || "", 0.28, "TITLEBLOCK"));
  e.push(txtL(col1 + 0.2, y + 4.8, "APPROVED BY", 0.22, "TITLEBLOCK"));
  e.push(txtL(col1 + 0.2, y + 4.1, data.approvedBy || "", 0.28, "TITLEBLOCK"));
  e.push(txtL(col1 + 0.2, y + 3.6, "CLIENT", 0.22, "TITLEBLOCK"));
  e.push(txtL(col1 + 0.2, y + 2.9, data.client || "PUBLIC WORKS DEPARTMENT", 0.24, "TITLEBLOCK"));

  e.push(txtL(col2 + 0.2, y + 7.2, "REVISION TABLE", 0.22, "TITLEBLOCK"));
  e.push(ln(col2, y + 6.8, x + W, y + 6.8, "TITLEBLOCK"));
  const revCols = [col2, col2 + 1.5, col2 + 5.5, col2 + 8.5];
  e.push(txtL(revCols[0] + 0.1, y + 6.9, "REV", 0.18, "TITLEBLOCK"));
  e.push(txtL(revCols[1] + 0.1, y + 6.9, "DATE", 0.18, "TITLEBLOCK"));
  e.push(txtL(revCols[2] + 0.1, y + 6.9, "DESCRIPTION", 0.18, "TITLEBLOCK"));
  e.push(txtL(revCols[3] + 0.1, y + 6.9, "BY", 0.18, "TITLEBLOCK"));
  for (const rc of revCols) e.push(ln(rc, y + 2.2, rc, y + 6.8, "TITLEBLOCK"));
  for (let r = 0; r < 3; r++) {
    e.push(ln(col2, y + 6.8 - (r + 1) * 1.5, x + W, y + 6.8 - (r + 1) * 1.5, "TITLEBLOCK"));
  }

  e.push(ln(x, y + 1.2, x + W, y + 1.2, "TITLEBLOCK"));
  e.push(txt(x + W / 2, y + 0.82, "ALL DIMENSIONS IN METRES UNLESS NOTED. REINFORCEMENT DIAMETERS IN mm.", 0.20, "TITLEBLOCK"));
  e.push(txt(x + W / 2, y + 0.42, "CONTRACTOR TO VERIFY ALL DIMENSIONS AT SITE BEFORE EXECUTION.", 0.20, "TITLEBLOCK"));

  return e;
}

export function ircNotesBlock(x: number, y: number, concreteGrade: string, steelGrade: string, coverDeck: number, coverStem: number, coverFoundation: number, designCode: string, loadClass: string): string[] {
  const e: string[] = [];
  const notes = [
    "GENERAL NOTES",
    "1. ALL DIMENSIONS ARE IN METRES UNLESS NOTED OTHERWISE.",
    "2. ALL REINFORCEMENT DIAMETERS ARE IN mm.",
    `3. CONCRETE GRADE: ${concreteGrade} (IS 456:2000 / IRC:112-2020)`,
    `4. REINFORCEMENT STEEL: ${steelGrade} (IS 1786)`,
    `5. CLEAR COVER: DECK=${coverDeck}mm  STEM/PIER=${coverStem}mm  FOUNDATION=${coverFoundation}mm`,
    `6. DESIGN CODE: ${designCode}`,
    `7. DESIGN LOADING: ${loadClass}`,
    "8. LAPS AND ANCHORAGE AS PER IRC:112-2020 Cl. 15.",
    "9. BAR BENDING SCHEDULE TO BE READ WITH THIS DRAWING.",
    "10. CONTRACTOR TO VERIFY ALL DIMENSIONS AT SITE BEFORE EXECUTION.",
  ];
  e.push(closedPoly([[x, y - notes.length * 0.38 - 0.3], [x + 15, y - notes.length * 0.38 - 0.3], [x + 15, y + 0.2], [x, y + 0.2]], "ANNOTATION"));
  notes.forEach((n, i) => {
    e.push(txtL(x + 0.2, y - i * 0.38, n, i === 0 ? 0.28 : 0.22, "ANNOTATION"));
  });
  return e;
}

export function makeHeader(extmin: number[], extmax: number[], extraLayers: string[] = []): string {
  const stdLayers = [
    layer("0", 7, "CONTINUOUS"),
    layer("STRUCTURE", 5, "CONTINUOUS"),
    layer("PIERS", 3, "CONTINUOUS"),
    layer("ABUTMENTS", 4, "CONTINUOUS"),
    layer("DIMENSIONS", 2, "CONTINUOUS"),
    layer("HATCH", 254, "CONTINUOUS"),
    layer("TEXT", 7, "CONTINUOUS"),
    layer("TITLEBLOCK", 6, "CONTINUOUS"),
    layer("REBAR", 1, "CONTINUOUS"),
    layer("CENTERLINE", 1, "CENTER"),
    layer("HIDDEN", 8, "DASHED"),
    layer("WATER_LEVEL", 140, "DASHED"),
    layer("ANNOTATION", 2, "CONTINUOUS"),
    layer("SOIL", 52, "DASHED"),
    layer("WEARING_COAT", 254, "CONTINUOUS"),
    layer("BED_PROTECTION", 30, "CONTINUOUS"),
    layer("NORTH_ARROW", 7, "CONTINUOUS"),
    layer("GRID", 253, "CENTER"),
    ...extraLayers.map((l, i) => layer(l, (i + 9) % 255, "CONTINUOUS")),
  ];

  const header = sec("HEADER", [
    varDxf("$ACADVER", "AC1021"),
    varDxf("$INSUNITS", 6),
    varDxf("$MEASUREMENT", 1),
    varDxf("$EXTMIN", extmin),
    varDxf("$EXTMAX", extmax),
    varDxf("$LIMMIN", [extmin[0], extmin[1]]),
    varDxf("$LIMMAX", [extmax[0], extmax[1]]),
  ]);

  const tables = sec("TABLES", [
    tbl("LTYPE", [
      ltype("CONTINUOUS", "Solid line", []),
      ltype("DASHED", "Dashed line", [0.6, -0.3]),
      ltype("CENTER", "Center line", [1.5, -0.3, 0.3, -0.3]),
      ltype("PHANTOM", "Phantom line", [1.5, -0.3, 0.3, -0.3, 0.3, -0.3]),
      ltype("HIDDEN", "Hidden line", [0.3, -0.15]),
    ]),
    tbl("LAYER", stdLayers),
    tbl("STYLE", [
      "  0\nSTYLE\n  2\nSTANDARD\n 70\n0\n 40\n0\n 41\n1\n 50\n0\n 71\n0\n 42\n0.2\n  3\narial.ttf\n  4\n\n",
    ]),
    tbl("VIEW", []),
    tbl("UCS", []),
    tbl("VPORT", []),
  ]);

  return header + tables + sec("CLASSES", []) + sec("BLOCKS", []);
}

export function finalizeDxf(entities: string[]): string {
  return sec("ENTITIES", entities) + sec("OBJECTS", []) + "  0\nEOF\n";
}