# PDF Reader and Table Extractor

This project is a Python-based PDF reader and table extractor that downloads a PDF from a given URL, extracts tables along with the preceding titles using `pdfplumber`, and saves the extracted tables as CSV files. The configuration is externalized using a `config.yml` file to keep the code clean and flexible.

## Features
* Downloads a PDF from a URL.
* Extracts tables from PDF pages.
* Matches each table with its corresponding title (precedes the table in the PDF).
* Saves extracted tables as CSV files, named after their corresponding title.
* Logs important events, errors, and progress.
* All configuration settings (PDF URL, table extraction settings, regex pattern for titles) are stored in a YAML file (config.yml).

## Project Structure

```           
├── pdf_reader/                    # Main package folder
│   ├── __init__.py                # Package initialization file
│   ├── main.py                    # Main script with the core logic
│   └── config.yml                 # Default configuration file (PDF URL, table settings, etc.)
├── results/                       # Directory where extracted CSV files will be saved
├── README.md                      # Project documentation
├── pyproject.toml                 # Poetry configuration file
├── dist/                          # Distribution folder for .whl and .tar.gz files
```

### Components

* `pdf_reader/main.py`: The main script that handles the PDF extraction process.
  * `PDFReader`: Core class that handles loading the config file, extracting tables, and saving them as CSV.
  * `main()`: Entry point for the package, which runs the PDF extraction process.
* `pdf_reader/config.yml`: YAML configuration file that contains:
  * The URL of the PDF file.
  * Settings for extracting tables (table detection strategies, tolerance settings).
  * Regex pattern to identify titles above tables.
* `results/`: Directory where the extracted CSV files will be saved. The user can specify a different path using command-line arguments.

## PDF Reader Package Usage

### Installation
To install this package, use the provided .whl or .tar.gz files in the `dist/` folder. Use the following command to install:
```
pip install pdf_reader-0.1.0-py3-none-any.whl
```

Alternatively, if you have the source code, you can install the package directly with:
```
pip install .
```

### Usage
After installing, you can run the package from the command line. By default, it uses the provided `config.yml` to extract tables from the PDF and save them as CSV files in the current working directory.

to run the package:

```
pdf-reader --config_file path_to_your_config.yml --results_path path_to_save_results
```

* `--config_file` (optional): Specify the path to a YAML configuration file.
If not provided, the default config.yml in the package will be used.
* `--results_path` (optional): Specify the directory where the extracted CSV files will be saved.
If not provided, results will be saved in the current working directory.

#### Example
```
pdf-reader --config_file config.yml --results_path output
```
This command will extract tables from the PDF specified in `config.yml` and save the results in the `output` folder.

## PDF Reader Repository Usage

### Installations and Setup

This project uses Poetry for dependency management. If you haven't installed Poetry yet, follow the instructions here.

### 1. Clone the repository (W.I.P.)

```
git clone https://github.com/mgranica/pdf-reader-extractor.git
cd pdf-reader-extractor
```

### 2. Install Dependencies

to create the virtual env within the root directory of the project, run:
```
poetry config virtualenvs.in-project true
```

to install the required dependencies, run:
```
poetry install
```
This will create a virtual environment and install all required packages as specified in pyproject.toml.

### 3. Activate the Virtual environment

After installation, activate the virtual environment:
```
poetry shell
```

### 4. Configuration

Modify the `config.yml` file with your desired settings. Below is the default example:

```
pdf_url: "https://example.com/your-pdf-file.pdf"
table_settings:
  join_x_tolerance: 3
  join_y_tolerance: 10
  intersection_x_tolerance: 3
  intersection_y_tolerance: 10
pattern: "Example.*?(\n|$)"
```

* `pdf_url`: The URL of the PDF file to be processed.
* `table_settings`: Custom settings to guide pdfplumber on how to extract tables.
* `pattern`: A regex pattern to find titles that precede tables.

### 5. Run the script

Run the PDF extraction process by executing the following command:
```
python -m src.main
```