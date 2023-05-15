# importing the required libraries 
import csv 
import json 
 
# defining the function to convert CSV file to JSON file 
def convjson(csvFilename, jsonFilename): 
     
    # creating a dictionary 
    mydata = {} 
     
    # reading the data from CSV file 
    with open(csvFilename, encoding = 'utf-8') as csvfile: 
        csvRead = csv.reader(csvfile, delimiter='~') 
         
        # Converting rows into dictionary and adding it to data 
        for rows in csvRead: 
            print(rows)

    # dumping the data 
    with open(jsonFilename, 'w', encoding = 'utf-8') as jsonfile: 
        jsonfile.write(json.dumps(mydata, indent = 4)) 
 
# filenames      
csvFilename = r'dataframe1.csv' 
jsonFilename = r'dataframe1.json' 
 
# Calling the convjson function 
convjson(csvFilename, jsonFilename)