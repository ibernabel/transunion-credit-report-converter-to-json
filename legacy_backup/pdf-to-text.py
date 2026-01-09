#Import libraries
import fitz #PyMuPDF (PDF extractor)
import unidecode #format accents
import sys #Module for interacting with the system and the Python interpreter

#Read, process and export file to txt
#print('Enter the file name (without: ".pdf"):')
input_name = input('Enter the file name (without: ".pdf"):')
file_name = f'{input_name}'

fname = f'./credit_reports/{file_name}.pdf'

#Raise error if PDF file has not found with provided name
try:
	doc = fitz.open(fname)  
except fitz.fitz.FileNotFoundError:
    raise ValueError(f'No such file called: {file_name}')
    #print(f'No such file called:  {file_name}')
    #sys.exit()

data = ''
for page in doc:  
    data += page.get_text() 

text = unidecode.unidecode( data.lower() )
#print(text)

##Save the file
with open(f'./output_text/{file_name}.txt', 'w') as f:
    f.write(text)
print(f"The File {file_name}.txt, was saved successful into output_text folder.")

#pdf-to-text.py
#This code is base on the code share for:
#Autor: Jeanna Schoonmaker
#AuthorURL: https://medium.com/@jeanna-schoonmaker
#ArticleURL: https://medium.com/social-impact-analytics/comparing-4-methods-for-pdf-text-extraction-in-python-fd34531034f