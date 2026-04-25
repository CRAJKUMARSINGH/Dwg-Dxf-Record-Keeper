import type { BridgeInput } from "../bridge-types";

/** Shared geometry / RL mapping for all pier-related DXF sheets. */
export type PierLayoutCtx = {
  inp: BridgeInput;
  pierWidth: number;
  pierLength: number;
  pierBaseWidth: number;
  pierBaseLength: number;
  pierCapHeight: number;
  pierCapWidth: number;
  pierMainBarDia: number;
  pierMainBarCount: number;
  pierLinksDia: number;
  pierLinksSpacing: number;
  coverStem: number;
  hfl: number;
  bedLevel: number;
  foundationLevel: number;
  rtl: number;
  toY: (lv: number) => number;
  deckBot: number;
  bedY: number;
  foundY: number;
  hflY: number;
  pierH: number;
  cvr: number;
  mainBarR: number;
  dX: number;
  xsOX: number;
  xsOY: number;
  bbsX: number;
  bbsY: number;
  tbX: number;
  tbY: number;
};

export function pierLayoutCtx(inp: BridgeInput): PierLayoutCtx {
  const {
    pierWidth,
    pierLength,
    pierBaseWidth,
    pierBaseLength,
    pierCapHeight,
    pierCapWidth,
    pierMainBarDia,
    pierMainBarCount,
    pierLinksDia,
    pierLinksSpacing,
    coverStem,
    hfl,
    bedLevel,
    foundationLevel,
    rtl,
  } = inp;

  const toY = (lv: number) => lv - (foundationLevel - 1);
  const deckBot = toY(rtl);
  const bedY = toY(bedLevel);
  const foundY = toY(foundationLevel);
  const hflY = toY(hfl);
  const pierH = deckBot - foundY;
  const cvr = coverStem / 1000;
  const mainBarR = pierMainBarDia / 2000;
  const dX = pierBaseWidth / 2 + 2;
  const xsOX = pierBaseWidth + 7;
  const xsOY = bedY + (deckBot - bedY) / 2;
  const bbsX = -pierBaseWidth / 2;
  const bbsY = foundY - 3;
  const tbX = -pierBaseWidth / 2 - 5;
  const tbY = foundY - 22;

  return {
    inp,
    pierWidth,
    pierLength,
    pierBaseWidth,
    pierBaseLength,
    pierCapHeight,
    pierCapWidth,
    pierMainBarDia,
    pierMainBarCount,
    pierLinksDia,
    pierLinksSpacing,
    coverStem,
    hfl,
    bedLevel,
    foundationLevel,
    rtl,
    toY,
    deckBot,
    bedY,
    foundY,
    hflY,
    pierH,
    cvr,
    mainBarR,
    dX,
    xsOX,
    xsOY,
    bbsX,
    bbsY,
    tbX,
    tbY,
  };
}
