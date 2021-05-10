import streamlit as st
from streamlit.hashing import _CodeHasher
from streamlit.report_thread import get_report_ctx
from streamlit.server.server import Server
from gtts import gTTS
from io import BytesIO
import requests
# new imports
from fpdf import FPDF
import base64
# our files
import spoon
import nutritionix



def main():
	state = _get_state()

	logocol, linkcol = st.sidebar.beta_columns(2)
	logocol.image('logo.png')
	#st.sidebar.title("Picky Eats")
	linkcol.markdown("[Post-Use Survey](https://docs.google.com/forms/d/e/1FAIpQLScaBvmxyaX-l4Q4_VZUF9Ve4N5jsxBXP7mqtI1ksG9J4oscbw/viewform)")

	pages = {

		"Add Ingredients" : page_ingredients,
		"Find Recipes" : page_recipe_spoonacular,
		"My Information": page_bmi,
		"Generate Report": page_report
		
	}

	page = st.sidebar.radio("Select page", tuple(pages.keys()))

	# Display the selected page with the session state
	pages[page](state)

	# Mandatory to avoid rollbacks with widgets, must be called at the end of your app
	state.sync()

@st.cache
def GetCalorieIntake(height, weight, age, gender, exercise, goal, goalWeight):
	url = "https://fitness-api.p.rapidapi.com/fitness"

	payload = "height=" + str(height * 2.54) + "&weight=" + str(weight / 2.205) + "&age=" + str(age) + "&gender=" + str(gender) + "&exercise=" + str(exercise) + "&goal=" + str(goal) + "&goalWeight=" + str(goalWeight / 2.205)
	headers = {
		'content-type': "application/x-www-form-urlencoded",
		#'x-rapidapi-key': "7ffbaae7d9msh7ce3fe51d091c84p19dc5cjsn2dfdbe13bc22",
		'x-rapidapi-key': "d4859a86famsh5bd6ac4a88c8f57p16f3dajsne6547e855a82",
		'x-rapidapi-host': "fitness-api.p.rapidapi.com"
		}

	response = requests.request("POST", url, data=payload, headers=headers)

	json_file = response.json()
	#st.write(json_file)
	Calorie_dict = json_file.get("neededEnergy").get("bmi").get("calories").get("value")

	return Calorie_dict

@st.cache(allow_output_mutation=True)
def getAudioInstructions(recipe):

	instructions_string = ''
	for s in recipe['analyzedInstructions'][0]['steps']:
		instructions_string += 'Step ' + str(s['number']) + ' '
		instructions_string += s['step'] + '\n'

	mp3_fp = BytesIO()
	speech = gTTS(instructions_string)
	speech.write_to_fp(mp3_fp)
	return mp3_fp


def page_bmi(state):

	# exercise_dict = {
	# 	'Little':'little', 
	# 	'Light':'light', 
	# 	'Moderate':'moderate', 
	# 	'Heavy':'heavy', 
	# 	'Very Heavy':'very_heavy'
	# }
	weightgoal_dict = {
		'Extreme Fat Loss'   :'fatloss_reckless',
		'Normal Fat Loss'    :'fatloss_aggressive',
		'Slow Fat Loss'      :'fatloss_moderate',
		'Maintenance'        :'maintenance',
		'Slow Bulking'       :'bulking_slow',
		'Normal Bulking'     :'bulking_normal',
		'Extreme Bulking'    :'bulking_aggressive'
	}
	# exercise_options = list(exercise_dict.keys())
	weightgoal_options = list(weightgoal_dict.keys())
	gender_options = ['Male', 'Female']
	st.header('Calculate Daily Calories')
	st.write('Recommended Daily Calorie Intake: ' + str(state.user_calories or state.user_base_calories or "Not Calculated"))
	st.subheader('My Info')
	with st.form(key='user_info'):
		#ftcol, incol, agecol, wtcol = st.beta_columns(4)
		col1, col2 = st.beta_columns(2)
		state.feet = col1.number_input('Height: Feet', min_value=1, value=int(state.feet or 6))
		state.inches = col1.number_input('Height: Inches', min_value=0, max_value= 11, value=int(state.inches or 2))
		height = state.feet * 12 + state.inches
		state.age = col1.number_input('Age', min_value=0, value=int(state.age or 22))
		state.weight = col1.number_input('Current Weight (lbs)', min_value=0, value=int(state.weight or 180))

		#gendercol, exercisecol, weightcol = st.beta_columns(3)
		state.gender = col2.radio('Gender', gender_options, gender_options.index(state.gender) if state.gender else 0)
		#state.exercise_level = exercisecol.radio('Exercise Level', exercise_options, exercise_options.index(state.exercise_level) if state.exercise_level else 0)
		state.weight_goal = col2.radio('Weight Goal', weightgoal_options, weightgoal_options.index(state.weight_goal) if state.weight_goal else 3)

		if st.form_submit_button('Calculate'):
			state.user_base_calories = GetCalorieIntake(height, state.weight, state.age, state.gender.lower(), 'little', weightgoal_dict[state.weight_goal], state.weight)
			state.user_calories = state.user_base_calories
		st.write('Base Calorie Requirements:', str(state.user_base_calories or 'Not Calculated'))
	#st.write(height, state.weight, state.age, state.gender.lower(), exercise_dict[state.exercise_level], weightgoal_dict[state.weight_goal], state.goalweight)
	if state.user_base_calories: # needs user data
		st.subheader('My Daily Exercises')
		with st.form(key='user_exercise'):
			col1, col2, col3 = st.beta_columns([3, 3, 1])
			exercise_type = col1.selectbox('Exercise Type', nutritionix.exercises)
			exercise_duration = col2.number_input('Duration (minutes)', min_value=0)
			col3.subheader('')
			if col3.form_submit_button('Add'):
				if not state.user_exercise_types:
					state.user_exercise_types = []
					state.user_exercise_durations = []
				state.user_exercise_types.append(exercise_type)
				state.user_exercise_durations.append(exercise_duration)
		st.write('Burned Calories: ' + str(state.user_burned_calories or 0))	
		if state.user_exercise_durations:
			for i in range(len(state.user_exercise_types) - 1, -1, -1):
				txtcol, btncol = st.beta_columns([5, 1])
				txtcol.write(state.user_exercise_types[i] + ' for ' + str(state.user_exercise_durations[i]) + ' minutes.')
				if btncol.button('Remove', key=i):
					state.user_exercise_types.pop(i)
					state.user_exercise_durations.pop(i)
			state.user_burned_calories = nutritionix.calculateAndReturn(state.user_exercise_types, state.user_exercise_durations, state.gender, state.weight, state.feet, state.inches, state.age)
			state.user_calories = state.user_base_calories + state.user_burned_calories
		
	

def page_ingredients(state):
	num_ingredients = 5
	#input ingredients
	if state.user_ingredients == None:
		state.user_ingredients = []
		state.found_ingredients = []
	

	if state.prev_input == None:
		state.prev_input = ""

	user_input = st.text_input("Search Ingredient", value="")

	if user_input and user_input != state.prev_input:
		state.prev_input = user_input
		state.found_ingredients = spoon.getIngredientAutocomplete(user_input, num_ingredients)


	if (len(state.found_ingredients) > 0):
		col1, col2 = st.beta_columns([3, 1])
		user_select_ingredient = col1.selectbox('Select Ingredient', state.found_ingredients, format_func=lambda x : x['name'].capitalize())
		col2.text("")
		col2.text("")
		addbtn = col2.button('Add')
		if addbtn and not user_select_ingredient in state.user_ingredients:
			state.user_ingredients.append(user_select_ingredient)
			state.new_ingredients = True
			
	#display ingredients
	st.text('')
	st.header('My Ingredients')
	for ing in state.user_ingredients:
		imgcol, txtcol, btncol = st.beta_columns([1, 2, 1])
		imgcol.image('https://spoonacular.com/cdn/ingredients_100x100/' + ing['image'])
		txtcol.header(ing['name'].capitalize())
		btncol.text('')
		b = btncol.button('Remove', key=ing)
		if b:
			state.user_ingredients.remove(ing)

def page_recipe_spoonacular(state):
	num_recipes = 10

	if state.user_recipes == None:
		state.user_recipes = []
	querycol, btncol = st.beta_columns([4, 1])
	recipe_query = querycol.text_input('Search Recipes (leave empty for suggestions based on your ingredients)')
	btncol.subheader('')
	#update the displayed recipes if user has added new ingredients
	if btncol.button('Search') or (state.user_ingredients and len(state.user_ingredients) > 0 and state.new_ingredients):
		print('new search', recipe_query)
		state.prev_query = recipe_query
		state.new_ingredients = False

		ingredients_names = [ing['name'] for ing in state.user_ingredients]
		if len(recipe_query) > 0 and len(state.user_ingredients) > 0:
			print('search 1')
			recipes = spoon.complexSearchAPI(num_recipes, recipe_query, ingredients_names)
			if recipes['totalResults'] < num_recipes:
				recipes['results'].extend(spoon.complexSearchAPI(num_recipes - recipes['totalResults'], recipe_query)['results'])
		elif len(recipe_query) > 0:
			print('search 2')
			recipes = spoon.complexSearchAPI(num_recipes, query=recipe_query)
		else:
			print('search 3')
			recipes = spoon.complexSearchAPI(num_recipes, ingredientsList=ingredients_names)

		state.recipe_info = recipes['results']

	else:
		print('no search')
	if state.recipe_info:
		for x in range(len(state.recipe_info)):
			imcol, titlecol, btncol = st.beta_columns((1, 3, 1))
			try:
				imcol.image(state.recipe_info[x]['image'])
			except:
				imcol.image('https://cdn2.iconfinder.com/data/icons/coronavirus-10/512/cooking-hot-cook-food-boiling-512.png')
			titlecol.markdown('[' + str(state.recipe_info[x]['title']) + '](' + str(state.recipe_info[x]['sourceUrl']) + ')')
			with titlecol.beta_expander('Details'):
				st.write("Calories per serving:", str(round(state.recipe_info[x]["nutrition"]["nutrients"][0]["amount"])))
				st.write("Cooking Time:", str(round(state.recipe_info[x]["readyInMinutes"])) + " minutes.")
				st.write("Servings:", str(state.recipe_info[x]['servings']))
				st.write("Price per Serving: ${price:.2f}".format(price = state.recipe_info[x]['pricePerServing'] / 100))
				st.write("Ingredients: ",[ing['name'] for ing in state.recipe_info[x]['nutrition']['ingredients']])
			btncol.subheader('')
			if btncol.button('Add to My List', key=x):
				state.user_recipes.append(state.recipe_info[x])
				
	
	# display the user's recipes on the sidebar
	if state.user_recipes != None:
		#nutrition info
		with st.sidebar.beta_expander('Selected Recipes Nutrition'):
			cal = round(sum([recipe["nutrition"]["nutrients"][0]["amount"] for recipe in state.user_recipes]))
			user_cal = state.user_calories or 2000
			st.write("Calories:", str(cal), '/ ' + str(user_cal))
			st.progress(cal / user_cal)
			nutrient_dict = {}
			for recipe in state.user_recipes:
				recipe_nutrients = recipe['nutrition']['nutrients']
				for i in range(1, len(recipe_nutrients)):
					nutrient_name = recipe_nutrients[i]['name']
					nutrient_amount = float(recipe_nutrients[i]['percentOfDailyNeeds'])
					nutrient_dict[nutrient_name] = nutrient_dict.get(nutrient_name, 0) + nutrient_amount
			for key, value in nutrient_dict.items():
				st.write(str(key) + ':', str(round(value, 2)) + '%')
				st.progress(min(round(value), 100))

		#recipes
		st.sidebar.subheader("")
		for recipe in state.user_recipes:
			imcol, btncol = st.sidebar.beta_columns((1, 1))
			try:
				imcol.image(recipe['image'])
			except:
				imcol.image('https://cdn2.iconfinder.com/data/icons/coronavirus-10/512/cooking-hot-cook-food-boiling-512.png')
			st.sidebar.markdown('[' + str(recipe['title']) + '](' + str(recipe['sourceUrl']) + ')')
			with st.sidebar.beta_expander('Details'):
				if len(recipe['analyzedInstructions']) == 0:
					st.write('Instructions unavailable, click link to view recipe.')
				else:
					audio = getAudioInstructions(recipe)
					st.write('Audio Instructions')
					st.audio(audio)
				st.write("Calories per serving:", str(round(recipe["nutrition"]["nutrients"][0]["amount"])))
				st.write("Cooking Time:", str(round(recipe["readyInMinutes"])) + " minutes.")
				st.write("Servings:", str(recipe['servings']))
				st.write("Price per Serving: ${price:.2f}".format(price = recipe['pricePerServing'] / 100))
				st.write("Ingredients: ",[ing['name'] for ing in recipe['nutrition']['ingredients']])
			if btncol.button('Remove', key=recipe['id']):
				state.user_recipes.remove(recipe)
			st.sidebar.text('')


def page_recipe_edamam(state):
	def findedamamrecipes(ingredients):
		url = "https://edamam-recipe-search.p.rapidapi.com/search"

		querystring = {"q":ingredients}

		headers = {
			'x-rapidapi-key': "7ffbaae7d9msh7ce3fe51d091c84p19dc5cjsn2dfdbe13bc22",
			'x-rapidapi-host': "edamam-recipe-search.p.rapidapi.com"
			}

		response = requests.request("GET", url, headers=headers, params=querystring)

		return response.json()


	user_input = st.text_area("Add Ingredients you already have!")
	st.write("ex: chicken,rice,eggs")

	if st.button("Ingredient List Finished, Find Recipies!"):
		response = findedamamrecipes(user_input)
		#st.write(response['hits'][0])
		for x in range(len(response.get("hits"))):
			#recipearray.update({response.get("hits")[x].get("recipe").get("label"): response.get("hits")[x].get("recipe").get("url")})
			recipe = response['hits'][x]['recipe']
			calories = recipe['calories'] / recipe['yield']
			cooktime = recipe['totalTime']
			imcol, titlecol = st.beta_columns((1, 4))
			try:
				imcol.image(recipe['image'])
			except:
				imcol.image('https://cdn2.iconfinder.com/data/icons/coronavirus-10/512/cooking-hot-cook-food-boiling-512.png')
			titlecol.markdown('[' + str(recipe['label']) + '](' + str(recipe['url']) + ')')
			with titlecol.beta_expander('Details'):
				st.write("Calories per serving:", str(round(calories)))
				st.write("Cooking Time:", str(round(cooktime)) + " minutes." if cooktime else "Not Listed.")

	


class _SessionState:

	def __init__(self, session, hash_funcs):
		"""Initialize SessionState instance."""
		self.__dict__["_state"] = {
			"data": {},
			"hash": None,
			"hasher": _CodeHasher(hash_funcs),
			"is_rerun": False,
			"session": session,
		}

	def __call__(self, **kwargs):
		"""Initialize state data once."""
		for item, value in kwargs.items():
			if item not in self._state["data"]:
				self._state["data"][item] = value

	def __getitem__(self, item):
		"""Return a saved state value, None if item is undefined."""
		return self._state["data"].get(item, None)
		
	def __getattr__(self, item):
		"""Return a saved state value, None if item is undefined."""
		return self._state["data"].get(item, None)

	def __setitem__(self, item, value):
		"""Set state value."""
		self._state["data"][item] = value

	def __setattr__(self, item, value):
		"""Set state value."""
		self._state["data"][item] = value
	
	def clear(self):
		"""Clear session state and request a rerun."""
		self._state["data"].clear()
		self._state["session"].request_rerun()
	
	def sync(self):
		"""Rerun the app with all state values up to date from the beginning to fix rollbacks."""

		# Ensure to rerun only once to avoid infinite loops
		# caused by a constantly changing state value at each run.
		#
		# Example: state.value += 1
		if self._state["is_rerun"]:
			self._state["is_rerun"] = False
		
		elif self._state["hash"] is not None:
			if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
				self._state["is_rerun"] = True
				self._state["session"].request_rerun()

		self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
	session_id = get_report_ctx().session_id
	session_info = Server.get_current()._get_session_info(session_id)

	if session_info is None:
		raise RuntimeError("Couldn't get your Streamlit Session object.")
	
	return session_info.session

def show_pdf(file_path):
    with open(file_path,"rb") as f:
          base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

def generatepdf(state):
	try:
		pdf = FPDF()	
		# Add a page
		pdf.add_page()
		
		# set style and size of font 
		# that you want in the pdf
		pdf.set_font("Arial", size = 12)
		lennth = 5
		linetrack = 1
		i = 0
		t = 0
		for x in range(len(state.user_recipes)):
			i+=1
			t += 1
			pdf.set_font("Arial", style='B' , size = 12)
			pdf.cell(200,10, txt = "Recipe name:  " + str(state.user_recipes[x]['title']), ln= i, align = '' )
			pdf.set_font("Arial", size = 12)
			value2 = str(state.user_recipes[x]['sourceUrl'])
			pdf.multi_cell(0, 10, txt= value2)
			ing = ""
			for j in range(len(state.user_recipes[x]['nutrition']['ingredients'])):
				#pdf.cell(200,10, txt =  str(t) + ". " + str(state.user_recipes[x]['nutrition']['ingredients'][j]['name']), ln= i, align = '' )
				if(j == len(state.user_recipes[x]['nutrition']['ingredients'])-1):
					ing += str(state.user_recipes[x]['nutrition']['ingredients'][j]['name']) + "."
				else:
					ing += str(state.user_recipes[x]['nutrition']['ingredients'][j]['name']) + ", "
				i+=1
				t+=1
			pdf.multi_cell(0, 10, txt = "Ingredients "  + ": " + ing , align = '')
			text = ""
			t = 0
			if len(state.user_recipes[x]['analyzedInstructions']) != 0:
				for steps in state.user_recipes[x]['analyzedInstructions'][0]['steps']:
					t = t + 1
					pdf.multi_cell(0,10,txt="Step " + str(t) + ": " + steps['step'])
				t = 0
		pdf.output("GFG.pdf")
		show_pdf("GFG.pdf")
	except:
		st.write("Please add recipes using the Find Recipes page!")
	

def page_report(state):
	if st.button("Generate PDF"):
		generatepdf(state)

def _get_state(hash_funcs=None):
	session = _get_session()

	if not hasattr(session, "_custom_session_state"):
		session._custom_session_state = _SessionState(session, hash_funcs)

	return session._custom_session_state


if __name__ == "__main__":
	main()