# StatNexus

StatNexus is a user-friendly flask webapp for creating random permutations of one or more Spotify playlists. The live build is hosted at https://statnex.us.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Python 3.10 and a web browser are all that's necessary for a local copy of StatNexus, but I highly suggest using PyCharm or your preferred IDE as well.

### Installing

To create a working copy of StatNexus on your machine, do the following:

1. Clone this repository with git
```git clone https://github.com/optidox/SpotifyShuffler```
2. Install the packages listed in [requirements.txt](requirements.txt)
```pip install -r requirements.txt```
3. Set `FLASK_APP=snow-warning.py`
4. Create a .env file with the following structure:

```
SECRET_KEY=[]
OSU_CLIENT_ID=[]
OSU_CLIENT_SECRET=[]
OSU_REDIRECT_URI=[]
BUNGIE_API_KEY=[]
BUNGIE_CLIENT_ID=[]
BUNGIE_CLIENT_SECRET=[]
RIOT_API_KEY=[]

```

## Running the tests

Once all the above steps are complete, navigate to the project's root directory in a command line and use the following commands to initialize the database and run the application:

```
flask db init
flask db migrate
flask db upgrade
flask run
```

Open your web browser and go to http://127.0.0.1:5000/ to use StatNexus.

## Built With

* [Flask](https://flask.palletsprojects.com/en/2.0.x/) - Web framework; multiple Pallets Projects were used to bridge Flask and other tools
* [SQLAlchemy](https://www.sqlalchemy.org/) - Object Relational Mapper
* [osu! API](https://osu.ppy.sh/wiki/en/osu%21api) - osu! Stats
* [Riot API](https://developer.riotgames.com/) - League of Legends Stats
* [Bungie API](https://github.com/Bungie-net/api/wiki/) - Destiny Stats

## Authors

* **Matthew Sims** - [Optidox](https://github.com/Optidox)
* **Andrew Butcher** - [ACButcher](https://github.com/ACButcher)
* **Aaron Hamburg** - [ahamburg23](https://github.com/ahamburg23)

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

Thank you to the many folks whose code, tutorials, or resources helped to create this project, especially:
* [Miguel Grinberg](https://github.com/miguelgrinberg)
