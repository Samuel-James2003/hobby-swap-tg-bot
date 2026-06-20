from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
import os
import requests
from debug import log_event

BOT_TOKEN = os.getenv('BOT_TOKEN')
SPOON_TOKEN = os.getenv('SPOON_TOKEN')
ADMINSFILE = os.path.curdir + "/files/admins.txt"
EXHAUSTED_USERSFILE = os.path.curdir + "/files/exhasteduser.txt"
DEBUGFILE = os.path.curdir + "/files/debug.log"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # When speaking directly to the bot saying /start
    user = update.effective_user.id
    welcome_message = """🍳 Welcome to Curly's Cuisine! 🍳
    Feeling hungry but have no idea what to cook? Fear not! Curly’s Cuisine is here to rescue your taste buds with random (and sometimes questionable) recipes!
    Just hit a button, and BAM! A new dish to try—whether it's a five-star meal or a food experiment gone wild, it's always an adventure!
    Ready to embrace culinary chaos? Let’s get cooking! 😈🧙‍♂️😁"""
    
    await context.bot.send_message(chat_id=user, text=welcome_message)
    
    return

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # When speaking directly to the bot saying /help
    help_text = (
        "🍽 *Curly's Cuisine Help Menu* 🍽\n\n"
        "Feeling hungry? Let me help you cook up something delicious\! Here’s how you can use me:\n\n"
        "🔹 */recipe* \- Get a random recipe with ingredients and instructions\.\n"
        "🔹 *Send a message* \- If it’s not a command, I’ll kindly remind you to use /recipe 😆\n\n"
        "That’s it\! Simple, right\? Now go forth and unleash your inner chef\! 👨‍🍳🔥"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode="MarkdownV2")
    return


def convert_html_list_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    # Check if the text contains lists
    has_lists = bool(soup.find("ol") or soup.find("ul"))

    message = ""

    # Process ordered lists (<ol>)
    for ol in soup.find_all("ol"):
        items = [f"{i+1}. {li.get_text(strip=True)}" for i, li in enumerate(ol.find_all("li"))]
        message += "\n".join(items) + "\n"

    # Process unordered lists (<ul>)
    for ul in soup.find_all("ul"):
        items = [f"- {li.get_text(strip=True)}" for li in ul.find_all("li")]
        message += "\n".join(items) + "\n"
        
    # If no lists were found, return the original text
    return message.strip() if has_lists else html.strip()

async def recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # When a message is received directly
    text_response, ingredients_response, instruction_response, image_url = get_random_recipes(SPOON_TOKEN, number=1)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_response)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ingredients:")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ingredients_response)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Instructions:")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=instruction_response)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enjoy your meal!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.business_message is not None and update.business_message.text is not None:
        # Get the business message
        if update.business_message.from_user.id == update.business_message.chat_id:
            #the user is not the sender
            if verify_permissions(update.business_message.chat_id):
                #the user has not used the bot yet
                text_response, ingredients_response, instruction_response, image_url = get_random_recipes(SPOON_TOKEN, number=1)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text_response, business_connection_id=update.business_message.business_connection_id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Ingredients:", business_connection_id=update.business_message.business_connection_id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=ingredients_response, business_connection_id=update.business_message.business_connection_id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Instructions:", business_connection_id=update.business_message.business_connection_id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=instruction_response, business_connection_id=update.business_message.business_connection_id)
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url, business_connection_id=update.business_message.business_connection_id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Enjoy your meal!", business_connection_id=update.business_message.business_connection_id)
                AddExhastedUser(update.business_message.chat_id)
            return
        else:
            #the user is the sender
            return
    if update.message is not None and update.message.text is not None:
        # A direct message to the bot 
        response = "Ah, a wild chef appears! 🧑‍🍳 But wait… you're missing the secret ingredient—the right command! Try typing /recipe, and I’ll whip up something delicious (or at least edible) for you! 🍕🔥"
        response += f"\nOh by the way, here's a little trivia \n{get_food_trivia(SPOON_TOKEN)}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        return
    return

async def error_handler(update: Update, context: CallbackContext) -> None:
    # Get the error message
    error_message = str(context.error)
    
    # Inform the user
    if update and update.effective_message:
        await update.effective_message.reply_text(f"Oops! Something went wrong. Please try again later.")

    # Optionally, log the error for debugging purposes
    log_event(f"Error occurred: {error_message}", level="CRITICAL", exc_info=True)

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_message.from_user.id) in GetAdmins():
        text = read_text_from_file(DEBUGFILE)
        if text == '':
            text = "No messages in debug file"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry can't help you with that.")
    return 

def get_random_recipes(api_key: str, number: int = 5, include_tags: str = "") -> tuple:
    """
    Fetches random recipes from the Spoonacular API.

    :param api_key: API key for authenticating with the Spoonacular API.
    :param number: Number of random recipes to fetch.
    :param include_tags: Tags to include in the recipe search.
    :return: A tuple containing the text response, ingredients response, instruction response, and image URL.
    """
    endpoint = "https://api.spoonacular.com/recipes/random"
    params = {
        "apiKey": api_key,
        "number": number,
        "include-tags": include_tags
    }
    try: 
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            data = response.json()  # Extract JSON response
            recipe = data.get("recipes", [])[0] 
            
            recipe_title = recipe['title']
            cooking_time = recipe['readyInMinutes']
            servings = recipe['servings']
            recipe_url = recipe['sourceUrl']
            image_url = recipe['image']
            instructions = recipe['instructions']
            ingredients = recipe['extendedIngredients']
            ingredients_response = ""
            for ingredient in ingredients:
                amount = ingredient['amount']
                unit = ingredient['unit']
                name = ingredient['name']
                ingredients_response += f"{amount} {unit} {name}\n"
            
            text_response = f"Title: {recipe_title}\nCooking Time: {cooking_time} minutes\nServings: {servings}\nRecipe URL: {recipe_url}"
            instruction_response = convert_html_list_to_text(instructions)
            return text_response, ingredients_response, instruction_response, image_url
        else:
            log_event(f"Request failed with status {response.status_code} with message {response.text}", level="ERROR", exc_info=True)
            return "Oops something went wrong! Please try again later."
    except Exception as e:
        log_event(f"An error occurred: {e}", level="ERROR",exc_info=True)
        return "An error occurred while fetching recipes. Please try again later."

def get_food_trivia(api_key: str):
    """
    Fetches random food trivia from the Spoonacular API.
    
    :param api_key: API key for authenticating with the Spoonacular API.
    :param number: Number of random food trivia to fetch.
    :param include_tags: Tags to include in the trivia search.
    :return: Food trivia.
    """
    
    endpoint = "https://api.spoonacular.com/food/trivia/random"
    params = {
        "apiKey": api_key
    }
    try: 
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            data = response.json()
            trivia = data.get("text", "No trivia found.")
            return trivia
    except Exception as e:
        log_event(f"An error occurred: {e}", level="ERROR",exc_info=True)
        return "An error occurred while fetching food trivia. Please try again later."


def isAnInt(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def read_text_from_file(file_path:str):
    """
    Reads text from a file.
    
    :param file_path: Path to the file to read.
    :return: The text read from the file.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:

        with open(file_path, 'w', encoding='utf-8') as file:
            pass
        return ""
    except Exception as e:
        log_event(f"An error occurred: {e}")
        return ""

def read_list_from_file(file_path: str):
    """
    Reads a list of items from a file. Each line in the file is treated as one item in the list.
    
    :param file_path: Path to the file to read.
    :return: A list of items read from the file.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            # Strip whitespace/newlines and return as a list
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        # If the file doesn't exist, create it and return an empty list
        with open(file_path, 'a', encoding='utf-8') as file:
            pass
        return []
    except Exception as e:
        log_event(f"An error occurred: {e}")
        return []

def write_list_to_file(file_path:str, items:list):
    """
    Writes a list of items to a file. Each item in the list is written on a new line.
    
    :param file_path: Path to the file to write.
    :param items: List of items to write to the file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for item in items:
                file.write(f"{item}\n")
        file.close()
        return True
    except FileNotFoundError:
        with open(file_path, 'a', encoding='utf-8') as file:
            for item in items:
                file.write(f"{item}\n")
        file.close()
        return True
    except Exception as e:
        log_event(f"An error occurred: {e}", level="ERROR", exc_info=True)
        return False

def verify_permissions(ID:str):
    """
    Check if the user has already used the bot.
    """
    ID = str(ID)
    return ID not in GetExhastedUser()

def GetExhastedUser():
    return read_list_from_file(os.path.curdir + "/files/exhasteduser.txt")
def GetAdmins():
    return read_list_from_file(ADMINSFILE)

def AddExhastedUser(ID:str):
    """
    Add a user to the list of users who have already used the bot.
    
    :param ID: User ID to add to the list.
    """
    ID = str(ID)
    users = GetExhastedUser()
    users.append(ID)
    write_list_to_file(os.path.curdir + "/files/exhasteduser.txt", users)
def main():
    # Create the application with your bot's token
    app = Application.builder().token(BOT_TOKEN).build()
    # Add a CommandHandler for the /start command
    app.add_handler(CommandHandler("start", start))
    # Add a CommandHandler for the /recipe command
    app.add_handler(CommandHandler("recipe", recipe))
    # Add a CommandHandler for the /help command
    app.add_handler(CommandHandler("help", help))
    # Add a CommandHandler for the /debug command
    app.add_handler(CommandHandler("debug", debug))
        
    app.add_error_handler(error_handler)
        
    # Add a MessageHandler for handling any  message
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    
    # Run the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
