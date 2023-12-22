import requests
import sys
from bs4 import BeautifulSoup
#using beautifulsoup4, requests from pip
#using a venv
#9/18, got the gear list ready, and name concat from args, next time need to ready url with given name and set up the status code if check 
#make seperate functions
#9/20, made continouxs query for toons, added a dict to save total gear, and added checks for responses
#next time, make gear amount from str to int to help accumalte
#source venv/bin/activate
# make a readme file and print that out explaining the whole meme


"""
        #ask for gear range, then toons name 
        start_level = input("Enter the starting gear level: ")
        end_level = input("Enter the final gear level: ")
        try:
            gear_range = (int(start_level),int(end_level))
        except:
            print("Please enter a number")

"""



"""
generate_url
Parameters:
    * search_type: a string either either 0 or 1, where 0 is a full gear search and 1 is 
        a specific range search
    * toon_name: a string of the character whoose gear the user is querying for 
Purpose: creates a url going to swgoh.gg, where the gear information is stored.
Returns: url, a string with the url to obtain the character's gear
"""
def generate_url(search_type, toon_name):
    url = ""
    if (search_type == "0"):
        temp_name = toon_name.replace(" ", "-")
        temp_name = temp_name.lower()
        print(temp_name)
        url = "https://swgoh.gg/characters/"+ temp_name + "/gear-list/"
    else:
        temp_name = toon_name.replace(" ", "-")
        temp_name = temp_name.lower()
        print(temp_name)
        url = "https://swgoh.gg/characters/"+ temp_name + "/gear/"
    return url

    
"""
prep_toon_url
Parameters: 
        * search_type: a string either either 0 or 1, where 0 is a full gear search and 1 is 
        a specific range search
Purpose: prepares the arguements neccessary for the function generate_url(),
Returns: url, a string with the url necessary to get the toon's gear list page
"""
def prep_toon_url(search_type):
    url = ""
    if (search_type == "0"):
        toon_name = input("Please enter the character's name: ")
        url = generate_url(search_type, toon_name)
    elif (search_type == "1"):
        toon_name = input("Please enter the character's name: ")
        url = generate_url(search_type, toon_name)
    else:
        print("Please enter either 0 or 1")
    return url




"""
find_start_level
Parameters: 
        * soup: a python data object that contains the response message from the server
        * start_level: a int that specifies where to start the gear scraping
Purpose: to find the starting point for the web scraping. Once the gear level is found we will
return the soup to start at that point
Returns: start, a python object focused onto the starting point for the web scraping
"""
def find_start_level(soup, start_level):
    level_locator = "gl" + start_level
    current_gear = soup.find(class_="media list-group-item")
    temp_check = current_gear.find("h4")
    temp_level = temp_check['id']
    print(temp_level)
    while (temp_level != level_locator):
        current_gear = current_gear.find_next_sibling("li", "media list-group-item")
        temp_check = current_gear.find("h4")
        temp_level = temp_check['id']
        print(temp_level)    
    return current_gear

"""
add_gear_dict()
Parameters:
    * temp_name, a string containing the name of the gear
    * gear_int_amount, a int specifiying the quanatiy of temp_name
Purpose: given the name of the gear and its amount, the function adds that gear and its amount as 
a new key, value pair if it's not already in the dictionary. Otherwise, the value is increased by the 
amount given as a parameter.
Returns: nothing
"""
def add_gear_dict(temp_name, gear_int_amount):
    if temp_name in gear_dict:
        #accumalte total value
        gear_int_amount = gear_dict.get(temp_name) + gear_int_amount
        gear_dict.update({temp_name: gear_int_amount})
    else:
        #add to dict as new key pair
        #print("adding new item")
        gear_dict[temp_name] = gear_int_amount

    return 



"""
get_gear_levels
Parameters: 
        * levels: a tuple containing strings where the first element is the starting gear level and the second 
        element is the final gear level
Purpose: parse the page object to obtain specific gear levels as stated by the user in the 
        The gear is added into a dictionary to keep track of the total amount needed
        for all toons requeted by the user
Returns: finalGearLevel, a string that contains the gear for the specified levels

"""
def get_gear_levels(toon_url, levels):
    final_gear_level = ""
    next_level = int(levels[0])
    total_loop = (int(levels[1]) - int(levels[0]) + 1) * 6
    page = requests.get(toon_url)
    count = 1
    if (page.status_code != requests.codes.ok):
        print("Toon does not exist or mispelled\n")
        return
    else:
        soup = BeautifulSoup(page.content, "html.parser")
        print(page.status_code)
        #find the start gear level, then return here to do the extraction
        start_point = find_start_level(soup, levels[0])
        temp_gear = start_point.find_next_sibling("li")
        for x in range(0, total_loop):
            #something
            testing = temp_gear.find(class_="list-inline")
            #empty_list = str(testing.string)
            #print(repr(empty_list))
            if (testing.string == "\n"):
                #no other gear, grab gear name input 1 for amount
                gear_name = temp_gear.find("h5")
                gear_name = gear_name.text
                gear_amount = 1
                #print(gear_name)
                add_gear_dict(gear_name, gear_amount)
                #save them to the dictionary, make that a function or not
            else:
                #grab the gear names from the li and the amounts
                temp_other = temp_gear.find_all("li")
                #print("else")
                for other_gear in temp_other:
                    gear_amount = other_gear.next_element
                    gear_amount = gear_amount.strip("\nx")
                    gear_amount = int(gear_amount)
                    gear_name = other_gear.find("span")
                    gear_name = gear_name.find("img", alt=True)
                    gear_name = gear_name['alt']
                    add_gear_dict(gear_name, gear_amount)
                    #print(gear_name, gear_amount)
                #.next_element to get the amount, stirp the x to get the number then typecast
                #name of gear is in find("span", "title")
                #this thing above a list, gotta loop through it
            #move start_point to the next point
            if (count == 6 and next_level != 12):
                temp_gear = temp_gear.find_next_sibling("li")
                temp_gear = temp_gear.find_next_sibling("li")
                count = 1
                next_level += 1
            else:
                temp_gear = temp_gear.find_next_sibling("li")
                count += 1
            #print(x)
    return final_gear_level



"""
get_full_gear
Parameter: 
        * page, a python data object that contains the response message from the server
Purpose: parse the page object to obtain the full gear list of a toon in the form of a string
         The gear is added into a dictionary to keep track of the total amount needed
         for all toons requeted by the user
Returns: finalGear, a string that contains the gear list for the toon requested
"""
def get_full_gear(toon_url):
    total_gear = ""
    page = requests.get(toon_url)
    if (page.status_code != requests.codes.ok):
        print("Toon does not exist or mispelled\n")
        return
    else:
        soup = BeautifulSoup(page.content, "html.parser")
        print(page.status_code)
        gears = soup.find_all("div", class_="media-heading")
        for gear in gears:
            gear_name = gear.find("h5")
            gear_amount = gear.find("p")
            temp_name = gear_name.text
            temp_amount = gear_amount.text
            gear_int_amount = temp_amount.strip("x")
            gear_int_amount = int(gear_int_amount)
            total_gear = total_gear + temp_name + ": " + temp_amount + "\n"
            add_gear_dict(temp_name, gear_int_amount)
    return total_gear

"""
showFullGear
Parameters: none
Purpose: goes through the dictionary and prints out the total amount of gear accumalted
Returns: nothing
"""
def show_full_gear():
    for x, y in gear_dict.items():
        print(x, y)
    return

"""
saveTotalGear
Parameters: none
Purpose: create a file containing the gear amounts as requested by the user
    Users can name the file as they wish
Return: nothing
"""
def save_total_gear():
    safe = 1
    while (safe != 0):
        filename = input("Enter a name for the file: ")
        try:
            f = open(filename, "x")
            safe = 0
        except:
            print("That filename already exists")
            response = input("Enter another name: ")
    for x, y in gear_dict.items():
        f.write(x + ": " + str(y) + "\n")
    f.close()
    return
    


"""
control_center
Parameters: 
        * response, a string that contains the users input
Purpose: Decides which function to enter based on the user's response. If 'quit'
    is typed then the program returns to the main function
Returns: response, the string the user typed
"""
def control_center(response):
    if (response == "0"):
        toon_url = prep_toon_url(response)
        gear_list = get_full_gear(toon_url)
    elif (response == "1"):
        #parse time, send it to the parse function
        toon_url = prep_toon_url(response)
        start_level = input("Please enter the gear level to start at: ")
        end_level = input("Please enter the gear level to end at: ")
        gear_list = get_gear_levels(toon_url, (start_level, end_level))
    elif (response == "total"):
        show_full_gear()
    elif (response == "checkout"):
        save_total_gear()
    response = input("Type 0, 1, total=print, checkout = file, quit: ")
    return response


"""
gohbuilder.py
Purpose: To obtain the total gear required to take a toon to either 
    * Gear level 13 from gear level 1
    * Gear level x to gear level y where (x,y) are specified by the user
The user selects either option then enters the toon's name. The program queries 
https://swgoh.gg and either prints that toon's gear or prints an error message. 
On a successful query, the gear is saved into a dictionary that accumulates the total
gear queried.

After a successful query, the user can type the following
    * Another toon to look up
    * 'total' to show the current gear totals
    * 'checkout' to save the current gear total as a file
    * 'quit' to exit the program
"""
def main():
    global gear_dict
    gear_dict = {}
    print("Welcome to the SWGOH Gear Calculator")
    print("Enter 0 for a full gear search, 1 for a specific range search, or quit to exit the program")
    response = input("Your response: ")
    print(response)
    while (response != "quit"):
        response = control_center(response)
    return

if __name__ == "__main__":
    main()