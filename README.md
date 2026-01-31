# SamuTracker
A shiny python interface to track samu-igual-samu

## Load the data
Add the `.csv` logs from BakkesMod pluggin [GameStats](https://bakkesplugins.com/plugin/532) in `data/` folder in the main dir of the repo. No parsing needed, just paste all the files there.

## Track players of interest
Add Account ID and player name (player name is can be anything, only used as display name on the app.) in `tracked_players.yml`.
Account ID can be retrieve from EPIC games or STEAM profile of the players.

## Start the app
`shiny run --reload --launch-browser app.py`

## Deploy on shinyapps.io
`rsconnect deploy shiny . --name potamochoerus --title SamuTracker`
