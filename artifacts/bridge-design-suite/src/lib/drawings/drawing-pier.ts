import type { BridgeInput } from "../bridge-types";
import {
  makeHeader,
  finalizeDxf,
  txt,
  txtL,
  closedPoly,
  ln,
  circle,
  dimH,
  dimV,
  rlMarker,
  hatchLines,
  ircTitleBlock,
  ircNotesBlock,
} from "../dxf-helpers";
import { pierLayoutCtx, type PierLayoutCtx } from "./pier-layout";

const BRIDGE_TOTAL_SHEETS = "12";

function pierElevationConcrete(L: PierLayoutCtx): string[] {
  const { pierCapWidth, pierWidth, pierBaseWidth, pierCapHeight, deckBot, bedY, foundY } = L;
  const e: string[] = [];
  e.push(
    closedPoly(
      [
        [-pierCapWidth / 2, deckBot - pierCapHeight],
        [pierCapWidth / 2, deckBot - pierCapHeight],
        [pierCapWidth / 2, deckBot],
        [-pierCapWidth / 2, deckBot],
      ],
      "PIERS",
    ),
  );
  e.push(...hatchLines(-pierCapWidth / 2, deckBot - pierCapHeight, pierCapWidth / 2, deckBot, 0.25, "HATCH"));
  e.push(txt(0, deckBot - pierCapHeight / 2, "PIER CAP", 0.28, "TEXT"));
  e.push(
    closedPoly(
      [
        [-pierWidth / 2, bedY],
        [pierWidth / 2, bedY],
        [pierWidth / 2, deckBot - pierCapHeight],
        [-pierWidth / 2, deckBot - pierCapHeight],
      ],
      "PIERS",
    ),
  );
  e.push(...hatchLines(-pierWidth / 2, bedY, pierWidth / 2, deckBot - pierCapHeight, 0.25, "HATCH"));
  e.push(
    closedPoly(
      [
        [-pierBaseWidth / 2, foundY],
        [pierBaseWidth / 2, foundY],
        [pierBaseWidth / 2, bedY],
        [-pierBaseWidth / 2, bedY],
      ],
      "PIERS",
    ),
  );
  e.push(...hatchLines(-pierBaseWidth / 2, foundY, pierBaseWidth / 2, bedY, 0.25, "HATCH"));
  return e;
}

function pierFoundationAndLevels(L: PierLayoutCtx): string[] {
  const { pierBaseWidth, foundY, hflY, bedY, deckBot, hfl, bedLevel, foundationLevel, rtl } = L;
  const e: string[] = [];
  e.push(ln(-pierBaseWidth / 2 - 0.5, foundY, pierBaseWidth / 2 + 0.5, foundY, "SOIL", "DASHED"));
  for (let sx = -pierBaseWidth / 2 - 0.5; sx <= pierBaseWidth / 2 + 0.5; sx += 0.35) {
    e.push(ln(sx, foundY, sx - 0.2, foundY - 0.3, "SOIL"));
  }
  e.push(ln(-5, hflY, 5, hflY, "WATER_LEVEL", "DASHED"));
  e.push(...rlMarker(-5, hflY, hfl, "HFL", "WATER_LEVEL"));
  e.push(...rlMarker(-5, bedY, bedLevel, "NBL", "ANNOTATION"));
  e.push(...rlMarker(-5, foundY, foundationLevel, "FL", "ANNOTATION"));
  e.push(...rlMarker(-5, deckBot, rtl, "RTL", "ANNOTATION"));
  return e;
}

function pierRebarElevationDashed(L: PierLayoutCtx): string[] {
  const { pierWidth, pierMainBarCount, pierLinksSpacing, cvr, mainBarR, bedY, deckBot, pierCapHeight } = L;
  const e: string[] = [];
  for (let i = 0; i < pierMainBarCount; i++) {
    const angle = (i / pierMainBarCount) * 2 * Math.PI;
    const bx = ((pierWidth / 2 - cvr - mainBarR) * Math.cos(angle));
    e.push(ln(bx, bedY, bx, deckBot - pierCapHeight, "REBAR", "DASHED"));
  }
  let ly = bedY;
  while (ly <= deckBot - pierCapHeight) {
    e.push(ln(-pierWidth / 2, ly, pierWidth / 2, ly, "REBAR", "DASHED"));
    ly += pierLinksSpacing / 1000;
  }
  return e;
}

function pierElevationDimensions(L: PierLayoutCtx): string[] {
  const { pierBaseWidth, pierWidth, pierCapWidth, pierCapHeight, dX, foundY, deckBot, bedY, pierH } = L;
  const e: string[] = [];
  e.push(...dimV(dX - 0.5, foundY, deckBot, dX, "DIMENSIONS", `H=${pierH.toFixed(2)}m`));
  e.push(...dimV(dX + 1.5, bedY, deckBot - pierCapHeight, dX + 2, "DIMENSIONS", `STEM=${(deckBot - pierCapHeight - bedY).toFixed(2)}m`));
  e.push(...dimH(-pierBaseWidth / 2, foundY, pierBaseWidth / 2, foundY - 1.2, "DIMENSIONS", `${pierBaseWidth.toFixed(2)}m (FOOTING WIDTH)`));
  e.push(...dimH(-pierWidth / 2, bedY, pierWidth / 2, bedY - 1.2, "DIMENSIONS", `${pierWidth.toFixed(2)}m (STEM WIDTH)`));
  e.push(...dimH(-pierCapWidth / 2, deckBot, pierCapWidth / 2, deckBot + 0.8, "DIMENSIONS", `${pierCapWidth.toFixed(2)}m (CAP WIDTH)`));
  e.push(...dimV(-dX, deckBot - pierCapHeight, deckBot, -dX - 0.5, "DIMENSIONS", `CAP H=${(pierCapHeight * 1000).toFixed(0)}mm`));
  return e;
}

function pierFootingLengthCallout(L: PierLayoutCtx): string[] {
  const { pierBaseLength, foundY } = L;
  const e: string[] = [];
  const y = foundY - 2.0;
  e.push(
    txt(
      0,
      y,
      `PIER FOOTING LENGTH (OUT-TO-OUT) = ${pierBaseLength.toFixed(2)}m  (SEE FOUNDATION PLAN IF ISSUED SEPARATELY)`,
      0.26,
      "TEXT",
    ),
  );
  return e;
}

function pierSectionAA(L: PierLayoutCtx): string[] {
  const { xsOX, xsOY, pierWidth, pierLength, cvr, mainBarR, pierMainBarCount, coverStem } = L;
  const e: string[] = [];
  e.push(txt(xsOX, xsOY + pierLength / 2 + 2.0, "PIER — SHEET 3 OF 4 — SECTION 01 — CROSS-SECTION A-A (AT MID-HEIGHT)", 0.36, "TEXT"));
  e.push(txt(xsOX, xsOY + pierLength / 2 + 1.5, `${(pierWidth * 1000).toFixed(0)} x ${(pierLength * 1000).toFixed(0)}mm`, 0.3, "TEXT"));
  e.push(
    closedPoly(
      [
        [xsOX - pierWidth / 2, xsOY - pierLength / 2],
        [xsOX + pierWidth / 2, xsOY - pierLength / 2],
        [xsOX + pierWidth / 2, xsOY + pierLength / 2],
        [xsOX - pierWidth / 2, xsOY + pierLength / 2],
      ],
      "PIERS",
    ),
  );
  e.push(...hatchLines(xsOX - pierWidth / 2, xsOY - pierLength / 2, xsOX + pierWidth / 2, xsOY + pierLength / 2, 0.18, "HATCH"));
  e.push(
    closedPoly(
      [
        [xsOX - pierWidth / 2 + cvr, xsOY - pierLength / 2 + cvr],
        [xsOX + pierWidth / 2 - cvr, xsOY - pierLength / 2 + cvr],
        [xsOX + pierWidth / 2 - cvr, xsOY + pierLength / 2 - cvr],
        [xsOX - pierWidth / 2 + cvr, xsOY + pierLength / 2 - cvr],
      ],
      "REBAR",
    ),
  );
  for (let i = 0; i < pierMainBarCount; i++) {
    const angle = (i / pierMainBarCount) * 2 * Math.PI;
    const bx = xsOX + (pierWidth / 2 - cvr - mainBarR * 2) * Math.cos(angle);
    const by = xsOY + (pierLength / 2 - cvr - mainBarR * 2) * Math.sin(angle);
    e.push(circle(bx, by, mainBarR, "REBAR"));
  }
  e.push(...dimH(xsOX - pierWidth / 2, xsOY - pierLength / 2, xsOX + pierWidth / 2, xsOY - pierLength / 2 - 1.0, "DIMENSIONS", `${(pierWidth * 1000).toFixed(0)}mm`));
  e.push(...dimV(xsOX + pierWidth / 2, xsOY - pierLength / 2, xsOY + pierLength / 2, xsOX + pierWidth / 2 + 1.5, "DIMENSIONS", `${(pierLength * 1000).toFixed(0)}mm`));
  e.push(ln(xsOX - pierWidth / 2, xsOY, xsOX - pierWidth / 2 + cvr, xsOY, "DIMENSIONS"));
  e.push(txtL(xsOX - pierWidth / 2 + cvr + 0.05, xsOY + 0.05, `COVER=${coverStem}mm`, 0.2, "DIMENSIONS"));
  return e;
}

function pierBBS(L: PierLayoutCtx): string[] {
  const {
    inp: { pierMainBarDia, pierMainBarCount, pierLinksDia, pierWidth, pierLength, pierLinksSpacing },
    pierH,
    bbsX,
    bbsY,
  } = L;
  const e: string[] = [];
  e.push(txt(bbsX + 8, bbsY + 0.5, "REINFORCEMENT — BAR BENDING SCHEDULE (PIER STEM & CAP)", 0.38, "TEXT"));
  const hdrs = ["MARK", "DIA (mm)", "NOS.", "LENGTH (m)", "SHAPE", "REMARKS"];
  const hW = 3.5;
  hdrs.forEach((h, i) => {
    e.push(closedPoly([[bbsX + i * hW, bbsY - 0.7], [bbsX + (i + 1) * hW, bbsY - 0.7], [bbsX + (i + 1) * hW, bbsY], [bbsX + i * hW, bbsY]], "TITLEBLOCK"));
    e.push(txt(bbsX + i * hW + hW / 2, bbsY - 0.45, h, 0.22, "TEXT"));
  });
  const bars = [
    ["V1", `${pierMainBarDia}`, `${pierMainBarCount}`, `${(pierH + 0.6).toFixed(2)}`, "STRAIGHT", "MAIN VERT. BARS"],
    ["L1", `${pierLinksDia}`, "AS REQ.", `${(2 * (pierWidth + pierLength) + 0.3).toFixed(2)}`, "RECT. LINK", `@ ${pierLinksSpacing}mm c/c`],
    ["C1", `${pierLinksDia}`, "AS REQ.", `${(pierWidth * 1.1).toFixed(2)}`, "STRAIGHT", "PIER CAP BARS"],
  ];
  bars.forEach((row, ri) => {
    const ry = bbsY - 0.7 - (ri + 1) * 0.65;
    row.forEach((cell, ci) => {
      e.push(closedPoly([[bbsX + ci * hW, ry], [bbsX + (ci + 1) * hW, ry], [bbsX + (ci + 1) * hW, ry + 0.65], [bbsX + ci * hW, ry + 0.65]], "TITLEBLOCK"));
      e.push(txt(bbsX + ci * hW + hW / 2, ry + 0.18, cell, 0.22, "TEXT"));
    });
  });
  return e;
}

function pierHeaderBounds(L: PierLayoutCtx): { min: [number, number, number]; max: [number, number, number] } {
  const { tbX, tbY, xsOX, pierWidth, deckBot } = L;
  return { min: [tbX - 1, tbY - 1, 0], max: [xsOX + pierWidth + 6, deckBot + 6, 0] };
}

/** @deprecated Prefer the four `generatePierSheet*` exports; kept for scripts that still expect one combined pier DXF. */
export function generatePierDrawing(inp: BridgeInput): string {
  const L = pierLayoutCtx(inp);
  const {
    inp: {
      concreteGrade,
      steelGrade,
      coverDeck,
      coverFoundation,
      designCode,
      loadClass,
      projectName,
      drawingNo,
      location,
      pierWidth,
      pierLength,
    },
  } = L;

  const e: string[] = [];
  e.push(txt(0, L.deckBot + 4.5, "PIER DETAILS — ELEVATION, SECTION & BAR SCHEDULE (COMBINED SHEET)", 0.55, "TEXT"));
  e.push(
    txt(
      0,
      L.deckBot + 3.8,
      `PIER DIMENSIONS: ${pierWidth.toFixed(2)}m x ${pierLength.toFixed(2)}m  |  CONCRETE: ${concreteGrade}  |  STEEL: ${steelGrade}`,
      0.3,
      "TEXT",
    ),
  );
  e.push(...pierElevationConcrete(L));
  e.push(...pierFoundationAndLevels(L));
  e.push(...pierRebarElevationDashed(L));
  e.push(...pierElevationDimensions(L));
  e.push(...pierSectionAA(L));
  e.push(...pierBBS(L));
  e.push(...ircNotesBlock(L.bbsX, L.bbsY - 5, concreteGrade, steelGrade, coverDeck, L.coverStem, coverFoundation, designCode, loadClass));
  e.push(
    ...ircTitleBlock(L.tbX, L.tbY, {
      projectName,
      drawingTitle: "PIER — COMBINED (GA, DIMENSIONS, SECTION 01, REINFORCEMENT)",
      drawingNo: `${drawingNo}/04-COMBINED`,
      scale: "1:50",
      location,
      sheetNo: "4",
      totalSheets: BRIDGE_TOTAL_SHEETS,
    }),
  );
  const { min, max } = pierHeaderBounds(L);
  return makeHeader(min, max) + finalizeDxf(e);
}

/** Pier sheet 1 of 4 — general arrangement & elevation (concrete + levels, no rebar schedule). */
export function generatePierSheet01GeneralArrangementElevation(inp: BridgeInput): string {
  const L = pierLayoutCtx(inp);
  const { projectName, drawingNo, location, concreteGrade, steelGrade } = L.inp;
  const { pierWidth, pierLength } = L;

  const e: string[] = [];
  e.push(txt(0, L.deckBot + 4.5, "PIER — SHEET 1 OF 4 — GENERAL ARRANGEMENT & ELEVATION", 0.55, "TEXT"));
  e.push(
    txt(
      0,
      L.deckBot + 3.8,
      `STEM ${pierWidth.toFixed(2)}m x ${pierLength.toFixed(2)}m  |  CONCRETE: ${concreteGrade}  |  STEEL: ${steelGrade}`,
      0.28,
      "TEXT",
    ),
  );
  e.push(...pierElevationConcrete(L));
  e.push(...pierFoundationAndLevels(L));
  e.push(
    ...ircTitleBlock(L.tbX, L.tbY, {
      projectName,
      drawingTitle: "PIER — GENERAL ARRANGEMENT & ELEVATION",
      drawingNo: `${drawingNo}/PIER-01`,
      scale: "1:50",
      location,
      sheetNo: "4",
      totalSheets: BRIDGE_TOTAL_SHEETS,
    }),
  );
  const { min, max } = pierHeaderBounds(L);
  return makeHeader(min, max) + finalizeDxf(e);
}

/** Pier sheet 2 of 4 — dimension details (elevation + footing length note). */
export function generatePierSheet02DimensionDetails(inp: BridgeInput): string {
  const L = pierLayoutCtx(inp);
  const { projectName, drawingNo, location } = L.inp;

  const e: string[] = [];
  e.push(txt(0, L.deckBot + 4.5, "PIER — SHEET 2 OF 4 — DIMENSION DETAILS", 0.55, "TEXT"));
  e.push(txt(0, L.deckBot + 3.85, "ALL DIMENSIONS IN METRES UNLESS NOTED", 0.26, "TEXT"));
  e.push(...pierElevationConcrete(L));
  e.push(...pierFoundationAndLevels(L));
  e.push(...pierElevationDimensions(L));
  e.push(...pierFootingLengthCallout(L));
  e.push(
    ...ircTitleBlock(L.tbX, L.tbY, {
      projectName,
      drawingTitle: "PIER — DIMENSION DETAILS",
      drawingNo: `${drawingNo}/PIER-02`,
      scale: "1:50",
      location,
      sheetNo: "5",
      totalSheets: BRIDGE_TOTAL_SHEETS,
    }),
  );
  const { min, max } = pierHeaderBounds(L);
  return makeHeader(min, max) + finalizeDxf(e);
}

/** Pier sheet 3 of 4 — section 01 (cross-section A-A). */
export function generatePierSheet03Section01(inp: BridgeInput): string {
  const L = pierLayoutCtx(inp);
  const { projectName, drawingNo, location, concreteGrade, steelGrade, coverDeck, coverFoundation, designCode, loadClass } = L.inp;

  const e: string[] = [];
  e.push(...pierSectionAA(L));
  e.push(...ircNotesBlock(L.bbsX, L.bbsY - 5, concreteGrade, steelGrade, coverDeck, L.coverStem, coverFoundation, designCode, loadClass));
  e.push(
    ...ircTitleBlock(L.tbX, L.tbY, {
      projectName,
      drawingTitle: "PIER — SECTION 01 — CROSS-SECTION A-A",
      drawingNo: `${drawingNo}/PIER-03`,
      scale: "1:25",
      location,
      sheetNo: "6",
      totalSheets: BRIDGE_TOTAL_SHEETS,
    }),
  );
  const { min, max } = pierHeaderBounds(L);
  return makeHeader(min, max) + finalizeDxf(e);
}

/** Pier sheet 4 of 4 — reinforcement & bar bending schedule. */
export function generatePierSheet04Reinforcement(inp: BridgeInput): string {
  const L = pierLayoutCtx(inp);
  const {
    projectName,
    drawingNo,
    location,
    concreteGrade,
    steelGrade,
    coverDeck,
    coverFoundation,
    designCode,
    loadClass,
  } = L.inp;

  const e: string[] = [];
  e.push(txt(0, L.deckBot + 4.5, "PIER — SHEET 4 OF 4 — REINFORCEMENT DETAILS", 0.55, "TEXT"));
  e.push(txt(0, L.deckBot + 3.85, "ELEVATION: MAIN VERTICALS & LINKS (SCHEMATIC)", 0.28, "TEXT"));
  e.push(...pierElevationConcrete(L));
  e.push(...pierFoundationAndLevels(L));
  e.push(...pierRebarElevationDashed(L));
  e.push(...pierBBS(L));
  e.push(...ircNotesBlock(L.bbsX, L.bbsY - 5, concreteGrade, steelGrade, coverDeck, L.coverStem, coverFoundation, designCode, loadClass));
  e.push(
    ...ircTitleBlock(L.tbX, L.tbY, {
      projectName,
      drawingTitle: "PIER — REINFORCEMENT & BAR BENDING SCHEDULE",
      drawingNo: `${drawingNo}/PIER-04`,
      scale: "1:50",
      location,
      sheetNo: "7",
      totalSheets: BRIDGE_TOTAL_SHEETS,
    }),
  );
  const { min, max } = pierHeaderBounds(L);
  return makeHeader(min, max) + finalizeDxf(e);
}
