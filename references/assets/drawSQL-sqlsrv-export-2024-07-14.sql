CREATE TABLE "validation_triplets"(
    "id" BIGINT NOT NULL,
    "reference_id" TEXT NOT NULL,
    "left_id" TEXT NOT NULL,
    "right_id" TEXT NOT NULL,
    "label" NVARCHAR(255) CHECK
        ("label" IN(N'')) NOT NULL,
        "left_encoder_id" TEXT NOT NULL,
        "right_encoder_id" TEXT NOT NULL,
        "user_id" TEXT NOT NULL,
        "retrieved_at" DATETIME NOT NULL
);
ALTER TABLE
    "validation_triplets" ADD CONSTRAINT "validation_triplets_id_primary" PRIMARY KEY("id");
CREATE TABLE "all_triplets_upload_statuses"(
    "id" BIGINT NOT NULL,
    "to_upload_count" BIGINT NOT NULL,
    "uploaded_count" BIGINT NOT NULL
);
ALTER TABLE
    "all_triplets_upload_statuses" ADD CONSTRAINT "all_triplets_upload_statuses_id_primary" PRIMARY KEY("id");
CREATE TABLE "triplets"(
    "id" BIGINT NOT NULL,
    "reference_id" TEXT NOT NULL,
    "left_id" TEXT NOT NULL,
    "right_id" TEXT NOT NULL,
    "label" NVARCHAR(255) CHECK
        ("label" IN(N'')) NOT NULL,
        "encoder_id" TEXT NOT NULL,
        "user_id" TEXT NOT NULL,
        "retrieved_at" DATETIME NOT NULL
);
ALTER TABLE
    "triplets" ADD CONSTRAINT "triplets_id_primary" PRIMARY KEY("id");
CREATE TABLE "items"(
    "id" TEXT NOT NULL,
    "length" FLOAT(53) NOT NULL,
    "scope" TEXT NOT NULL,
    "embedding" VARCHAR(255) NOT NULL,
    "label" NVARCHAR(255) CHECK
        ("label" IN(N'')) NOT NULL
);
ALTER TABLE
    "items" ADD CONSTRAINT "items_id_primary" PRIMARY KEY("id");
ALTER TABLE
    "triplets" ADD CONSTRAINT "triplets_right_id_foreign" FOREIGN KEY("right_id") REFERENCES "items"("id");
ALTER TABLE
    "triplets" ADD CONSTRAINT "triplets_left_id_foreign" FOREIGN KEY("left_id") REFERENCES "items"("id");
ALTER TABLE
    "validation_triplets" ADD CONSTRAINT "validation_triplets_left_id_foreign" FOREIGN KEY("left_id") REFERENCES "items"("id");
ALTER TABLE
    "validation_triplets" ADD CONSTRAINT "validation_triplets_right_id_foreign" FOREIGN KEY("right_id") REFERENCES "items"("id");
ALTER TABLE
    "triplets" ADD CONSTRAINT "triplets_reference_id_foreign" FOREIGN KEY("reference_id") REFERENCES "items"("id");
ALTER TABLE
    "validation_triplets" ADD CONSTRAINT "validation_triplets_reference_id_foreign" FOREIGN KEY("reference_id") REFERENCES "items"("id");