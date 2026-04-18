import { mkdirSync, writeFileSync } from "fs";
import { join } from "path";

import { generateGAD }                from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-gad";
import { generatePlanView }           from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-plan";
import { generateCrossSection }       from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-xsection";
import { generatePierDrawing }        from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-pier";
import { generateAbutmentDrawing }    from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-abutment";
import { generateDeckRebarDrawing }   from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-deck-rebar";
import { generateWingWallDrawing }    from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-wingwall";
import { generateLongitudinalSection }from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-longitudinal";
import { generateBedProtection }      from "../artifacts/bridge-design-suite/src/lib/drawings/drawing-bed-protection";

const inp = {
  projectName:  "SUBMERSIBLE BRIDGE ACROSS RIVER SOM",
  drawingNo:    "PWD/RAJ/KHW/BR/001",
  location:     "KHERWARA-JAWAS-SUVERI ROAD KM 9/000 KHERWARA RAJASTHAN",
  riverName:    "SOM RIVER",
  bridgeType:   "submersible" as const,
  loadClass:    "IRC CLASS 70-R / CLASS-A (2 LANES)",
  designCode:   "IRC SP-13:2004 / IRC:6-2017 / IRC:112-2020 / IRC:78-2014",
  spanLength:    8.80,
  numberOfSpans: 9,
  totalLength:   79.20,
  numberOfPiers: 8,
  carriageWidth: 8.40,
  numberOfLanes: 2,
  footpathWidth: 0.00,
  kerbWidth:     0.225,
  kerbHeight:    0.225,
  guardrailHeight: 0.00,
  rtl:             101.600,
  hfl:             100.600,
  ofl:              97.600,
  dwl:              97.600,
  bedLevel:         96.470,
  foundationLevel:  93.470,
  agl:              96.600,
  discharge:        899.93,
  manningN:         0.033,
  afflux:           0.15,
  slabThickness:        0.750,
  wearingCoatThickness: 0.075,
  kerb:                 true,
  bottomHaunchDepth:    0.150,
  bottomHaunchWidth:    0.200,
  dirtWallHeight:       0.750,
  pierWidth:      1.200,
  pierLength:     3.800,
  pierDepth:      4.000,
  pierBaseWidth:  3.800,
  pierBaseLength: 12.000,
  pierCapHeight:  1.200,
  pierCapWidth:   2.000,
  pierMainBarDia:    20,
  pierMainBarCount:  16,
  pierLinksDia:      10,
  pierLinksSpacing:  200,
  abutmentHeight:    5.130,
  abutmentWidth:     1.050,
  abutmentBaseWidth: 8.050,
  abutmentDepth:     1.000,
  returnWallLength:  4.500,
  wingWallAngle:     45,
  mainBarDia:     20,
  mainBarSpacing: 125,
  distBarDia:     12,
  distBarSpacing: 200,
  topBarDia:      12,
  topBarSpacing:  200,
  stirrupDia:     10,
  stirrupSpacing: 200,
  coverDeck:       40,
  coverStem:       50,
  coverFoundation: 75,
  concreteGrade: "M30",
  steelGrade:    "Fe415",
  fck:           30,
  fy:            415,
  soilType:  "Medium hard rock",
  sbc:       200,
  phi:       30,
};

const outDir = "GENERATED_DRAWINGS/KHERWARA_SOM_RIVER_BRIDGE";
mkdirSync(outDir, { recursive: true });

const drawings = [
  { name: "DRG-01_GAD_ELEVATION",        fn: () => generateGAD(inp) },
  { name: "DRG-02_PLAN_VIEW",            fn: () => generatePlanView(inp) },
  { name: "DRG-03_CROSS_SECTION",        fn: () => generateCrossSection(inp) },
  { name: "DRG-04_PIER_DETAILS",         fn: () => generatePierDrawing(inp) },
  { name: "DRG-05_ABUTMENT_DETAILS",     fn: () => generateAbutmentDrawing(inp) },
  { name: "DRG-06_DECK_REBAR_BBS",       fn: () => generateDeckRebarDrawing(inp) },
  { name: "DRG-07_WING_WALL",            fn: () => generateWingWallDrawing(inp) },
  { name: "DRG-08_LONGITUDINAL_SECTION", fn: () => generateLongitudinalSection(inp) },
  { name: "DRG-09_BED_PROTECTION",       fn: () => generateBedProtection(inp) },
];

let ok = 0, fail = 0;
for (const drw of drawings) {
  try {
    const dxf = drw.fn();
    const filePath = join(outDir, drw.name + ".dxf");
    writeFileSync(filePath, dxf, "utf8");
    const kb = (dxf.length / 1024).toFixed(1);
    console.log("  OK  " + drw.name + ".dxf  (" + kb + " KB)");
    ok++;
  } catch (err) {
    console.error("  FAIL  " + drw.name + "  ERROR: " + err);
    fail++;
  }
}
console.log("");
console.log("GENERATED: " + ok + " drawings   FAILED: " + fail);
console.log("OUTPUT:    " + outDir);