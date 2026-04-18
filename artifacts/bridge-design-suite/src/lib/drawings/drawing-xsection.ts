import type { BridgeInput } from "../bridge-types";
import { makeHeader, finalizeDxf, txt, txtL, closedPoly, ln, circle, dimH, dimV, hatchLines, ircTitleBlock, ircNotesBlock } from "../dxf-helpers";

export function generateCrossSection(inp: BridgeInput): string {
  const { carriageWidth, footpathWidth, kerbWidth, kerbHeight, slabThickness, wearingCoatThickness,
    guardrailHeight, bottomHaunchDepth, bottomHaunchWidth, mainBarDia, mainBarSpacing,
    distBarDia, topBarDia, topBarSpacing, stirrupDia, stirrupSpacing, coverDeck,
    projectName, drawingNo, location, concreteGrade, steelGrade, coverStem, coverFoundation, designCode, loadClass } = inp;

  const e: string[] = [];
  const totW = carriageWidth + 2 * (footpathWidth + kerbWidth);
  const top = slabThickness + wearingCoatThickness;
  const cvr = coverDeck / 1000;

  e.push(txt(totW / 2, top + 4.5, "CROSS-SECTION AT MID-SPAN", 0.60, "TEXT"));
  e.push(txt(totW / 2, top + 3.8, `SCALE 1:20  |  SLAB THICKNESS = ${(slabThickness * 1000).toFixed(0)}mm  |  TOTAL WIDTH = ${totW.toFixed(3)}m`, 0.30, "TEXT"));

  // Slab body
  e.push(closedPoly([[0, 0], [totW, 0], [totW, slabThickness], [0, slabThickness]], "STRUCTURE"));
  e.push(...hatchLines(0, 0, totW, slabThickness, 0.15, "HATCH"));
  // Wearing coat
  e.push(closedPoly([[0, slabThickness], [totW, slabThickness], [totW, top], [0, top]], "WEARING_COAT"));
  e.push(...hatchLines(0, slabThickness, totW, top, 0.08, "HATCH"));
  e.push(txt(totW / 2, slabThickness + wearingCoatThickness / 2, `WC ${(wearingCoatThickness * 1000).toFixed(0)}mm`, 0.20, "ANNOTATION"));

  // Haunches
  e.push(closedPoly([[0, 0], [bottomHaunchWidth, -bottomHaunchDepth], [totW - bottomHaunchWidth, -bottomHaunchDepth], [totW, 0]], "STRUCTURE"));
  e.push(...hatchLines(0, -bottomHaunchDepth, bottomHaunchWidth, 0, 0.12, "HATCH"));
  e.push(...hatchLines(totW - bottomHaunchWidth, -bottomHaunchDepth, totW, 0, 0.12, "HATCH"));

  // Left kerb
  const kL = footpathWidth + kerbWidth;
  e.push(closedPoly([[0, slabThickness], [kL, slabThickness], [kL, slabThickness + kerbHeight], [footpathWidth, slabThickness + kerbHeight], [footpathWidth, slabThickness], [0, slabThickness]], "STRUCTURE"));
  e.push(...hatchLines(0, slabThickness, kL, slabThickness + kerbHeight, 0.12, "HATCH"));
  // Right kerb
  e.push(closedPoly([[totW - kL, slabThickness], [totW, slabThickness], [totW, slabThickness + kerbHeight], [totW - footpathWidth, slabThickness + kerbHeight], [totW - footpathWidth, slabThickness], [totW - kL, slabThickness]], "STRUCTURE"));
  e.push(...hatchLines(totW - kL, slabThickness, totW, slabThickness + kerbHeight, 0.12, "HATCH"));

  // Guard rails
  if (inp.kerb) {
    e.push(ln(0, slabThickness + kerbHeight, 0, slabThickness + kerbHeight + guardrailHeight, "REBAR"));
    e.push(ln(totW, slabThickness + kerbHeight, totW, slabThickness + kerbHeight + guardrailHeight, "REBAR"));
    e.push(circle(0, slabThickness + kerbHeight + guardrailHeight, 0.04, "REBAR"));
    e.push(circle(totW, slabThickness + kerbHeight + guardrailHeight, 0.04, "REBAR"));
    e.push(txt(0, slabThickness + kerbHeight + guardrailHeight + 0.08, "RG", 0.20, "TEXT"));
    e.push(txt(totW, slabThickness + kerbHeight + guardrailHeight + 0.08, "RG", 0.20, "TEXT"));
  }

  // Bottom main bars
  const barY = cvr + mainBarDia / 2000;
  const nBars = Math.floor(totW / (mainBarSpacing / 1000)) + 1;
  for (let i = 0; i < nBars; i++) {
    const bx = i * (mainBarSpacing / 1000);
    if (bx <= totW) e.push(circle(bx, barY, mainBarDia / 2000, "REBAR"));
  }
  // Top bars
  const topBarY = slabThickness - cvr - topBarDia / 2000;
  const nTop = Math.floor(totW / (topBarSpacing / 1000)) + 1;
  for (let i = 0; i < nTop; i++) {
    const bx = i * (topBarSpacing / 1000);
    if (bx <= totW) e.push(circle(bx, topBarY, topBarDia / 2000, "REBAR"));
  }
  // Distribution bars (shown as dots at mid-depth)
  const distY = slabThickness / 2;
  for (let i = 0; i <= 4; i++) {
    e.push(circle(i * totW / 4, distY, distBarDia / 2000, "REBAR"));
  }

  // Rebar leaders
  e.push(ln(totW * 0.3, barY, totW + 1.5, barY - 0.3, "REBAR"));
  e.push(txtL(totW + 1.55, barY - 0.3, `T${mainBarDia} @ ${mainBarSpacing}mm c/c (MAIN BOTTOM)`, 0.25, "ANNOTATION"));
  e.push(ln(totW * 0.7, topBarY, totW + 1.5, topBarY + 0.3, "REBAR"));
  e.push(txtL(totW + 1.55, topBarY + 0.3, `T${topBarDia} @ ${topBarSpacing}mm c/c (TOP)`, 0.25, "ANNOTATION"));
  e.push(ln(totW * 0.5, distY, totW + 1.5, distY, "REBAR"));
  e.push(txtL(totW + 1.55, distY, `T${distBarDia} @ ${inp.distBarSpacing}mm c/c (DIST.)`, 0.25, "ANNOTATION"));

  // Cover annotations
  e.push(ln(cvr, 0, cvr, -0.3, "DIMENSIONS"));
  e.push(txtL(cvr + 0.05, -0.35, `COVER=${coverDeck}mm`, 0.20, "DIMENSIONS"));

  // Dimensions
  const dimY = -bottomHaunchDepth - 1.5;
  e.push(...dimH(0, 0, totW, dimY, "DIMENSIONS", `TOTAL WIDTH = ${totW.toFixed(3)}m`));
  e.push(...dimH(kL, 0, totW - kL, dimY - 1.2, "DIMENSIONS", `CARRIAGEWAY = ${carriageWidth.toFixed(2)}m`));
  e.push(...dimH(0, 0, footpathWidth, dimY - 2.4, "DIMENSIONS", `FP=${footpathWidth.toFixed(2)}m`));
  e.push(...dimH(footpathWidth, 0, kL, dimY - 2.4, "DIMENSIONS", `KERB=${kerbWidth.toFixed(2)}m`));
  e.push(...dimV(totW + 0.5, 0, slabThickness, totW + 1.0, "DIMENSIONS", `D=${(slabThickness * 1000).toFixed(0)}mm`));
  e.push(...dimV(totW + 0.5, -bottomHaunchDepth, 0, totW + 2.5, "DIMENSIONS", `HAUNCH=${(bottomHaunchDepth * 1000).toFixed(0)}mm`));

  // Section label
  e.push(txt(totW / 2, -bottomHaunchDepth - 0.5, "SECTION A-A", 0.35, "TEXT"));

  e.push(...ircNotesBlock(0, dimY - 3, concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation, designCode, loadClass));

  const tbX = -3, tbY = dimY - 17;
  e.push(...ircTitleBlock(tbX, tbY, {
    projectName, drawingTitle: "CROSS-SECTION AT MID-SPAN",
    drawingNo: `${drawingNo}/03`, scale: "1:20", location, sheetNo: "3", totalSheets: "8",
  }));

  return makeHeader([tbX - 1, tbY - 1, 0], [totW + 10, top + 6, 0]) + finalizeDxf(e);
}