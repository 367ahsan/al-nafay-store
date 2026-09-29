CREATE TABLE "orders" (
	"id" serial PRIMARY KEY,
	"created_at" text NOT NULL,
	"product_id" integer DEFAULT 0 NOT NULL,
	"product" text DEFAULT '' NOT NULL,
	"tone" text DEFAULT '' NOT NULL,
	"option" text DEFAULT '' NOT NULL,
	"unit_price" double precision DEFAULT 0 NOT NULL,
	"quantity" integer DEFAULT 1 NOT NULL,
	"total" double precision DEFAULT 0 NOT NULL,
	"name" text DEFAULT '' NOT NULL,
	"email" text DEFAULT '' NOT NULL,
	"phone" text DEFAULT '' NOT NULL,
	"city" text DEFAULT '' NOT NULL,
	"address" text DEFAULT '' NOT NULL,
	"note" text DEFAULT '' NOT NULL,
	"status" text DEFAULT 'Pending' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "products" (
	"id" serial PRIMARY KEY,
	"name" text NOT NULL,
	"code" text DEFAULT '' NOT NULL,
	"fabric" text DEFAULT '' NOT NULL,
	"color" text DEFAULT '' NOT NULL,
	"thaan" double precision DEFAULT 0 NOT NULL,
	"suit" double precision DEFAULT 0 NOT NULL,
	"sale_thaan" double precision DEFAULT 0 NOT NULL,
	"sale_suit" double precision DEFAULT 0 NOT NULL,
	"image" text DEFAULT '' NOT NULL,
	"description" text DEFAULT '' NOT NULL,
	"sale_on" boolean DEFAULT false NOT NULL,
	"new_arrival" boolean DEFAULT false NOT NULL,
	"stock" boolean DEFAULT true NOT NULL
);
--> statement-breakpoint
CREATE TABLE "settings" (
	"id" integer PRIMARY KEY,
	"name" text,
	"tagline" text,
	"wa" text,
	"phone" text,
	"ig" text
);
