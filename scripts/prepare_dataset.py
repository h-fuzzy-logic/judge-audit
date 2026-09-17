import os

import pandas as pd
from datasets import load_dataset


def map_ragtruth_to_score(processed_labels: dict) -> int:
    """
    Maps RAGTruth's processed hallucination label counts to a 3-point groundedness scale:
      2 = Fully Grounded (No hallucination spans of any kind)
      1 = Partially Grounded (Only baseless/unsupported info present)
      0 = Fully Ungrounded / Evident Conflict (Hard contradiction present)
    """
    if not processed_labels:
        return 2  # Clean, fully grounded

    if processed_labels.get("evident_conflict", 0) > 0:
        return 0  # Severe contradiction

    if processed_labels.get("baseless_info", 0) > 0:
        return 1  # Partially grounded / baseless additions

    return 2


def prepare_ragtruth_dataset(output_path: str = "data/processed/source_groundedness_150.csv", seed: int = 42):
    print("Loading RAGTruth dataset from Hugging Face (wandb/RAGTruth-processed)...")

    # Load dataset split from Hugging Face
    dataset = load_dataset("wandb/RAGTruth-processed", split="train")
    df = dataset.to_pandas()

    print(f"Total raw samples loaded: {len(df)}")

    # Extract required fields (standardize schema)
    # RAGTruth-processed fields: 'context', 'output', 'hallucination_labels_processed'
    context_col = "context" if "context" in df.columns else "source_info"
    response_col = "output" if "output" in df.columns else (
        "response" if "response" in df.columns else "generation"
    )

    # Clean text columns
    df["context"] = df[context_col].astype(str).str.strip()
    df["response"] = df[response_col].astype(str).str.strip()

    # Filter out non-"good" quality rows (refusals, truncated generations).
    # These aren't real groundedness judgments: e.g. a refusal has no hallucination
    # spans to detect, so it would otherwise default to score 2 (Fully Grounded)
    # without ever having been evaluated for groundedness at all.
    if "quality" in df.columns:
        before = len(df)
        df = df[df["quality"] == "good"]
        print(f"Dropped {before - len(df)} non-'good' quality rows (refusals/truncated).")

    # Map human labels to 3-point score scale
    if "hallucination_labels_processed" in df.columns:
        df["human_groundedness_score"] = df["hallucination_labels_processed"].apply(map_ragtruth_to_score)
    else:
        # Fallback mapping if categorical flag exists
        df["human_groundedness_score"] = df["type"].apply(
            lambda x: 2 if x == "Grounded" else (0 if "Conflict" in str(x) else 1)
        )

    # Filter out empty or extremely short inputs
    df = df[(df["context"].str.len() > 50) & (df["response"].str.len() > 20)]

    print("\n--- Raw Score Distribution ---")
    print(df["human_groundedness_score"].value_counts())

    # Perform stratified sampling: 50 items per score class (0, 1, 2)
    sample_size_per_class = 50
    sampled_dfs = []

    for score_class in [0, 1, 2]:
        sub_df = df[df["human_groundedness_score"] == score_class]

        if len(sub_df) < sample_size_per_class:
            print(f"Warning: Class {score_class} has only {len(sub_df)} samples. Sampling all available.")
            sampled_dfs.append(sub_df)
        else:
            sampled_dfs.append(sub_df.sample(n=sample_size_per_class, random_state=seed))

    final_df = pd.concat(sampled_dfs, ignore_index=True)

    # Shuffle dataset
    final_df = final_df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    # Keep only necessary fields for Promptfoo
    output_df = final_df[["context", "response", "human_groundedness_score"]]

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_df.to_csv(output_path, index=False)

    print("\n" + "=" * 60)
    print(f"Successfully exported 150 balanced samples to: {output_path}")
    print("=" * 60)
    print("Final Sample Count per Groundedness Score:")
    print(output_df["human_groundedness_score"].value_counts().to_string())


if __name__ == "__main__":
    # Dependencies: pip install datasets pandas
    prepare_ragtruth_dataset()
