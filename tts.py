import requests
import spoon
import pyttsx3
from playsound import playsound

def convertToMP3(text):
	#Old API Code, couldn't figure out how to convert the response to a usable mp3 and documentation is bad
	#pyttsx3 Python works better anyways tho (if we really need the 3rd API I can try to make it work)
	#url = "https://voicerss-text-to-speech.p.rapidapi.com/"
	#querystring = {"key":"1dc546d1f0534ee697fabc66671affe4","hl":"en-us","src":text,"f":"8khz_8bit_mono","c":"mp3","r":"0"}
	#headers = {
    #	'x-rapidapi-key': "d4859a86famsh5bd6ac4a88c8f57p16f3dajsne6547e855a82",
    #	'x-rapidapi-host': "voicerss-text-to-speech.p.rapidapi.com"
    #}
	#response = requests.request("GET", url, headers=headers, params=querystring)
	#filename = "new.mp3"
	#print(response.text)
	#return response.text
	
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

def convertRecipesToString(recipes): #Takes in an array of recipes (Should work with how recipes are stored currently on the website)
	stringtoMP3 = ""
	for x in range(len(recipes)):
		stringtoMP3 = stringtoMP3 + recipes[x]['title'] + "\n"
		print(recipes[x])
		for y in range(len(recipes[x]['extendedIngredients'])):
			stringtoMP3 = stringtoMP3 + str(recipes[x]['extendedIngredients'][y]['amount']) + " " + recipes[x]['extendedIngredients'][y]['unit'] + " " + recipes[x]['extendedIngredients'][y]['name'] + "\n"
	print(stringtoMP3)
	return stringtoMP3


#TESTING FUNCTIONALITY 
####################################################################
APIkey = "&apiKey=8280ebd83c544703b64be0d7d3432e38"
numResults = 5 #WILL CHANGE TO WHAT LOOKS BEST ON FRONTEND OR IF DAILY POINTS IS CLOSE
ingredientsList = ("chicken", "honey") #HARD CODED, WILL PULL FROM FRONTEND

spoon_data1 = spoon.findByIngredientsAPI(ingredientsList, numResults)
recipe_IDs = spoon.getRecipeIDs(spoon_data1) #Array of Recipe IDs
spoon_data2 = spoon.getRecipeInfoBulkAPI(recipe_IDs)

chosen_recipes = [] #Testing an Array of Recipes from JSON file, should be like it is on the website
for x in range(3):
	chosen_recipes.append(spoon_data2[x])

recipes_string = convertRecipesToString(chosen_recipes)
convertToMP3(recipes_string) #For now it just instantly speaks through the console