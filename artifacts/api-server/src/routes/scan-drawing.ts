import { Router, type IRouter } from "express";
import Anthropic from "@anthropic-ai/sdk";

const router: IRouter = Router();

const client = new Anthropic({
  baseURL: process.env.AI_INTEGRATIONS_ANTHROPIC_BASE_URL,
  apiKey: process.env.AI_INTEGRATIONS_ANTHROPIC_API_KEY ?? "dummy",
});

const EXTRACTION_PROMPT = `You are an expert structural engineer who reads AutoCAD engineering drawings for RCC slab bridges (IRC SP-13, IRC:6, IRC:112 codes, India).

Analyse this bridge drawing image carefully and extract every dimension, level, and parameter you can see. Return a JSON object with ONLY the fields you can read — do not guess or invent values you cannot see. Use null for anything not visible.

Return valid JSON matching this schema:
{
  "projectName": string | null,
  "riverName": string | null,
  "location": string | null,
  "bridgeType": "submersible" | "highlevel" | null,
  "drawingType": "GAD" | "plan" | "cross_section" | "pier" | "abutment" | "deck_rebar" | "wing_wall" | "longitudinal" | "unknown",
  "spanLength": number | null,
  "numberOfSpans": number | null,
  "totalLength": number | null,
  "numberOfPiers": number | null,
  "carriageWidth": number | null,
  "footpathWidth": number | null,
  "numberOfLanes": number | null,
  "rtl": number | null,
  "hfl": number | null,
  "ofl": number | null,
  "dwl": number | null,
  "bedLevel": number | null,
  "foundationLevel": number | null,
  "agl": number | null,
  "discharge": number | null,
  "afflux": number | null,
  "slabThickness": number | null,
  "wearingCoatThickness": number | null,
  "kerbHeight": number | null,
  "kerbWidth": number | null,
  "dirtWallHeight": number | null,
  "pierWidth": number | null,
  "pierLength": number | null,
  "pierDepth": number | null,
  "pierBaseWidth": number | null,
  "pierBaseLength": number | null,
  "pierCapHeight": number | null,
  "pierCapWidth": number | null,
  "abutmentHeight": number | null,
  "abutmentWidth": number | null,
  "abutmentBaseWidth": number | null,
  "abutmentDepth": number | null,
  "returnWallLength": number | null,
  "wingWallAngle": number | null,
  "mainBarDia": number | null,
  "mainBarSpacing": number | null,
  "distBarDia": number | null,
  "distBarSpacing": number | null,
  "topBarDia": number | null,
  "topBarSpacing": number | null,
  "stirrupDia": number | null,
  "stirrupSpacing": number | null,
  "pierMainBarDia": number | null,
  "pierMainBarCount": number | null,
  "pierLinksDia": number | null,
  "pierLinksSpacing": number | null,
  "concreteGrade": string | null,
  "steelGrade": string | null,
  "fck": number | null,
  "fy": number | null,
  "sbc": number | null,
  "phi": number | null,
  "loadClass": string | null,
  "designCode": string | null,
  "notes": string
}

The "notes" field should summarise what drawing type this is and what you could/could not read clearly. All lengths in metres, angles in degrees, bar diameters in mm, spacings in mm, levels in m MSL.`;

router.post("/api/scan-drawing", async (req, res) => {
  try {
    const { imageBase64, mimeType } = req.body as { imageBase64: string; mimeType: string };

    if (!imageBase64) {
      res.status(400).json({ error: "imageBase64 is required" });
      return;
    }

    const validMime = (mimeType === "image/jpeg" || mimeType === "image/png" ||
      mimeType === "image/gif" || mimeType === "image/webp")
      ? mimeType as "image/jpeg" | "image/png" | "image/gif" | "image/webp"
      : "image/jpeg";

    const message = await client.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 8192,
      messages: [{
        role: "user",
        content: [
          { type: "image", source: { type: "base64", media_type: validMime, data: imageBase64 } },
          { type: "text", text: EXTRACTION_PROMPT },
        ],
      }],
    });

    const rawText = message.content
      .filter((b) => b.type === "text")
      .map((b) => (b as { type: "text"; text: string }).text)
      .join("");

    const jsonMatch = rawText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      res.status(422).json({ error: "Could not parse AI response", raw: rawText });
      return;
    }

    res.json({ success: true, data: JSON.parse(jsonMatch[0]) });
  } catch (err: unknown) {
    res.status(500).json({ error: err instanceof Error ? err.message : String(err) });
  }
});

export default router;
