import { Router, type IRouter } from "express";
import { eq, and, sql } from "drizzle-orm";
import { db, analysisRecordsTable } from "@workspace/db";
import {
  CreateAnalysisRecordBody,
  GetAnalysisRecordParams,
  UpdateAnalysisRecordParams,
  UpdateAnalysisRecordBody,
  DeleteAnalysisRecordParams,
  ListAnalysisRecordsQueryParams,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/records/variations", async (req, res): Promise<void> => {
  const allRecords = await db.select().from(analysisRecordsTable).orderBy(analysisRecordsTable.createdAt);

  const grouped: Record<string, typeof allRecords> = {};
  for (const record of allRecords) {
    if (!grouped[record.variationType]) {
      grouped[record.variationType] = [];
    }
    grouped[record.variationType].push(record);
  }

  const result = Object.entries(grouped).map(([variationType, records]) => ({
    variationType,
    count: records.length,
    examples: records.slice(0, 3),
  }));

  res.json(result);
});

router.get("/records", async (req, res): Promise<void> => {
  const params = ListAnalysisRecordsQueryParams.safeParse(req.query);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const conditions = [];
  if (params.data.projectId != null) {
    conditions.push(eq(analysisRecordsTable.projectId, params.data.projectId));
  }
  if (params.data.fileId != null) {
    conditions.push(eq(analysisRecordsTable.fileId, params.data.fileId));
  }

  const records = conditions.length > 0
    ? await db.select().from(analysisRecordsTable).where(and(...conditions)).orderBy(analysisRecordsTable.createdAt)
    : await db.select().from(analysisRecordsTable).orderBy(analysisRecordsTable.createdAt);

  res.json(records);
});

router.post("/records", async (req, res): Promise<void> => {
  const parsed = CreateAnalysisRecordBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  const [record] = await db.insert(analysisRecordsTable).values(parsed.data).returning();
  res.status(201).json(record);
});

router.get("/records/:id", async (req, res): Promise<void> => {
  const params = GetAnalysisRecordParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [record] = await db.select().from(analysisRecordsTable).where(eq(analysisRecordsTable.id, params.data.id));
  if (!record) {
    res.status(404).json({ error: "Analysis record not found" });
    return;
  }
  res.json(record);
});

router.patch("/records/:id", async (req, res): Promise<void> => {
  const params = UpdateAnalysisRecordParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const parsed = UpdateAnalysisRecordBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const updateData: Record<string, unknown> = {};
  const d = parsed.data;
  if (d.title != null) updateData.title = d.title;
  if (d.variationType != null) updateData.variationType = d.variationType;
  if (d.description !== undefined) updateData.description = d.description;
  if (d.parameters !== undefined) updateData.parameters = d.parameters;
  if (d.notes !== undefined) updateData.notes = d.notes;
  if (d.referenceFiles !== undefined) updateData.referenceFiles = d.referenceFiles;
  if (d.isFavorite != null) updateData.isFavorite = d.isFavorite;

  const [record] = await db
    .update(analysisRecordsTable)
    .set(updateData)
    .where(eq(analysisRecordsTable.id, params.data.id))
    .returning();

  if (!record) {
    res.status(404).json({ error: "Analysis record not found" });
    return;
  }
  res.json(record);
});

router.delete("/records/:id", async (req, res): Promise<void> => {
  const params = DeleteAnalysisRecordParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [record] = await db.delete(analysisRecordsTable).where(eq(analysisRecordsTable.id, params.data.id)).returning();
  if (!record) {
    res.status(404).json({ error: "Analysis record not found" });
    return;
  }
  res.sendStatus(204);
});

export default router;
