# Daily Article Selector

A Streamlit application that selects a random article daily from The Hindu or The Telegraph based on specified topic probabilities:

- Business and economics (20%)
- Science, environment, and technology (50%)
- Art and literary criticism (20%)
- Philosophy and sociology (10%)

## Features

- Web scraping from multiple news sources
- Daily article selection (same article throughout the day)
- Topic-based probability distribution
- Clean and intuitive UI

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```
   streamlit run app/main.py
   ```

## Project Structure

```
VARC_APP/
├── app/
│   ├── components/   # UI components
│   ├── scrapers/     # Web scraping modules for each source
│   ├── utils/        # Utility functions
│   └── main.py       # Main Streamlit application
├── data/             # Cached articles and app data
├── requirements.txt  # Dependencies
└── README.md         # Project documentation
``` 