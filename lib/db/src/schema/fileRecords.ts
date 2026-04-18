import { pgTable, text, serial, timestamp, integer, real } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const fileRecordsTable = pgTable("file_records", {
  id: serial("id").primaryKey(),
  projectId: integer("project_id"),
  fileName: text("file_name").notNull(),
  fileType: text("file_type").notNull(),
  fileSizeKb: real("file_size_kb"),
  bridgeType: text("bridge_type"),
  spanLength: real("span_length"),
  width: real("width"),
  height: real("height"),
  material: text("material"),
  loadCapacity: real("load_capacity"),
  designCode: text("design_code"),
  layers: text("layers"),
  pageCount: integer("page_count"),
  extractedData: text("extracted_data"),
  tags: text("tags"),
  notes: text("notes"),
  analysisStatus: text("analysis_status").notNull().default("pending"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
});

export const insertFileRecordSchema = createInsertSchema(fileRecordsTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertFileRecord = z.infer<typeof insertFileRecordSchema>;
export type FileRecord = typeof fileRecordsTable.$inferSelect;
