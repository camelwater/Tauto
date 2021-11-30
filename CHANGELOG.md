# Change Log
A history of all of TM Bot's notable changes over time.

## 0.4.0 - IN PROGRESS
Complete rework of GenChannel and Generator logic, with new formats (Double-Elimination and Champions League) added.

### Added
- Two new formats: Double-Elimination and Champions League
- New parameter requirements for Champions League tournaments

### Changed
- Logic between Generation cog commands and `GenChannel`s redone, due to new formats added.
- Generation optional parameters changed from `open` and `random` to `seeding` and `bracket`, with server settings updated to reflect that

## 0.3.2 - 11/28/21
Various bug fixes to v0.3.0.

### Fixed
- Fixed `open`, `advance`, `unadvance`, `close`, and `finish` bugs

### Changed
- Reformatted several return messages and strings.
- Bot mention serves as a `help` command

### Changed
- Updated required command permissions from `ADMINISTRATOR` to `MANAGE_GUILD`

## 0.3.1 - 11/20/21
AWS server deployment.

### Fixed
- AWS CodeDeploy issues
- YAML files

## 0.3.0 - 11/18/21
Bot now has end-to-end functionality.

### Added
- `status` command: view current round's status
- `results` command: view round's results - who advanced and who lost
- All round results are saved to Google Sheets.
- New server settings

## 0.2.0 - 11/10/21
Building upon v0.1.0 by filling out its featureset as a Discord Bot.

### Added
- Ability to seed players
- Preliminary Round for tournaments that need it
- Discord.py integration
- Ability to register players via Discord
- Basic command set, such as `open`, `close`, and `start`
- Server settings and prefixes customization
- Google Sheets integration for player registrations

## 0.1.0 - 11/4/21
Initial commit.

### Added
- Basic generation completed
- Players can be advanced
- Rounds can be incremented