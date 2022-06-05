###############################################################


import requests
import json
import time

if choice == "y":
    token = input ("Your Webex Token?") 
    accessToken ="Bearer ()".format(token)

else:
    accessToken= "Bearer YzEzZGJhYzAtYjI5YS00OTUzLTk4NjMtNDRhYjE4MTA5N2M1ZmI0MWYxNzYtNmVm_P0A1_ffe50b97-2b4a-4965-8373-9822eafeddfd"

r = requests.get(   "https://webexapis.com/v1/rooms",
                    headers = {"Authorization": accessToken}
                )

print("List of rooms:")
rooms = r.json()["items"]
for room in rooms:
    print(f'Room title: {room["title"]}, room type: {room["type"]}')

while True:
    roomNameToSearch = input("Which room should be monitored for /location messages? ")
    roomIdToGetMessages = None
    
    for room in rooms:
        if(room["title"].find(roomNameToSearch) != -1):
            print ("Found rooms with the word " + roomNameToSearch)
            print(room["title"])
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Found room : " + roomTitleToGetMessages)
            break

    if(roomIdToGetMessages == None):
        print("Sorry, I didn't find any room with " + roomNameToSearch + " in it.")
        print("Please try again...")
    else:
        break

while True:
    time.sleep(1)
    GetParameters = {
                            "roomId": roomIdToGetMessages,
                            "max": 1
    }
    r = requests.get("https://webexapis.com/v1/messages", 
                         params = GetParameters, 
                         headers = {"Authorization": accessToken}
                    )

    if not r.status_code == 200:
        raise Exception( "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
    
    json_data = r.json()
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")
    
    messages = json_data["items"]
    message = messages[0]["text"]
    print("Received message: " + message)
    
    if message.find("/") == 0:
        location = message[1:]
         mapsAPIGetParameters = { 
                                "location": location, 
                                "key": "56boLkpXLKaKIopQKfGrOOeJhCXFFAPv"
                               }
         r = requests.get("https://www.mapquestapi.com/geocoding/v1/address", 
                             params = mapsAPIGetParameters
                        )
        json_data = r.json()

        if not json_data["info"]["statuscode"] == 0:
            raise Exception("Incorrect reply from MapQuest API. Status code: {}".format(r.statuscode))

        locationResults = json_data["results"][0]["providedLocation"]["location"]
        print("Location: " + locationResults)

        locationLat = json_data["results"][0]["locations"][0]["latLng"]["lat"]
        locationLng = json_data["results"][0]["locations"][0]["latLng"]["lng"]
        print("Location GPS coordinates: " + str(locationLat) + ", " + str(locationLng))
        
        issAPIGetParameters = { 
                                "lat": locationLat, 
                                "lon": locationLng
                              }
        r = requests.get("http://api.open-notify.org/iss/v1/", 
                             params = issAPIGetParameters
                        )

        json_data = r.json()

        if not "response" in json_data:
            raise Exception("Incorrect reply from open-notify.org API. Status code: {}. Text: {}".format(r.status_code, r.text))

        risetimeInEpochSeconds = json_data["response"][0]["risetime"]
        durationInSeconds      = json_data["response"][0]["duration"]

        risetimeInFormattedString = time.strftime('%a %b %d %H:%M:%S %Y', time.localtime(risetimeInEpochSeconds))

        responseMessage = "In {} the ISS will fly over on {} for {} seconds.".format(locationResults, risetimeInFormattedString, durationInSeconds)

        print("Sending to Webex Teams: " +responseMessage)

        HTTPHeaders = { 
                             "Authorization": accessToken,
                             "Content-Type": "application/json"
                           }
        PostData = {
                            "roomId": roomIdToGetMessages,
                            "text": roomTitleToGetMessages
                        }

        r = requests.post( "https://webexapis.com/v1/messages", 
                              data = json.dumps(PostData), 
                              headers = HTTPHeaders
                         )
        if not r.status_code == 200:
            raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
