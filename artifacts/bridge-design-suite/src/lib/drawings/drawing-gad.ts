import type { BridgeInput } from "../bridge-types";
import {
  makeHeader, finalizeDxf, txt, txtL, closedPoly, ln, circle,
  dimH, dimV, rlMarker, hatchLines, northArrow, scaleBar,
  ircTitleBlock, ircNotesBlock
} from "../dxf-helpers";

export function generateGAD(inp: BridgeInput): string {
  const {
    totalLength, spanLength, numberOfSpans, carriageWidth, footpathWidth,
    hfl, ofl, dwl, bedLevel, foundationLevel, rtl, agl,
    pierWidth, pierDepth, pierBaseWidth, pierCapHeight, pierCapWidth,
    abutmentWidth, abutmentBaseWidth, abutmentHeight, abutmentDepth,
    slabThickness, wearingCoatThickness, kerbHeight, kerbWidth,
    numberOfPiers, projectName, drawingNo, bridgeType,
    concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation,
    designCode, loadClass, location,
  } = inp;

  const e: string[] = [];
  const abt = abutmentWidth;
  const toY = (lv: number) => lv - (bedLevel - 2);

  const slabY   = toY(rtl);
  const hflY    = toY(hfl);
  const oflY    = toY(ofl);
  const dwlY    = toY(dwl);
  const bedY    = toY(bedLevel);
  const foundY  = toY(foundationLevel);
  const aglY    = toY(agl);
  const deckTop = slabY + slabThickness + wearingCoatThickness;
  const deckBot = slabY;

  //  Title 
  e.push(txt(abt + totalLength / 2, deckTop + 4.5,
    `GENERAL ARRANGEMENT DRAWING — ${bridgeType === "submersible" ? "SUBMERSIBLE" : "HIGH LEVEL"} RCC SLAB BRIDGE`, 0.65, "TEXT"));
  e.push(txt(abt + totalLength / 2, deckTop + 3.8,
    `ACROSS ${inp.riverName.toUpperCase()} — ${projectName.toUpperCase()}`, 0.45, "TEXT"));

  //  Deck spans 
  for (let i = 0; i < numberOfSpans; i++) {
    const x1 = abt + i * spanLength, x2 = abt + (i + 1) * spanLength;
    // Slab body
    e.push(closedPoly([[x1, deckBot], [x2, deckBot], [x2, deckTop - wearingCoatThickness], [x1, deckTop - wearingCoatThickness]], "STRUCTURE"));
    // Wearing coat
    e.push(closedPoly([[x1, deckTop - wearingCoatThickness], [x2, deckTop - wearingCoatThickness], [x2, deckTop], [x1, deckTop]], "WEARING_COAT"));
    // Hatch wearing coat
    e.push(...hatchLines(x1, deckTop - wearingCoatThickness, x2, deckTop, 0.3, "HATCH"));
    // Kerbs
    if (inp.kerb) {
      e.push(closedPoly([[x1, deckTop - wearingCoatThickness], [x1 + kerbWidth, deckTop - wearingCoatThickness], [x1 + kerbWidth, deckTop - wearingCoatThickness + kerbHeight], [x1, deckTop - wearingCoatThickness + kerbHeight]], "STRUCTURE"));
      e.push(closedPoly([[x2 - kerbWidth, deckTop - wearingCoatThickness], [x2, deckTop - wearingCoatThickness], [x2, deckTop - wearingCoatThickness + kerbHeight], [x2 - kerbWidth, deckTop - wearingCoatThickness + kerbHeight]], "STRUCTURE"));
    }
    // Span dimension
    e.push(...dimH(x1, deckTop, x2, deckTop + 1.2, "DIMENSIONS", `${spanLength.toFixed(2)}m`));
    // Span label
    e.push(txt((x1 + x2) / 2, deckBot + slabThickness / 2, `SPAN ${i + 1}`, 0.28, "TEXT"));
  }

  //  Total span dimension 
  e.push(...dimH(abt, deckTop, abt + totalLength, deckTop + 2.2, "DIMENSIONS",
    `TOTAL CLEAR SPAN = ${totalLength.toFixed(2)}m (${numberOfSpans} x ${spanLength.toFixed(2)}m)`));

  //  Abutments 
  // Left abutment
  e.push(closedPoly([[0, foundY], [abt, foundY], [abt, deckTop], [0, deckTop]], "ABUTMENTS"));
  e.push(...hatchLines(0, foundY, abt, deckTop, 0.4, "HATCH"));
  e.push(txt(abt / 2, (foundY + slabY) / 2, "ABT-L", 0.32, "TEXT"));
  // Right abutment
  const rx = abt + totalLength;
  e.push(closedPoly([[rx, foundY], [rx + abt, foundY], [rx + abt, deckTop], [rx, deckTop]], "ABUTMENTS"));
  e.push(...hatchLines(rx, foundY, rx + abt, deckTop, 0.4, "HATCH"));
  e.push(txt(rx + abt / 2, (foundY + slabY) / 2, "ABT-R", 0.32, "TEXT"));
  // Abutment footing
  const fOff = (abutmentBaseWidth - abt) / 2;
  e.push(closedPoly([[-fOff, foundY - abutmentDepth / 2], [abt + fOff, foundY - abutmentDepth / 2], [abt + fOff, foundY], [-fOff, foundY]], "ABUTMENTS"));
  e.push(closedPoly([[rx - fOff, foundY - abutmentDepth / 2], [rx + abt + fOff, foundY - abutmentDepth / 2], [rx + abt + fOff, foundY], [rx - fOff, foundY]], "ABUTMENTS"));

  //  Piers 
  for (let i = 1; i <= numberOfPiers; i++) {
    const px = abt + i * spanLength;
    // Pier cap
    e.push(closedPoly([[px - pierCapWidth / 2, deckBot - pierCapHeight], [px + pierCapWidth / 2, deckBot - pierCapHeight], [px + pierCapWidth / 2, deckBot], [px - pierCapWidth / 2, deckBot]], "PIERS"));
    e.push(...hatchLines(px - pierCapWidth / 2, deckBot - pierCapHeight, px + pierCapWidth / 2, deckBot, 0.35, "HATCH"));
    // Pier stem
    e.push(closedPoly([[px - pierWidth / 2, bedY], [px + pierWidth / 2, bedY], [px + pierWidth / 2, deckBot - pierCapHeight], [px - pierWidth / 2, deckBot - pierCapHeight]], "PIERS"));
    e.push(...hatchLines(px - pierWidth / 2, bedY, px + pierWidth / 2, deckBot - pierCapHeight, 0.35, "HATCH"));
    // Pier footing
    e.push(closedPoly([[px - pierBaseWidth / 2, foundY], [px + pierBaseWidth / 2, foundY], [px + pierBaseWidth / 2, bedY], [px - pierBaseWidth / 2, bedY]], "PIERS"));
    e.push(...hatchLines(px - pierBaseWidth / 2, foundY, px + pierBaseWidth / 2, bedY, 0.35, "HATCH"));
    e.push(txt(px, bedY + pierDepth / 2, `P${i}`, 0.30, "TEXT"));
  }

  //  Water levels 
  const lvlX1 = -4, lvlX2 = abt * 2 + totalLength + 4;
  e.push(ln(lvlX1, hflY, lvlX2, hflY, "WATER_LEVEL", "DASHED"));
  e.push(...rlMarker(lvlX1, hflY, hfl, "HFL", "WATER_LEVEL"));
  e.push(ln(lvlX1, oflY, lvlX2, oflY, "WATER_LEVEL", "DASHED"));
  e.push(...rlMarker(lvlX1, oflY, ofl, "OFL", "WATER_LEVEL"));
  e.push(ln(lvlX1, dwlY, lvlX2, dwlY, "WATER_LEVEL", "DASHED"));
  e.push(...rlMarker(lvlX1, dwlY, dwl, "DWL", "WATER_LEVEL"));
  e.push(ln(lvlX1, bedY, lvlX2, bedY, "STRUCTURE"));
  e.push(...rlMarker(lvlX1, bedY, bedLevel, "NBL", "ANNOTATION"));
  e.push(ln(lvlX1, aglY, lvlX2, aglY, "SOIL", "DASHED"));
  e.push(...rlMarker(lvlX1, aglY, agl, "AGL", "ANNOTATION"));
  e.push(ln(lvlX1, foundY, lvlX2, foundY, "SOIL", "DASHED"));
  e.push(...rlMarker(lvlX1, foundY, foundationLevel, "FL", "ANNOTATION"));
  e.push(...rlMarker(lvlX1, deckTop, rtl, "RTL", "ANNOTATION"));

  //  Ground hatching 
  for (let sx = lvlX1; sx <= lvlX2; sx += 0.5) {
    e.push(ln(sx, bedY, sx - 0.25, bedY - 0.35, "SOIL"));
  }

  //  Vertical dimension (bridge height) 
  const vdX = abt * 2 + totalLength + 5;
  e.push(...dimV(vdX - 0.5, foundY, deckTop, vdX, "DIMENSIONS",
    `H=${(rtl - foundationLevel).toFixed(2)}m`));

  //  Carriageway annotation 
  e.push(ln(abt, deckTop + 0.4, abt + totalLength, deckTop + 0.4, "DIMENSIONS", "DASHED"));
  e.push(txt(abt + totalLength / 2, deckTop + 0.55,
    `CARRIAGEWAY = ${carriageWidth.toFixed(2)}m + 2 x ${footpathWidth.toFixed(2)}m FOOTPATH`, 0.28, "ANNOTATION"));

  //  North arrow + scale bar 
  e.push(...northArrow(abt * 2 + totalLength + 6, deckTop + 2, "NORTH_ARROW"));
  e.push(...scaleBar(abt, foundY - 3, 10, "DIMENSIONS"));
  e.push(txt(abt + 5, foundY - 3.5, "SCALE 1:100", 0.28, "DIMENSIONS"));

  //  Notes 
  e.push(...ircNotesBlock(abt, foundY - 6, concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation, designCode, loadClass));

  //  Title block 
  const tbX = -5, tbY = foundY - 18;
  e.push(...ircTitleBlock(tbX, tbY, {
    projectName,
    drawingTitle: "GENERAL ARRANGEMENT DRAWING (ELEVATION)",
    drawingNo: `${drawingNo}/01`,
    scale: "1:100",
    location,
    sheetNo: "1",
    totalSheets: "12",
  }));

  const xMin = tbX - 1, xMax = vdX + 2;
  const yMin = tbY - 1, yMax = deckTop + 6;
  return makeHeader([xMin, yMin, 0], [xMax, yMax, 0]) + finalizeDxf(e);
}