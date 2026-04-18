import { Router, type IRouter } from "express";
import healthRouter from "./health";
import projectsRouter from "./projects";
import filesRouter from "./files";
import recordsRouter from "./records";
import comparisonsRouter from "./comparisons";
import statsRouter from "./stats";
import scanDrawingRouter from "./scan-drawing";

const router: IRouter = Router();

router.use(healthRouter);
router.use(projectsRouter);
router.use(filesRouter);
router.use(recordsRouter);
router.use(comparisonsRouter);
router.use(statsRouter);
router.use(scanDrawingRouter);

export default router;
