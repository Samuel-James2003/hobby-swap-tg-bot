# Curly's Cuisine Bot

Curly's Cuisine is a fun and interactive Telegram bot that helps users discover random recipes, complete with ingredients, instructions, and images. The bot integrates with the Spoonacular API to fetch recipes and food trivia, ensuring an engaging and delicious experience for all users.

## Features
- **/start**: Welcome message introducing the bot.
- **/help**: Provides a help menu with instructions on how to use the bot.
- **/recipe**: Fetches a random recipe, displaying the title, ingredients, instructions, and an image.
- **Handles Messages**: If a user sends a message without using a command, the bot will guide them to use /recipe.
- **Error Handling**: Logs errors and notifies users if something goes wrong.
- **Admin Debugging**: Allows admins to view debug messages stored in a log file.
- **Food Trivia**: Provides random food-related trivia for added entertainment.

## Getting Started
### Run initialization script (Recommended)
#### For Linux
```bash
./init.sh
```
#### For Windows
```bash
./init.ps1
```
### Or run the scrips manually 
#### Creating a virtual environment
```sh
python -m venv myvenv 
.\myvenv\Scripts\Activate.ps1 
```
#### Install the packages
```sh 
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Variables
To run the bot, set up the following environment variables:
- `BOT_TOKEN`: Your Telegram bot token.
- `SPOON_TOKEN`: API key for the Spoonacular API.

## File Structure
- `/files/admins.txt`: List of bot admins.
- `/files/exhasteduser.txt`: Tracks users who have already used the bot.
- `/files/debug.txt`: Stores debug logs.

## How to Run
1. Set up the required environment variables.
2. Run the bot using:
   ```bash
   python bot.py
   ```
3. The bot will start polling and be ready for interactions.

## API Integration
This bot fetches recipes from the Spoonacular API using:
- **Random Recipe Endpoint**: `https://api.spoonacular.com/recipes/random`
- **Food Trivia Endpoint**: `https://api.spoonacular.com/food/trivia/random`

## Error Handling
The bot includes logging to capture critical errors and provide feedback to users. Logs are stored in `debug.txt` for reference.

## Contributing
If you'd like to contribute, feel free to submit a pull request or report issues!

## License
MIT License.