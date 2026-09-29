import { pgTable, serial, text, integer, doublePrecision, boolean } from "drizzle-orm/pg-core";

export const products = pgTable("products", {
  id: serial().primaryKey(),
  name: text().notNull(),
  code: text().notNull().default(""),
  fabric: text().notNull().default(""),
  color: text().notNull().default(""),
  thaan: doublePrecision().notNull().default(0),
  suit: doublePrecision().notNull().default(0),
  sale_thaan: doublePrecision("sale_thaan").notNull().default(0),
  sale_suit: doublePrecision("sale_suit").notNull().default(0),
  image: text().notNull().default(""),
  description: text().notNull().default(""),
  sale_on: boolean("sale_on").notNull().default(false),
  new_arrival: boolean("new_arrival").notNull().default(false),
  stock: boolean().notNull().default(true),
});

export const orders = pgTable("orders", {
  id: serial().primaryKey(),
  created_at: text("created_at").notNull(),
  product_id: integer("product_id").notNull().default(0),
  product: text().notNull().default(""),
  tone: text().notNull().default(""),
  option: text().notNull().default(""),
  unit_price: doublePrecision("unit_price").notNull().default(0),
  quantity: integer().notNull().default(1),
  total: doublePrecision().notNull().default(0),
  name: text().notNull().default(""),
  email: text().notNull().default(""),
  phone: text().notNull().default(""),
  city: text().notNull().default(""),
  address: text().notNull().default(""),
  note: text().notNull().default(""),
  status: text().notNull().default("Pending"),
});

export const settings = pgTable("settings", {
  id: integer().primaryKey(),
  name: text(),
  tagline: text(),
  wa: text(),
  phone: text(),
  ig: text(),
});
