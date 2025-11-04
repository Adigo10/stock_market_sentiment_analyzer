# Keyphrase Analyzer — Short README

This repository contains a keyphrase analyzer for financial and business text. The analyzer extracts and classifies keyphrases into positive, neutral, and negative groups using a mix of NLP techniques.

File
- `src/keyphrase_analyzer.py` — The keyphrase analyzer implementation. It intelligently uses NLTK features (tokenization, POS tagging, NER, lemmatization) when available, but gracefully falls back to pattern-based extraction if NLTK is unavailable or if there are SciPy/NumPy compatibility issues.

Key features
- Extracts noun phrases, named entities, technical/domain terms, context phrases, and collocations (when supported).
- Classifies keyphrases into `positive`, `neutral`, and `negative` with confidence scores.
- Uses lemmatization when available to improve matching and reduce duplicates.
- Robust fallbacks: code runs without NLTK and avoids SciPy/NumPy compatibility issues by using pattern-based extraction.

Usage (PowerShell)

```powershell
# Run the keyphrase analyzer with example inputs
python .\src\keyphrase_analyzer_standalone.py
```

The script will display which NLP features are enabled/disabled, then run three example analyses.

Notes
- **NLTK is optional**: The analyzer works without any external dependencies using pattern-based extraction.
- **Enhanced with NLTK**: If NLTK is installed, the analyzer automatically uses advanced features like POS tagging, NER, lemmatization, and collocation detection for better accuracy.
- **SciPy compatibility**: On systems with SciPy/NumPy compatibility issues, POS tagging may be disabled but other NLTK features (tokenization, stopwords) still work.
- To enable full NLTK features, install NLTK and download required data:

```powershell
pip install nltk
python -m nltk.downloader punkt averaged_perceptron_tagger stopwords wordnet omw-1.4 maxent_ne_chunker words
```

- The analyzer is designed for news and financial text; sentiment lexicons and patterns can be extended in `src/keyphrase_analyzer_standalone.py`.

## Fixing NLTK/SciPy Compatibility Issues

If you see errors like `ValueError: numpy.dtype size changed` or `may indicate binary incompatibility`, this is due to version mismatches between NumPy and SciPy. Here are solutions:

### Solution 1: Reinstall with Compatible Versions (Recommended)
```powershell
# Uninstall incompatible versions
pip uninstall numpy scipy -y

# Install compatible versions
pip install numpy==1.26.4
pip install scipy==1.11.4
pip install nltk

# Download NLTK data
python -m nltk.downloader punkt averaged_perceptron_tagger stopwords wordnet omw-1.4 maxent_ne_chunker words
```

### Solution 2: Use Conda Environment (Best for avoiding conflicts)
```powershell
# Create new conda environment
conda create -n sentiment_analysis python=3.11 -y
conda activate sentiment_analysis

# Install packages via conda (handles compatibility automatically)
conda install numpy scipy nltk -c conda-forge -y

# Download NLTK data
python -m nltk.downloader punkt averaged_perceptron_tagger stopwords wordnet omw-1.4 maxent_ne_chunker words
```

### Solution 3: Upgrade Everything
```powershell
# Upgrade to latest compatible versions
pip install --upgrade numpy scipy nltk

# If still issues, try forcing reinstall
pip install --force-reinstall --no-cache-dir numpy scipy
```

### Solution 4: Use Without SciPy Features
The analyzer is designed to work without SciPy! If compatibility issues persist:
- The code will automatically disable POS tagging and collocation detection
- Basic NLTK features (tokenization, stopwords, lemmatization) still work
- Pattern-based extraction provides good results even without NLTK

Check the feature status when running:
```powershell
python .\src\keyphrase_analyzer_standalone.py
```

You'll see which features are enabled/disabled at the start of the output.

Programmatic Usage

```python
from src.keyphrase_analyzer_standalone import KeyphraseAnalyzer

analyzer = KeyphraseAnalyzer()

source = "Your news text here..."
sentiment = "<senti>Neutral<reason>Your reason here"

analysis = analyzer.analyze_source_with_sentiment(source, sentiment)
print(analyzer.format_analysis_output(analysis))
```

If you want, I can also:
- Add a short unit test that runs both files on a sample input and asserts expected categories.
- Add a small CLI wrapper to accept `--source` and `--sentiment` arguments for scripted usage.
