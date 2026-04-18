import { pgTable, text, serial, timestamp, integer, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const analysisRecordsTable = pgTable("analysis_records", {
  id: serial("id").primaryKey(),
  projectId: integer("project_id"),
  fileId: integer("file_id"),
  title: text("title").notNull(),
  variationType: text("variation_type").notNull(),
  description: text("description"),
  parameters: text("parameters"),
  notes: text("notes"),
  referenceFiles: text("reference_files"),
  isFavorite: boolean("is_favorite").notNull().default(false),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
});

export const insertAnalysisRecordSchema = createInsertSchema(analysisRecordsTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertAnalysisRecord = z.infer<typeof insertAnalysisRecordSchema>;
export type AnalysisRecord = typeof analysisRecordsTable.$inferSelect;
