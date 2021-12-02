import PyPDF2
import pandas as pd
import sys
import os
import re


def pdfMain(filepath):
    pdf_to_scan = open(filepath, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_to_scan)

    results = pd.DataFrame(columns=['body'])
    num_pages = pdf_reader.numPages
    cur_text = ''
    to_add = ''
    #results = results.append({'body':"No pages error" + str(num_pages)}, ignore_index=True)
    for page in range(0, num_pages):
        cur_page = pdf_reader.getPage(page)
        cur_text = cur_page.extractText()
        #results = results.append({'body':cur_text}, ignore_index=True)
        breakup = cur_text.splitlines()
        new_entry = ''
        for i in range (0, len(breakup)):
            new_entry = str(new_entry) + str(breakup[i])
            if (i % 3 == 0):
                results = results.append({'body':new_entry}, ignore_index=True)
                new_entry = ''
        if (len(new_entry) > 1):
                results = results.append({'body':new_entry}, ignore_index=True)
       
    return results
