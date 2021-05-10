import streamlit as st
from streamlit.hashing import _CodeHasher
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
import spoon
import requests

user_input = st.text_input("Search Recipies", value="")

from fpdf import FPDF
  
  
# save FPDF() class into a 
# variable pdf
pdf = FPDF()
  
# Add a page
pdf.add_page()
  
# set style and size of font 
# that you want in the pdf
pdf.set_font("Arial", size = 15)

def edmameAPI(val):
    url = "https://edamam-recipe-search.p.rapidapi.com/search"

    querystring = {"q": val}

    headers = {
        'x-rapidapi-key': "7ffbaae7d9msh7ce3fe51d091c84p19dc5cjsn2dfdbe13bc22",
        'x-rapidapi-host': "edamam-recipe-search.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    recipe_info = response.json()
    
    for x in range(len(recipe_info["hits"])):
            imcol, titlecol, btncol = st.beta_columns((1, 5, 1))
            try:
                imcol.image(recipe_info["hits"][x]["recipe"]["image"])
            except:
                imcol.image('https://cdn2.iconfinder.com/data/icons/coronavirus-10/512/cooking-hot-cook-food-boiling-512.png')
                titlecol.markdown('[' + str(recipe_info[x]['title']) + '](' + str(recipe_info[x]['sourceUrl']) + ')')
            with titlecol.beta_expander('Details'):
                st.write("Name: ", str((recipe_info["hits"][x]["recipe"]["label"])))
                st.write("Total Calories: ", str(round(recipe_info["hits"][x]["recipe"]["calories"])))
                st.write("URL: ", str((recipe_info["hits"][x]["recipe"]["url"])))
                for i in range(len((recipe_info["hits"][x]["recipe"]["ingredientLines"]))):
                    st.write("Ingredient " + str(i+1) + ": ", str((recipe_info["hits"][x]["recipe"]["ingredientLines"][i])))



if st.button("Get recipies"):
    edmameAPI(str(user_input))

