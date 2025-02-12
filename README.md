# streamlit-slickgrid

A wrapper that allows you to use [SlickGrid](https://github.com/ghiscoding/slickgrid-universal) in Streamlit.

View demo:

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://slickgrid.streamlit.app/)

IMPORTANT: This is not an officially-maintained package by Streamlit. We built this to "scratch our own itch" with some internal Finance folks who needed it for their apps. Consider this a community project, for all intents and purposes. That said, we think it's awesome :)

## Installation instructions

```sh
pip install streamlit-slickgrid
```

## Usage instructions

See [streamlit_slickgrid/examples/streamlit_app.py](https://github.com/streamlit/streamlit-slickgrid/blob/main/streamlit_slickgrid/example/streamlit_app.py).

## Contributing

### Development setup

In one terminal:

```sh
cd [this folder]
python -m venv .venv # One-time only.
source .venv/bin/activate
pip install -e .[dev]
streamlit run streamlit_slickgrid/examples/streamlit_app.py
```

In another terminal:

```sh
cd [this folder]
cd streamlit_slickgrid/frontend
npm install
npm run start
```

### Building wheel file

```sh
cd [this folder]

# Build front end
cd streamlit_slickgrid/frontend
npm run build

# Build Python library
cd ../..
rm dist/*
python -m build --wheel # or: uv build
# The wheel file is in dist/ now.
```
