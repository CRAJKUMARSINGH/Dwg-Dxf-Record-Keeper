import { Router, type IRouter } from "express";
import { eq, and } from "drizzle-orm";
import { db, comparisonsTable } from "@workspace/db";
import {
  CreateComparisonBody,
  GetComparisonParams,
  DeleteComparisonParams,
  ListComparisonsQueryParams,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/comparisons", async (req, res): Promise<void> => {
  const params = ListComparisonsQueryParams.safeParse(req.query);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const comparisons = params.data.projectId != null
    ? await db.select().from(comparisonsTable).where(eq(comparisonsTable.projectId, params.data.projectId)).orderBy(comparisonsTable.createdAt)
    : await db.select().from(comparisonsTable).orderBy(comparisonsTable.createdAt);

  res.json(comparisons);
});

router.post("/comparisons", async (req, res): Promise<void> => {
  const parsed = CreateComparisonBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }
  const [comparison] = await db.insert(comparisonsTable).values(parsed.data).returning();
  res.status(201).json(comparison);
});

router.get("/comparisons/:id", async (req, res): Promise<void> => {
  const params = GetComparisonParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [comparison] = await db.select().from(comparisonsTable).where(eq(comparisonsTable.id, params.data.id));
  if (!comparison) {
    res.status(404).json({ error: "Comparison not found" });
    return;
  }
  res.json(comparison);
});

router.delete("/comparisons/:id", async (req, res): Promise<void> => {
  const params = DeleteComparisonParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }
  const [comparison] = await db.delete(comparisonsTable).where(eq(comparisonsTable.id, params.data.id)).returning();
  if (!comparison) {
    res.status(404).json({ error: "Comparison not found" });
    return;
  }
  res.sendStatus(204);
});

export default router;
