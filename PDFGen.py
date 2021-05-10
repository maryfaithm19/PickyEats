import streamlit as st
from streamlit.hashing import _CodeHasher
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
import spoon
import requests


from fpdf import FPDF
  
  
# save FPDF() class into a 
# variable pdf
pdf = FPDF()
  
# Add a page
pdf.add_page()
  
# set style and size of font 
# that you want in the pdf
pdf.set_font("Arial", size = 15)
  
link = "WWW.ThisIsTheLink.com"
Totalcalories = 2500

import streamlit as st
import base64
def show_pdf(file_path):
    with open(file_path,"rb") as f:
          base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# add another cell
if st.button("Generate PDF!"):
  lennth = 5
  linetrack = 1
  pdf.cell(200, 10, txt = "Ingredients", ln = 1, align = 'C')
  for i in range(1, lennth+1):
    pdf.cell(200, 10, txt = "Recipe " + str(i) + ": " + "ham, cheese, bread, loafs, chicken, ketchup", ln = i, align = '')
    linetrack = linetrack +1

  linetrack+=1
  lennth = 5
  pdf.cell(200, 10, txt = "Link to the Website", ln = linetrack-1, align = 'C')
  temp = 0
  for i in range(linetrack, lennth+linetrack):
    temp += 1
    pdf.cell(200, 10, txt = "Recipe " + str(temp) + ": " + "WWW.ThisIsTheWebsite.Com", ln = i, align = '')
  
  pdf.cell(200, 10, txt = "Total Recomended Intake: " + str(Totalcalories), ln = 5, align = '')

  pdf.output("GFG.pdf")
  show_pdf("GFG.pdf") 
  
# save the pdf with name .pdf
pdf.output("GFG.pdf") 



