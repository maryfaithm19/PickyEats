import requests
import json

spoonURL = "https://api.spoonacular.com/"
APIkey = "&apiKey=756937ad284e40029989f875b53fc845"
APIkey2 = "&apiKey=8280ebd83c544703b64be0d7d3432e38"

def requestWithAPIKey(request):
	global APIkey, APIkey2
	response = requests.get(request + APIkey).json()
	#print(response)
	if isinstance(response, dict) and response.get('status', '') == 'failure':
		APIkey = APIkey2
		response = requests.get(request + APIkey).json()
		print('switched API key')
	return response


#Functions to Format Variables to String for API Calls
######################################################################
def createIngredientsString(ingredientsList): #Create string for ingredients list
	ingredientsRequest = ""
	for x in ingredientsList:
		ingredientsRequest = ingredientsRequest + x + "%2C,"
	ingredientsRequest = ingredientsRequest[:-1] #Getting rid of last comma
	return ingredientsRequest

def createRecipeIDsString(recipeIDs):
	recipeRequest = ""
	for x in recipeIDs:
		recipeRequest = recipeRequest + str(x) + "," #Getting rid of last comma
	recipeRequest = recipeRequest[:-1]
	return recipeRequest


#Functions to Create API Call and Request JSON Response (WHERE THE POINTS ARE USED)
######################################################################
def findByIngredientsAPI(ingredientsList, number):
	findByIngredients = "recipes/findByIngredients?ingredients="
	request = spoonURL + findByIngredients + createIngredientsString(ingredientsList) + "&number=" + str(number)
	#response = requests.get(request)
	spoon_data = requestWithAPIKey(request)
	return spoon_data

def complexSearchAPI(number, query=None, ingredientsList=None):
	print('complex search', query, ingredientsList)
	complexSearch = 'recipes/complexSearch?'
	request = spoonURL + complexSearch + 'number=' + str(number) + '&addRecipeNutrition=true'
	if query:
		request += '&query=' + query
	if ingredientsList:
		request += '&includeIngredients=' + createIngredientsString(ingredientsList) + '&sort=max-used-ingredients'#&fillIngredients=true'
	#response = requests.get(request)
	spoon_data = requestWithAPIKey(request)
	#print(spoon_data)
	return spoon_data

def findByNutritionAPI(calories, number):
	findByNutrition = "recipes/findByNutrients?maxCalories="
	request = spoonURL + findByNutrition + str(calories) + "&number=" + str(number)
	#response = requests.get(request)
	spoon_data = requestWithAPIKey(request)
	return spoon_data

def getRecipeInfoBulkAPI(recipeIDs):
	request = spoonURL + "recipes/informationBulk?ids=" + createRecipeIDsString(recipeIDs) + "&includeNutrition=true"
	#response = requests.get(request)
	spoon_data = requestWithAPIKey(request)
	return spoon_data

def getIngredientAutocomplete(user_input, number):
	print('ingredient autocomplete')
	ingredientAutocomplete = "food/ingredients/autocomplete?query="
	request = spoonURL + ingredientAutocomplete + str(user_input) + "&number=" + str(number)
	#response = requests.get(request)
	spoon_data = requestWithAPIKey(request)
	return spoon_data


#Functions that gets Results from API CALLS
######################################################################
def getRecipeIDs(spoon_data): #FROM findByIngredientsAPI & findByNutritionAPI
	recipeIDs = []
	for x in range(len(spoon_data)):
		recipeIDs.append(spoon_data[x]["id"])
	return recipeIDs
	#Returns Array of Recipe IDs

def getRecipeTitles(spoon_data): #FROM getRecipeInfoBulkAPI
	recipeTitles = []
	for x in range(len(spoon_data)):
		recipeTitles.append(spoon_data[x]['title'])
	return recipeTitles
	#Returns Array of Recipe Titles

def getRecipeCalories(spoon_data): #FROM getRecipeInfoBulkAPI
	recipeCalories = []
	for x in range(len(spoon_data)):
		recipeCalories.append(spoon_data[x]["nutrition"]["nutrients"][0]["amount"])
	return recipeCalories
	#Returns Array of Recipe Calories

def getRecipeURLs(spoon_data): #FROM getRecipeInfoBulkAPI
	recipeURLs = []
	for x in range(len(spoon_data)):
		recipeURLs.append(spoon_data[x]["sourceUrl"])
	return recipeURLs
	#Returns Array of Recipe URLS

def getRecipeImageURLs(spoon_data): #FROM getRecipeInfoBulkAPI
	recipeImageURLs = []
	for x in range(len(spoon_data)):
		recipeImageURLs.append(spoon_data[x]["image"])
	return recipeImageURLs
	#Returns Array of Recipe URLS

def getRecipeTimes(spoon_data):
	recipeTimes = []
	for x in range(len(spoon_data)):
		recipeTimes.append(spoon_data[x]["readyInMinutes"])
	return recipeTimes
	#Returns Array of Recipe Total Cook Times




#TESTING FUNCTIONALITY
# ######################################################################

# numResults = 5 #WILL CHANGE TO WHAT LOOKS BEST ON FRONTEND OR IF DAILY POINTS IS CLOSE

# ingredientsList = ("bread", "ham", "cheese", "mayonaise") #HARD CODED FOR NOW, WILL PULL FROM FRONTEND
# calories = 1000 #HARD CODED FOR NOW, WILL PULL FROM FRONTEND

# if (len(ingredientsList) > 0): #If no Ingredients are Given
# 	spoon_data1 = findByIngredientsAPI(ingredientsList, numResults)
# 	#Finds Recipes by On Hand Ingredients Only
# else:
# 	spoon_data1 = findByNutritionAPI(calories, numResults)
# 	#Finds Recipes by maxCalories Only

# recipeIDs = getRecipeIDs(spoon_data1) #Array of Recipe IDs
# spoon_data2 = getRecipeInfoBulkAPI(recipeIDs)
# recipeCalories = getRecipeCalories(spoon_data2) #Array of Recipe Calories
# recipeURLs = getRecipeURLs(spoon_data2) #Array of Recipe URLs
# recipeImageURLs = getRecipeImageURLs(spoon_data2)
# recipeTimes = getRecipeTimes(spoon_data2) #Array of Recipe Cook Times

# #LOOPING THROUGH ARRAYS TO SHOW RESULTS
# ######################################################################
# for x in range(len(recipeIDs)):
# 	print("Recipe ID: " + str(recipeIDs[x]))
# 	print("recipe Calories: " + str(recipeCalories[x]))
# 	print("Recipe URL: " + recipeURLs[x])
# 	print("Recipe Image URL: " + recipeImageURLs[x])
# 	print("Recipe Total Cook Time: " + str(recipeTimes[x]) + " minutes")
# 	print("-" * 100)