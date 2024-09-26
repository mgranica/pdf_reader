import requests as re
import pandas as pd
import pdfplumber
import logging
import argparse
from io import BytesIO
import yaml
import os

# Set up a basic logger configuration
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class PDFReader:
    def __init__(self, config_file, results_path):
        """
        Initializes the PDFReader class by loading the config file.

        Parameters:
        config_path (str): Path to the YAML configuration file.
        """
        self.results_path = results_path
        self.config = self.load_config(config_file)
        self.url = self.config["pdf_url"]
        self.table_settings = self.config["table_settings"]
        self.title_pattern = self.config["pattern"]
        
    def load_config(self, config_path):
        """
        Loads the YAML configuration file.

        Parameters:
        config_path (str): Path to the YAML config file.

        Returns:
        dict: Parsed configuration.
        """
        try:
            with open(config_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logging.error(f"Configuration file not found at {config_path}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML config: {e}")
            raise
    
    def extract_pdf_from_url(self):
        """
        Extracts the PDF content from the URL and stores it in memory.
        """
        try:
            response = re.get(self.url)
            response.raise_for_status()  # Raises HTTPError if the request failed
            self.pdf_file = BytesIO(response.content)
            logging.info(f"PDF successfully downloaded from {self.url}")
        except re.exceptions.RequestException as e:
            logging.error(f"Error downloading the PDF: {e}")
            raise 
        
    def extract_titles_from_page(self, page):
        """
        Extracts titles from a PDF page using the regex pattern.

        Parameters:
        page (pdfplumber.page.Page): The page to search for titles.

        Returns:
        list: A list of title dictionaries containing text and position info.
        """
        return [title for title in page.search(self.title_pattern, return_groups=False, return_chars=False)]

    def find_title_for_table(self, titles, table_top):
        """
        Finds the title that comes before the table based on the Y-position.

        Parameters:
        titles (list): A list of titles extracted from the page.
        table_top (float): The Y-position of the table.

        Returns:
        str: The title corresponding to the table, or None if no match found.
        """
        title_top = max((title["top"] for title in titles if title["top"] < table_top), default=None)
        if title_top:
            return next((title["text"].replace("\n", "") for title in titles if title["top"] == title_top), None)
        return None
    
    def extract_tables_from_page(self, page, page_num):
        """
        Extracts tables and their corresponding titles from a given PDF page.

        Parameters:
        page (pdfplumber.page.Page): The current page being processed.
        page_num (int): The current page number.

        Returns:
        dict: A dictionary with table titles as keys and DataFrames as values.
        """
        tables_dict = {}
        titles = self.extract_titles_from_page(page)
        tables = page.extract_tables(self.table_settings)

        if not tables:
            return tables_dict

        for index, table in enumerate(tables):
            try:
                table_bbox = page.find_tables(self.table_settings)[index].bbox[1]
                title = self.find_title_for_table(titles, table_bbox)
                if title:
                    logging.info(f"Extracted table title: {title}")
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables_dict[title] = df
            except Exception as e:
                logging.error(f"Error extracting tables found on page {page_num}: {e}.")

        return tables_dict

    def extract_content_from_pdf(self):
        """
        Extracts tables and their corresponding titles from all pages of the PDF.

        Returns:
        dict: A combined dictionary of tables from all pages.
        
        Raises:
        Exception: If there is an error processing the PDF file.
        """
        if self.pdf_file is None:
            raise Exception("PDF file not loaded. Please call extract_pdf_from_url() first.")

        combined_tables = {}

        try:
            with pdfplumber.open(self.pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    tables_dict = self.extract_tables_from_page(page, page_num)
                    combined_tables.update(tables_dict)
            return combined_tables
        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            raise
        
    def save_as_csv(self, df, title):
        """
        Saves the given DataFrame as a CSV file with the title as the filename.

        Parameters:
        df (pd.DataFrame): The DataFrame to be saved.
        title (str): The title to be used as the filename.
        """
        results_path = os.path.join(self.results_path, "results")
        os.makedirs(results_path, exist_ok=True)
        # Remove or replace invalid characters in the filename
        filename = f"{title}.csv".replace(" ", "_").lower()
        filepath = os.path.join(results_path, filename)
        
        try:
            df.to_csv(filepath, index=False)
            logging.info(f"Table saved as {filepath}")
        except Exception as e:
            logging.error(f"Error saving the table to CSV: {e}")     
    
    def load_tables(self, tables):
        """
        Loads tables from a dictionary and saves them as CSV files.

        Parameters:
        tables (dict): Dictionary where keys are table titles and values are DataFrames.
        """
        if not isinstance(tables, dict) or not tables:
            logging.error("No valid tables to process.")
            return

        # Iterate over tables and try saving each one
        for title, table in tables.items():
            self.save_as_csv(table, title)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract tables from a PDF file and save them as CSV.")
    # Set default configuration
    default_config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    parser.add_argument("--config_file", type=str, nargs="?", default=default_config_path,                
        help="Path to the YAML configuration file (default: config.yml in the current directory).")
    parser.add_argument("--results_path", type=str, default=os.getcwd(),
        help="Directory where results will be saved.")
    
    # Parse command-line arguments
    args = parser.parse_args()  
    extractor = PDFReader(args.config_file, args.results_path)
    # Step 1: Extract PDF
    extractor.extract_pdf_from_url()
    # Step 2: Extract tables
    raw_tables = extractor.extract_content_from_pdf()
    # Step 3: Save tables to CSV
    extractor.load_tables(raw_tables)  
    


if __name__ == "__main__":
    
    main()