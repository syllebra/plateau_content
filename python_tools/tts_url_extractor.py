import json
import re
import os
import argparse
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, List


def extract_urls(data: Dict) -> Dict[str, List[str]]:
    """Extract URLs from JSON data and group them by object type"""
    url_pattern = re.compile(r"https?://[^\s]+")
    url_groups = {}

    def recursive_extract(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and url_pattern.match(value):
                    group = key if key not in url_groups else key
                    url_groups.setdefault(group, []).append(value)
                recursive_extract(value)
        elif isinstance(obj, list):
            for item in obj:
                recursive_extract(item)

    recursive_extract(data)
    return url_groups


def download_file(url: str, output_dir: Path):
    """Download a single file to the output directory"""
    try:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path) or "index.html"

        # Add .obj extension for mesh files if no extension exists
        if not os.path.splitext(filename)[1] and ("MeshURL" in str(output_dir) or "ColliderURL" in str(output_dir)):
            filename += ".obj"

        output_path = output_dir / filename

        # Basic download implementation
        import urllib.request

        urllib.request.urlretrieve(url, output_path)
        print(f"Downloaded: {url}")
    except Exception as e:
        print(f"Failed to download {url}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="JSON URL Extractor and Downloader")
    parser.add_argument("input", help="Path to input JSON file")
    parser.add_argument("-o", "--output", default="downloads", help="Output directory for downloads")
    parser.add_argument("-j", "--jobs", type=int, default=4, help="Number of parallel downloads")

    args = parser.parse_args()

    # Read and parse JSON
    with open(args.input) as f:
        data = json.load(f)

    # Extract URLs
    url_groups = extract_urls(data)

    # Create output directory structure
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    # Download files in parallel
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        for group, urls in url_groups.items():
            group_dir = output_dir / group
            group_dir.mkdir(exist_ok=True)

            for url in urls:
                executor.submit(download_file, url, group_dir)


if __name__ == "__main__":
    main()
