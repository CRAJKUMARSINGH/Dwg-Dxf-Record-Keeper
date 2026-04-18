import type { BridgeInput } from "../bridge-types";
import { makeHeader, finalizeDxf, txt, txtL, closedPoly, ln, circle, dimH, dimV, rlMarker, hatchLines, ircTitleBlock, ircNotesBlock } from "../dxf-helpers";

export function generateAbutmentDrawing(inp: BridgeInput): string {
  const { abutmentHeight, abutmentWidth, abutmentBaseWidth, abutmentDepth, dirtWallHeight,
    returnWallLength, wingWallAngle, slabThickness, hfl, bedLevel, foundationLevel, rtl, agl,
    coverStem, coverFoundation, mainBarDia, mainBarSpacing, distBarDia, distBarSpacing,
    concreteGrade, steelGrade, coverDeck, designCode, loadClass, projectName, drawingNo, location } = inp;

  const e: string[] = [];
  const toY = (lv: number) => lv - (foundationLevel - 0.5);
  const abutH = rtl - foundationLevel;
  const topY = toY(rtl), bedY = toY(bedLevel), aglY = toY(agl);
  const foundY = toY(foundationLevel), hflY = toY(hfl);
  const deckTop = topY + slabThickness;
  const cvr = coverStem / 1000;

  e.push(txt(abutmentBaseWidth/2, deckTop + 4.5, "ABUTMENT DETAILS — ELEVATION, PLAN & REINFORCEMENT", 0.60, "TEXT"));
  e.push(txt(abutmentBaseWidth/2, deckTop + 3.8, `ABUTMENT HEIGHT = ${abutH.toFixed(2)}m  |  BASE WIDTH = ${abutmentBaseWidth.toFixed(2)}m  |  CONCRETE: ${concreteGrade}`, 0.30, "TEXT"));

  //  ELEVATION 
  // Deck slab (partial)
  e.push(closedPoly([[0, topY], [abutmentWidth, topY+slabThickness], [abutmentWidth, topY], [0, topY]], "STRUCTURE"));
  e.push(...hatchLines(0, topY, abutmentWidth, topY+slabThickness, 0.15, "HATCH"));
  e.push(txt(abutmentWidth/2, topY+slabThickness/2, "DECK SLAB", 0.22, "TEXT"));
  // Abutment cap
  e.push(closedPoly([[0, topY-0.3], [abutmentWidth+abutmentDepth, topY-0.3], [abutmentWidth+abutmentDepth, topY], [0, topY]], "ABUTMENTS"));
  e.push(...hatchLines(0, topY-0.3, abutmentWidth+abutmentDepth, topY, 0.12, "HATCH"));
  e.push(txt((abutmentWidth+abutmentDepth)/2, topY-0.15, "ABUTMENT CAP", 0.20, "TEXT"));
  // Stem
  e.push(closedPoly([[abutmentWidth, foundY], [abutmentWidth+abutmentDepth, foundY], [abutmentWidth+abutmentDepth, topY-0.3], [abutmentWidth, topY-0.3]], "ABUTMENTS"));
  e.push(...hatchLines(abutmentWidth, foundY, abutmentWidth+abutmentDepth, topY-0.3, 0.25, "HATCH"));
  e.push(txt(abutmentWidth+abutmentDepth/2, (foundY+topY)/2, "STEM", 0.28, "TEXT"));
  // Base slab
  e.push(closedPoly([[0, foundY], [abutmentBaseWidth, foundY], [abutmentBaseWidth, foundY+abutmentDepth/2], [0, foundY+abutmentDepth/2]], "ABUTMENTS"));
  e.push(...hatchLines(0, foundY, abutmentBaseWidth, foundY+abutmentDepth/2, 0.25, "HATCH"));
  e.push(txt(abutmentBaseWidth/2, foundY+abutmentDepth/4, "BASE SLAB", 0.28, "TEXT"));
  // Dirt wall
  e.push(closedPoly([[abutmentWidth+abutmentDepth, topY-dirtWallHeight], [abutmentWidth+abutmentDepth+0.3, topY-dirtWallHeight], [abutmentWidth+abutmentDepth+0.3, topY], [abutmentWidth+abutmentDepth, topY]], "ABUTMENTS"));
  e.push(...hatchLines(abutmentWidth+abutmentDepth, topY-dirtWallHeight, abutmentWidth+abutmentDepth+0.3, topY, 0.12, "HATCH"));
  e.push(txt(abutmentWidth+abutmentDepth+0.15, topY-dirtWallHeight/2, "DW", 0.20, "TEXT"));
  // Approach slab (dashed)
  e.push(closedPoly([[abutmentWidth+abutmentDepth+0.3, topY-0.3], [abutmentWidth+abutmentDepth+3.5, topY-0.3], [abutmentWidth+abutmentDepth+3.5, topY], [abutmentWidth+abutmentDepth+0.3, topY]], "HIDDEN", "DASHED"));
  e.push(txt(abutmentWidth+abutmentDepth+2, topY-0.15, "APPROACH SLAB", 0.20, "HIDDEN"));

  // Levels
  const lvX = -4;
  e.push(ln(lvX, hflY, abutmentBaseWidth+4, hflY, "WATER_LEVEL", "DASHED"));
  e.push(...rlMarker(lvX, hflY, hfl, "HFL", "WATER_LEVEL"));
  e.push(ln(lvX, bedY, abutmentBaseWidth+4, bedY, "STRUCTURE"));
  e.push(...rlMarker(lvX, bedY, bedLevel, "NBL", "ANNOTATION"));
  e.push(ln(lvX, aglY, abutmentBaseWidth+4, aglY, "SOIL", "DASHED"));
  e.push(...rlMarker(lvX, aglY, agl, "AGL", "ANNOTATION"));
  e.push(ln(lvX, foundY, abutmentBaseWidth+4, foundY, "SOIL"));
  e.push(...rlMarker(lvX, foundY, foundationLevel, "FL", "ANNOTATION"));
  e.push(...rlMarker(lvX, topY, rtl, "RTL", "ANNOTATION"));
  // Ground hatching
  for (let sx = lvX; sx <= abutmentBaseWidth+4; sx += 0.4) {
    e.push(ln(sx, foundY, sx-0.2, foundY-0.3, "SOIL"));
  }

  // Reinforcement bars in stem
  const nBars = Math.floor(abutmentDepth / (mainBarSpacing/1000));
  for (let i = 0; i <= nBars; i++) {
    const bx = abutmentWidth + cvr + mainBarDia/2000;
    const by = foundY + i*(mainBarSpacing/1000);
    if (by <= topY) e.push(circle(bx, by, mainBarDia/2000, "REBAR"));
  }
  const nDist = Math.floor(abutH / (distBarSpacing/1000));
  for (let i = 0; i <= nDist; i++) {
    const bx = abutmentBaseWidth - cvr - distBarDia/2000;
    const by = foundY + i*(distBarSpacing/1000);
    if (by <= topY) e.push(circle(bx, by, distBarDia/2000, "REBAR"));
  }

  // Dimensions
  const dY = foundY - 1.5;
  e.push(...dimH(0, foundY, abutmentBaseWidth, dY, "DIMENSIONS", `BASE = ${abutmentBaseWidth.toFixed(2)}m`));
  e.push(...dimH(abutmentWidth, foundY, abutmentWidth+abutmentDepth, dY-1.2, "DIMENSIONS", `STEM = ${(abutmentDepth*1000).toFixed(0)}mm`));
  const dX = abutmentBaseWidth + 2;
  e.push(...dimV(dX-0.5, foundY, topY, dX, "DIMENSIONS", `H=${abutH.toFixed(2)}m`));
  e.push(...dimV(dX+1.5, topY-dirtWallHeight, topY, dX+2, "DIMENSIONS", `DW=${(dirtWallHeight*1000).toFixed(0)}mm`));

  //  PLAN AT FOUNDATION 
  const planOY = foundY - 8;
  e.push(txt(abutmentBaseWidth/2, planOY+returnWallLength+2.5, "PLAN AT FOUNDATION LEVEL", 0.40, "TEXT"));
  e.push(closedPoly([[0, planOY], [abutmentBaseWidth, planOY], [abutmentBaseWidth, planOY+returnWallLength], [0, planOY+returnWallLength]], "ABUTMENTS"));
  e.push(...hatchLines(0, planOY, abutmentBaseWidth, planOY+returnWallLength, 0.3, "HATCH"));
  // Wing walls
  const angle = (wingWallAngle * Math.PI) / 180;
  const wwLen = returnWallLength;
  e.push(ln(0, planOY, -wwLen*Math.cos(angle), planOY-wwLen*Math.sin(angle), "ABUTMENTS"));
  e.push(ln(abutmentBaseWidth, planOY, abutmentBaseWidth+wwLen*Math.cos(angle), planOY-wwLen*Math.sin(angle), "ABUTMENTS"));
  e.push(txt(abutmentBaseWidth/2, planOY-1.2, `WING WALLS @ ${wingWallAngle}`, 0.28, "TEXT"));
  // Plan dimensions
  e.push(...dimH(0, planOY, abutmentBaseWidth, planOY-1.8, "DIMENSIONS", `${abutmentBaseWidth.toFixed(2)}m`));
  e.push(...dimV(abutmentBaseWidth+1, planOY, planOY+returnWallLength, abutmentBaseWidth+1.5, "DIMENSIONS", `${returnWallLength.toFixed(2)}m`));

  //  BAR SCHEDULE 
  const bbsX = 0, bbsY = planOY - 4;
  e.push(txt(bbsX+8, bbsY+0.5, "BAR BENDING SCHEDULE — ABUTMENT", 0.38, "TEXT"));
  const hdrs = ["MARK", "DIA (mm)", "NOS.", "LENGTH (m)", "SHAPE", "REMARKS"];
  const hW = 3.5;
  hdrs.forEach((h, i) => {
    e.push(closedPoly([[bbsX+i*hW, bbsY-0.7], [bbsX+(i+1)*hW, bbsY-0.7], [bbsX+(i+1)*hW, bbsY], [bbsX+i*hW, bbsY]], "TITLEBLOCK"));
    e.push(txt(bbsX+i*hW+hW/2, bbsY-0.45, h, 0.22, "TEXT"));
  });
  const bars = [
    ["A1", `${mainBarDia}`, "AS REQ.", `${(abutH+0.5).toFixed(2)}`, "STRAIGHT", `MAIN @ ${mainBarSpacing}mm c/c`],
    ["A2", `${distBarDia}`, "AS REQ.", `${(abutmentBaseWidth+0.3).toFixed(2)}`, "STRAIGHT", `DIST @ ${distBarSpacing}mm c/c`],
    ["A3", `12`, "AS REQ.", `${(abutmentBaseWidth*2+returnWallLength*2+0.3).toFixed(2)}`, "RECT.", "S&T REINF @ 125mm c/c"],
  ];
  bars.forEach((row, ri) => {
    const ry = bbsY - 0.7 - (ri+1)*0.65;
    row.forEach((cell, ci) => {
      e.push(closedPoly([[bbsX+ci*hW, ry], [bbsX+(ci+1)*hW, ry], [bbsX+(ci+1)*hW, ry+0.65], [bbsX+ci*hW, ry+0.65]], "TITLEBLOCK"));
      e.push(txt(bbsX+ci*hW+hW/2, ry+0.18, cell, 0.22, "TEXT"));
    });
  });

  e.push(...ircNotesBlock(bbsX, bbsY-5, concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation, designCode, loadClass));

  const tbX = -6, tbY = planOY - 22;
  e.push(...ircTitleBlock(tbX, tbY, {
    projectName, drawingTitle: "ABUTMENT DETAILS — ELEVATION, PLAN & REINFORCEMENT",
    drawingNo: `${drawingNo}/05`, scale: "1:50", location, sheetNo: "5", totalSheets: "8",
  }));

  return makeHeader([tbX-1, tbY-1, 0], [abutmentBaseWidth+8, deckTop+6, 0]) + finalizeDxf(e);
}