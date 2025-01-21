# JSON URL Extractor and Downloader

A Python tool to extract URLs from JSON files, organize them by object groups, and download them in parallel.

## Requirements

- Python 3.10+
- No additional packages required

## Installation

1. Clone or download the repository
2. Navigate to the `python_tools` directory
3. The tool is ready to use

## Usage

```bash
python url_extractor.py <input_json> [options]
```

### Options

| Option           | Description                    | Default     |
| ---------------- | ------------------------------ | ----------- |
| `-o`, `--output` | Output directory for downloads | `downloads` |
| `-j`, `--jobs`   | Number of parallel downloads   | `4`         |

### Example

```bash
# Basic usage
python url_extractor.py example.json

# Custom output directory and parallel jobs
python url_extractor.py example.json -o my_downloads -j 8
```

## Features

- Extracts URLs from JSON files
- Groups URLs by their object type
- Creates subdirectories for each group
- Downloads files in parallel
- Automatically adds `.obj` extension to mesh files without extensions

## Error Handling

- Failed downloads are logged to console
- HTTP errors (like 403 Forbidden) are reported
- The tool continues processing other URLs even if some fail

## Notes

- The tool creates a directory structure based on URL groups
- Mesh URLs (containing 'MeshURL') automatically get `.obj` extension if no extension exists
- Existing files are overwritten
