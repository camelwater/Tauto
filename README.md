# Tournament-Generator

TM Bot is a general-purpose Discord Bot for managing tournaments of different formats: single-elimination, double-elimination, Swiss, Round-Robin, and Champions League. TM BOT ameliorates tournament management by automating registrations and match generations, with support for seeded match-making.

## Bot Setup

In order to set up and open a tournament, you must first create a Google Spreadsheet and share the spreadsheet with TM BOT's Google service client (`tournament-generator@tournament-generator-332215.iam.gserviceaccount.com`) with **edit** access.

After you've created the spreadsheet and added TM BOT as an editor, you will need the spreadsheet's ID, which can be found in the spreadsheet's URL. For example, given a spreadsheet URL https://docs.google.com/spreadsheets/d/5GQbuk86jqBbBMeLvj1c4VVsIqNdtGc-quWF3Hx6ImLI/edit#gid=0, the spreadsheet ID would be `5GQbuk86jqBbBMeLvj1c4VVsIqNdtGc-quWF3Hx6ImLI`. The spreadsheet ID is always the long string of characters after the `/d/`.

## Full Documentation

To see all of TM BOT's commands, their descriptions, and examples, see the [documentation](https://www.github.com/camelwater/tournament-generator/wiki).
