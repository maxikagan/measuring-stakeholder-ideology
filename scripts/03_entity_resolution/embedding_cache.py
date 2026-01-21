#!/usr/bin/env python3
"""
Efficient embedding cache manager.

Stores name → embedding mappings in efficient binary format.
Supports incremental updates and cross-methodology reuse.

Cache structure:
  - {msa}_embeddings.parquet: [name, embedding] where embedding is numpy array
  - Uses float16 to halve storage (minimal quality loss for similarity)
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import time

from openai import OpenAI

CACHE_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/singleton_matching/embedding_cache_v2")
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 3072
BATCH_SIZE = 2000


class EmbeddingCache:
    """Manages cached embeddings for POI/company names."""

    def __init__(self, msa: str):
        self.msa = msa
        self.cache_file = CACHE_DIR / f"{msa}_embeddings.parquet"
        self.cache: Dict[str, np.ndarray] = {}
        self._load_cache()

    def _load_cache(self):
        """Load existing cache from disk."""
        if self.cache_file.exists():
            df = pd.read_parquet(self.cache_file)
            for _, row in df.iterrows():
                self.cache[row['name']] = np.array(row['embedding'], dtype=np.float16)
            print(f"  Loaded {len(self.cache):,} cached embeddings from {self.cache_file.name}")

    def save_cache(self):
        """Save cache to disk in efficient format."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        records = [
            {'name': name, 'embedding': emb.tolist()}
            for name, emb in self.cache.items()
        ]
        df = pd.DataFrame(records)
        df.to_parquet(self.cache_file, index=False)

        # Also save as numpy for even faster loading
        names = list(self.cache.keys())
        embeddings = np.array([self.cache[n] for n in names], dtype=np.float16)

        np.save(CACHE_DIR / f"{self.msa}_names.npy", np.array(names, dtype=object))
        np.save(CACHE_DIR / f"{self.msa}_embeddings.npy", embeddings)

        print(f"  Saved {len(self.cache):,} embeddings to cache")

    def get_embeddings(self, names: List[str], client: OpenAI) -> np.ndarray:
        """
        Get embeddings for names, using cache when available.
        Only calls API for names not in cache.
        """
        # Identify which names need embedding
        names_to_embed = [n for n in names if n not in self.cache]
        cached_count = len(names) - len(names_to_embed)

        if cached_count > 0:
            print(f"    Found {cached_count:,} in cache, need to embed {len(names_to_embed):,}")

        # Embed missing names
        if names_to_embed:
            new_embeddings = self._embed_names(names_to_embed, client)
            for name, emb in zip(names_to_embed, new_embeddings):
                self.cache[name] = emb.astype(np.float16)

            # Save incrementally
            self.save_cache()

        # Return embeddings in original order
        return np.array([self.cache[n] for n in names], dtype=np.float32)

    def _embed_names(self, names: List[str], client: OpenAI) -> np.ndarray:
        """Call OpenAI API to embed names with progress saving."""
        all_embeddings = []
        total_batches = (len(names) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(names), BATCH_SIZE):
            batch = names[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1

            if batch_num % 5 == 0 or batch_num == total_batches:
                print(f"      Batch {batch_num}/{total_batches}...")

            success = False
            for attempt in range(3):
                try:
                    response = client.embeddings.create(input=batch, model=EMBEDDING_MODEL)
                    embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(embeddings)
                    success = True
                    time.sleep(0.1)
                    break
                except Exception as e:
                    print(f"      Attempt {attempt+1} failed: {e}")
                    time.sleep(5 * (attempt + 1))

            if not success:
                raise RuntimeError(f"Failed to embed batch {batch_num} after 3 attempts")

            # Save progress every 10 batches
            if batch_num % 10 == 0:
                for name, emb in zip(names[i:i+len(batch)], embeddings):
                    self.cache[name] = np.array(emb, dtype=np.float16)
                self.save_cache()

        return np.array(all_embeddings)


def convert_old_cache_to_new(msa: str):
    """Convert old JSON cache to new efficient format.

    Processes POI and company caches separately to avoid OOM.
    """
    import json
    import gc

    old_cache_dir = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/singleton_matching/embedding_cache")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    poi_cache = old_cache_dir / f"{msa}_poi_embeddings.json"
    company_cache = old_cache_dir / f"{msa}_company_embeddings.json"

    poi_file = Path(f"/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/entity_resolution/unbranded_pois_by_msa/{msa}.parquet")
    paw_file = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology/outputs/entity_resolution/paw_company_by_msa.parquet")

    def sanitize(name):
        if name is None or not isinstance(name, str):
            return ""
        name = name.strip()[:8000]
        name = ''.join(c if c.isprintable() or c in ' \t' else ' ' for c in name)
        return ' '.join(name.split())

    all_names = []
    all_embeddings = []

    # Process POI embeddings first
    if poi_cache.exists() and poi_file.exists():
        print(f"Converting POI embeddings for {msa}...")
        pois = pd.read_parquet(poi_file)
        poi_names = pois['location_name'].unique().tolist()
        del pois
        gc.collect()

        poi_names_clean = [sanitize(n) for n in poi_names if sanitize(n)]
        del poi_names
        gc.collect()

        print(f"  Loading POI JSON ({poi_cache.stat().st_size / 1e9:.1f} GB)...")
        with open(poi_cache, 'r') as f:
            poi_embeddings = json.load(f)

        if len(poi_embeddings) == len(poi_names_clean):
            for name, emb in zip(poi_names_clean, poi_embeddings):
                all_names.append(name)
                all_embeddings.append(np.array(emb, dtype=np.float16))
            print(f"  Added {len(poi_names_clean):,} POI embeddings")

        del poi_embeddings, poi_names_clean
        gc.collect()
        print(f"  Memory cleared after POI processing")

    # Process company embeddings
    if company_cache.exists():
        print(f"Converting company embeddings for {msa}...")
        paw = pd.read_parquet(paw_file)
        paw_msa = paw[paw['msa'] == msa]
        company_names = paw_msa['company_name'].unique().tolist()
        del paw, paw_msa
        gc.collect()

        company_names_clean = [sanitize(n) for n in company_names if sanitize(n)]
        del company_names
        gc.collect()

        print(f"  Loading company JSON ({company_cache.stat().st_size / 1e9:.1f} GB)...")
        with open(company_cache, 'r') as f:
            company_embeddings = json.load(f)

        if len(company_embeddings) == len(company_names_clean):
            for name, emb in zip(company_names_clean, company_embeddings):
                all_names.append(name)
                all_embeddings.append(np.array(emb, dtype=np.float16))
            print(f"  Added {len(company_names_clean):,} company embeddings")

        del company_embeddings, company_names_clean
        gc.collect()
        print(f"  Memory cleared after company processing")

    # Save combined cache
    print(f"Saving {len(all_names):,} total embeddings...")

    embeddings_array = np.array(all_embeddings, dtype=np.float16)
    del all_embeddings
    gc.collect()

    np.save(CACHE_DIR / f"{msa}_names.npy", np.array(all_names, dtype=object))
    np.save(CACHE_DIR / f"{msa}_embeddings.npy", embeddings_array)

    print(f"Saved to {CACHE_DIR}")
    print(f"  Names: {CACHE_DIR / f'{msa}_names.npy'}")
    print(f"  Embeddings: {CACHE_DIR / f'{msa}_embeddings.npy'}")

    emb_size_mb = embeddings_array.nbytes / 1e6
    print(f"  Embedding array size: {emb_size_mb:.1f} MB")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'convert':
        msa = sys.argv[2] if len(sys.argv) > 2 else 'columbus_oh'
        convert_old_cache_to_new(msa)
