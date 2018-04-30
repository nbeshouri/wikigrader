# wikigrader

A tool to automatically rate Wikipedia articles.

## Getting Started

### Prerequisites

* Python 3.6 or higher
* `numpy`
* `pandas`
* `bs4`
* `sklearn`
* `keras`
* `click`
* `joblib`

### Installation

The tool can be run through `main.py`, so installation is optional.

```bash
cd <repo directory>
pip install .
```

### Usage

If you installed with `pip`:

```bash
wikigrader predict <article_name>
```

If you didn't:
```bash
python main.py predict <article_name>
```

Note that it currently takes about 30 seconds to score an article because of the time required to import dependencies and scrape the required data.
