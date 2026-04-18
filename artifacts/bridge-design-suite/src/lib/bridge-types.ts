export interface BridgeInput {
  projectName: string;
  drawingNo: string;
  location: string;
  riverName: string;
  bridgeType: 'submersible' | 'highlevel';

  spanLength: number;
  numberOfSpans: number;
  carriageWidth: number;
  numberOfLanes: number;
  totalLength: number;
  footpathWidth: number;

  hfl: number;
  ofl: number;
  dwl: number;
  bedLevel: number;
  foundationLevel: number;
  rtl: number;
  agl: number;
  discharge: number;
  manningN: number;
  afflux: number;

  slabThickness: number;
  wearingCoatThickness: number;
  kerb: boolean;
  kerbHeight: number;
  kerbWidth: number;
  guardrailHeight: number;
  bottomHaunchDepth: number;
  bottomHaunchWidth: number;

  pierWidth: number;
  pierLength: number;
  pierDepth: number;
  numberOfPiers: number;
  pierBaseWidth: number;
  pierBaseLength: number;
  pierCapHeight: number;
  pierCapWidth: number;

  abutmentHeight: number;
  abutmentWidth: number;
  abutmentBaseWidth: number;
  abutmentDepth: number;
  dirtWallHeight: number;
  returnWallLength: number;
  wingWallAngle: number;

  concreteGrade: string;
  steelGrade: string;
  fck: number;
  fy: number;
  coverFoundation: number;
  coverStem: number;
  coverDeck: number;

  mainBarDia: number;
  mainBarSpacing: number;
  distBarDia: number;
  distBarSpacing: number;
  topBarDia: number;
  topBarSpacing: number;
  stirrupDia: number;
  stirrupSpacing: number;
  pierMainBarDia: number;
  pierMainBarCount: number;
  pierLinksDia: number;
  pierLinksSpacing: number;

  designCode: string;
  loadClass: string;
  soilType: string;
  sbc: number;
  phi: number;
}

export const DEFAULT_BRIDGE_INPUT: BridgeInput = {
  projectName: 'RCC Slab Bridge — Sample Project',
  drawingNo: 'DRG/BR/001',
  location: 'Rajasthan, India',
  riverName: 'Sample River',
  bridgeType: 'submersible',
  spanLength: 10,
  numberOfSpans: 3,
  carriageWidth: 7.5,
  numberOfLanes: 2,
  totalLength: 30,
  footpathWidth: 1.25,
  hfl: 285.50,
  ofl: 284.80,
  dwl: 285.75,
  bedLevel: 280.20,
  foundationLevel: 276.50,
  rtl: 287.00,
  agl: 280.20,
  discharge: 900,
  manningN: 0.033,
  afflux: 0.15,
  slabThickness: 0.60,
  wearingCoatThickness: 0.075,
  kerb: true,
  kerbHeight: 0.225,
  kerbWidth: 0.225,
  guardrailHeight: 0.90,
  bottomHaunchDepth: 0.15,
  bottomHaunchWidth: 0.20,
  pierWidth: 1.20,
  pierLength: 3.50,
  pierDepth: 4.00,
  numberOfPiers: 2,
  pierBaseWidth: 2.50,
  pierBaseLength: 4.50,
  pierCapHeight: 0.80,
  pierCapWidth: 1.80,
  abutmentHeight: 5.50,
  abutmentWidth: 3.00,
  abutmentBaseWidth: 4.50,
  abutmentDepth: 1.20,
  dirtWallHeight: 2.50,
  returnWallLength: 6.00,
  wingWallAngle: 45,
  concreteGrade: 'M25',
  steelGrade: 'Fe415',
  fck: 25,
  fy: 415,
  coverFoundation: 75,
  coverStem: 50,
  coverDeck: 40,
  mainBarDia: 16,
  mainBarSpacing: 150,
  distBarDia: 10,
  distBarSpacing: 200,
  topBarDia: 10,
  topBarSpacing: 200,
  stirrupDia: 8,
  stirrupSpacing: 200,
  pierMainBarDia: 20,
  pierMainBarCount: 8,
  pierLinksDia: 10,
  pierLinksSpacing: 200,
  designCode: 'IRC SP-13 / IRC:6 / IRC:112',
  loadClass: 'IRC Class A (2 lanes)',
  soilType: 'Medium hard rock',
  sbc: 200,
  phi: 30,
};
