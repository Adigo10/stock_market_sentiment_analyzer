## Project Layout

```
stock_market_sentiment_analyzer/
├── frontend.py                # Streamlit UI entry point
├── server.py                  # FastAPI backend for orchestration
├── model_pipeline.py          # End-to-end orchestration script
├── setup_nltk.py              # Helper to download required NLTK corpora
├── src/
│   ├── fetch_data.py          # News collection logic
│   ├── rule_based_ranker.py   # Ranking heuristics for fetched articles
│   ├── sentiment_predictor.py # Interfaces with the Flan-T5 model
│   └── ...                    # Additional utilities and analyzers
├── pipeline/                  # Batch pipeline utilities
├── model/                     # Expected location for model weights (see below)
└── data/                      # Sample datasets for experimentation
```

## Model Setup (Flan-T5 Base)

The finetuned Flan-T5 model lives on Hugging Face. To mirror the code expectations:

1. Create the `model` directory at the repository root if it does not exist.
2. Inside `model`, clone the Hugging Face repository:

	```powershell
	cd model
	git clone https://huggingface.co/tssrihari/Flan_T5_Base
	```

	Git LFS is required because the weights are stored as `.safetensors` files. Install it from <https://git-lfs.com> if you have not already and run `git lfs install` before cloning.

3. After cloning, the on-disk layout should include `model/Flan_T5_Base/` with the tokenizer, config, and safetensor weight files referenced by `src/sentiment_predictor.py`.

## NLTK Resources

The backend requires several NLTK tokenizers and corpora. The repository provides a helper script to automate the downloads:

```powershell
python setup_nltk.py
```

Run this once before starting the API or Streamlit app to ensure the required resources are cached locally. The script is idempotent and can be re-run safely if you are unsure whether the downloads completed.

## Environment Notes

- Install Python dependencies with `pip install -r requirements.txt` at the repository root.
- Start the backend with `python .\server.py` and launch the Streamlit frontend using `streamlit run .\frontend.py`.
- Both services expect the model weights and NLTK assets to be present as described above.


