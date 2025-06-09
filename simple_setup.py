import os
import shutil

def organize_documents(source_folder, destination_folder):
    """
    Organizes documents from the source folder into subfolders in the destination folder based on file extensions.

    Args:
        source_folder (str): Path to the folder containing the documents to organize.
        destination_folder (str): Path to the folder where organized documents will be stored.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(filename)[1].lower()
            extension_folder = os.path.join(destination_folder, file_extension[1:] if file_extension else "unknown")

            if not os.path.exists(extension_folder):
                os.makedirs(extension_folder)

            shutil.move(file_path, os.path.join(extension_folder, filename))

if __name__ == "__main__":
    source = input("Enter the path to the source folder: ")
    destination = input("Enter the path to the destination folder: ")
    organize_documents(source, destination)
    print("Documents organized successfully!")