import time

from bs4 import BeautifulSoup
import requests
import csv

from scrap.domain.Clubs import Club
from scrap.domain.Transfer import Transfer

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
}

START_SEASON = 1992
END_SEASON = 2023
CLUBS_FILE = "clubsMissing.csv"




def read_leagues():
    with open("../data/league_data/all_leagues.txt", "r") as league_file:
        leagues = [league.strip('\n') for league in league_file.readlines()]
    return leagues


def create_table(file, header):
    with open('../data/' + str(file), 'w') as csv_table:
        writer = csv.writer(csv_table)
        writer.writerow(header)


def get_urls(season, leagues):
    err_list = []
    while season <= END_SEASON:
        for lg in leagues:
            url = 'https://www.transfermarkt.com/premier-league/transfers/wettbewerb/' + lg + '/plus/?saison_id=' \
                  + str(season) + '&s_w=&leihe=1&intern=0&intern=1'
            try:
                print("Trying to fetch: " + url)
                html = requests.get(url, headers=headers)
                print("Connection success, status code: " + str(html.status_code))

                scrapped_league_data = scrap_url(html.text, lg)
                try:
                    data_len = len(scrapped_league_data)
                    if data_len > 0:
                        Club.persist_club_data(scrapped_league_data, CLUBS_FILE)
                        print('\n' + str(data_len) + ' clubs were stored')
                    else:
                        print("No data stored")
                except Exception:
                    print("No data stored, caught in exception")

                print('\nFetching next url... \n')

            except requests.exceptions.RequestException as err:
                print("\nAn error occurred with the request: ")
                print(err)
                err_list.append(url)

        season = season + 1
    return err_list


def scrap_url(html_content, league):
    try:
        clubs = []
        soup = BeautifulSoup(html_content, features='lxml')
        header = soup.find('header', class_='data-header')
        transfer_season_tag = soup.find('h1', class_='content-box-headline').text.split()
        transfer_season = transfer_season_tag[1]
        league_name = (header
                       .find('div', class_='data-header__headline-wrapper data-header__headline-wrapper--oswald')
                       .text.strip())
        league_country = header.find('span', class_='data-header__club').text.strip()
        boxes = soup.find_all('h2',
                              class_='content-box-headline content-box-headline--inverted content-box-headline--logo')

        for box in boxes:
            club_name = box.text.strip()
            club = Club(club_name, league_name, league, league_country, transfer_season)
            clubs.append(club)

        return clubs
    except Exception:
        print("HTML is empty of useful data")


def main():
    leagues = read_leagues()
    print(leagues)
    clubs_header = ['Club', 'League', 'League_Sigla', 'Country', 'Season']
    create_table(CLUBS_FILE, clubs_header)

    err_s = get_urls(START_SEASON, leagues)
    no_err = len(err_s)
    print("Execution finished, errors: " + str(no_err))
    if no_err > 0:
        for err in err_s:
            print(err)




if __name__ == "__main__":
    main()
