"""
NLTK Data Setup Script

Downloads all required NLTK data for the Stock Market Sentiment Analyzer.
Run this once after installing the package.

Usage:
    python setup_nltk.py
"""

import nltk
import sys

def download_nltk_data():
    """Download all required NLTK data packages."""
    
    print("\n" + "="*80)
    print("DOWNLOADING NLTK DATA")
    print("="*80 + "\n")
    
    # List of required NLTK data packages
    packages = [
        'punkt',
        'punkt_tab',
        'stopwords',
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng',
        'maxent_ne_chunker',
        'maxent_ne_chunker_tab',
        'words',
        'wordnet',
        'omw-1.4'
    ]
    
    success = []
    failed = []
    
    for package in packages:
        try:
            print(f"Downloading '{package}'...", end=" ")
            nltk.download(package, quiet=True)
            print("✓")
            success.append(package)
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            failed.append(package)
    
    print("\n" + "="*80)
    print("DOWNLOAD SUMMARY")
    print("="*80)
    print(f"✓ Successfully downloaded: {len(success)}/{len(packages)} packages")
    
    if success:
        print("\nSuccessful packages:")
        for pkg in success:
            print(f"  • {pkg}")
    
    if failed:
        print(f"\n✗ Failed packages: {len(failed)}")
        for pkg in failed:
            print(f"  • {pkg}")
        print("\nNote: Some packages may not be critical for operation.")
    
    print("\n" + "="*80)
    print("✓ NLTK DATA SETUP COMPLETE")
    print("="*80 + "\n")
    
    return len(failed) == 0

if __name__ == "__main__":
    try:
        success = download_nltk_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Setup failed with error: {str(e)}")
        sys.exit(1)
