import type { BridgeInput } from "../bridge-types";
import { makeHeader, finalizeDxf, txt, txtL, closedPoly, ln, circle, dimH, dimV, northArrow, scaleBar, ircTitleBlock, ircNotesBlock } from "../dxf-helpers";

export function generatePlanView(inp: BridgeInput): string {
  const { totalLength, spanLength, numberOfSpans, carriageWidth, footpathWidth, kerbWidth, numberOfLanes,
    pierWidth, pierLength, pierBaseLength, pierBaseWidth, numberOfPiers, abutmentWidth,
    projectName, drawingNo, location, concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation, designCode, loadClass } = inp;

  const e: string[] = [];
  const abt = abutmentWidth;
  const totW = carriageWidth + 2 * (footpathWidth + kerbWidth);
  const cwY1 = footpathWidth + kerbWidth, cwY2 = totW - footpathWidth - kerbWidth;

  e.push(txt(abt + totalLength / 2, totW + 5, "PLAN VIEW — TOP OF BRIDGE DECK", 0.60, "TEXT"));
  e.push(txt(abt + totalLength / 2, totW + 4.3, `TOTAL WIDTH = ${totW.toFixed(3)}m  |  CARRIAGEWAY = ${carriageWidth.toFixed(2)}m  |  ${numberOfLanes} LANES`, 0.32, "TEXT"));

  // Outer deck boundary
  e.push(closedPoly([[-abt, 0], [totalLength + 2 * abt, 0], [totalLength + 2 * abt, totW], [-abt, totW]], "STRUCTURE"));
  // Carriageway boundary
  e.push(closedPoly([[0, cwY1], [totalLength, cwY1], [totalLength, cwY2], [0, cwY2]], "STRUCTURE"));
  // Kerb lines
  e.push(ln(0, footpathWidth, totalLength, footpathWidth, "STRUCTURE"));
  e.push(ln(0, totW - footpathWidth, totalLength, totW - footpathWidth, "STRUCTURE"));

  // Labels
  e.push(txt(abt + totalLength / 2, cwY1 + (cwY2 - cwY1) / 2, `CARRIAGEWAY ${carriageWidth.toFixed(2)}m (${numberOfLanes} LANES)`, 0.38, "TEXT"));
  e.push(txt(-abt / 2, footpathWidth / 2, "FP", 0.28, "TEXT"));
  e.push(txt(totalLength + abt * 1.5, footpathWidth / 2, "FP", 0.28, "TEXT"));
  e.push(txt(-abt / 2, totW - footpathWidth / 2, "FP", 0.28, "TEXT"));
  e.push(txt(totalLength + abt * 1.5, totW - footpathWidth / 2, "FP", 0.28, "TEXT"));
  e.push(txt(-abt / 2, cwY1 + (cwY2 - cwY1) / 2, "KERB", 0.22, "TEXT"));
  e.push(txt(totalLength + abt * 1.2, cwY1 + (cwY2 - cwY1) / 2, "KERB", 0.22, "TEXT"));

  // Piers
  for (let i = 1; i <= numberOfPiers; i++) {
    const px = i * spanLength;
    const py = (totW - pierBaseLength) / 2;
    e.push(closedPoly([[px - pierBaseWidth / 2, py], [px + pierBaseWidth / 2, py], [px + pierBaseWidth / 2, py + pierBaseLength], [px - pierBaseWidth / 2, py + pierBaseLength]], "PIERS"));
    // Pier cap outline (dashed)
    e.push(closedPoly([[px - pierWidth / 2 - 0.1, py - 0.1], [px + pierWidth / 2 + 0.1, py - 0.1], [px + pierWidth / 2 + 0.1, py + pierBaseLength + 0.1], [px - pierWidth / 2 - 0.1, py + pierBaseLength + 0.1]], "HIDDEN", "DASHED"));
    e.push(txt(px, py + pierBaseLength / 2, `P${i}`, 0.30, "TEXT"));
    // Pier dimension
    e.push(...dimH(px - pierBaseWidth / 2, py, px + pierBaseWidth / 2, py - 1.0, "DIMENSIONS", `${pierBaseWidth.toFixed(2)}m`));
  }

  // Centerlines
  for (let i = 0; i <= numberOfSpans; i++) {
    e.push(ln(i * spanLength, -0.8, i * spanLength, totW + 0.8, "CENTERLINE", "CENTER"));
  }
  e.push(ln(-abt - 0.5, totW / 2, totalLength + abt + 0.5, totW / 2, "CENTERLINE", "CENTER"));
  e.push(txt(totalLength + abt + 0.8, totW / 2, "C/L", 0.25, "CENTERLINE"));

  // Span dimensions
  for (let i = 0; i < numberOfSpans; i++) {
    const x1 = i * spanLength, x2 = (i + 1) * spanLength;
    e.push(...dimH(x1, 0, x2, -1.5, "DIMENSIONS", `${spanLength.toFixed(2)}m`));
  }
  e.push(...dimH(0, 0, totalLength, -2.8, "DIMENSIONS", `TOTAL = ${totalLength.toFixed(2)}m`));

  // Width dimensions
  const wdX = totalLength + abt + 2;
  e.push(...dimV(wdX - 0.5, 0, totW, wdX, "DIMENSIONS", `${totW.toFixed(3)}m`));
  e.push(...dimV(wdX + 1.5, cwY1, cwY2, wdX + 2, "DIMENSIONS", `CW=${carriageWidth.toFixed(2)}m`));

  // Abutment labels
  e.push(txt(-abt / 2, totW / 2, "ABUTMENT\nA1", 0.30, "ABUTMENTS"));
  e.push(txt(totalLength + abt * 1.5, totW / 2, "ABUTMENT\nA2", 0.30, "ABUTMENTS"));

  // North arrow
  e.push(...northArrow(totalLength + abt + 5, totW + 2, "NORTH_ARROW"));
  e.push(...scaleBar(0, -4.5, 10, "DIMENSIONS"));
  e.push(txt(5, -5.0, "SCALE 1:100", 0.28, "DIMENSIONS"));

  e.push(...ircNotesBlock(0, -6, concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation, designCode, loadClass));

  const tbX = -abt - 3, tbY = -20;
  e.push(...ircTitleBlock(tbX, tbY, {
    projectName, drawingTitle: "PLAN VIEW — TOP OF BRIDGE DECK",
    drawingNo: `${drawingNo}/02`, scale: "1:100", location, sheetNo: "2", totalSheets: "8",
  }));

  return makeHeader([tbX - 1, tbY - 1, 0], [totalLength + abt * 2 + 8, totW + 7, 0]) + finalizeDxf(e);
}