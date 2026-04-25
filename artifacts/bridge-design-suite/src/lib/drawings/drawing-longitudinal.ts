import type { BridgeInput } from "../bridge-types";
import { makeHeader, finalizeDxf, txt, txtL, closedPoly, ln, circle, dimH, dimV, rlMarker, hatchLines, northArrow, scaleBar, ircTitleBlock, ircNotesBlock } from "../dxf-helpers";

export function generateLongitudinalSection(inp: BridgeInput): string {
  const { totalLength, spanLength, numberOfSpans, slabThickness, wearingCoatThickness,
    pierWidth, pierCapHeight, pierCapWidth, pierBaseWidth, abutmentWidth,
    mainBarDia, mainBarSpacing, topBarDia, topBarSpacing, stirrupDia, stirrupSpacing,
    coverDeck, hfl, ofl, bedLevel, foundationLevel, rtl, agl, numberOfPiers,
    concreteGrade, steelGrade, coverStem, coverFoundation, designCode, loadClass,
    projectName, drawingNo, location } = inp;

  const e: string[] = [];
  const toY = (lv: number) => lv - (foundationLevel - 0.5);
  const deckBot = toY(rtl), deckTop = deckBot+slabThickness, wcTop = deckTop+wearingCoatThickness;
  const bedY = toY(bedLevel), foundY = toY(foundationLevel), hflY = toY(hfl), oflY = toY(ofl);
  const abt = abutmentWidth;
  const cvr = coverDeck/1000;

  e.push(txt(abt+totalLength/2, wcTop+4.5, "LONGITUDINAL SECTION THROUGH CENTRE LINE", 0.60, "TEXT"));
  e.push(txt(abt+totalLength/2, wcTop+3.8, `SCALE 1:100  |  ${numberOfSpans} SPANS @ ${spanLength.toFixed(2)}m = ${totalLength.toFixed(2)}m TOTAL`, 0.30, "TEXT"));

  //  Deck spans 
  for (let i = 0; i < numberOfSpans; i++) {
    const x1 = abt+i*spanLength, x2 = abt+(i+1)*spanLength;
    // Slab
    e.push(closedPoly([[x1,deckBot],[x2,deckBot],[x2,deckTop],[x1,deckTop]], "STRUCTURE"));
    e.push(...hatchLines(x1, deckBot, x2, deckTop, 0.25, "HATCH"));
    // Wearing coat
    e.push(closedPoly([[x1,deckTop],[x2,deckTop],[x2,wcTop],[x1,wcTop]], "WEARING_COAT"));
    e.push(...hatchLines(x1, deckTop, x2, wcTop, 0.12, "HATCH"));
    // Rebar in section
    const mainBarY = deckBot+cvr+mainBarDia/2000;
    const nMain = Math.floor(spanLength/(mainBarSpacing/1000));
    for (let b = 0; b <= nMain; b++) {
      const bx = x1+b*(mainBarSpacing/1000);
      if (bx <= x2) e.push(circle(bx, mainBarY, mainBarDia/2000, "REBAR"));
    }
    const topBarY = deckTop-cvr-topBarDia/2000;
    const nTop = Math.floor(spanLength/(topBarSpacing/1000));
    for (let b = 0; b <= nTop; b++) {
      const bx = x1+b*(topBarSpacing/1000);
      if (bx <= x2) e.push(circle(bx, topBarY, topBarDia/2000, "REBAR"));
    }
    // Stirrups
    const nStir = Math.floor(spanLength/(stirrupSpacing/1000));
    for (let b = 0; b <= nStir; b++) {
      const sx = x1+b*(stirrupSpacing/1000);
      if (sx <= x2) e.push(ln(sx, deckBot+cvr, sx, deckTop-cvr, "REBAR"));
    }
    // Span label
    e.push(txt((x1+x2)/2, deckBot+slabThickness/2, `SPAN ${i+1}`, 0.28, "TEXT"));
    // Span dimension
    e.push(...dimH(x1, wcTop, x2, wcTop+1.0, "DIMENSIONS", `${spanLength.toFixed(2)}m`));
  }
  // Total span dimension
  e.push(...dimH(abt, wcTop, abt+totalLength, wcTop+2.0, "DIMENSIONS", `TOTAL = ${totalLength.toFixed(2)}m`));

  //  Abutments 
  e.push(closedPoly([[0,foundY],[abt,foundY],[abt,deckTop],[0,deckTop]], "ABUTMENTS"));
  e.push(...hatchLines(0, foundY, abt, deckTop, 0.3, "HATCH"));
  e.push(txt(abt/2, (foundY+deckBot)/2, "ABT\nA1", 0.28, "TEXT"));
  const rx = abt+totalLength;
  e.push(closedPoly([[rx,foundY],[rx+abt,foundY],[rx+abt,deckTop],[rx,deckTop]], "ABUTMENTS"));
  e.push(...hatchLines(rx, foundY, rx+abt, deckTop, 0.3, "HATCH"));
  e.push(txt(rx+abt/2, (foundY+deckBot)/2, "ABT\nA2", 0.28, "TEXT"));

  //  Piers 
  for (let i = 1; i <= numberOfPiers; i++) {
    const px = abt+i*spanLength;
    e.push(closedPoly([[px-pierCapWidth/2,deckBot-pierCapHeight],[px+pierCapWidth/2,deckBot-pierCapHeight],[px+pierCapWidth/2,deckBot],[px-pierCapWidth/2,deckBot]], "PIERS"));
    e.push(...hatchLines(px-pierCapWidth/2, deckBot-pierCapHeight, px+pierCapWidth/2, deckBot, 0.2, "HATCH"));
    e.push(closedPoly([[px-pierWidth/2,bedY],[px+pierWidth/2,bedY],[px+pierWidth/2,deckBot-pierCapHeight],[px-pierWidth/2,deckBot-pierCapHeight]], "PIERS"));
    e.push(...hatchLines(px-pierWidth/2, bedY, px+pierWidth/2, deckBot-pierCapHeight, 0.2, "HATCH"));
    e.push(closedPoly([[px-pierBaseWidth/2,foundY],[px+pierBaseWidth/2,foundY],[px+pierBaseWidth/2,bedY],[px-pierBaseWidth/2,bedY]], "PIERS"));
    e.push(...hatchLines(px-pierBaseWidth/2, foundY, px+pierBaseWidth/2, bedY, 0.2, "HATCH"));
    e.push(txt(px, (foundY+bedY)/2, `P${i}`, 0.28, "TEXT"));
  }

  //  Levels 
  const lvX1 = -3, lvX2 = abt*2+totalLength+3;
  e.push(ln(lvX1, hflY, lvX2, hflY, "WATER_LEVEL", "DASHED"));
  e.push(...rlMarker(lvX1, hflY, hfl, "HFL", "WATER_LEVEL"));
  e.push(ln(lvX1, oflY, lvX2, oflY, "WATER_LEVEL", "DASHED"));
  e.push(...rlMarker(lvX1, oflY, ofl, "OFL", "WATER_LEVEL"));
  e.push(ln(lvX1, bedY, lvX2, bedY, "STRUCTURE"));
  e.push(...rlMarker(lvX1, bedY, bedLevel, "NBL", "ANNOTATION"));
  e.push(ln(lvX1, foundY, lvX2, foundY, "SOIL"));
  e.push(...rlMarker(lvX1, foundY, foundationLevel, "FL", "ANNOTATION"));
  e.push(...rlMarker(lvX1, deckBot, rtl, "RTL", "ANNOTATION"));
  e.push(...rlMarker(lvX1, wcTop, rtl+wearingCoatThickness, "FRL", "ANNOTATION"));
  // Ground hatching
  for (let sx = lvX1; sx <= lvX2; sx += 0.4) {
    e.push(ln(sx, foundY, sx-0.2, foundY-0.3, "SOIL"));
  }

  //  Vertical dimensions 
  const vdX = abt*2+totalLength+5;
  e.push(...dimV(vdX-0.5, foundY, wcTop, vdX, "DIMENSIONS", `TOTAL H=${(rtl+wearingCoatThickness-foundationLevel).toFixed(2)}m`));
  e.push(...dimV(vdX+2, deckBot, deckTop, vdX+2.5, "DIMENSIONS", `D=${(slabThickness*1000).toFixed(0)}mm`));

  //  Rebar annotation 
  e.push(txtL(abt, wcTop+3.2, `BOTTOM: T${mainBarDia}@${mainBarSpacing}mm c/c  |  TOP: T${topBarDia}@${topBarSpacing}mm c/c  |  STIRRUPS: T${stirrupDia}@${stirrupSpacing}mm c/c`, 0.28, "ANNOTATION"));

  //  North arrow + scale 
  e.push(...northArrow(abt*2+totalLength+7, wcTop+2, "NORTH_ARROW"));
  e.push(...scaleBar(abt, foundY-2, 10, "DIMENSIONS"));
  e.push(txt(abt+5, foundY-2.5, "SCALE 1:100", 0.28, "DIMENSIONS"));

  e.push(...ircNotesBlock(abt, foundY-5, concreteGrade, steelGrade, coverDeck, coverStem, coverFoundation, designCode, loadClass));

  const tbX = -5, tbY = foundY - 18;
  e.push(...ircTitleBlock(tbX, tbY, {
    projectName, drawingTitle: "LONGITUDINAL SECTION THROUGH CENTRE LINE",
    drawingNo: `${drawingNo}/08`, scale: "1:100", location, sheetNo: "11", totalSheets: "12",
  }));

  return makeHeader([tbX-1, tbY-1, 0], [vdX+4, wcTop+6, 0]) + finalizeDxf(e);
}