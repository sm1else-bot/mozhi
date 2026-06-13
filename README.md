# Mozhi Documentation Site

This directory contains the documentation source files for the **Mozhi** programming language.

## Quick Start

You can build and serve this documentation site locally using [MkDocs](https://www.mkdocs.org/).

### 1. Install Dependencies

Ensure you have Python installed, then install MkDocs and the Material theme:

```bash
pip install mkdocs mkdocs-material
```

### 2. Serve the Site Locally

Run the development server from this directory:

```bash
mkdocs serve
```

This will start a local server, usually at `http://127.0.0.1:8000/`. The site will automatically reload as you make changes to the Markdown files.

### 3. Build for Production

To compile the Markdown files into static HTML pages:

```bash
mkdocs build
```

The output will be generated inside the `site/` folder.
