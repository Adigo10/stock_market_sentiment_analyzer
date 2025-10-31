# Similarity score and filtering component
- Takes summary of top 5 articles from input.json
- Uses cosine similarity (subject to change) to compare against remaining 20 articles
- Extracts top 10 articles + "x" articles with similarity score > threshold value (customizable through pipeline instantiation)
- Appends all to a final output.json, maintaining initial ID values for future metrics or something and also appends similarity score value


## Usage

Run the notebook.py cells in order

Otherwise simply
```
pip install -r requirements.txt
```

Import the pipeline class:
```python

from pipeline import SimilarityExpansionPipeline
```

Select your model configuration and threshold values:
```python
pipeline = SimilarityExpansionPipeline(
    model_name='all-MiniLM-L6-v2',
    similarity_threshold=0.5,
    top_k=10
)
```

Specify your input and output file paths:
```
INPUT_FILE = 'sample.json'
OUTPUT_FILE = 'output.json'
```

Run the pipeline:
```
final_articles = pipeline.run(INPUT_FILE, OUTPUT_FILE)
```

Visualize results (Optional):
```
pipeline.visualize_results(final_articles)
```