import type { BridgeInput } from "../bridge-types";
import { makeHeader, finalizeDxf, txt, txtL, closedPoly, ln, circle, dimH, dimV, rlMarker, hatchLines, ircTitleBlock, ircNotesBlock } from "../dxf-helpers";

export function generateWingWallDrawing(inp: BridgeInput): string {
  const { returnWallLength, wingWallAngle, abutmentBaseWidth, coverStem,
    mainBarDia, mainBarSpacing, distBarDia, distBarSpacing,
    hfl, bedLevel, foundationLevel, rtl, agl,
    concreteGrade, steelGrade, coverDeck, coverFoundation, designCode, loadClass,
    projectName, drawingNo, location } = inp;

  const e: string[] = [];
  const toY = (lv: number) => lv - (foundationLevel - 0.5);
  const topY = toY(rtl), foundY = toY(foundationLevel), hflY = toY(hfl), bedY = toY(bedLevel);
  const angle = (wingWallAngle * Math.PI) / 180;
  const wwThk = 0.30, abtW = abutmentBaseWidth;
  const cvr = coverStem / 1000;

  e.push(txt(abtW/2, topY+4.5, "WING WALL & RETURN WALL DETAILS", 0.60, "TEXT"));
  e.push(txt(abtW/2, topY+3.8, `WING WALL ANGLE = ${wingWallAngle}  |  RETURN WALL LENGTH = ${returnWallLength.toFixed(2)}m  |  THICKNESS = ${(wwThk*1000).toFixed(0)}mm`, 0.30, "TEXT"));

  //  ELEVATION 
  // Abutment body (reference)
  e.push(closedPoly([[0, foundY], [abtW, foundY], [abtW, topY], [0, topY]], "ABUTMENTS"));
  e.push(...hatchLines(0, foundY, abtW, topY, 0.3, "HATCH"));
  e.push(txt(abtW/2, (foundY+topY)/2, "ABUTMENT", 0.30, "TEXT"));
  // Wing wall (angled)
  const wx2 = abtW + returnWallLength*Math.cos(angle);
  const wy2 = topY - returnWallLength*Math.sin(angle);
  e.push(closedPoly([[abtW, topY], [wx2, wy2], [wx2+wwThk*Math.cos(Math.PI/2-angle), wy2-wwThk*Math.sin(Math.PI/2-angle)], [abtW+wwThk, topY]], "ABUTMENTS"));
  e.push(...hatchLines(abtW, wy2, wx2, topY, 0.2, "HATCH"));
  e.push(txt((abtW+wx2)/2+0.3, (topY+wy2)/2, "WING WALL", 0.28, "TEXT"));
  // Return wall (vertical)
  e.push(closedPoly([[-wwThk, topY], [0, topY], [0, topY-returnWallLength], [-wwThk, topY-returnWallLength]], "ABUTMENTS"));
  e.push(...hatchLines(-wwThk, topY-returnWallLength, 0, topY, 0.2, "HATCH"));
  e.push(txt(-wwThk-1.2, (topY+topY-returnWallLength)/2, "RETURN\nWALL", 0.25, "TEXT"));

  // Levels
  const lvX = -4;
  e.push(ln(lvX, hflY, abtW+returnWallLength+2, hflY, "WATER_LEVEL", "DASHED"));
  e.push(...rlMarker(lvX, hflY, hfl, "HFL", "WATER_LEVEL"));
  e.push(ln(lvX, bedY, abtW+returnWallLength+2, bedY, "STRUCTURE"));
  e.push(...rlMarker(lvX, bedY, bedLevel, "NBL", "ANNOTATION"));
  e.push(ln(lvX, foundY, abtW+returnWallLength+2, foundY, "SOIL"));
  e.push(...rlMarker(lvX, foundY, foundationLevel, "FL", "ANNOTATION"));
  e.push(...rlMarker(lvX, topY, rtl, "RTL", "ANNOTATION"));
  for (let sx = lvX; sx <= abtW+returnWallLength+2; sx += 0.4) {
    e.push(ln(sx, foundY, sx-0.2, foundY-0.3, "SOIL"));
  }

  // Reinforcement in return wall
  const nBars = Math.floor(returnWallLength/(mainBarSpacing/1000));
  for (let i = 0; i <= nBars; i++) {
    const by = topY - i*(mainBarSpacing/1000);
    if (by >= topY-returnWallLength) e.push(circle(-wwThk+cvr+mainBarDia/2000, by, mainBarDia/2000, "REBAR"));
  }

  // Dimensions
  e.push(...dimH(abtW, topY, wx2, topY+1.2, "DIMENSIONS", `${returnWallLength.toFixed(2)}m`));
  e.push(...dimV(-wwThk-1.5, topY-returnWallLength, topY, -wwThk-2, "DIMENSIONS", `${returnWallLength.toFixed(2)}m`));
  e.push(...dimH(-wwThk, topY, 0, topY+0.8, "DIMENSIONS", `${(wwThk*1000).toFixed(0)}mm`));
  e.push(...dimV(abtW+returnWallLength+1, foundY, topY, abtW+returnWallLength+1.5, "DIMENSIONS", `H=${(rtl-foundationLevel).toFixed(2)}m`));

  //  PLAN VIEW 
  const planOY = foundY - 8;
  e.push(txt(abtW/2, planOY+abtW+2.5, "PLAN VIEW (AT FOUNDATION LEVEL)", 0.40, "TEXT"));
  e.push(closedPoly([[0, planOY], [abtW, planOY], [abtW, planOY+abtW], [0, planOY+abtW]], "ABUTMENTS"));
  e.push(...hatchLines(0, planOY, abtW, planOY+abtW, 0.3, "HATCH"));
  // Wing walls in plan
  const planWW2x = abtW + returnWallLength*Math.cos(angle);
  const planWW2y = planOY - returnWallLength*Math.sin(angle);
  e.push(ln(abtW, planOY, planWW2x, planWW2y, "ABUTMENTS"));
  e.push(ln(abtW, planOY+abtW, planWW2x, planWW2y+abtW*Math.cos(angle), "ABUTMENTS"));
  // Return walls in plan
  e.push(ln(0, planOY, -returnWallLength, planOY, "ABUTMENTS"));
  e.push(ln(0, planOY+abtW, -returnWallLength, planOY+abtW, "ABUTMENTS"));
  // Angle annotation
  e.push(txt(abtW+returnWallLength*0.4, planOY-0.5, `WING WALL @ ${wingWallAngle}`, 0.28, "ANNOTATION"));
  e.push(txt(-returnWallLength/2, planOY-0.5, `RETURN WALL (${returnWallLength.toFixed(2)}m)`, 0.28, "ANNOTATION"));
  // Plan dimensions
  e.push(...dimH(0, planOY, abtW, planOY-1.5, "DIMENSIONS", `${abtW.toFixed(2)}m`));
  e.push(...dimH(-returnWallLength, planOY, 0, planOY-1.5, "DIMENSIONS", `${returnWallLength.toFixed(2)}m`));

  //  NOTES 
  const notesX = 0, notesY = planOY - 4;
  e.push(txtL(notesX, notesY, `MAIN BARS: T${mainBarDia} @ ${mainBarSpacing}mm c/c (BOTH FACES)`, 0.25, "ANNOTATION"));
  e.push(txtL(notesX, notesY-0.4, `DIST. BARS: T${distBarDia} @ ${distBarSpacing}mm c/c`, 0.25, "ANNOTATION"));
  e.push(txtL(notesX, notesY-0.8, `CLEAR COVER: ${coverStem}mm`, 0.25, "ANNOTATION"));
  e.push(txtL(notesX, notesY-1.2, `CONCRETE: ${concreteGrade}  |  STEEL: ${steelGrade}`, 0.25, "ANNOTATION"));

  e.push(...ircNotesBlock(notesX, notesY-2, concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation, designCode, loadClass));

  const tbX = -6, tbY = planOY - 20;
  e.push(...ircTitleBlock(tbX, tbY, {
    projectName, drawingTitle: "WING WALL & RETURN WALL DETAILS",
    drawingNo: `${drawingNo}/07`, scale: "1:50", location, sheetNo: "7", totalSheets: "8",
  }));

  return makeHeader([tbX-1, tbY-1, 0], [abtW+returnWallLength+6, topY+6, 0]) + finalizeDxf(e);
}