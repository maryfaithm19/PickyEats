import requests
import http.client
import json

#Functions to Convert Variables
######################################################################
def heightToCm(feet, inches):
    inches += (12 * feet)
    heightCm = 2.54 * inches
    return heightCm

def weightToKg(pounds):
    weightKg = pounds / 2.205
    return weightKg

#Function that formats exercise for API Call
######################################################################
def formatExerciseString(exercise, time):
    exerciseString = exercise + ' for ' + str(time) + ' minutes'
    return exerciseString 

#Function that Makes API Call
######################################################################
def getExerciseData(query, gender, weight, height, age):
    myAppID = "806f4723"
    myAppKey = "f79276b05f9b592345c1519713e009f0"
    conn = http.client.HTTPSConnection("trackapi.nutritionix.com")
    payload = 'query=' + query + '&gender=' + gender + '&weight_kg=' + str(weight) + '&height_cm=' + str(height)  + '&age=' + str(age)
    
    headers = {
        'x-app-id':myAppID,
        'x-app-key':myAppKey,
        'content':'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    conn.request("POST", "/v2/natural/exercise", payload, headers)
    res = conn.getresponse()
    rawData = res.read()
    data = json.loads(rawData.decode("utf-8"))
    return data

#Functions that gets Results from API Calls
######################################################################
def printSampleData(data): #Prints to Console for Testing
    for x in range(len(data["exercises"])):
        print("Exercise: " + data["exercises"][x]["user_input"])
        print("Calories: " + str(data["exercises"][x]["nf_calories"]))
        print("Image URL: " + data["exercises"][x]["photo"]["highres"])
        #All images I've looked at are dummy images. (I don't recommend using it)

def getTotalCalories(data): 
    calories = 0
    for x in range(len(data["exercises"])):
        calories += data["exercises"][x]["nf_calories"]
    return calories

def calculateAndReturn(exercises, durations, gender, weightlb, heightft, heightin, age):
	weightKg = weightToKg(weightlb)
	heightCm = heightToCm(heightft, heightin)
	totalCal = 0
	for i in range(len(exercises)):
		query = formatExerciseString(exercises[i], durations[i])
		totalCal += getTotalCalories(getExerciseData(query, gender.lower(), weightKg, heightCm, age))
	return round(totalCal)

#Example for Functionality
######################################################################
exercises = ["Run", "Jog", "Walk", 'Hike', 'Cycle', 'Yoga', 'Dance', 'Weight Lifting', 'Aerobics']
#List of Exercises 
# textToCalculate = "30 minutes Aerobics, ran 10 miles"#, walked 2 miles" #Get from User

# testMinutes = 40
# textToCalculate = formatExerciseString(exercises[8], testMinutes)

# testGender = "male"
# testWeightLb = 125
# testHeightFt = 5
# testHeightIn = 11
# testAge = 20

# nutr_data = getExerciseData(textToCalculate, testGender, weightToKg(testWeightLb), heightToCm(testHeightFt, testHeightIn), testAge)
# printSampleData(nutr_data)
# print("\nTotal Calories: " + str(getTotalCalories(nutr_data)))
# While the API allows multiple exercises in the query, it bugs out (I recommend only 1-2 per call)
# Can input miles or time for exercise query, I recommend using time when possible
# Also no documenation on the types of excercies covered, below are ones that I've found:
# Walked, Ran, Jogged(Uses Walked sometimes), Weight Lifting, Yoga, Biked, Swam, Aerobics