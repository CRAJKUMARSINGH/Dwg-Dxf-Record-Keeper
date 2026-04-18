import type { BridgeInput } from "../bridge-types";
import { makeHeader, finalizeDxf, txt, txtL, closedPoly, ln, circle, dimH, dimV, hatchLines, ircTitleBlock, ircNotesBlock } from "../dxf-helpers";

export function generateDeckRebarDrawing(inp: BridgeInput): string {
  const { spanLength, carriageWidth, footpathWidth, kerbWidth, slabThickness, wearingCoatThickness,
    mainBarDia, mainBarSpacing, distBarDia, distBarSpacing, topBarDia, topBarSpacing,
    stirrupDia, stirrupSpacing, coverDeck, bottomHaunchDepth, bottomHaunchWidth,
    concreteGrade, steelGrade, coverStem, coverFoundation, designCode, loadClass,
    projectName, drawingNo, location } = inp;

  const e: string[] = [];
  const totW = carriageWidth + 2*(footpathWidth+kerbWidth);
  const cvr = coverDeck/1000;
  const top = slabThickness;

  e.push(txt(spanLength/2, top+4.5, "DECK SLAB REINFORCEMENT DETAILS", 0.60, "TEXT"));
  e.push(txt(spanLength/2, top+3.8, `LONGITUDINAL SECTION  |  SCALE 1:20  |  SLAB THICKNESS = ${(slabThickness*1000).toFixed(0)}mm`, 0.30, "TEXT"));

  // Slab outline
  e.push(closedPoly([[0,0],[spanLength,0],[spanLength,top],[0,top]], "STRUCTURE"));
  e.push(...hatchLines(0, 0, spanLength, top, 0.12, "HATCH"));
  // Wearing coat
  e.push(closedPoly([[0,top],[spanLength,top],[spanLength,top+wearingCoatThickness],[0,top+wearingCoatThickness]], "WEARING_COAT"));
  e.push(...hatchLines(0, top, spanLength, top+wearingCoatThickness, 0.06, "HATCH"));
  e.push(txt(spanLength/2, top+wearingCoatThickness/2, `WC ${(wearingCoatThickness*1000).toFixed(0)}mm`, 0.20, "ANNOTATION"));
  // Haunches
  e.push(closedPoly([[0,-bottomHaunchDepth],[bottomHaunchWidth,0],[0,0]], "STRUCTURE"));
  e.push(closedPoly([[spanLength-bottomHaunchWidth,0],[spanLength,-bottomHaunchDepth],[spanLength,0]], "STRUCTURE"));
  e.push(...hatchLines(0,-bottomHaunchDepth,bottomHaunchWidth,0,0.10,"HATCH"));
  e.push(...hatchLines(spanLength-bottomHaunchWidth,-bottomHaunchDepth,spanLength,0,0.10,"HATCH"));

  // Bottom main bars (longitudinal)
  const mainBarY = cvr + mainBarDia/2000;
  const nMain = Math.floor(spanLength/(mainBarSpacing/1000));
  for (let i = 0; i <= nMain; i++) {
    const bx = i*(mainBarSpacing/1000);
    if (bx <= spanLength) {
      e.push(ln(bx, 0, bx, top, "REBAR"));
      e.push(circle(bx, mainBarY, mainBarDia/2000, "REBAR"));
    }
  }
  // Top bars
  const topBarY = top - cvr - topBarDia/2000;
  const nTop = Math.floor(spanLength/(topBarSpacing/1000));
  for (let i = 0; i <= nTop; i++) {
    const bx = i*(topBarSpacing/1000);
    if (bx <= spanLength) {
      e.push(circle(bx, topBarY, topBarDia/2000, "REBAR"));
    }
  }
  // Distribution bars (shown as circles at mid-depth)
  const distBarY = top/2;
  const nDist = Math.floor(spanLength/(distBarSpacing/1000));
  for (let i = 0; i <= nDist; i++) {
    const bx = i*(distBarSpacing/1000);
    if (bx <= spanLength) e.push(circle(bx, distBarY, distBarDia/2000, "REBAR"));
  }
  // Stirrups
  const nStir = Math.floor(spanLength/(stirrupSpacing/1000));
  for (let i = 0; i <= nStir; i++) {
    const sx = i*(stirrupSpacing/1000);
    if (sx <= spanLength) {
      e.push(closedPoly([[sx-0.015,cvr],[sx+0.015,cvr],[sx+0.015,top-cvr],[sx-0.015,top-cvr]], "REBAR"));
    }
  }

  // Rebar leaders
  e.push(ln(spanLength*0.3, mainBarY, spanLength+1.5, mainBarY-0.3, "REBAR"));
  e.push(txtL(spanLength+1.6, mainBarY-0.3, `T${mainBarDia} @ ${mainBarSpacing}mm c/c (MAIN BOTTOM)`, 0.25, "ANNOTATION"));
  e.push(ln(spanLength*0.7, topBarY, spanLength+1.5, topBarY+0.3, "REBAR"));
  e.push(txtL(spanLength+1.6, topBarY+0.3, `T${topBarDia} @ ${topBarSpacing}mm c/c (TOP)`, 0.25, "ANNOTATION"));
  e.push(ln(spanLength*0.5, distBarY, spanLength+1.5, distBarY, "REBAR"));
  e.push(txtL(spanLength+1.6, distBarY, `T${distBarDia} @ ${distBarSpacing}mm c/c (DIST.)`, 0.25, "ANNOTATION"));
  e.push(ln(spanLength*0.4, top/2, spanLength+1.5, top/2-0.5, "REBAR"));
  e.push(txtL(spanLength+1.6, top/2-0.5, `T${stirrupDia} @ ${stirrupSpacing}mm c/c (STIRRUPS)`, 0.25, "ANNOTATION"));

  // Cover annotations
  e.push(ln(0, cvr, -0.4, cvr, "DIMENSIONS"));
  e.push(txtL(-1.8, cvr-0.05, `COVER=${coverDeck}mm`, 0.20, "DIMENSIONS"));
  e.push(ln(0, top-cvr, -0.4, top-cvr, "DIMENSIONS"));
  e.push(txtL(-1.8, top-cvr-0.05, `COVER=${coverDeck}mm`, 0.20, "DIMENSIONS"));

  // Dimensions
  const dimY = -bottomHaunchDepth - 1.5;
  e.push(...dimH(0, 0, spanLength, dimY, "DIMENSIONS", `CLEAR SPAN = ${spanLength.toFixed(2)}m`));
  e.push(...dimV(spanLength+0.5, 0, top, spanLength+1.0, "DIMENSIONS", `D=${(slabThickness*1000).toFixed(0)}mm`));
  e.push(...dimV(spanLength+2.0, -bottomHaunchDepth, 0, spanLength+2.5, "DIMENSIONS", `HAUNCH=${(bottomHaunchDepth*1000).toFixed(0)}mm`));

  // Section label
  e.push(txt(spanLength/2, -bottomHaunchDepth-0.5, "LONGITUDINAL SECTION B-B", 0.35, "TEXT"));

  //  BAR BENDING SCHEDULE 
  const bbsY = dimY - 2.5;
  e.push(txt(spanLength/2, bbsY+0.5, "BAR BENDING SCHEDULE — DECK SLAB", 0.40, "TEXT"));
  const hdrs = ["MARK", "DIA (mm)", "SPACING (mm)", "NOS.", "CUT LENGTH (m)", "SHAPE", "TOTAL WT. (kg)"];
  const hW = 3.2;
  hdrs.forEach((h, i) => {
    e.push(closedPoly([[i*hW, bbsY-0.7],[( i+1)*hW, bbsY-0.7],[(i+1)*hW, bbsY],[i*hW, bbsY]], "TITLEBLOCK"));
    e.push(txt(i*hW+hW/2, bbsY-0.45, h, 0.20, "TEXT"));
  });
  const nMainBars = Math.round(totW/(mainBarSpacing/1000))+1;
  const nTopBars  = Math.round(totW/(topBarSpacing/1000))+1;
  const nDistBars = Math.round(spanLength/(distBarSpacing/1000))+1;
  const nStirBars = Math.round(spanLength/(stirrupSpacing/1000))+1;
  const wt = (n: number, d: number, l: number) => ((n * (Math.PI/4) * (d/1000)**2 * l * 7850)).toFixed(1);
  const mainL = spanLength + 0.6;
  const topL  = spanLength + 0.4;
  const distL = totW + 0.4;
  const stirL = 2*(slabThickness-2*cvr) + 0.3;
  const bars = [
    ["B1", `${mainBarDia}`, `${mainBarSpacing}`, `${nMainBars}`, mainL.toFixed(2), "STRAIGHT", wt(nMainBars, mainBarDia, mainL)],
    ["B2", `${topBarDia}`,  `${topBarSpacing}`,  `${nTopBars}`,  topL.toFixed(2),  "STRAIGHT", wt(nTopBars, topBarDia, topL)],
    ["B3", `${distBarDia}`, `${distBarSpacing}`, `${nDistBars}`, distL.toFixed(2), "STRAIGHT", wt(nDistBars, distBarDia, distL)],
    ["B4", `${stirrupDia}`, `${stirrupSpacing}`, `${nStirBars}`, stirL.toFixed(2), "RECT.",    wt(nStirBars, stirrupDia, stirL)],
  ];
  bars.forEach((row, ri) => {
    const ry = bbsY - 0.7 - (ri+1)*0.65;
    row.forEach((cell, ci) => {
      e.push(closedPoly([[ci*hW, ry],[(ci+1)*hW, ry],[(ci+1)*hW, ry+0.65],[ci*hW, ry+0.65]], "TITLEBLOCK"));
      e.push(txt(ci*hW+hW/2, ry+0.18, cell, 0.20, "TEXT"));
    });
  });
  // Total weight
  const totalWt = bars.reduce((s, r) => s + parseFloat(r[6]), 0);
  const totY = bbsY - 0.7 - bars.length*0.65;
  e.push(closedPoly([[0, totY-0.65],[hdrs.length*hW, totY-0.65],[hdrs.length*hW, totY],[0, totY]], "TITLEBLOCK"));
  e.push(txt(hdrs.length*hW/2, totY-0.42, `TOTAL STEEL WEIGHT = ${totalWt.toFixed(1)} kg`, 0.25, "TEXT"));

  e.push(...ircNotesBlock(0, totY-2, concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation, designCode, loadClass));

  const tbX = -3, tbY = totY - 18;
  e.push(...ircTitleBlock(tbX, tbY, {
    projectName, drawingTitle: "DECK SLAB REINFORCEMENT — LONGITUDINAL SECTION & BBS",
    drawingNo: `${drawingNo}/06`, scale: "1:20", location, sheetNo: "6", totalSheets: "8",
  }));

  return makeHeader([tbX-1, tbY-1, 0], [spanLength+14, top+6, 0]) + finalizeDxf(e);
}