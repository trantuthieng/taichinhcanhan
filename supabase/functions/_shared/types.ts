export interface PriceSnapshotRow {
  assetKey: string;
  assetType: "gold" | "stock";
  buyPrice: number;
  sellPrice?: number;
  source: string;
  fetchedAt: string;
}
