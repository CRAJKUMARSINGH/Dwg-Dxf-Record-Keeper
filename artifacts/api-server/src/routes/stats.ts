import { Router, type IRouter } from "express";
import { sql } from "drizzle-orm";
import { db, projectsTable, fileRecordsTable, analysisRecordsTable, comparisonsTable } from "@workspace/db";

const router: IRouter = Router();

router.get("/stats/summary", async (req, res): Promise<void> => {
  const [projectCount] = await db.select({ count: sql<number>`count(*)::int` }).from(projectsTable);
  const [fileCount] = await db.select({ count: sql<number>`count(*)::int` }).from(fileRecordsTable);
  const [recordCount] = await db.select({ count: sql<number>`count(*)::int` }).from(analysisRecordsTable);
  const [comparisonCount] = await db.select({ count: sql<number>`count(*)::int` }).from(comparisonsTable);

  const filesByTypeRaw = await db
    .select({ label: fileRecordsTable.fileType, count: sql<number>`count(*)::int` })
    .from(fileRecordsTable)
    .groupBy(fileRecordsTable.fileType);

  const recordsByTypeRaw = await db
    .select({ label: analysisRecordsTable.variationType, count: sql<number>`count(*)::int` })
    .from(analysisRecordsTable)
    .groupBy(analysisRecordsTable.variationType);

  const recentFiles = await db
    .select()
    .from(fileRecordsTable)
    .orderBy(sql`created_at desc`)
    .limit(5);

  res.json({
    totalProjects: projectCount?.count ?? 0,
    totalFiles: fileCount?.count ?? 0,
    totalRecords: recordCount?.count ?? 0,
    totalComparisons: comparisonCount?.count ?? 0,
    filesByType: filesByTypeRaw,
    recordsByVariationType: recordsByTypeRaw,
    recentFiles,
  });
});

export default router;
