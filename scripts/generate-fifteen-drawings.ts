import { mkdirSync, writeFileSync } from "fs";
import { join } from "path";

import type { BridgeInput } from "../artifacts/bridge-design-suite/src/lib/bridge-types";
import { DEFAULT_BRIDGE_INPUT } from "../artifacts/bridge-design-suite/src/lib/bridge-types";
import { generateGAD } from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-gad";
import { generatePlanView } from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-plan";
import { generateCrossSection } from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-xsection";
import {
  generatePierSheet01GeneralArrangementElevation,
  generatePierSheet02DimensionDetails,
  generatePierSheet03Section01,
  generatePierSheet04Reinforcement,
} from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-pier";
import { generateAbutmentDrawing } from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-abutment";
import { generateDeckRebarDrawing } from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-deck-rebar";
import { generateWingWallDrawing } from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-wingwall";
import { generateLongitudinalSection } from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-longitudinal";
import { generateBedProtection } from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-bed-protection";

const kherwaraInp: BridgeInput = {
  projectName: "SUBMERSIBLE BRIDGE ACROSS RIVER SOM",
  drawingNo: "PWD/RAJ/KHW/BR/001",
  location: "KHERWARA-JAWAS-SUVERI ROAD KM 9/000 KHERWARA RAJASTHAN",
  riverName: "SOM RIVER",
  bridgeType: "submersible",
  loadClass: "IRC CLASS 70-R / CLASS-A (2 LANES)",
  designCode: "IRC SP-13:2004 / IRC:6-2017 / IRC:112-2020 / IRC:78-2014",
  spanLength: 8.8,
  numberOfSpans: 9,
  totalLength: 79.2,
  numberOfPiers: 8,
  carriageWidth: 8.4,
  numberOfLanes: 2,
  footpathWidth: 0,
  kerbWidth: 0.225,
  kerbHeight: 0.225,
  guardrailHeight: 0,
  rtl: 101.6,
  hfl: 100.6,
  ofl: 97.6,
  dwl: 97.6,
  bedLevel: 96.47,
  foundationLevel: 93.47,
  agl: 96.6,
  discharge: 899.93,
  manningN: 0.033,
  afflux: 0.15,
  slabThickness: 0.75,
  wearingCoatThickness: 0.075,
  kerb: true,
  bottomHaunchDepth: 0.15,
  bottomHaunchWidth: 0.2,
  dirtWallHeight: 0.75,
  pierWidth: 1.2,
  pierLength: 3.8,
  pierDepth: 4,
  pierBaseWidth: 3.8,
  pierBaseLength: 12,
  pierCapHeight: 1.2,
  pierCapWidth: 2,
  pierMainBarDia: 20,
  pierMainBarCount: 16,
  pierLinksDia: 10,
  pierLinksSpacing: 200,
  abutmentHeight: 5.13,
  abutmentWidth: 1.05,
  abutmentBaseWidth: 8.05,
  abutmentDepth: 1,
  returnWallLength: 4.5,
  wingWallAngle: 45,
  mainBarDia: 20,
  mainBarSpacing: 125,
  distBarDia: 12,
  distBarSpacing: 200,
  topBarDia: 12,
  topBarSpacing: 200,
  stirrupDia: 10,
  stirrupSpacing: 200,
  coverDeck: 40,
  coverStem: 50,
  coverFoundation: 75,
  concreteGrade: "M30",
  steelGrade: "Fe415",
  fck: 30,
  fy: 415,
  soilType: "Medium hard rock",
  sbc: 200,
  phi: 30,
};

type GenRow = { file: string; fn: () => string };

const fullSet = (prefix: string, inp: BridgeInput): GenRow[] => [
  { file: `${prefix}_DRG-01_GAD_ELEVATION.dxf`, fn: () => generateGAD(inp) },
  { file: `${prefix}_DRG-02_PLAN_VIEW.dxf`, fn: () => generatePlanView(inp) },
  { file: `${prefix}_DRG-03_CROSS_SECTION.dxf`, fn: () => generateCrossSection(inp) },
  { file: `${prefix}_DRG-04_PIER-01_GA_ELEVATION.dxf`, fn: () => generatePierSheet01GeneralArrangementElevation(inp) },
  { file: `${prefix}_DRG-05_PIER-02_DIMENSIONS.dxf`, fn: () => generatePierSheet02DimensionDetails(inp) },
  { file: `${prefix}_DRG-06_PIER-03_SECTION-01.dxf`, fn: () => generatePierSheet03Section01(inp) },
  { file: `${prefix}_DRG-07_PIER-04_REINFORCEMENT.dxf`, fn: () => generatePierSheet04Reinforcement(inp) },
  { file: `${prefix}_DRG-08_ABUTMENT_DETAILS.dxf`, fn: () => generateAbutmentDrawing(inp) },
  { file: `${prefix}_DRG-09_DECK_REBAR_BBS.dxf`, fn: () => generateDeckRebarDrawing(inp) },
  { file: `${prefix}_DRG-10_WING_WALL.dxf`, fn: () => generateWingWallDrawing(inp) },
  { file: `${prefix}_DRG-11_LONGITUDINAL_SECTION.dxf`, fn: () => generateLongitudinalSection(inp) },
  { file: `${prefix}_DRG-12_BED_PROTECTION.dxf`, fn: () => generateBedProtection(inp) },
];

const outDir = join("GENERATED_DRAWINGS", "test-run-15-download");
mkdirSync(outDir, { recursive: true });

const sampleInp: BridgeInput = { ...DEFAULT_BRIDGE_INPUT };
const rows: GenRow[] = [
  ...fullSet("KHW_SOM", kherwaraInp),
  ...fullSet("SMP_RIV", sampleInp).slice(0, 3),
];

let ok = 0;
let fail = 0;
for (const row of rows) {
  try {
    const dxf = row.fn();
    writeFileSync(join(outDir, row.file), dxf, "utf8");
    console.log(`  OK  ${row.file}  (${(dxf.length / 1024).toFixed(1)} KB)`);
    ok++;
  } catch (err) {
    console.error(`  FAIL  ${row.file}`, err);
    fail++;
  }
}

console.log("");
console.log(`GENERATED: ${ok} drawings   FAILED: ${fail}`);
console.log(`OUTPUT:    ${outDir}`);
if (rows.length !== 15) {
  console.error(`Expected 15 rows, got ${rows.length}`);
  process.exit(1);
}
