import { Router, type IRouter } from "express";
import { eq, and, isNull, or, sql } from "drizzle-orm";
import { db, fileRecordsTable } from "@workspace/db";
import {
  CreateFileRecordBody,
  GetFileRecordParams,
  UpdateFileRecordParams,
  UpdateFileRecordBody,
  DeleteFileRecordParams,
  ListFilesQueryParams,
  GetSimilarFilesParams,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/files", async (req, res): Promise<void> => {
  const params = ListFilesQueryParams.safeParse(req.query);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const conditions = [];
  if (params.data.projectId != null) {
    conditions.push(eq(fileRecordsTable.projectId, params.data.projectId));
  }
  if (params.data.fileType != null) {
    conditions.push(eq(fileRecordsTable.fileType, params.data.fileType));
  }

  const files = conditions.length > 0
    ? await db.select().from(fileRecordsTable).where(and(...conditions)).orderBy(fileRecordsTable.createdAt)
    : await db.select().from(fileRecordsTable).orderBy(fileRecordsTable.createdAt);

  res.json(files);
});

router.post("/files", async (req, res): Promise<void> => {
  const parsed = CreateFileRecordBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  const [file] = await db.insert(fileRecordsTable).values(parsed.data).returning();
  res.status(201).json(file);
});

router.get("/files/:id", async (req, res): Promise<void> => {
  const params = GetFileRecordParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [file] = await db.select().from(fileRecordsTable).where(eq(fileRecordsTable.id, params.data.id));
  if (!file) {
    res.status(404).json({ error: "File record not found" });
    return;
  }
  res.json(file);
});

router.patch("/files/:id", async (req, res): Promise<void> => {
  const params = UpdateFileRecordParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const parsed = UpdateFileRecordBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const updateData: Record<string, unknown> = {};
  const d = parsed.data;
  if (d.projectId !== undefined) updateData.projectId = d.projectId;
  if (d.bridgeType !== undefined) updateData.bridgeType = d.bridgeType;
  if (d.spanLength !== undefined) updateData.spanLength = d.spanLength;
  if (d.width !== undefined) updateData.width = d.width;
  if (d.height !== undefined) updateData.height = d.height;
  if (d.material !== undefined) updateData.material = d.material;
  if (d.loadCapacity !== undefined) updateData.loadCapacity = d.loadCapacity;
  if (d.designCode !== undefined) updateData.designCode = d.designCode;
  if (d.layers !== undefined) updateData.layers = d.layers;
  if (d.pageCount !== undefined) updateData.pageCount = d.pageCount;
  if (d.extractedData !== undefined) updateData.extractedData = d.extractedData;
  if (d.tags !== undefined) updateData.tags = d.tags;
  if (d.notes !== undefined) updateData.notes = d.notes;
  if (d.analysisStatus != null) updateData.analysisStatus = d.analysisStatus;

  const [file] = await db
    .update(fileRecordsTable)
    .set(updateData)
    .where(eq(fileRecordsTable.id, params.data.id))
    .returning();

  if (!file) {
    res.status(404).json({ error: "File record not found" });
    return;
  }
  res.json(file);
});

router.delete("/files/:id", async (req, res): Promise<void> => {
  const params = DeleteFileRecordParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [file] = await db.delete(fileRecordsTable).where(eq(fileRecordsTable.id, params.data.id)).returning();
  if (!file) {
    res.status(404).json({ error: "File record not found" });
    return;
  }
  res.sendStatus(204);
});

router.get("/files/:id/similar", async (req, res): Promise<void> => {
  const params = GetSimilarFilesParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [target] = await db.select().from(fileRecordsTable).where(eq(fileRecordsTable.id, params.data.id));
  if (!target) {
    res.status(404).json({ error: "File record not found" });
    return;
  }

  const similar = await db.select().from(fileRecordsTable).where(
    and(
      eq(fileRecordsTable.id, params.data.id),
    )
  );

  const allFiles = await db.select().from(fileRecordsTable);
  const others = allFiles
    .filter((f) => f.id !== target.id)
    .filter((f) => {
      let score = 0;
      if (f.bridgeType && f.bridgeType === target.bridgeType) score += 3;
      if (f.material && f.material === target.material) score += 2;
      if (f.fileType === target.fileType) score += 1;
      if (f.spanLength && target.spanLength && Math.abs(f.spanLength - target.spanLength) < target.spanLength * 0.2) score += 2;
      return score >= 2;
    })
    .slice(0, 5);

  res.json(others);
});

export default router;
