import { Router, type IRouter } from "express";
import { eq, sql } from "drizzle-orm";
import { db, projectsTable, fileRecordsTable, analysisRecordsTable } from "@workspace/db";
import {
  CreateProjectBody,
  GetProjectParams,
  UpdateProjectParams,
  UpdateProjectBody,
  DeleteProjectParams,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/projects", async (req, res): Promise<void> => {
  const projects = await db.select().from(projectsTable).orderBy(projectsTable.createdAt);

  const fileCounts = await db
    .select({ projectId: fileRecordsTable.projectId, count: sql<number>`count(*)::int` })
    .from(fileRecordsTable)
    .groupBy(fileRecordsTable.projectId);

  const recordCounts = await db
    .select({ projectId: analysisRecordsTable.projectId, count: sql<number>`count(*)::int` })
    .from(analysisRecordsTable)
    .groupBy(analysisRecordsTable.projectId);

  const fileCountMap = Object.fromEntries(fileCounts.map((f) => [f.projectId, f.count]));
  const recordCountMap = Object.fromEntries(recordCounts.map((r) => [r.projectId, r.count]));

  const result = projects.map((p) => ({
    ...p,
    fileCount: fileCountMap[p.id] ?? 0,
    recordCount: recordCountMap[p.id] ?? 0,
  }));

  res.json(result);
});

router.post("/projects", async (req, res): Promise<void> => {
  const parsed = CreateProjectBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  const [project] = await db.insert(projectsTable).values(parsed.data).returning();
  res.status(201).json({ ...project, fileCount: 0, recordCount: 0 });
});

router.get("/projects/:id", async (req, res): Promise<void> => {
  const params = GetProjectParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [project] = await db.select().from(projectsTable).where(eq(projectsTable.id, params.data.id));
  if (!project) {
    res.status(404).json({ error: "Project not found" });
    return;
  }

  const [fileCount] = await db
    .select({ count: sql<number>`count(*)::int` })
    .from(fileRecordsTable)
    .where(eq(fileRecordsTable.projectId, project.id));

  const [recordCount] = await db
    .select({ count: sql<number>`count(*)::int` })
    .from(analysisRecordsTable)
    .where(eq(analysisRecordsTable.projectId, project.id));

  res.json({ ...project, fileCount: fileCount?.count ?? 0, recordCount: recordCount?.count ?? 0 });
});

router.patch("/projects/:id", async (req, res): Promise<void> => {
  const params = UpdateProjectParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const parsed = UpdateProjectBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const updateData: Record<string, unknown> = {};
  if (parsed.data.name != null) updateData.name = parsed.data.name;
  if (parsed.data.description !== undefined) updateData.description = parsed.data.description;
  if (parsed.data.bridgeType !== undefined) updateData.bridgeType = parsed.data.bridgeType;
  if (parsed.data.location !== undefined) updateData.location = parsed.data.location;
  if (parsed.data.status != null) updateData.status = parsed.data.status;

  const [project] = await db
    .update(projectsTable)
    .set(updateData)
    .where(eq(projectsTable.id, params.data.id))
    .returning();

  if (!project) {
    res.status(404).json({ error: "Project not found" });
    return;
  }

  const [fileCount] = await db
    .select({ count: sql<number>`count(*)::int` })
    .from(fileRecordsTable)
    .where(eq(fileRecordsTable.projectId, project.id));

  const [recordCount] = await db
    .select({ count: sql<number>`count(*)::int` })
    .from(analysisRecordsTable)
    .where(eq(analysisRecordsTable.projectId, project.id));

  res.json({ ...project, fileCount: fileCount?.count ?? 0, recordCount: recordCount?.count ?? 0 });
});

router.delete("/projects/:id", async (req, res): Promise<void> => {
  const params = DeleteProjectParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [project] = await db.delete(projectsTable).where(eq(projectsTable.id, params.data.id)).returning();
  if (!project) {
    res.status(404).json({ error: "Project not found" });
    return;
  }
  res.sendStatus(204);
});

export default router;
