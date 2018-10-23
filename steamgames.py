from requests import get
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error:
        print("Database not found")
 
    return None

def getSteamKey():
    '''
    Returns the Steam Web API Key stored in a database.
    
    '''
    conn = create_connection('config.db')
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT Key FROM api_keys WHERE Service = 'Steam';")
        key = cur.fetchone()[0]
        return key

def getSteamId(steamUserName):
    '''
    Uses the Steam username give to find the User's Steam ID.
    
    Args-
        steamUserName: The User's Steam username.
    '''
    id_parameters = {'key' : getSteamKey(), 'vanityurl' : steamUserName}
    steamId = get("https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/", 
                  params=id_parameters)
        
    if list(steamId.json()['response'].values())[1] == 'No match':
       return False
    else:
       steamId = list(steamId.json()['response'].values())[0]
    
    return steamId

def callSteamAPI(steamUserName):
    '''
    Calls the Steam API.
    
    Args-
        steamUserName: The User's Steam username.
    '''
    steamIdResults = getSteamId(steamUserName)
    
    if steamIdResults:
        api_parameters = {'key' : getSteamKey(), 'steamid' : steamIdResults, 
                          'format' : 'json'}
        steamApi = get("http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?",
               params=api_parameters)
        return steamApi
    else:
        print("\nUsername not found.")
        return False

def getGameInfo(steamUserName):
    '''
    Returns the games the User has played within the last two weeks.
    
    Args-
        steamUserName: The User's Steam username.
    '''
    gamesPlayed = callSteamAPI(steamUserName)
    
    if gamesPlayed:
        lastGamesPlayed = gamesPlayed.json()
        gameInfo = lastGamesPlayed['response']['games']
        return(d['name'] for d in gameInfo)
    else:
        return False
    
def main():
    '''
    Allows the User to enter their Steam username. Also, prints out the
    games the User has played within the last two weeks.
    '''
    steamUserName = input("Please enter your Steam Username: ")
    listOfGames = getGameInfo(steamUserName)
    if listOfGames:
        listOfGames = "\n".join(list(listOfGames))
        print("\nHere are the games you played in the last two weeks: \n")
        print(listOfGames)
            
if __name__ == "__main__":
    main()