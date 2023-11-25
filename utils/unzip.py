"""This allows  to unzip even without unzip unix" """
import zipfile
import os
from search_engine import REPO_PATH

os.chdir(REPO_PATH)


def unzip_file(zip_path, extract_to=None):
    """
    Unzip a ZIP file.

    Args:
    zip_path (str): The path to the ZIP file.
    extract_to (str, optional): The directory to extract the files into. Defaults to the same directory as the ZIP file.
    """

    if extract_to is None:
        extract_to = os.path.dirname(zip_path)

    # Ensure the extraction directory exists
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # Open the zip file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


# Example usage
zip_file_path = "indexes.zip"  # Replace with your zip file path
output_directory = "indexes"  # Replace with your desired output directory
unzip_file(zip_file_path, output_directory)
