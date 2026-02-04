# Python Project - Utility Functions

**Language:** Python 3.13.3

## Project Description

As part of my training, I developed a Python program containing several utility functions for file manipulation, system process management, and network operations. This project allows me to discover and review Python language features.

## Implemented Features

### 1. Function `display_time()`
I created this function to display the current time in HH:MM:SS format.

### 2. Function `file_size(file_path)`
This function allows me to get the size of a file in bytes from its path.

### 3. Function `copy_directory(source, destination)`
I implemented this function to recursively copy all files and subdirectories from a source directory to a destination.

### 4. Function `create_files_csv(directory, csv_filename)`
I developed this function to create a CSV file listing all files in a directory with their metadata:
- File name
- Full path
- Creation date
- Last modification date
- Size in bytes

### 5. Function `list_processes()`
This function returns a dictionary of running processes with their PID as key and their name as value.

### 6. Function `ping_address(address, ping_count=10)`
I created this function to perform a ping on an address and return the average delay or an error message.

### 7. Function `compress_directory(directory, zip_file)`
I implemented this function to compress a directory and all its subdirectories into a ZIP file.

### 8. Function `weather(city)`
I created this function to return a JSON-formatted string containing the weather of a city passed as parameter. I use the free wttr.in API.

### 9. Function `split_file(file_path, num_parts)`
I developed this procedure to split a file of any type into multiple files. The different files bear the original filename with an underscore and a sequence number added.

### 10. Function `reconstruct_file(base_file_path, num_parts)`
I implemented this procedure to reconstruct the file from its split parts.

### 11. PyQt6 Graphical User Interface
I created a modern graphical interface that allows easy interactive use of all my functions (exercises 5 to 9). The interface is organized in tabs with a common results area.

## Installation and Usage

### Prerequisites
- Python 3.13.3 (or compatible version)
- `psutil` module for process management
- `requests` module for weather requests
- `PyQt6` module for the graphical interface

### Installation

1. Clone or download this project

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

### Execution

**Command line program:**
```bash
python3 fonctions_python.py
```

**Graphical interface:**
```bash
python3 interface_graphique.py
```

The command line script contains automatic tests that demonstrate the operation of all the functions I developed. The graphical interface allows interactive use of the functions.

### Using Functions Individually

```python
from fonctions_python import *

# Display the time
afficher_heure()

# Get a file size
size = taille_fichier("my_file.txt")

# Copy a directory
copier_repertoire("source/", "destination/")

# Create a CSV of files
creer_csv_fichiers("my_directory/", "list.csv")

# Get the process list
processes = liste_processus()

# Test a network connection
result = ping_adresse("8.8.8.8", 5)

# Compress a directory
compresser_repertoire("my_directory/", "archive.zip")

# Get weather for a city
weather_json = meteo("Paris")

# Split a file into 3 parts
decouper_fichier("large_file.zip", 3)

# Reconstruct the file
reconstituer_fichier("large_file.zip", 3)
```

## Project Structure

```
PythonE2IIA/
|-- fonctions_python.py    # Main program with all my functions
|-- module_utilitaires.py  # Module containing all functions
|-- interface_graphique.py # PyQt6 graphical interface
|-- requirements.txt       # Dependencies I use
|-- README.md             # This documentation
|-- GUI_README.md         # Graphical interface documentation
|-- venv/                 # Virtual environment I created
|-- liste_fichiers.csv    # Example of generated CSV file
+-- archive_test.zip      # Example of created ZIP archive
```

## Tests Performed

I tested all functions with:
- [x] Display of current time
- [x] Size calculation for existing and non-existing files
- [x] Recursive copy of directories with subfolders
- [x] CSV file generation with metadata
- [x] Retrieval of system process list
- [x] Network ping test to 8.8.8.8
- [x] Directory compression to ZIP
- [x] Weather data retrieval in JSON
- [x] File splitting into multiple parts
- [x] File reconstruction from parts
- [x] PyQt6 graphical interface with all exercises 5 to 9

## Error Handling

I implemented robust error handling in all my functions:
- Verification of file and directory existence
- Exception handling during file operations
- Explicit error messages to facilitate debugging
- Consistent return values (True/False for operations, -1 for errors)

## Technologies Used

- **Python 3**: Main language I use
- **psutil**: Library for system process management
- **requests**: Library for HTTP requests (weather)
- **PyQt6**: Framework for modern graphical interface
- **csv**: Built-in module for CSV file generation
- **zipfile**: Built-in module for ZIP compression
- **subprocess**: Built-in module for system command execution
- **datetime**: Built-in module for date and time management
- **json**: Built-in module for JSON data processing
- **os/shutil**: Built-in modules for file operations
