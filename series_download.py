import json
import datetime
import requests
from bs4 import BeautifulSoup
import os
import time


def load_series_json():
    """Loads JSON file with series information"""

    try:
        with open('series_config.json', 'r') as json_series:
           series = json.load(json_series)
        return series
    except FileNotFoundError as ex:
        print("JSON config file not found")


def get_episode_for_today(series_file):
    """Gets the episodes that are released today, based on weekday (Monday == 0, Tuesday == 1...)"""

    today_number = datetime.datetime.today().weekday()
    episodes_to_download = { serie: serie_data for serie, serie_data in series_file['series'].items() if serie_data['release_date'] == today_number}
    return episodes_to_download

def get_episodes_torrent_data(serie):
    """Takes a serie as argument, and return torrent data with endpoint, and seeds"""

    base_url = f"https://1337x.to/sort-search/{serie}/time/desc/1/"
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
    web_source_code = requests.get(base_url, headers={"User-Agent": user_agent})
    time.sleep(1)
    try:
        soup = BeautifulSoup(web_source_code.text, 'html.parser')
        table = soup.find("tbody")
        rows = table.find_all("tr")
    except Exception as ex:
        print("Problem parsing source code for this serie --> " + serie)

    name_torrent = 'Torrent-'
    counter = 0
    torrent_data = {}

    episode_acronym =  _get_last_episode_from_api(serie) #returns S03E21

    if episode_acronym == None:
        print("Not able to find episode_acronym for this serie --> " + str(serie))
        for row in rows:
            links = row.td.find_all('a')
            seeds = row.find(class_="coll-2 seeds").text
            # Torrent data = link, and seeds
            torrent_data[name_torrent+str(counter)] = {"link" : links[1]['href'], "seeds": seeds}
            counter+=1
    else:
        # print(episode_acronym)
        for row in rows:
            links = row.td.find_all('a')
            seeds = row.find(class_="coll-2 seeds").text

            # Torrent data = link, and seeds
            if episode_acronym in links[1]['href']:
                torrent_data[name_torrent+str(counter)] = {"link" : links[1]['href'], "seeds": seeds}
                counter+=1
            else:
                pass

    return torrent_data



def _get_last_episode_from_api(serie):
    """Internal function that will extract the last episode that was released, by calling a public API"""

    headers = {'Content-Type' : 'application/json'} #No need for token
    if "'" in serie:
        serie = serie.replace("'", "-")
    if " " in serie:
        serie = serie.replace(" ", "-")

    response = requests.get(f"https://www.episodate.com/api/show-details?q={serie}")
    if response.status_code == 200:
        serie_data_json = json.loads(response.content.decode('utf-8'))
        try:
            episodes = serie_data_json['tvShow']['episodes']
            # today = datetime.date.today().strftime("%Y-%m-%d") #to be uncomented
            # last_episode = serie_data_json['tvShow']['episodes'][-1]
            for ser_episode in episodes:
                if '2020-03-18' in ser_episode['air_date']: #Change date for 'today' variablee
                    print(ser_episode)

                    if int(ser_episode['season']) < 10:
                        season = 'S0' + str(ser_episode['season'])
                    else:
                        season = 'S' + str(ser_episode['season'])
                    if int(ser_episode['episode']) < 10:
                        episode = 'E0' + str(ser_episode['episode'])
                    else:
                        episode = 'E' + str(ser_episode['episode'])

                    last_episode_acronym = season+episode
                    print(last_episode_acronym)
                    return last_episode_acronym
                else:
                    pass
        except Exception as ex:
            print("Error retrieving serie data from episodate.com api for serie " + serie)
            print(str(ex))
    else:
        return None

def get_magnet_link(link_to_download):
    """Extracts the magnet link from the episode with more seeds"""

    base_url = f"https://1337x.to{link_to_download}"
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
    web_source_code = requests.get(base_url, headers={"User-Agent": user_agent})
    soup = BeautifulSoup(web_source_code.text, 'html.parser')
    magnet_link = soup.select_one("a[href*=magnet]")
    return magnet_link['href']

def open_magnet_link(magnet_link):
    """Opens the magnet link with any torrent client installed"""

    os.startfile(magnet_link)


def main():
    series_file = load_series_json()

    try:
        if len(series_file['series']) == 0:
            print("The series_config.json does not contain any series")
        else:
            episodes_to_download = get_episode_for_today(series_file)
            # print(episodes_to_download)
    except KeyError as ex:
        print("Error reading the JSON -->" + str(ex))

    try:
        if len(episodes_to_download) == 0:
            print("No episodes for today")
        else:
            for serie, data in episodes_to_download.items():
                
                episodes_torrent_data = get_episodes_torrent_data(serie)
                print("Maximum torrent with seeds is --- ")
                max_seeds = max(int(d['seeds']) for d in episodes_torrent_data.values()) #Obtain the most seeded link
                list_torrent_data = episodes_torrent_data.values()
                
                link_to_download = None
                for torrent in list_torrent_data:
                    if str(torrent['seeds']) == str(max_seeds):
                        link_to_download = torrent['link']
                    else:
                        pass
                
                magnet_link = get_magnet_link(link_to_download)
                print("Serie is: " + serie)
                print("Found episode with this number of seeds " + str(max_seeds))
                print("Magnet link is: " + magnet_link)
                open_magnet_link(magnet_link)

    
    except Exception as ex:
        print("Unknown error ocurred --> " + str(ex))


if __name__ == "__main__":
    main()