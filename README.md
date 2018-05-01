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

The tool can be installed using `setuptools` or `pip`, but you can also run it directly from the repo folder using `main.py` as long as you have all the prerequisites.

```bash
python setup.py install
```

Or:

```bash
cd <repo directory>
pip install .
```

### Usage

If you installed it:

```bash
wikigrader predict <article_name>
```

If you didn't:
```bash
python main.py predict <article_name>
```
## Known issues

1. It currently takes about 30 seconds to score an article because of the time required to import dependencies and scrape the required data.
2. You have to give it the canonical article name. Minor variations will result in an unhelpful error messages.
3. The command line interface doesn't yet have nice help messages and command descriptions.
4. You should only expect it to be accurate within about 0.7 of a point on a 5 point quality scale (where 0 is a Stub and 5 is a Featured Article).
