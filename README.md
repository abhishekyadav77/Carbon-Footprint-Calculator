# Carbon Footprint Calculator

Requires **Python 3.10, 3.11 or 3.12** (not 3.13+).

## Easiest way
- Windows: double-click `run_windows.bat`
- Mac/Linux: `./run_mac_linux.sh`

## Manual way
```
python -m venv venv
venv\Scripts\activate        (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```
Then open http://localhost:8501

## Design notes
- Theme colours live in `.streamlit/config.toml` and as CSS variables at the top of `style/style.css`.
- Fonts (Nunito, Archivo Black) load from Google Fonts; the page falls back to system fonts when offline.
- The layout uses the CSS `:has()` selector, so use a recent browser (Chrome 105+, Safari 15.4+, Firefox 121+).
