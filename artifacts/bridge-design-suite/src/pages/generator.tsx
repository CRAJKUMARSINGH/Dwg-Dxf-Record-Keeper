import { useState, useCallback, useRef, DragEvent } from "react";
import { DEFAULT_BRIDGE_INPUT } from "@/lib/bridge-types";
import type { BridgeInput } from "@/lib/bridge-types";
import {
  generateGAD,
  generatePlanView,
  generateCrossSection,
  generatePierDrawing,
  generateAbutmentDrawing,
  generateDeckRebarDrawing,
  generateWingWallDrawing,
  generateLongitudinalSection,
  generateBedProtection,
} from "@/lib/drawings";
import {
  Download, FileText, Layers, ChevronDown, ChevronUp,
  Info, Zap, Upload, ScanLine, CheckCircle, AlertCircle, X,
} from "lucide-react";

type DrawingDef = {
  key: string;
  title: string;
  subtitle: string;
  gen: (inp: BridgeInput) => string;
};

const DRAWINGS: DrawingDef[] = [
  { key: 'gad',  title: 'DRG 1 — General Arrangement (Elevation)', subtitle: 'Full bridge elevation with all levels',          gen: generateGAD },
  { key: 'plan', title: 'DRG 2 — Plan View (Top of Deck)',          subtitle: 'Plan showing carriageway, footpaths, piers',   gen: generatePlanView },
  { key: 'xsec', title: 'DRG 3 — Cross-Section at Mid-Span',        subtitle: 'Transverse section with reinforcement',         gen: generateCrossSection },
  { key: 'pier', title: 'DRG 4 — Pier Details',                      subtitle: 'Pier elevation, section, bar schedule',        gen: generatePierDrawing },
  { key: 'abt',  title: 'DRG 5 — Abutment Details',                  subtitle: 'Abutment elevation, plan, reinforcement',      gen: generateAbutmentDrawing },
  { key: 'rebar',title: 'DRG 6 — Deck Slab Reinforcement',           subtitle: 'Longitudinal section with bar bending schedule',gen: generateDeckRebarDrawing },
  { key: 'wing', title: 'DRG 7 — Wing Wall & Return Wall',            subtitle: 'Wing wall elevation and plan details',         gen: generateWingWallDrawing },
  { key: 'long', title: 'DRG 8 — Longitudinal Section',               subtitle: 'Section along centre line',                   gen: generateLongitudinalSection },
  { key: 'bed',  title: 'DRG 9 — Bed Protection Details',            subtitle: 'Upstream/downstream protection with cutoff walls', gen: generateBedProtection },
];

type SectionKey = 'project'|'geometry'|'hydraulics'|'piers'|'abutments'|'slab'|'rebar'|'materials';

const SECTIONS: { key: SectionKey; label: string; icon: string }[] = [
  { key: 'project',   label: 'Project Info',       icon: '📋' },
  { key: 'geometry',  label: 'Bridge Geometry',     icon: '📐' },
  { key: 'hydraulics',label: 'Hydraulic Levels',    icon: '🌊' },
  { key: 'piers',     label: 'Pier Data',           icon: '🏛' },
  { key: 'abutments', label: 'Abutment Data',       icon: '🧱' },
  { key: 'slab',      label: 'Deck Slab',           icon: '📊' },
  { key: 'rebar',     label: 'Reinforcement',       icon: '🔩' },
  { key: 'materials', label: 'Materials & Soil',    icon: '⚗' },
];

type ScanResult = {
  projectName?: string; riverName?: string; location?: string;
  bridgeType?: 'submersible'|'highlevel';
  spanLength?: number; numberOfSpans?: number; totalLength?: number;
  numberOfPiers?: number; carriageWidth?: number; footpathWidth?: number; numberOfLanes?: number;
  rtl?: number; hfl?: number; ofl?: number; dwl?: number;
  bedLevel?: number; foundationLevel?: number; agl?: number;
  discharge?: number; afflux?: number;
  slabThickness?: number; wearingCoatThickness?: number; kerbHeight?: number;
  kerbWidth?: number; dirtWallHeight?: number;
  pierWidth?: number; pierLength?: number; pierDepth?: number;
  pierBaseWidth?: number; pierBaseLength?: number; pierCapHeight?: number; pierCapWidth?: number;
  abutmentHeight?: number; abutmentWidth?: number; abutmentBaseWidth?: number;
  abutmentDepth?: number; returnWallLength?: number; wingWallAngle?: number;
  mainBarDia?: number; mainBarSpacing?: number; distBarDia?: number; distBarSpacing?: number;
  topBarDia?: number; topBarSpacing?: number; stirrupDia?: number; stirrupSpacing?: number;
  pierMainBarDia?: number; pierMainBarCount?: number; pierLinksDia?: number; pierLinksSpacing?: number;
  concreteGrade?: string; steelGrade?: string; fck?: number; fy?: number;
  sbc?: number; phi?: number; loadClass?: string; designCode?: string;
  notes?: string; drawingType?: string;
};

function N(v: string): number { return parseFloat(v) || 0; }

function applyScannedData(prev: BridgeInput, data: ScanResult): BridgeInput {
  const next = { ...prev };
  const apply = <K extends keyof BridgeInput>(key: K, val: BridgeInput[K] | undefined | null) => {
    if (val !== undefined && val !== null) (next as Record<string, unknown>)[key] = val;
  };
  apply('projectName',       data.projectName as string);
  apply('riverName',         data.riverName as string);
  apply('location',          data.location as string);
  apply('bridgeType',        data.bridgeType as 'submersible'|'highlevel');
  apply('spanLength',        data.spanLength as number);
  apply('numberOfSpans',     data.numberOfSpans as number);
  apply('totalLength',       data.totalLength ?? (data.spanLength && data.numberOfSpans ? data.spanLength * data.numberOfSpans : undefined) as number);
  apply('numberOfPiers',     data.numberOfPiers ?? (data.numberOfSpans ? data.numberOfSpans - 1 : undefined) as number);
  apply('carriageWidth',     data.carriageWidth as number);
  apply('footpathWidth',     data.footpathWidth as number);
  apply('numberOfLanes',     data.numberOfLanes as number);
  apply('rtl',               data.rtl as number);
  apply('hfl',               data.hfl as number);
  apply('ofl',               data.ofl as number);
  apply('dwl',               data.dwl as number);
  apply('bedLevel',          data.bedLevel as number);
  apply('foundationLevel',   data.foundationLevel as number);
  apply('agl',               data.agl as number);
  apply('discharge',         data.discharge as number);
  apply('afflux',            data.afflux as number);
  apply('slabThickness',     data.slabThickness as number);
  apply('wearingCoatThickness', data.wearingCoatThickness as number);
  apply('kerbHeight',        data.kerbHeight as number);
  apply('kerbWidth',         data.kerbWidth as number);
  apply('dirtWallHeight',    data.dirtWallHeight as number);
  apply('pierWidth',         data.pierWidth as number);
  apply('pierLength',        data.pierLength as number);
  apply('pierDepth',         data.pierDepth as number);
  apply('pierBaseWidth',     data.pierBaseWidth as number);
  apply('pierBaseLength',    data.pierBaseLength as number);
  apply('pierCapHeight',     data.pierCapHeight as number);
  apply('pierCapWidth',      data.pierCapWidth as number);
  apply('abutmentHeight',    data.abutmentHeight as number);
  apply('abutmentWidth',     data.abutmentWidth as number);
  apply('abutmentBaseWidth', data.abutmentBaseWidth as number);
  apply('abutmentDepth',     data.abutmentDepth as number);
  apply('returnWallLength',  data.returnWallLength as number);
  apply('wingWallAngle',     data.wingWallAngle as number);
  apply('mainBarDia',        data.mainBarDia as number);
  apply('mainBarSpacing',    data.mainBarSpacing as number);
  apply('distBarDia',        data.distBarDia as number);
  apply('distBarSpacing',    data.distBarSpacing as number);
  apply('topBarDia',         data.topBarDia as number);
  apply('topBarSpacing',     data.topBarSpacing as number);
  apply('stirrupDia',        data.stirrupDia as number);
  apply('stirrupSpacing',    data.stirrupSpacing as number);
  apply('pierMainBarDia',    data.pierMainBarDia as number);
  apply('pierMainBarCount',  data.pierMainBarCount as number);
  apply('pierLinksDia',      data.pierLinksDia as number);
  apply('pierLinksSpacing',  data.pierLinksSpacing as number);
  apply('concreteGrade',     data.concreteGrade as string);
  apply('steelGrade',        data.steelGrade as string);
  apply('fck',               data.fck as number);
  apply('fy',                data.fy as number);
  apply('sbc',               data.sbc as number);
  apply('phi',               data.phi as number);
  apply('loadClass',         data.loadClass as string);
  apply('designCode',        data.designCode as string);
  return next;
}

function countExtracted(data: ScanResult): number {
  const skip = new Set(['notes', 'drawingType']);
  return Object.entries(data).filter(([k, v]) => !skip.has(k) && v !== null && v !== undefined).length;
}

function Field({ label, value, onChange, type = 'number', unit, step = '0.001', min }:
  { label: string; value: string|number; onChange: (v: string) => void; type?: string; unit?: string; step?: string; min?: string }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-muted-foreground">
        {label}{unit && <span className="ml-1 text-[10px] opacity-70">({unit})</span>}
      </label>
      <input type={type} value={value} step={step} min={min}
        onChange={e => onChange(e.target.value)}
        className="rounded border border-border bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors" />
    </div>
  );
}

function SelectField({ label, value, onChange, options }:
  { label: string; value: string; onChange: (v: string) => void; options: { value: string; label: string }[] }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-muted-foreground">{label}</label>
      <select value={value} onChange={e => onChange(e.target.value)}
        className="rounded border border-border bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary transition-colors">
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );
}

function CheckField({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="flex items-center gap-2 text-sm cursor-pointer">
      <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} className="w-4 h-4 accent-primary" />
      {label}
    </label>
  );
}

export default function BridgeGenerator() {
  const [inp, setInp]         = useState<BridgeInput>({ ...DEFAULT_BRIDGE_INPUT });
  const [selected, setSelected] = useState<Set<string>>(new Set(DRAWINGS.map(d => d.key)));
  const [openSections, setOpenSections] = useState<Set<SectionKey>>(new Set(['project','geometry','hydraulics']));
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated]   = useState(false);

  // scan state
  const [scanImage, setScanImage]     = useState<string | null>(null);
  const [scanMime, setScanMime]       = useState<string>('image/jpeg');
  const [scanFile, setScanFile]       = useState<string>('');
  const [scanning, setScanning]       = useState(false);
  const [scanResult, setScanResult]   = useState<ScanResult | null>(null);
  const [scanError, setScanError]     = useState<string | null>(null);
  const [scanApplied, setScanApplied] = useState(false);
  const [scanOpen, setScanOpen]       = useState(true);
  const [dragging, setDragging]       = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const set = useCallback(<K extends keyof BridgeInput>(key: K, value: BridgeInput[K]) => {
    setInp(prev => {
      const next = { ...prev, [key]: value };
      if (key === 'spanLength' || key === 'numberOfSpans') {
        next.totalLength  = N(String(next.spanLength)) * N(String(next.numberOfSpans));
        next.numberOfPiers = N(String(next.numberOfSpans)) - 1;
      }
      return next;
    });
  }, []);
  const setN = useCallback(<K extends keyof BridgeInput>(key: K) => (v: string) => set(key, N(v) as BridgeInput[K]), [set]);
  const setS = useCallback(<K extends keyof BridgeInput>(key: K) => (v: string) => set(key, v as BridgeInput[K]), [set]);

  const toggleSection = (key: SectionKey) => setOpenSections(prev => {
    const next = new Set(prev);
    if (next.has(key)) next.delete(key); else next.add(key);
    return next;
  });

  const toggleDrawing = (key: string) => setSelected(prev => {
    const next = new Set(prev);
    if (next.has(key)) next.delete(key); else next.add(key);
    return next;
  });

  const downloadDxf = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'application/dxf' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
  };

  const generateAll = async () => {
    setGenerating(true); setGenerated(false);
    await new Promise(r => setTimeout(r, 50));
    for (const drw of DRAWINGS.filter(d => selected.has(d.key))) {
      try {
        const content = drw.gen(inp);
        const prefix  = inp.drawingNo.replace(/\//g, '-');
        downloadDxf(content, `${prefix}-${drw.key.toUpperCase()}.dxf`);
        await new Promise(r => setTimeout(r, 100));
      } catch (e) { console.error(`Error generating ${drw.key}:`, e); }
    }
    setGenerating(false); setGenerated(true);
  };

  const downloadSingle = (drw: DrawingDef) => {
    try {
      const content = drw.gen(inp);
      downloadDxf(content, `${inp.drawingNo.replace(/\//g,'-')}-${drw.key.toUpperCase()}.dxf`);
    } catch (e) { console.error(e); }
  };

  const loadImageFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setScanError('Please upload an image file (JPG, PNG, BMP, TIFF or PDF-as-image).');
      return;
    }
    setScanFile(file.name);
    setScanMime(file.type);
    setScanResult(null); setScanError(null); setScanApplied(false);
    const reader = new FileReader();
    reader.onload = e => {
      const dataUrl = e.target?.result as string;
      const base64  = dataUrl.split(',')[1];
      setScanImage(base64);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault(); setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) loadImageFile(file);
  };

  const scanDrawing = async () => {
    if (!scanImage) return;
    setScanning(true); setScanError(null); setScanResult(null);
    try {
      const res  = await fetch('/api/scan-drawing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imageBase64: scanImage, mimeType: scanMime }),
      });
      const json = await res.json();
      if (!res.ok || !json.success) throw new Error(json.error ?? 'Scan failed');
      // clean nulls
      const data: ScanResult = Object.fromEntries(
        Object.entries(json.data).filter(([, v]) => v !== null)
      ) as ScanResult;
      setScanResult(data);
    } catch (e) {
      setScanError(e instanceof Error ? e.message : String(e));
    } finally {
      setScanning(false);
    }
  };

  const applyScan = () => {
    if (!scanResult) return;
    setInp(prev => applyScannedData(prev, scanResult));
    setScanApplied(true);
    setOpenSections(new Set(['project','geometry','hydraulics','piers','abutments','slab','rebar','materials']));
  };

  const clearScan = () => {
    setScanImage(null); setScanFile(''); setScanResult(null);
    setScanError(null); setScanApplied(false);
  };

  const SectionHeader = ({ sec }: { sec: typeof SECTIONS[0] }) => (
    <button onClick={() => toggleSection(sec.key)}
      className="flex items-center justify-between w-full px-4 py-3 bg-sidebar text-sidebar-foreground rounded-lg hover:bg-sidebar-accent transition-colors">
      <span className="flex items-center gap-2 font-semibold text-sm"><span>{sec.icon}</span>{sec.label}</span>
      {openSections.has(sec.key) ? <ChevronUp className="w-4 h-4 opacity-70"/> : <ChevronDown className="w-4 h-4 opacity-70"/>}
    </button>
  );

  const Section = ({ sec, children }: { sec: typeof SECTIONS[0]; children: React.ReactNode }) => (
    <div className="mb-2">
      <SectionHeader sec={sec}/>
      {openSections.has(sec.key) && <div className="mt-2 px-1 grid grid-cols-2 gap-3">{children}</div>}
    </div>
  );

  const extractedCount = scanResult ? countExtracted(scanResult) : 0;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="bg-sidebar text-sidebar-foreground px-6 py-4 shadow-lg">
        <div className="max-w-[1800px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary rounded-lg p-2"><Layers className="w-6 h-6 text-white"/></div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">RCC Slab Bridge — DXF Drawing Generator</h1>
              <p className="text-xs text-sidebar-foreground/70 mt-0.5">IRC SP-13 / IRC:6 / IRC:112 — Submersible & High Level Bridges</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-sidebar-foreground/60">
            <Info className="w-4 h-4"/>
            <span>Generates {selected.size} of {DRAWINGS.length} drawings</span>
          </div>
        </div>
      </header>

      <div className="flex flex-1 max-w-[1800px] mx-auto w-full px-4 py-6 gap-6">
        {/* Left: Parameters */}
        <div className="w-80 flex-shrink-0 flex flex-col gap-2 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 100px)' }}>
          <div className="bg-card border border-card-border rounded-xl p-4 mb-2">
            <p className="text-xs text-muted-foreground flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5"/>
              Enter parameters manually below, or upload a reference drawing to auto-fill.
            </p>
          </div>

          <Section sec={SECTIONS[0]}>
            <div className="col-span-2"><Field label="Project Name" value={inp.projectName} onChange={setS('projectName')} type="text"/></div>
            <div className="col-span-2"><Field label="Drawing Number" value={inp.drawingNo} onChange={setS('drawingNo')} type="text"/></div>
            <div className="col-span-2"><Field label="Location" value={inp.location} onChange={setS('location')} type="text"/></div>
            <div className="col-span-2"><Field label="River Name" value={inp.riverName} onChange={setS('riverName')} type="text"/></div>
            <div className="col-span-2">
              <SelectField label="Bridge Type" value={inp.bridgeType} onChange={setS('bridgeType')}
                options={[{value:'submersible',label:'Submersible Bridge'},{value:'highlevel',label:'High Level Bridge'}]}/>
            </div>
            <div className="col-span-2"><Field label="Load Class" value={inp.loadClass} onChange={setS('loadClass')} type="text"/></div>
            <div className="col-span-2"><Field label="Design Code" value={inp.designCode} onChange={setS('designCode')} type="text"/></div>
          </Section>

          <Section sec={SECTIONS[1]}>
            <Field label="Span Length"        value={inp.spanLength}      onChange={setN('spanLength')}      unit="m"/>
            <Field label="No. of Spans"       value={inp.numberOfSpans}   onChange={setN('numberOfSpans')}   unit="nos" step="1" min="1"/>
            <Field label="Total Length"       value={inp.totalLength}     onChange={setN('totalLength')}     unit="m"/>
            <Field label="No. of Piers"       value={inp.numberOfPiers}   onChange={setN('numberOfPiers')}   unit="nos" step="1"/>
            <Field label="Carriageway Width"  value={inp.carriageWidth}   onChange={setN('carriageWidth')}   unit="m"/>
            <Field label="No. of Lanes"       value={inp.numberOfLanes}   onChange={setN('numberOfLanes')}   unit="nos" step="1"/>
            <Field label="Footpath Width"     value={inp.footpathWidth}   onChange={setN('footpathWidth')}   unit="m"/>
            <Field label="Kerb Width"         value={inp.kerbWidth}       onChange={setN('kerbWidth')}       unit="m"/>
            <Field label="Kerb Height"        value={inp.kerbHeight}      onChange={setN('kerbHeight')}      unit="m"/>
            <Field label="Guardrail Height"   value={inp.guardrailHeight} onChange={setN('guardrailHeight')} unit="m"/>
          </Section>

          <Section sec={SECTIONS[2]}>
            <Field label="Road Top Level (RTL)"  value={inp.rtl}             onChange={setN('rtl')}             unit="m MSL"/>
            <Field label="Avg Ground Level (AGL)"value={inp.agl}             onChange={setN('agl')}             unit="m MSL"/>
            <Field label="HFL"                   value={inp.hfl}             onChange={setN('hfl')}             unit="m MSL"/>
            <Field label="OFL"                   value={inp.ofl}             onChange={setN('ofl')}             unit="m MSL"/>
            <Field label="DWL"                   value={inp.dwl}             onChange={setN('dwl')}             unit="m MSL"/>
            <Field label="Bed Level"             value={inp.bedLevel}        onChange={setN('bedLevel')}        unit="m MSL"/>
            <Field label="Foundation Level"      value={inp.foundationLevel} onChange={setN('foundationLevel')} unit="m MSL"/>
            <Field label="Design Discharge"      value={inp.discharge}       onChange={setN('discharge')}       unit="cumecs"/>
            <Field label="Manning's N"           value={inp.manningN}        onChange={setN('manningN')}        unit="" step="0.001"/>
            <Field label="Afflux"                value={inp.afflux}          onChange={setN('afflux')}          unit="m" step="0.01"/>
          </Section>

          <Section sec={SECTIONS[3]}>
            <Field label="Pier Width"      value={inp.pierWidth}      onChange={setN('pierWidth')}      unit="m"/>
            <Field label="Pier Length"     value={inp.pierLength}     onChange={setN('pierLength')}     unit="m"/>
            <Field label="Pier Depth"      value={inp.pierDepth}      onChange={setN('pierDepth')}      unit="m"/>
            <Field label="Pier Base Width" value={inp.pierBaseWidth}  onChange={setN('pierBaseWidth')}  unit="m"/>
            <Field label="Pier Base Length"value={inp.pierBaseLength} onChange={setN('pierBaseLength')} unit="m"/>
            <Field label="Pier Cap Height" value={inp.pierCapHeight}  onChange={setN('pierCapHeight')}  unit="m"/>
            <Field label="Pier Cap Width"  value={inp.pierCapWidth}   onChange={setN('pierCapWidth')}   unit="m"/>
          </Section>

          <Section sec={SECTIONS[4]}>
            <Field label="Abutment Height"     value={inp.abutmentHeight}    onChange={setN('abutmentHeight')}    unit="m"/>
            <Field label="Abutment Width"      value={inp.abutmentWidth}     onChange={setN('abutmentWidth')}     unit="m"/>
            <Field label="Abutment Base Width" value={inp.abutmentBaseWidth} onChange={setN('abutmentBaseWidth')} unit="m"/>
            <Field label="Abutment Depth"      value={inp.abutmentDepth}     onChange={setN('abutmentDepth')}     unit="m"/>
            <Field label="Dirt Wall Height"    value={inp.dirtWallHeight}    onChange={setN('dirtWallHeight')}    unit="m"/>
            <Field label="Return Wall Length"  value={inp.returnWallLength}  onChange={setN('returnWallLength')}  unit="m"/>
            <Field label="Wing Wall Angle"     value={inp.wingWallAngle}     onChange={setN('wingWallAngle')}     unit="°" step="5"/>
          </Section>

          <Section sec={SECTIONS[5]}>
            <Field label="Slab Thickness"  value={inp.slabThickness}         onChange={setN('slabThickness')}         unit="m"/>
            <Field label="Wearing Coat"    value={inp.wearingCoatThickness}   onChange={setN('wearingCoatThickness')}  unit="m"/>
            <Field label="Haunch Depth"    value={inp.bottomHaunchDepth}      onChange={setN('bottomHaunchDepth')}     unit="m"/>
            <Field label="Haunch Width"    value={inp.bottomHaunchWidth}      onChange={setN('bottomHaunchWidth')}     unit="m"/>
            <div className="col-span-2 pt-1"><CheckField label="Include Kerb" checked={inp.kerb} onChange={v => set('kerb', v)}/></div>
          </Section>

          <Section sec={SECTIONS[6]}>
            <Field label="Main Bar Dia"        value={inp.mainBarDia}        onChange={setN('mainBarDia')}        unit="mm" step="2"/>
            <Field label="Main Bar Spacing"    value={inp.mainBarSpacing}    onChange={setN('mainBarSpacing')}    unit="mm" step="25"/>
            <Field label="Dist. Bar Dia"       value={inp.distBarDia}        onChange={setN('distBarDia')}        unit="mm" step="2"/>
            <Field label="Dist. Bar Spacing"   value={inp.distBarSpacing}    onChange={setN('distBarSpacing')}    unit="mm" step="25"/>
            <Field label="Top Bar Dia"         value={inp.topBarDia}         onChange={setN('topBarDia')}         unit="mm" step="2"/>
            <Field label="Top Bar Spacing"     value={inp.topBarSpacing}     onChange={setN('topBarSpacing')}     unit="mm" step="25"/>
            <Field label="Stirrup Dia"         value={inp.stirrupDia}        onChange={setN('stirrupDia')}        unit="mm" step="2"/>
            <Field label="Stirrup Spacing"     value={inp.stirrupSpacing}    onChange={setN('stirrupSpacing')}    unit="mm" step="25"/>
            <Field label="Pier Main Bar Dia"   value={inp.pierMainBarDia}    onChange={setN('pierMainBarDia')}    unit="mm" step="2"/>
            <Field label="Pier Main Bar Count" value={inp.pierMainBarCount}  onChange={setN('pierMainBarCount')}  unit="nos" step="2"/>
            <Field label="Pier Links Dia"      value={inp.pierLinksDia}      onChange={setN('pierLinksDia')}      unit="mm" step="2"/>
            <Field label="Pier Links Spacing"  value={inp.pierLinksSpacing}  onChange={setN('pierLinksSpacing')}  unit="mm" step="25"/>
            <Field label="Cover — Foundation"  value={inp.coverFoundation}   onChange={setN('coverFoundation')}   unit="mm" step="5"/>
            <Field label="Cover — Stem"        value={inp.coverStem}         onChange={setN('coverStem')}         unit="mm" step="5"/>
            <Field label="Cover — Deck"        value={inp.coverDeck}         onChange={setN('coverDeck')}         unit="mm" step="5"/>
          </Section>

          <Section sec={SECTIONS[7]}>
            <div className="col-span-2">
              <SelectField label="Concrete Grade" value={inp.concreteGrade} onChange={setS('concreteGrade')}
                options={['M20','M25','M30','M35','M40'].map(v=>({value:v,label:v}))}/>
            </div>
            <Field label="fck" value={inp.fck} onChange={setN('fck')} unit="MPa"/>
            <div>
              <SelectField label="Steel Grade" value={inp.steelGrade} onChange={setS('steelGrade')}
                options={['Fe415','Fe500','Fe550'].map(v=>({value:v,label:v}))}/>
            </div>
            <Field label="fy" value={inp.fy} onChange={setN('fy')} unit="MPa"/>
            <div className="col-span-2">
              <SelectField label="Soil Type" value={inp.soilType} onChange={setS('soilType')}
                options={[
                  {value:'Medium hard rock',label:'Medium Hard Rock'},
                  {value:'Hard rock',       label:'Hard Rock'},
                  {value:'Soft rock',       label:'Soft Rock'},
                  {value:'Hard soil',       label:'Hard Soil'},
                  {value:'Medium soil',     label:'Medium Soil'},
                ]}/>
            </div>
            <Field label="SBC" value={inp.sbc} onChange={setN('sbc')} unit="kPa"/>
            <Field label="Phi (Φ)" value={inp.phi} onChange={setN('phi')} unit="°" step="1"/>
          </Section>
        </div>

        {/* Right: Scan + Drawings */}
        <div className="flex-1 flex flex-col gap-4 min-w-0">

          {/* ── SCAN REFERENCE DRAWING PANEL ── */}
          <div className="bg-card border border-card-border rounded-xl overflow-hidden">
            <button
              onClick={() => setScanOpen(o => !o)}
              className="flex items-center justify-between w-full px-5 py-4 hover:bg-muted/30 transition-colors"
            >
              <div className="flex items-center gap-2">
                <ScanLine className="w-5 h-5 text-primary"/>
                <span className="font-bold text-sm">Scan Reference Drawing — Auto-Fill Parameters</span>
                {scanResult && !scanApplied && (
                  <span className="ml-2 text-[10px] font-semibold bg-amber-500/15 text-amber-700 dark:text-amber-400 px-2 py-0.5 rounded-full">
                    {extractedCount} fields ready to apply
                  </span>
                )}
                {scanApplied && (
                  <span className="ml-2 text-[10px] font-semibold bg-chart-3/15 text-chart-3 px-2 py-0.5 rounded-full">
                    Applied ✓
                  </span>
                )}
              </div>
              {scanOpen ? <ChevronUp className="w-4 h-4 opacity-60"/> : <ChevronDown className="w-4 h-4 opacity-60"/>}
            </button>

            {scanOpen && (
              <div className="px-5 pb-5 flex flex-col gap-4">
                <p className="text-xs text-muted-foreground">
                  Upload any page from your physical reference drawings (JPG / PNG). AI reads all visible dimensions,
                  levels, and reinforcement details and auto-fills the parameter form. Then generate a similitude DXF.
                </p>

                {/* Drop zone */}
                {!scanImage ? (
                  <div
                    className={`border-2 border-dashed rounded-xl flex flex-col items-center justify-center py-8 px-4 cursor-pointer transition-all ${dragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/60 hover:bg-muted/30'}`}
                    onDragOver={e => { e.preventDefault(); setDragging(true); }}
                    onDragLeave={() => setDragging(false)}
                    onDrop={handleDrop}
                    onClick={() => fileRef.current?.click()}
                  >
                    <Upload className="w-8 h-8 text-muted-foreground mb-2"/>
                    <p className="text-sm font-medium text-foreground">Drop reference drawing here</p>
                    <p className="text-xs text-muted-foreground mt-1">or click to browse — JPG, PNG supported</p>
                    <input ref={fileRef} type="file" accept="image/*" className="hidden"
                      onChange={e => { const f = e.target.files?.[0]; if (f) loadImageFile(f); }}/>
                  </div>
                ) : (
                  <div className="flex gap-4 items-start">
                    {/* Thumbnail */}
                    <div className="relative flex-shrink-0">
                      <img
                        src={`data:${scanMime};base64,${scanImage}`}
                        alt="Reference drawing"
                        className="w-40 h-28 object-contain border border-border rounded-lg bg-white"
                      />
                      <button
                        onClick={clearScan}
                        className="absolute -top-2 -right-2 w-5 h-5 bg-destructive text-white rounded-full flex items-center justify-center hover:bg-destructive/80"
                      >
                        <X className="w-3 h-3"/>
                      </button>
                    </div>

                    <div className="flex-1 flex flex-col gap-2">
                      <p className="text-xs text-muted-foreground truncate">{scanFile}</p>

                      {!scanResult && !scanning && (
                        <button
                          onClick={scanDrawing}
                          className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-all shadow"
                        >
                          <ScanLine className="w-4 h-4"/>
                          Read Drawing with AI
                        </button>
                      )}

                      {scanning && (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"/>
                          Scanning drawing… extracting dimensions & levels…
                        </div>
                      )}

                      {scanError && (
                        <div className="flex items-start gap-2 text-xs text-destructive bg-destructive/10 rounded-lg p-3">
                          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5"/>
                          <span>{scanError}</span>
                        </div>
                      )}

                      {scanResult && (
                        <div className="flex flex-col gap-2">
                          <div className="flex items-center gap-2 text-xs text-chart-3 font-medium">
                            <CheckCircle className="w-4 h-4"/>
                            <span>{extractedCount} parameters extracted from drawing</span>
                          </div>
                          {scanResult.drawingType && (
                            <p className="text-xs text-muted-foreground">Detected: <strong>{scanResult.drawingType}</strong></p>
                          )}
                          {scanResult.notes && (
                            <p className="text-xs text-muted-foreground italic border-l-2 border-muted pl-2">{scanResult.notes}</p>
                          )}
                          {!scanApplied ? (
                            <button
                              onClick={applyScan}
                              className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-chart-3/90 text-white text-sm font-semibold hover:bg-chart-3 transition-all"
                            >
                              <CheckCircle className="w-4 h-4"/>
                              Apply {extractedCount} Extracted Values to Form
                            </button>
                          ) : (
                            <div className="flex items-center gap-2 text-xs text-chart-3 font-semibold">
                              <CheckCircle className="w-4 h-4"/> Form updated — now generate your similitude DXF drawings.
                            </div>
                          )}

                          {/* Extracted values preview */}
                          <details className="text-xs">
                            <summary className="cursor-pointer text-muted-foreground hover:text-foreground">Show extracted values</summary>
                            <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-0.5 max-h-48 overflow-y-auto pr-1">
                              {Object.entries(scanResult)
                                .filter(([k, v]) => k !== 'notes' && k !== 'drawingType' && v !== null && v !== undefined)
                                .map(([k, v]) => (
                                  <div key={k} className="flex gap-1">
                                    <span className="text-muted-foreground shrink-0 capitalize">{k.replace(/([A-Z])/g,' $1').trim()}:</span>
                                    <span className="font-medium text-foreground truncate">{String(v)}</span>
                                  </div>
                                ))}
                            </div>
                          </details>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ── DRAWING SELECTION ── */}
          <div className="bg-card border border-card-border rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-bold text-foreground">Drawing Set Selection</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Select drawings to generate and download as DXF files</p>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => setSelected(new Set(DRAWINGS.map(d => d.key)))}
                  className="text-xs text-primary hover:underline">All</button>
                <span className="text-muted-foreground text-xs">|</span>
                <button onClick={() => setSelected(new Set())}
                  className="text-xs text-muted-foreground hover:underline">None</button>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-2">
              {DRAWINGS.map(drw => (
                <div key={drw.key}
                  className={`flex items-center justify-between border rounded-lg px-4 py-3 transition-all cursor-pointer ${selected.has(drw.key) ? 'border-primary bg-primary/5' : 'border-border bg-background hover:border-muted-foreground'}`}
                  onClick={() => toggleDrawing(drw.key)}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all ${selected.has(drw.key) ? 'border-primary bg-primary' : 'border-muted-foreground'}`}>
                      {selected.has(drw.key) && <div className="w-2 h-2 bg-white rounded-sm"/>}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{drw.title}</p>
                      <p className="text-xs text-muted-foreground">{drw.subtitle}</p>
                    </div>
                  </div>
                  <button
                    onClick={e => { e.stopPropagation(); downloadSingle(drw); }}
                    className="ml-4 p-1.5 rounded-md text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors"
                    title="Download this drawing"
                  >
                    <Download className="w-4 h-4"/>
                  </button>
                </div>
              ))}
            </div>

            <div className="mt-5 flex flex-col gap-3">
              <button
                onClick={generateAll}
                disabled={generating || selected.size === 0}
                className="flex items-center justify-center gap-2 w-full py-3 rounded-lg bg-primary text-primary-foreground font-semibold text-sm hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md"
              >
                {generating
                  ? <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"/><span>Generating DXF Files…</span></>
                  : <><Zap className="w-4 h-4"/><span>Generate & Download {selected.size} DXF Drawing{selected.size !== 1 ? 's' : ''}</span></>
                }
              </button>
              {generated && (
                <div className="rounded-lg bg-chart-3/10 border border-chart-3/30 px-4 py-2.5 flex items-center gap-2">
                  <div className="w-5 h-5 rounded-full bg-chart-3 flex items-center justify-center text-white text-xs">✓</div>
                  <p className="text-sm text-foreground">
                    <span className="font-semibold">{selected.size} DXF file{selected.size !== 1 ? 's' : ''}</span> downloaded — open in AutoCAD, BricsCAD, or LibreCAD.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* ── PROJECT SUMMARY ── */}
          <div className="bg-card border border-card-border rounded-xl p-5">
            <h3 className="font-bold text-sm mb-3 flex items-center gap-2"><FileText className="w-4 h-4"/> Project Summary</h3>
            <div className="grid grid-cols-2 gap-x-8 gap-y-1.5 text-xs">
              {[
                ['Project',          inp.projectName],
                ['Drawing No.',      inp.drawingNo],
                ['Type',             inp.bridgeType === 'submersible' ? 'Submersible' : 'High Level'],
                ['Span Arrangement', `${inp.numberOfSpans} × ${inp.spanLength}m = ${inp.totalLength}m`],
                ['Total Width',      `${(inp.carriageWidth + 2*(inp.footpathWidth + inp.kerbWidth)).toFixed(2)}m`],
                ['Carriageway',      `${inp.carriageWidth}m (${inp.numberOfLanes} lanes)`],
                ['HFL',              `${inp.hfl.toFixed(2)} m MSL`],
                ['Bed Level',        `${inp.bedLevel.toFixed(2)} m MSL`],
                ['Foundation Level', `${inp.foundationLevel.toFixed(2)} m MSL`],
                ['RTL',              `${inp.rtl.toFixed(2)} m MSL`],
                ['Pier Size',        `${inp.pierWidth}×${inp.pierLength}m, ${inp.pierDepth}m deep`],
                ['Slab Thickness',   `${(inp.slabThickness*1000).toFixed(0)} mm`],
                ['Concrete',         `${inp.concreteGrade} (fck=${inp.fck} MPa)`],
                ['Steel',            `${inp.steelGrade} (fy=${inp.fy} MPa)`],
                ['Main Rebar',       `T${inp.mainBarDia} @ ${inp.mainBarSpacing}mm c/c`],
                ['Load',             inp.loadClass],
              ].map(([k,v]) => (
                <div key={k} className="flex gap-2">
                  <span className="text-muted-foreground min-w-[120px] shrink-0">{k}:</span>
                  <span className="font-medium truncate">{v}</span>
                </div>
              ))}
            </div>
          </div>

          {/* ── HOW TO USE ── */}
          <div className="bg-card border border-card-border rounded-xl p-5">
            <h3 className="font-bold text-sm mb-3">Workflow — Reference to Similitude DXF</h3>
            <ol className="text-xs text-muted-foreground space-y-2 list-decimal list-inside">
              <li><strong>Scan</strong> — Upload any page from your reference drawing set (PNG/JPG). AI reads all visible dimensions, levels, and rebar specs.</li>
              <li><strong>Apply</strong> — Click "Apply Extracted Values" to auto-fill all parameters. Review and adjust any values if needed.</li>
              <li><strong>Generate</strong> — Click "Generate & Download DXF". All 8 drawings are produced as <code className="bg-muted px-1 rounded">.dxf</code> files matching your reference bridge geometry.</li>
              <li><strong>Open in AutoCAD</strong> — Layers are pre-defined: STRUCTURE (blue), PIERS (green), ABUTMENTS (cyan), REBAR (red), DIMENSIONS (yellow).</li>
              <li><strong>Repeat</strong> — Upload each drawing page from your 25-set collection to build a library of similitude DXFs.</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
