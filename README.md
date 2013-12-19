nbaDB
=====

for now, a simple python script for d/l nba boxscore data to a local mongoDB instance.
all data is taken from Erik Berg's [xmlstats](https://erikberg.com/api)

## Installation


### all you need is:

- Love
- Python 2.7
- MongoDB (a running instance, to install mongo as a service, click [here](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-windows/#mongodb-as-a-windows-service))

## Usage


run `nba.py` with a specific year in YYYY format to insert data from all the games during that year. for example:
`python nba.py 2013` will retrieve all the games from the year 2013. For each game, and for each player, a document will be stored in the `games` collection that will hold the following details:

```
 {
            "last_name": "Young",
            "first_name": "Thaddeus",
            "display_name": "Thaddeus Young",
            "position": "PF",
            "minutes": 32,
            "points": 14,
            "assists": 2,
            "turnovers": 3,
            "steals": 1,
            "blocks": 0,
            "rebounds": 4,
            "field_goals_attempted": 13,
            "field_goals_made": 6,
            "three_point_field_goals_attempted": 1,
            "three_point_field_goals_made": 0,
            "free_throws_attempted": 4,
            "free_throws_made": 2,
            "defensive_rebounds": 3,
            "offensive_rebounds": 1,
            "personal_fouls": 1,
            "team_abbreviation": "PHI",
            "is_starter": true,
            "field_goal_percentage": 0.462,
            "three_point_percentage": 0,
            "free_throw_percentage": 0.5,
            "field_goal_percentage_string": "46.2",
            "three_point_field_goal_percentage_string": "0.0",
            "free_throw_percentage_string": "50.0"
        }
```
The document will also hold several "general parameters" for the specific boxscore:
- event_id (for exmaple: `20131029-orlando-magic-at-indiana-pacers`)
- type (regular/playoff)
- date 
- season (in YYYY-YYYY format, for example: `2012-2013')
- home_team (`washington-wizards`)
- away_team

To get a local copy of a collection from the DB, run `mongo2csv.py`. It loads the configuration from `cfg.py`, reads a collection and makes a table from it, then writes that table to CSV file with the same name as the collection. This can then be read in `R` or with `pandas` to do some statistics locally.



## Goals


- Get Ofer to another NBA game
- Hopefully Yoav too
- Grantland, here we come!






