/*
  Warnings:

  - You are about to drop the column `position` on the `Chunk` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[documentId,index]` on the table `Chunk` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `index` to the `Chunk` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Chunk" DROP COLUMN "position",
ADD COLUMN     "index" INTEGER NOT NULL,
ADD COLUMN     "tokenCount" INTEGER NOT NULL DEFAULT 0;

-- AlterTable
ALTER TABLE "Document" ADD COLUMN     "content" TEXT,
ADD COLUMN     "error" TEXT;

-- CreateIndex
CREATE UNIQUE INDEX "Chunk_documentId_index_key" ON "Chunk"("documentId", "index");
