import type { BridgeInput } from "../bridge-types";
import { makeHeader, finalizeDxf, txt, txtL, closedPoly, ln, circle, dimH, dimV, rlMarker, hatchLines, ircTitleBlock, ircNotesBlock } from "../dxf-helpers";

export function generatePierDrawing(inp: BridgeInput): string {
  const { pierWidth, pierLength, pierDepth, pierBaseWidth, pierBaseLength, pierCapHeight, pierCapWidth,
    pierMainBarDia, pierMainBarCount, pierLinksDia, pierLinksSpacing, coverStem,
    hfl, bedLevel, foundationLevel, rtl, concreteGrade, steelGrade,
    coverDeck, coverFoundation, designCode, loadClass, projectName, drawingNo, location } = inp;

  const e: string[] = [];
  const toY = (lv: number) => lv - (foundationLevel - 1);
  const deckBot = toY(rtl), bedY = toY(bedLevel), foundY = toY(foundationLevel), hflY = toY(hfl);
  const pierH = deckBot - foundY;
  const cvr = coverStem / 1000;

  e.push(txt(0, deckBot + 4.5, "PIER DETAILS — ELEVATION, SECTION & BAR SCHEDULE", 0.60, "TEXT"));
  e.push(txt(0, deckBot + 3.8, `PIER DIMENSIONS: ${pierWidth.toFixed(2)}m x ${pierLength.toFixed(2)}m  |  CONCRETE: ${concreteGrade}  |  STEEL: ${steelGrade}`, 0.30, "TEXT"));

  //  ELEVATION (left side) 
  // Pier cap
  e.push(closedPoly([[-pierCapWidth/2, deckBot-pierCapHeight], [pierCapWidth/2, deckBot-pierCapHeight], [pierCapWidth/2, deckBot], [-pierCapWidth/2, deckBot]], "PIERS"));
  e.push(...hatchLines(-pierCapWidth/2, deckBot-pierCapHeight, pierCapWidth/2, deckBot, 0.25, "HATCH"));
  e.push(txt(0, deckBot - pierCapHeight/2, "PIER CAP", 0.28, "TEXT"));
  // Pier stem
  e.push(closedPoly([[-pierWidth/2, bedY], [pierWidth/2, bedY], [pierWidth/2, deckBot-pierCapHeight], [-pierWidth/2, deckBot-pierCapHeight]], "PIERS"));
  e.push(...hatchLines(-pierWidth/2, bedY, pierWidth/2, deckBot-pierCapHeight, 0.25, "HATCH"));
  // Pier footing
  e.push(closedPoly([[-pierBaseWidth/2, foundY], [pierBaseWidth/2, foundY], [pierBaseWidth/2, bedY], [-pierBaseWidth/2, bedY]], "PIERS"));
  e.push(...hatchLines(-pierBaseWidth/2, foundY, pierBaseWidth/2, bedY, 0.25, "HATCH"));
  // Foundation line
  e.push(ln(-pierBaseWidth/2 - 0.5, foundY, pierBaseWidth/2 + 0.5, foundY, "SOIL", "DASHED"));
  for (let sx = -pierBaseWidth/2 - 0.5; sx <= pierBaseWidth/2 + 0.5; sx += 0.35) {
    e.push(ln(sx, foundY, sx - 0.2, foundY - 0.3, "SOIL"));
  }
  // Water level
  e.push(ln(-5, hflY, 5, hflY, "WATER_LEVEL", "DASHED"));
  e.push(...rlMarker(-5, hflY, hfl, "HFL", "WATER_LEVEL"));
  e.push(...rlMarker(-5, bedY, bedLevel, "NBL", "ANNOTATION"));
  e.push(...rlMarker(-5, foundY, foundationLevel, "FL", "ANNOTATION"));
  e.push(...rlMarker(-5, deckBot, rtl, "RTL", "ANNOTATION"));
  // Rebar in elevation (vertical bars shown dashed)
  const mainBarR = pierMainBarDia / 2000;
  for (let i = 0; i < pierMainBarCount; i++) {
    const angle = (i / pierMainBarCount) * 2 * Math.PI;
    const bx = (pierWidth/2 - cvr - mainBarR) * Math.cos(angle);
    e.push(ln(bx, bedY, bx, deckBot - pierCapHeight, "REBAR", "DASHED"));
  }
  // Links shown as horizontal dashed lines
  let ly = bedY;
  while (ly <= deckBot - pierCapHeight) {
    e.push(ln(-pierWidth/2, ly, pierWidth/2, ly, "REBAR", "DASHED"));
    ly += pierLinksSpacing / 1000;
  }

  //  DIMENSIONS (elevation) 
  const dX = pierBaseWidth/2 + 2;
  e.push(...dimV(dX - 0.5, foundY, deckBot, dX, "DIMENSIONS", `H=${pierH.toFixed(2)}m`));
  e.push(...dimV(dX + 1.5, bedY, deckBot - pierCapHeight, dX + 2, "DIMENSIONS", `STEM=${(deckBot-pierCapHeight-bedY).toFixed(2)}m`));
  e.push(...dimH(-pierBaseWidth/2, foundY, pierBaseWidth/2, foundY - 1.2, "DIMENSIONS", `${pierBaseWidth.toFixed(2)}m (FOOTING)`));
  e.push(...dimH(-pierWidth/2, bedY, pierWidth/2, bedY - 1.2, "DIMENSIONS", `${pierWidth.toFixed(2)}m (STEM)`));
  e.push(...dimH(-pierCapWidth/2, deckBot, pierCapWidth/2, deckBot + 0.8, "DIMENSIONS", `${pierCapWidth.toFixed(2)}m (CAP)`));
  e.push(...dimV(-dX, deckBot - pierCapHeight, deckBot, -dX - 0.5, "DIMENSIONS", `CAP H=${(pierCapHeight*1000).toFixed(0)}mm`));

  //  CROSS-SECTION A-A (right side) 
  const xsOX = pierBaseWidth + 7;
  const xsOY = bedY + (deckBot - bedY) / 2;
  e.push(txt(xsOX, xsOY + pierLength/2 + 2.0, "SECTION A-A (AT MID-HEIGHT)", 0.38, "TEXT"));
  e.push(txt(xsOX, xsOY + pierLength/2 + 1.5, `${(pierWidth*1000).toFixed(0)} x ${(pierLength*1000).toFixed(0)}mm`, 0.30, "TEXT"));
  // Section outline
  e.push(closedPoly([[xsOX-pierWidth/2, xsOY-pierLength/2], [xsOX+pierWidth/2, xsOY-pierLength/2], [xsOX+pierWidth/2, xsOY+pierLength/2], [xsOX-pierWidth/2, xsOY+pierLength/2]], "PIERS"));
  e.push(...hatchLines(xsOX-pierWidth/2, xsOY-pierLength/2, xsOX+pierWidth/2, xsOY+pierLength/2, 0.18, "HATCH"));
  // Cover rectangle
  e.push(closedPoly([[xsOX-pierWidth/2+cvr, xsOY-pierLength/2+cvr], [xsOX+pierWidth/2-cvr, xsOY-pierLength/2+cvr], [xsOX+pierWidth/2-cvr, xsOY+pierLength/2-cvr], [xsOX-pierWidth/2+cvr, xsOY+pierLength/2-cvr]], "REBAR"));
  // Main bars
  for (let i = 0; i < pierMainBarCount; i++) {
    const angle = (i / pierMainBarCount) * 2 * Math.PI;
    const bx = xsOX + (pierWidth/2 - cvr - mainBarR*2) * Math.cos(angle);
    const by = xsOY + (pierLength/2 - cvr - mainBarR*2) * Math.sin(angle);
    e.push(circle(bx, by, mainBarR, "REBAR"));
  }
  // Section dimensions
  e.push(...dimH(xsOX-pierWidth/2, xsOY-pierLength/2, xsOX+pierWidth/2, xsOY-pierLength/2-1.0, "DIMENSIONS", `${(pierWidth*1000).toFixed(0)}mm`));
  e.push(...dimV(xsOX+pierWidth/2, xsOY-pierLength/2, xsOY+pierLength/2, xsOX+pierWidth/2+1.5, "DIMENSIONS", `${(pierLength*1000).toFixed(0)}mm`));
  // Cover annotation
  e.push(ln(xsOX-pierWidth/2, xsOY, xsOX-pierWidth/2+cvr, xsOY, "DIMENSIONS"));
  e.push(txtL(xsOX-pierWidth/2+cvr+0.05, xsOY+0.05, `COVER=${coverStem}mm`, 0.20, "DIMENSIONS"));

  //  BAR BENDING SCHEDULE 
  const bbsX = -pierBaseWidth/2, bbsY = foundY - 3;
  e.push(txt(bbsX + 8, bbsY + 0.5, "BAR BENDING SCHEDULE — PIER", 0.38, "TEXT"));
  const hdrs = ["MARK", "DIA (mm)", "NOS.", "LENGTH (m)", "SHAPE", "REMARKS"];
  const hW = 3.5;
  hdrs.forEach((h, i) => {
    e.push(closedPoly([[bbsX+i*hW, bbsY-0.7], [bbsX+(i+1)*hW, bbsY-0.7], [bbsX+(i+1)*hW, bbsY], [bbsX+i*hW, bbsY]], "TITLEBLOCK"));
    e.push(txt(bbsX+i*hW+hW/2, bbsY-0.45, h, 0.22, "TEXT"));
  });
  const bars = [
    ["V1", `${pierMainBarDia}`, `${pierMainBarCount}`, `${(pierH + 0.6).toFixed(2)}`, "STRAIGHT", "MAIN VERT. BARS"],
    ["L1", `${pierLinksDia}`, "AS REQ.", `${(2*(pierWidth+pierLength)+0.3).toFixed(2)}`, "RECT. LINK", `@ ${pierLinksSpacing}mm c/c`],
    ["C1", `${pierLinksDia}`, "AS REQ.", `${(pierWidth*1.1).toFixed(2)}`, "STRAIGHT", "PIER CAP BARS"],
  ];
  bars.forEach((row, ri) => {
    const ry = bbsY - 0.7 - (ri+1)*0.65;
    row.forEach((cell, ci) => {
      e.push(closedPoly([[bbsX+ci*hW, ry], [bbsX+(ci+1)*hW, ry], [bbsX+(ci+1)*hW, ry+0.65], [bbsX+ci*hW, ry+0.65]], "TITLEBLOCK"));
      e.push(txt(bbsX+ci*hW+hW/2, ry+0.18, cell, 0.22, "TEXT"));
    });
  });

  e.push(...ircNotesBlock(bbsX, bbsY - 5, concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation, designCode, loadClass));

  const tbX = -pierBaseWidth/2 - 5, tbY = foundY - 22;
  e.push(...ircTitleBlock(tbX, tbY, {
    projectName, drawingTitle: "PIER DETAILS — ELEVATION, SECTION & BAR SCHEDULE",
    drawingNo: `${drawingNo}/04`, scale: "1:50", location, sheetNo: "4", totalSheets: "8",
  }));

  return makeHeader([tbX-1, tbY-1, 0], [xsOX+pierWidth+6, deckBot+6, 0]) + finalizeDxf(e);
}