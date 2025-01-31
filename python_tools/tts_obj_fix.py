import argparse
import hashlib
import json
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List


def create_uuid_from_string(val: str):
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)


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


def get_path_from_url(url: str, output_dir: Path):
    if "pastebin.com" in url and "raw" not in url:
        url = url.replace("pastebin.com", "pastebin.com/raw")

    # filename = os.path.basename(parsed_url.path) or "index.html"
    filename = str(create_uuid_from_string(url)) + ".obj"

    if not os.path.splitext(filename)[1]:
        filename += ".obj"

    return os.path.join(output_dir, filename)


def download_file(url: str, output_dir: Path):
    """Download a single file to the output directory"""
    try:
        # Add .obj extension for mesh files if no extension exists
        if not ("MeshURL" in str(output_dir) or "ColliderURL" in str(output_dir)):
            return

        output_path = get_path_from_url(url, output_dir)

        if os.path.exists(output_path):
            return

        # Basic download implementation
        import urllib.request

        urllib.request.urlretrieve(url, output_path)
        print(f"Downloaded: {url}")
    except Exception as e:
        print(f"Failed to download {url}: {str(e)}")


def check_backslash_in_obj(path):

    with open(path, "rt", encoding="utf-8") as f:
        data = f.read()

    if "\\" not in data:
        return False

    print(path, " has backslashes")
    os.makedirs("fixed", exist_ok=True)
    fixed_path = os.path.join("fixed", os.path.basename(path))
    data = data.replace("\\\n", " ")
    with open(fixed_path, "wt", encoding="utf-8") as f:
        f.write(data)

    return True


def check_urls_obj(url_groups, output_dir):
    lst = {}
    for group, urls in url_groups.items():
        group_dir = output_dir / group
        group_dir.mkdir(exist_ok=True)

        for url in urls:
            path = get_path_from_url(url, group_dir)
            if not ("MeshURL" in str(path) or "ColliderURL" in str(path)):
                continue
            if url not in lst:
                lst[url] = path

    toreplace = {}

    for url, path in lst.items():
        if check_backslash_in_obj(path):
            fixed_url = (
                "https://raw.githubusercontent.com/syllebra/plateau_content/refs/heads/main/fixed/"
                + os.path.basename(path)
            )
            toreplace[url] = fixed_url
            print("Need to replace ", url, " by ", fixed_url)

    return toreplace


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

    toreplace = check_urls_obj(url_groups, output_dir)
    if len(toreplace) > 0:
        with open(args.input, "rt", encoding="utf-8") as f:
            fd = f.read()

        for url, fixed_url in toreplace.items():
            print("Replacing ", url, " by ", fixed_url)
            fd = fd.replace(url, fixed_url)

        with open(args.input, "wt", encoding="utf-8") as f:
            f.write(fd)


if __name__ == "__main__":
    main()
