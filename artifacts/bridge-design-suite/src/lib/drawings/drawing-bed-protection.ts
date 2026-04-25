import { BridgeInput } from '@/lib/bridge-types';
import { ln, txt, txtL, closedPoly, poly, circle, dimH, dimV, rlMarker, hatchLines, northArrow, scaleBar, ircTitleBlock, ircNotesBlock, makeHeader, finalizeDxf } from '../dxf-helpers';

export function generateBedProtection(inp: BridgeInput): string {
  const e: string[] = [];
  // Bed protection plan and section
  // Standard IRC SP-13 bed protection: 1.5D upstream, 2D downstream (D = scour depth)
  const scourDepth = Math.max(inp.hfl - inp.bedLevel, 2.0);
  const upstreamL  = Math.max(1.5 * scourDepth, 3.0);
  const downstreamL = Math.max(2.0 * scourDepth, 4.0);
  const protWidth  = inp.totalLength + 2.0; // protection extends beyond bridge width
  const blockThk   = 0.30;  // CC block thickness
  const filterThk  = 0.15;  // filter media
  const sandThk    = 0.10;  // sand layer
  const cutoffD    = 1.0;   // cutoff wall depth
  const cutoffW    = 0.45;  // cutoff wall width
  //  PLAN VIEW
  const planOriginX = 0; const planOriginY = 0;
  e.push(txt(protWidth/2, protWidth*0.5+2,'PLAN VIEW - BED PROTECTION',0.45,'TEXT'));
  // Bridge outline in plan
  e.push(closedPoly([[upstreamL,0],[upstreamL+inp.totalLength,0],[upstreamL+inp.totalLength,protWidth],[upstreamL,protWidth]],'STRUCTURE'));
  e.push(txt(upstreamL+inp.totalLength/2,protWidth/2,'BRIDGE',0.35,'TEXT'));
  // Upstream protection
  e.push(closedPoly([[0,0],[upstreamL,0],[upstreamL,protWidth],[0,protWidth]],'BED_PROTECTION'));
  for (const h of hatchLines(0,0,upstreamL,protWidth,0.4,'HATCH')) e.push(h);
  e.push(txt(upstreamL/2,protWidth/2,'UPSTREAM\\nPROTECTION',0.28,'TEXT'));
  // Downstream protection
  const dsX = upstreamL+inp.totalLength;
  e.push(closedPoly([[dsX,0],[dsX+downstreamL,0],[dsX+downstreamL,protWidth],[dsX,protWidth]],'BED_PROTECTION'));
  for (const h of hatchLines(dsX,0,dsX+downstreamL,protWidth,0.4,'HATCH')) e.push(h);
  e.push(txt(dsX+downstreamL/2,protWidth/2,'DOWNSTREAM\\nPROTECTION',0.28,'TEXT'));
  // Cutoff walls
  e.push(closedPoly([[0-cutoffW,0],[0,0],[0,protWidth],[0-cutoffW,protWidth]],'STRUCTURE'));
  e.push(closedPoly([[dsX+downstreamL,0],[dsX+downstreamL+cutoffW,0],[dsX+downstreamL+cutoffW,protWidth],[dsX+downstreamL,protWidth]],'STRUCTURE'));
  // Pier apron circles in plan
  const pierXs: number[] = [];
  for (let i=1;i<=inp.numberOfPiers;i++) pierXs.push(upstreamL+inp.abutmentBaseWidth+inp.spanLength*i);
  for (const px of pierXs) {
    e.push(circle(px,protWidth/2,Math.max(inp.pierBaseWidth,inp.pierBaseLength)*0.7,'BED_PROTECTION'));
    e.push(txt(px,protWidth/2,'APRON',0.22,'TEXT'));
  }
  // Plan dimensions
  for (const s of dimH(0,protWidth+1,upstreamL,protWidth+1.5,'DIMENSIONS','US = '+upstreamL.toFixed(1)+'m')) e.push(s);
  for (const s of dimH(upstreamL,protWidth+1,upstreamL+inp.totalLength,protWidth+1.5,'DIMENSIONS',inp.totalLength.toFixed(1)+'m')) e.push(s);
  for (const s of dimH(dsX,protWidth+1,dsX+downstreamL,protWidth+1.5,'DIMENSIONS','DS = '+downstreamL.toFixed(1)+'m')) e.push(s);
  //  SECTION THROUGH BED PROTECTION (below plan)
  const secY = -4;
  const totalProtL = upstreamL + inp.totalLength + downstreamL;
  e.push(txt(totalProtL/2,secY+1.5,'SECTION THROUGH BED PROTECTION',0.40,'TEXT'));
  // Natural bed
  e.push(ln(-cutoffW,secY,totalProtL+cutoffW,secY,'WATER_LEVEL'));
  e.push(txt(totalProtL/2,secY-0.3,'NATURAL BED',0.25,'TEXT'));
  // Sand layer
  e.push(closedPoly([[-cutoffW,secY],[totalProtL+cutoffW,secY],[totalProtL+cutoffW,secY+sandThk],[-cutoffW,secY+sandThk]],'BED_PROTECTION'));
  e.push(txt(totalProtL/2,secY+sandThk/2,'SAND LAYER ('+Math.round(sandThk*1000)+'mm)',0.22,'TEXT'));
  // Filter media
  e.push(closedPoly([[-cutoffW,secY+sandThk],[totalProtL+cutoffW,secY+sandThk],[totalProtL+cutoffW,secY+sandThk+filterThk],[-cutoffW,secY+sandThk+filterThk]],'BED_PROTECTION'));
  for (const h of hatchLines(-cutoffW,secY+sandThk,totalProtL+cutoffW,secY+sandThk+filterThk,0.1,'HATCH')) e.push(h);
  e.push(txt(totalProtL/2,secY+sandThk+filterThk/2,'FILTER MEDIA - GRAVEL ('+Math.round(filterThk*1000)+'mm)',0.22,'TEXT'));
  // CC blocks / stone pitching
  e.push(closedPoly([[-cutoffW,secY+sandThk+filterThk],[totalProtL+cutoffW,secY+sandThk+filterThk],[totalProtL+cutoffW,secY+sandThk+filterThk+blockThk],[-cutoffW,secY+sandThk+filterThk+blockThk]],'BED_PROTECTION'));
  for (let bx=0; bx<totalProtL; bx+=0.5) e.push(ln(bx,secY+sandThk+filterThk,bx,secY+sandThk+filterThk+blockThk,'BED_PROTECTION'));
  e.push(txt(totalProtL/2,secY+sandThk+filterThk+blockThk/2,'CC BLOCKS / STONE PITCHING ('+Math.round(blockThk*1000)+'mm)',0.22,'TEXT'));
  // Cutoff walls in section
  e.push(closedPoly([[-cutoffW,secY-cutoffD],[0,secY-cutoffD],[0,secY+sandThk+filterThk+blockThk],[-cutoffW,secY+sandThk+filterThk+blockThk]],'STRUCTURE'));
  e.push(closedPoly([[totalProtL,secY-cutoffD],[totalProtL+cutoffW,secY-cutoffD],[totalProtL+cutoffW,secY+sandThk+filterThk+blockThk],[totalProtL,secY+sandThk+filterThk+blockThk]],'STRUCTURE'));
  e.push(txt(-cutoffW/2,secY-cutoffD/2,'CUTOFF\\nWALL',0.20,'TEXT'));
  e.push(txt(totalProtL+cutoffW/2,secY-cutoffD/2,'CUTOFF\\nWALL',0.20,'TEXT'));
  // Section dimensions
  const topOfProt = secY+sandThk+filterThk+blockThk;
  for (const s of dimV(totalProtL+cutoffW,secY,topOfProt,totalProtL+cutoffW+2,'DIMENSIONS','TOTAL = '+((sandThk+filterThk+blockThk)*1000).toFixed(0)+'mm')) e.push(s);
  for (const s of dimV(-cutoffW,secY-cutoffD,secY,-cutoffW-2,'DIMENSIONS',String(Math.round(cutoffD*1000))+'mm')) e.push(s);
  // RL marker at bed level
  for (const s of rlMarker(-cutoffW-4,inp.bedLevel,inp.bedLevel,'BED LEVEL','WATER_LEVEL')) e.push(s);
  // North arrow
  for (const s of northArrow(totalProtL+5,protWidth+3,'NORTH_ARROW')) e.push(s);
  // Scale bar
  for (const s of scaleBar(0,secY-3,5,'DIMENSIONS')) e.push(s);
  e.push(txt(2.5,secY-3.6,'SCALE 1:100',0.28,'TEXT'));
  const tbX=totalProtL-28; const tbY=secY-14;
  for (const s of ircTitleBlock(tbX,tbY,{projectName:inp.projectName,drawingTitle:'BED PROTECTION DETAILS',drawingNo:inp.drawingNo+'/BP',scale:'1:100',location:inp.location,sheetNo:'12',totalSheets:'12',client:'PUBLIC WORKS DEPARTMENT'})) e.push(s);
  for (const s of ircNotesBlock(tbX,tbY-1,inp.concreteGrade,inp.steelGrade,inp.coverDeck,inp.coverStem,inp.coverFoundation,inp.designCode,inp.loadClass)) e.push(s);
  return makeHeader([tbX-2,tbY-6],[totalProtL+10,protWidth+6])+finalizeDxf(e);
}
