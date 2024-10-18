import sys
import requests
from PyPDF2 import PdfReader
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to check API and search for the string in the PDF files with context
def check_api_for_pdfs(api_url, search_string, context_lines=2):
    try:        
        # Step 1: Send GET request to the API to retrieve the JSON data
        # Disable SSL verification in requests.get()
        response = requests.get(api_url, verify=False)        
        
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            
            # Check if "ok" is True and "objeto" array exists
            if data.get("ok") and "objeto" in data:
                pdfs = data["objeto"]  # Get the list of PDFs
                
                # Loop through each PDF object in the "objeto" array
                for pdf_info in pdfs:
                    per_id = pdf_info.get("perid")  # Extract id periodico
                    pdf_file_name = pdf_info.get("perarchivofile")  # Extract file name
                    perfecha = pdf_info.get("perfecha")  # Extract date
                    print(f"Procesando PDF: {pdf_file_name} - Fecha: {perfecha}")
                    
                    # Step 2: Download the PDF
                    # Disable SSL verification in requests.get()
                    pdf_download_url = 'https://backperiodico.guanajuato.gob.mx/api/Periodico/DescargarPeriodicoId/' + str(per_id)
                    pdf_response = requests.get(pdf_download_url, verify=False)
                    
                    if pdf_response.status_code == 200:
                        pdf_file_path = pdf_file_name
                        with open(pdf_file_path, 'wb') as pdf_file:
                            pdf_file.write(pdf_response.content)
                        
                        # Step 3: Read the PDF and extract text page by page
                        reader = PdfReader(pdf_file_path)
                        found = False  # Track if the string is found
                        
                        for page_num, page in enumerate(reader.pages, start=1):
                            page_text = page.extract_text()
                            lines = page_text.splitlines()  # Split text into lines

                            # Step 4: Search for the string in the current page's text
                            for i, line in enumerate(lines):
                                if search_string.lower() in line.lower():
                                    found = True
                                    # Print the found string with context (before and after lines)
                                    start_index = max(i - context_lines, 0)
                                    end_index = min(i + context_lines + 1, len(lines))
                                    
                                    print(f'String "{search_string}" found in {pdf_file_name}, Page {page_num} at line {i}:')
                                    for context_line in lines[start_index:end_index]:
                                        print(context_line)
                                    print("-" * 40)  # Divider after each result
                                    break  # Stop searching after finding the string
                        
                        if not found:
                            print(f'String "{search_string}" NOT found in {pdf_file_name}.')
                    else:
                        print(f"Failed to download PDF: {pdf_file_name}. Status code: {pdf_response.status_code}")
            else:
                print(f"API did not return valid data. Response: {data}")
        else:
            print(f"Failed to connect to API. Status code: {response.status_code}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# API URL and search string
api_url = 'https://backperiodico.guanajuato.gob.mx/api/Periodico/BusquedaPeriodicoPublicacion/2024/210/null/null/null/0/0'

print("Ejecución: python busca_text_en_periodico.py <texto_a_buscar>")
# Check if search string is provided as a command-line argument, otherwise use a default value for local testing
if len(sys.argv) < 2:
    search_string = 'Ruben'  # Default search term for local testing
    print(f"No se encontró texto a buscar, usar por defecto: {search_string}")
else:
    search_string = sys.argv[1]  # The search string passed as a command-line argument

context_lines = 2  # Number of lines to show before and after the found string

print(f"Búsqueda de cadena de texto: {search_string}")
print("************************************")
check_api_for_pdfs(api_url, search_string, context_lines)
