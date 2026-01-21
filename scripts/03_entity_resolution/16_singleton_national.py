#!/usr/bin/env python3
"""
National singleton matching using trained logistic regression model.

Processes one or more MSAs, using cached embeddings when available.
Generates crosswalk files mapping singleton POIs to PAW companies.
"""

import os
import sys
import re
import numpy as np
import pandas as pd
import pickle
import time
from pathlib import Path
from typing import List, Dict, Tuple
from rapidfuzz.distance import JaroWinkler

from openai import OpenAI

PROJECT_DIR = Path("/global/scratch/users/maxkagan/measuring_stakeholder_ideology")
POI_DIR = PROJECT_DIR / "outputs" / "entity_resolution" / "unbranded_pois_by_msa"
PAW_FILE = PROJECT_DIR / "outputs" / "entity_resolution" / "paw_company_by_msa.parquet"
MODEL_FILE = PROJECT_DIR / "outputs" / "singleton_matching" / "training_samples" / "columbus_oh_logit_model_v2.pkl"
CACHE_DIR = PROJECT_DIR / "outputs" / "singleton_matching" / "embedding_cache_v2"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "singleton_matching" / "crosswalks"

EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 3072
BATCH_SIZE = 2000
SIMILARITY_THRESHOLD = 0.50
PREDICTION_THRESHOLD = 0.4


def sanitize_name(name: str) -> str:
    """Clean name for embedding API."""
    if name is None or not isinstance(name, str):
        return ""
    name = name.strip()[:8000]
    name = ''.join(c if c.isprintable() or c in ' \t' else ' ' for c in name)
    return ' '.join(name.split())


def normalize_name(name: str) -> str:
    """Normalize name for Jaro-Winkler comparison."""
    name = name.lower().strip()

    suffixes = [
        r'\s+inc\.?$', r'\s+llc\.?$', r'\s+corp\.?$', r'\s+co\.?$',
        r'\s+ltd\.?$', r'\s+lp\.?$', r'\s+llp\.?$', r'\s+pllc\.?$',
        r'\s+pc\.?$', r'\s+pa\.?$', r'\s+company$', r'\s+incorporated$',
        r'\s+corporation$', r'\s+limited$'
    ]
    for suffix in suffixes:
        name = re.sub(suffix, '', name, flags=re.IGNORECASE)

    title_patterns = [
        (r'd\s*\.?\s*d\s*\.?\s*s\.?', 'dds'),
        (r'm\s*\.?\s*d\.?', 'md'),
        (r'd\s*\.?\s*o\.?', 'do'),
        (r'p\s*\.?\s*a\.?', 'pa'),
        (r'd\s*\.?\s*v\s*\.?\s*m\.?', 'dvm'),
        (r'd\s*\.?\s*c\.?', 'dc'),
    ]
    for pattern, replacement in title_patterns:
        name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)

    name = re.sub(r"['\"]", '', name)
    name = re.sub(r'\s+', ' ', name)

    return name.strip()


class EmbeddingCache:
    """Manages cached embeddings with incremental updates."""

    def __init__(self, msa: str):
        self.msa = msa
        self.names_file = CACHE_DIR / f"{msa}_names.npy"
        self.emb_file = CACHE_DIR / f"{msa}_embeddings.npy"
        self.cache: Dict[str, np.ndarray] = {}
        self._load_cache()

    def _load_cache(self):
        """Load existing cache from numpy files."""
        if self.names_file.exists() and self.emb_file.exists():
            names = np.load(self.names_file, allow_pickle=True)
            embeddings = np.load(self.emb_file)
            for name, emb in zip(names, embeddings):
                self.cache[name] = emb
            print(f"    Loaded {len(self.cache):,} cached embeddings")

    def save_cache(self):
        """Save cache to numpy files."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        names = np.array(list(self.cache.keys()), dtype=object)
        embeddings = np.array([self.cache[n] for n in names], dtype=np.float16)
        np.save(self.names_file, names)
        np.save(self.emb_file, embeddings)
        print(f"    Saved {len(self.cache):,} embeddings to cache")

    def get_embeddings(self, names: List[str], client: OpenAI) -> np.ndarray:
        """Get embeddings, using cache when available."""
        names_to_embed = [n for n in names if n not in self.cache]
        cached_count = len(names) - len(names_to_embed)

        if cached_count > 0:
            print(f"    Cache hit: {cached_count:,}, need to embed: {len(names_to_embed):,}")

        if names_to_embed:
            new_embeddings = self._embed_batch(names_to_embed, client)
            for name, emb in zip(names_to_embed, new_embeddings):
                self.cache[name] = emb.astype(np.float16)
            self.save_cache()

        return np.array([self.cache[n] for n in names], dtype=np.float32)

    def _embed_batch(self, names: List[str], client: OpenAI) -> np.ndarray:
        """Embed names in batches with retry logic."""
        all_embeddings = []
        total_batches = (len(names) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(names), BATCH_SIZE):
            batch = names[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1

            if batch_num % 10 == 0 or batch_num == total_batches:
                print(f"      Embedding batch {batch_num}/{total_batches}...")

            for attempt in range(3):
                try:
                    response = client.embeddings.create(input=batch, model=EMBEDDING_MODEL)
                    embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(embeddings)
                    time.sleep(0.1)
                    break
                except Exception as e:
                    print(f"      Attempt {attempt+1} failed: {e}")
                    time.sleep(5 * (attempt + 1))
            else:
                raise RuntimeError(f"Failed to embed batch {batch_num}")

        return np.array(all_embeddings)


def compute_features(poi_names: List[str], company_names: List[str],
                     poi_emb: np.ndarray, company_emb: np.ndarray) -> pd.DataFrame:
    """Compute candidate pairs and features using vectorized operations."""

    # Normalize embeddings for cosine similarity
    poi_norm = poi_emb / np.linalg.norm(poi_emb, axis=1, keepdims=True)
    company_norm = company_emb / np.linalg.norm(company_emb, axis=1, keepdims=True)

    # Compute similarity matrix
    print(f"    Computing similarity matrix ({len(poi_names):,} x {len(company_names):,})...")
    similarity_matrix = poi_norm @ company_norm.T

    # Find candidates above threshold
    poi_idx, company_idx = np.where(similarity_matrix >= SIMILARITY_THRESHOLD)
    similarities = similarity_matrix[poi_idx, company_idx]

    print(f"    Found {len(poi_idx):,} candidate pairs above {SIMILARITY_THRESHOLD} threshold")

    if len(poi_idx) == 0:
        return pd.DataFrame()

    # Build candidate dataframe
    candidates = pd.DataFrame({
        'poi_name': [poi_names[i] for i in poi_idx],
        'company_name': [company_names[i] for i in company_idx],
        'cos_sim': similarities
    })

    # Compute string similarity features
    print(f"    Computing string similarity features...")

    candidates['jaro_winkler'] = candidates.apply(
        lambda r: JaroWinkler.similarity(r['poi_name'], r['company_name']),
        axis=1
    )

    poi_norm_names = [normalize_name(n) for n in candidates['poi_name']]
    company_norm_names = [normalize_name(n) for n in candidates['company_name']]
    candidates['jaro_winkler_norm'] = [
        JaroWinkler.similarity(p, c)
        for p, c in zip(poi_norm_names, company_norm_names)
    ]

    def token_jaccard(a: str, b: str) -> float:
        tokens_a = set(a.lower().split())
        tokens_b = set(b.lower().split())
        if not tokens_a or not tokens_b:
            return 0.0
        return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)

    candidates['token_jaccard'] = candidates.apply(
        lambda r: token_jaccard(r['poi_name'], r['company_name']),
        axis=1
    )

    candidates['contains_match'] = candidates.apply(
        lambda r: float(
            r['poi_name'].lower() in r['company_name'].lower() or
            r['company_name'].lower() in r['poi_name'].lower()
        ),
        axis=1
    )

    return candidates


def process_msa(msa: str, paw_df: pd.DataFrame, model, client: OpenAI) -> Tuple[int, int]:
    """Process a single MSA and generate crosswalk."""

    print(f"\n{'='*60}")
    print(f"Processing: {msa}")
    print(f"{'='*60}")

    poi_file = POI_DIR / f"{msa}.parquet"
    if not poi_file.exists():
        print(f"  WARNING: POI file not found, skipping")
        return 0, 0

    # Load POI names
    pois = pd.read_parquet(poi_file)
    poi_names_raw = pois['location_name'].unique().tolist()
    poi_names = [sanitize_name(n) for n in poi_names_raw if sanitize_name(n)]
    print(f"  POI names: {len(poi_names):,}")

    # Load company names for this MSA
    paw_msa = paw_df[paw_df['msa'] == msa]
    if len(paw_msa) == 0:
        print(f"  WARNING: No PAW companies for this MSA, skipping")
        return 0, 0

    company_names_raw = paw_msa['company_name'].unique().tolist()
    company_names = [sanitize_name(n) for n in company_names_raw if sanitize_name(n)]
    print(f"  Company names: {len(company_names):,}")

    # Get embeddings
    print(f"  Getting embeddings...")
    cache = EmbeddingCache(msa)

    all_names = list(set(poi_names + company_names))
    all_embeddings = cache.get_embeddings(all_names, client)

    name_to_idx = {n: i for i, n in enumerate(all_names)}
    poi_emb = all_embeddings[[name_to_idx[n] for n in poi_names]]
    company_emb = all_embeddings[[name_to_idx[n] for n in company_names]]

    # Compute features
    candidates = compute_features(poi_names, company_names, poi_emb, company_emb)

    if len(candidates) == 0:
        print(f"  No candidate pairs found")
        return len(poi_names), 0

    # Apply model
    print(f"  Applying trained model...")
    feature_cols = ['cos_sim', 'jaro_winkler', 'jaro_winkler_norm',
                    'token_jaccard', 'contains_match']
    X = candidates[feature_cols].values

    candidates['match_prob'] = model.predict_proba(X)[:, 1]
    candidates['predicted_match'] = (candidates['match_prob'] >= PREDICTION_THRESHOLD).astype(int)

    # Filter to matches
    matches = candidates[candidates['predicted_match'] == 1].copy()
    print(f"  Predicted matches: {len(matches):,} ({100*len(matches)/len(candidates):.1f}% of candidates)")

    # For each POI, keep best match
    matches_best = matches.loc[matches.groupby('poi_name')['match_prob'].idxmax()]

    # Save crosswalk
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"{msa}_singleton_crosswalk.parquet"

    crosswalk = matches_best[['poi_name', 'company_name', 'match_prob',
                              'cos_sim', 'jaro_winkler_norm']].copy()
    crosswalk['msa'] = msa
    crosswalk.to_parquet(output_file, index=False)

    n_matched = len(crosswalk)
    print(f"  Saved crosswalk: {n_matched:,} POI names matched ({100*n_matched/len(poi_names):.1f}%)")

    return len(poi_names), n_matched


def main(msas: List[str]):
    """Process multiple MSAs."""

    print("=" * 70)
    print("National Singleton Matching")
    print("=" * 70)
    print(f"MSAs to process: {len(msas)}")

    # Load model
    print(f"\nLoading trained model from {MODEL_FILE.name}...")
    with open(MODEL_FILE, 'rb') as f:
        model_dict = pickle.load(f)
        model = model_dict['model']
    print(f"  Features: {model_dict.get('features', 'N/A')}")

    # Load PAW data
    print(f"Loading PAW company data...")
    paw_df = pd.read_parquet(PAW_FILE)
    print(f"  Total companies: {len(paw_df):,}")

    # Initialize OpenAI client
    client = OpenAI()

    # Process each MSA
    results = []
    for msa in msas:
        try:
            n_pois, n_matched = process_msa(msa, paw_df, model, client)
            results.append({
                'msa': msa,
                'n_pois': n_pois,
                'n_matched': n_matched,
                'match_rate': n_matched / n_pois if n_pois > 0 else 0,
                'status': 'success'
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                'msa': msa,
                'n_pois': 0,
                'n_matched': 0,
                'match_rate': 0,
                'status': f'error: {str(e)[:100]}'
            })

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    results_df = pd.DataFrame(results)
    successful = results_df[results_df['status'] == 'success']

    print(f"MSAs processed: {len(msas)}")
    print(f"Successful: {len(successful)}")
    print(f"Total POI names: {successful['n_pois'].sum():,}")
    print(f"Total matched: {successful['n_matched'].sum():,}")
    if len(successful) > 0:
        overall_rate = successful['n_matched'].sum() / successful['n_pois'].sum()
        print(f"Overall match rate: {100*overall_rate:.1f}%")

    # Save results summary
    summary_file = OUTPUT_DIR / "processing_summary.parquet"
    if summary_file.exists():
        existing = pd.read_parquet(summary_file)
        results_df = pd.concat([existing, results_df]).drop_duplicates(subset=['msa'], keep='last')
    results_df.to_parquet(summary_file, index=False)
    print(f"\nSummary saved to {summary_file}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python 16_singleton_national.py <msa1> [msa2] ...")
        print("   or: python 16_singleton_national.py --file <msa_list.txt>")
        sys.exit(1)

    if sys.argv[1] == '--file':
        with open(sys.argv[2], 'r') as f:
            msas = [line.strip() for line in f if line.strip()]
    else:
        msas = sys.argv[1:]

    main(msas)
