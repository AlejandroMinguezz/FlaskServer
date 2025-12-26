"""
Generate complete synthetic dataset for document classification
"""

import os
import json
import pandas as pd
from pathlib import Path
import argparse
from tqdm import tqdm

from .template_generator import generate_document, GENERATORS
from .augmentation import generate_variations


def load_categories(config_path='ai/config/categories.json'):
    """Load category definitions"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config['categories']


def generate_synthetic_documents(
    num_docs_per_category=100,
    num_variations=3,
    output_dir='ai/datasets/synthetic',
    save_txt=True
):
    """
    Generate synthetic documents for all categories

    Args:
        num_docs_per_category: Number of base documents per category
        num_variations: Number of augmented variations per document
        output_dir: Directory to save generated documents
        save_txt: Whether to save individual text files

    Returns:
        DataFrame with all generated documents and labels
    """
    categories = load_categories()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    all_documents = []

    print(f"Generating {num_docs_per_category} documents per category...")
    print(f"With {num_variations} variations each = {num_docs_per_category * (1 + num_variations)} per category")
    print(f"Total documents: {len(categories) * num_docs_per_category * (1 + num_variations)}\n")

    for category in categories:
        category_id = category['id']
        category_name = category['name']

        print(f"Generating documents for category: {category_name}")

        # Create category directory
        if save_txt:
            category_dir = output_path / category_id
            category_dir.mkdir(exist_ok=True)

        for doc_idx in tqdm(range(num_docs_per_category), desc=f"  {category_name}"):
            try:
                # Generate base document
                base_text = generate_document(category_id)

                # Save original
                all_documents.append({
                    'text': base_text,
                    'category': category_id,
                    'category_name': category_name,
                    'doc_id': f"{category_id}_{doc_idx}_orig",
                    'is_augmented': False
                })

                if save_txt:
                    txt_path = category_dir / f"{category_id}_{doc_idx}_orig.txt"
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(base_text)

                # Generate augmented variations
                variations = generate_variations(base_text, num_variations, intensity='light')

                for var_idx, var_text in enumerate(variations):
                    all_documents.append({
                        'text': var_text,
                        'category': category_id,
                        'category_name': category_name,
                        'doc_id': f"{category_id}_{doc_idx}_aug{var_idx}",
                        'is_augmented': True
                    })

                    if save_txt:
                        txt_path = category_dir / f"{category_id}_{doc_idx}_aug{var_idx}.txt"
                        with open(txt_path, 'w', encoding='utf-8') as f:
                            f.write(var_text)

            except Exception as e:
                print(f"\n  Error generating document {doc_idx} for {category_name}: {e}")
                continue

    # Create DataFrame
    df = pd.DataFrame(all_documents)

    print(f"\n[OK] Total documents generated: {len(df)}")
    print(f"\nDistribution by category:")
    print(df['category_name'].value_counts().sort_index())

    return df


def split_dataset(df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, random_state=42):
    """
    Split dataset into train, validation, and test sets

    Args:
        df: DataFrame with documents
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing
        random_state: Random seed

    Returns:
        train_df, val_df, test_df
    """
    from sklearn.model_selection import train_test_split

    # First split: train + val vs test
    train_val_df, test_df = train_test_split(
        df,
        test_size=test_ratio,
        random_state=random_state,
        stratify=df['category']
    )

    # Second split: train vs val
    relative_val_ratio = val_ratio / (train_ratio + val_ratio)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=relative_val_ratio,
        random_state=random_state,
        stratify=train_val_df['category']
    )

    print(f"\n[OK] Dataset split:")
    print(f"  Train: {len(train_df)} documents ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  Val:   {len(val_df)} documents ({len(val_df)/len(df)*100:.1f}%)")
    print(f"  Test:  {len(test_df)} documents ({len(test_df)/len(df)*100:.1f}%)")

    return train_df, val_df, test_df


def save_processed_datasets(train_df, val_df, test_df, output_dir='ai/datasets/processed'):
    """Save processed datasets as CSV files"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    train_path = output_path / 'train.csv'
    val_path = output_path / 'val.csv'
    test_path = output_path / 'test.csv'

    train_df.to_csv(train_path, index=False, encoding='utf-8')
    val_df.to_csv(val_path, index=False, encoding='utf-8')
    test_df.to_csv(test_path, index=False, encoding='utf-8')

    print(f"\n[OK] Datasets saved:")
    print(f"  Train: {train_path}")
    print(f"  Val:   {val_path}")
    print(f"  Test:  {test_path}")

    # Save metadata
    metadata = {
        'total_documents': len(train_df) + len(val_df) + len(test_df),
        'train_size': len(train_df),
        'val_size': len(val_df),
        'test_size': len(test_df),
        'categories': train_df['category'].unique().tolist(),
        'num_categories': train_df['category'].nunique(),
    }

    metadata_path = output_path / 'metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"  Metadata: {metadata_path}")


def main():
    """Main function to generate complete dataset"""
    parser = argparse.ArgumentParser(description='Generate synthetic document dataset')
    parser.add_argument('--num-docs', type=int, default=100,
                       help='Number of base documents per category (default: 100)')
    parser.add_argument('--num-variations', type=int, default=3,
                       help='Number of augmented variations per document (default: 3)')
    parser.add_argument('--no-txt', action='store_true',
                       help='Do not save individual text files')
    parser.add_argument('--train-ratio', type=float, default=0.7,
                       help='Training set ratio (default: 0.7)')
    parser.add_argument('--val-ratio', type=float, default=0.15,
                       help='Validation set ratio (default: 0.15)')
    parser.add_argument('--test-ratio', type=float, default=0.15,
                       help='Test set ratio (default: 0.15)')

    args = parser.parse_args()

    # Validate ratios
    total_ratio = args.train_ratio + args.val_ratio + args.test_ratio
    if abs(total_ratio - 1.0) > 0.01:
        print(f"Error: Ratios must sum to 1.0 (current sum: {total_ratio})")
        return

    print("=" * 70)
    print("SYNTHETIC DATASET GENERATION")
    print("=" * 70)

    # Generate documents
    df = generate_synthetic_documents(
        num_docs_per_category=args.num_docs,
        num_variations=args.num_variations,
        save_txt=not args.no_txt
    )

    # Split dataset
    train_df, val_df, test_df = split_dataset(
        df,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )

    # Save processed datasets
    save_processed_datasets(train_df, val_df, test_df)

    print("\n" + "=" * 70)
    print("[OK] DATASET GENERATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
