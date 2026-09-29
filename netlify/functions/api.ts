import type { Config } from "@netlify/functions";
import { asc, desc, eq, sql } from "drizzle-orm";
import { db } from "../../db/index.js";
import { orders, products, settings } from "../../db/schema.js";

const ORDER_STATUSES = ["Pending", "Confirmed", "Completed", "Cancelled"];

const json = (obj: unknown, status = 200) => Response.json(obj, { status });

const num = (v: unknown, fallback = 0) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
};
const str = (v: unknown) => (v == null ? "" : String(v));

function productValues(d: Record<string, any>) {
  return {
    name: str(d.name) || "Unnamed Product",
    code: str(d.code),
    fabric: str(d.fabric),
    color: str(d.color),
    thaan: num(d.thaan),
    suit: num(d.suit),
    sale_thaan: num(d.sale_thaan),
    sale_suit: num(d.sale_suit),
    image: str(d.image),
    description: str(d.description),
    sale_on: Boolean(d.sale_on),
    new_arrival: Boolean(d.new_arrival),
    stock: d.stock === undefined ? true : Boolean(d.stock),
  };
}

// Same starter data the original Python server created on first run
async function seedIfEmpty() {
  const [{ count }] = await db.select({ count: sql<number>`count(*)::int` }).from(products);
  if (count === 0) {
    await db.insert(products).values({
      name: "Premium Black",
      code: "AN-SC-BLK-001",
      fabric: "Premium Gents Unstitched",
      color: "Black",
      thaan: 3843,
      suit: 5243,
      image: JSON.stringify(["/media/fabric_1.png", "/media/fabric_2.png", "/media/fabric_3.png", "/media/fabric_4.png"]),
      description: "Premium black fabric. Four product views are shown on the card and product page.",
      new_arrival: true,
      stock: true,
    });
  }
  await db
    .insert(settings)
    .values({ id: 1, name: "AL NAFAY", tagline: "Quality · Comfort · Style" })
    .onConflictDoNothing();
}

async function readBody(req: Request): Promise<Record<string, any>> {
  try {
    return (await req.json()) ?? {};
  } catch {
    return {};
  }
}

export default async (req: Request) => {
  const path = new URL(req.url).pathname.replace(/\/+$/, "");
  const parts = path.split("/").filter(Boolean); // ["api", resource, id?]
  const resource = parts[1];
  const id = parts[2] !== undefined ? parseInt(parts[2], 10) : null;
  if (parts[2] !== undefined && !Number.isInteger(id)) return json({ error: "Not found" }, 404);

  try {
    if (req.method === "GET") {
      await seedIfEmpty();
      if (resource === "products" && id === null) {
        return json(await db.select().from(products).orderBy(asc(products.id)));
      }
      if (resource === "orders" && id === null) {
        return json(await db.select().from(orders).orderBy(desc(orders.id)));
      }
      if (resource === "customers") {
        const rows = await db
          .select({
            name: orders.name,
            phone: orders.phone,
            email: orders.email,
            city: orders.city,
            address: orders.address,
            order_count: sql<number>`count(*)::int`,
            last_order_at: sql<string>`max(${orders.created_at})`,
          })
          .from(orders)
          .where(sql`${orders.name} <> ''`)
          .groupBy(orders.name, orders.phone, orders.email, orders.city, orders.address)
          .orderBy(sql`max(${orders.created_at}) desc`);
        return json(rows);
      }
      if (resource === "settings") {
        const [row] = await db.select().from(settings).where(eq(settings.id, 1));
        return json(row ?? {});
      }
    }

    if (req.method === "POST") {
      const d = await readBody(req);
      if (resource === "products" && id === null) {
        const [row] = await db.insert(products).values(productValues(d)).returning();
        return json(row, 201);
      }
      if (resource === "orders" && id === null) {
        const now = new Date().toISOString().slice(0, 19).replace("T", " ");
        const [row] = await db
          .insert(orders)
          .values({
            created_at: now,
            product_id: Math.trunc(num(d.product_id)),
            product: str(d.product),
            tone: str(d.tone),
            option: str(d.option),
            unit_price: num(d.unit_price),
            quantity: Math.max(1, Math.trunc(num(d.quantity, 1))),
            total: num(d.total),
            name: str(d.name),
            email: str(d.email),
            phone: str(d.phone),
            city: str(d.city),
            address: str(d.address),
            note: str(d.note),
            status: "Pending",
          })
          .returning();
        return json(row, 201);
      }
      if (resource === "settings") {
        const values = {
          name: str(d.name) || "AL NAFAY",
          tagline: str(d.tagline) || "Quality · Comfort · Style",
          wa: str(d.wa),
          phone: str(d.phone),
          ig: str(d.ig),
        };
        const [row] = await db
          .insert(settings)
          .values({ id: 1, ...values })
          .onConflictDoUpdate({ target: settings.id, set: values })
          .returning();
        return json(row);
      }
    }

    if (req.method === "PUT" && id !== null) {
      const d = await readBody(req);
      if (resource === "products") {
        const [row] = await db.update(products).set(productValues(d)).where(eq(products.id, id)).returning();
        return row ? json(row) : json({ error: "Product not found" }, 404);
      }
      if (resource === "orders") {
        const status = str(d.status) || "Pending";
        if (!ORDER_STATUSES.includes(status)) return json({ error: "Invalid status" }, 400);
        const [row] = await db.update(orders).set({ status }).where(eq(orders.id, id)).returning();
        return row ? json(row) : json({ error: "Order not found" }, 404);
      }
    }

    if (req.method === "DELETE" && id !== null && resource === "products") {
      await db.delete(products).where(eq(products.id, id));
      return json({ ok: true });
    }

    return json({ error: "Not found" }, 404);
  } catch (err) {
    console.error(err);
    return json({ error: "Server error" }, 500);
  }
};

export const config: Config = {
  path: ["/api/:resource", "/api/:resource/:id"],
};
