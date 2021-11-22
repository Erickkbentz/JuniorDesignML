import PyPDF2
import pandas as pd
import sys


def main(filepath):
    pdf_to_scan = open(filepath, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_to_scan)

    results = pd.DataFrame(columns=['body'])
    num_pages = pdf_reader.numPages
    cur_text = []
    to_add = []
    for page in range(0, num_pages):
        cur_page = pdf_reader.getPage(page)
        cur_text = cur_page.extractText()
        for i in range(0, len(cur_text)):
            cur_char = cur_text[i]
            if (cur_char == '.' or cur_char == '!' or cur_char == '?'):
                to_add = str(to_add) + cur_char
                to_add = to_add.replace("\n", "")
                results = results.append({'body':to_add[2:]}, ignore_index=True)
                to_add = []
            else:
                to_add = str(to_add) + cur_char

    pd.set_option("display.max_rows", None, "display.max_columns", None, "display.max_colwidt", None)
    results.head(n=50)
    print("Finsihed")
    return results
