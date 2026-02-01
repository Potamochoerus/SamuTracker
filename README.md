# SamuTracker
A shiny python interface to track samu-igual-samu

## Load the data
Add the `.csv` logs from BakkesMod pluggin [GameStats](https://bakkesplugins.com/plugin/532) in `data/` folder in the main dir of the repo. No parsing needed, just paste all the files there.

## Track players of interest
Add Account ID and player name in `tracked_players.yml` (player name can be anything, it is only used as display name on the app).
Account ID can be retrieved from EPIC games or STEAM profile.

## Start the app
`shiny run --reload --launch-browser app.py`

## Deploy on shinyapps.io
`rsconnect deploy shiny . --name potamochoerus --title SamuTracker`
