from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
import os
import spoonacular

BOT_TOKEN = os.getenv('BOT_TOKEN')
SPOON_TOKEN = os.getenv('SPOON_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # When speaking directly to the bot saying /start
    return

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # When speaking directly to the bot saying /help
    return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # When a message is received directly and indirectly
    configuration = spoonacular.Configuration(
    host = "https://api.spoonacular.com"
    )
    configuration.api_key['apiKeyScheme'] =  SPOON_TOKEN
    
    if update.business_message is not None and update.business_message.text is not None:
        # Get the business message
        if update.business_message.from_user.id == update.business_message.chat_id:
            #the user is not the sender
            return
        else:
            #the user is the sender
            return
    if update.message is not None and update.message.text is not None:
        # A direct message to the bot 
        return
    return

async def error_handler(update: Update, context: CallbackContext) -> None:
    # Inform the user
    if update and update.effective_message:
        await update.effective_message.reply_text("Oops! Something went wrong.")
    return

def get_random_recipes(configuration):
    with spoonacular.ApiClient(configuration) as api_client:
    # Create an instance of the API class
        api_instance = spoonacular.RecipesApi(api_client)
        include_nutrition = False # bool | Include nutrition data in the recipe information. Nutrition data is per serving. If you want the nutrition data for the entire recipe, just multiply by the number of servings. (optional) (default to False)
        include_tags = 'vegetarian,gluten' # str | A comma-separated list of tags that the random recipe(s) must adhere to. (optional)
        exclude_tags = 'meat,dairy' # str | A comma-separated list of tags that the random recipe(s) must not adhere to. (optional)
        number = 10 # int | The maximum number of items to return (between 1 and 100). Defaults to 10. (optional) (default to 10)

        try:
            # Get Random Recipes
            api_response = api_instance.get_random_recipes(include_nutrition=include_nutrition, include_tags=include_tags, exclude_tags=exclude_tags, number=number)
            return api_response
        except Exception as e:
            return "Exception when calling RecipesApi->get_random_recipes: %s\n" % e

def get_food_trivia(configuration):
    with spoonacular.ApiClient(configuration) as api_client:
    # Create an instance of the API class
        api_instance = spoonacular.MiscApi(api_client)

        try:
            # Random Food Trivia
            api_response = api_instance.get_random_food_trivia()
            return api_response
        except Exception as e:
            return "Exception when calling MiscApi->get_random_food_trivia: %s\n" % e

def get_food_jokes(configuration):
    with spoonacular.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = spoonacular.MiscApi(api_client)

        try:
            # Random Food Joke
            api_response = api_instance.get_a_random_food_joke()
            return api_response
        except Exception as e:
            return "Exception when calling MiscApi->get_a_random_food_joke: %s\n" % e

def main():
    # Create the application with your bot's token
    app = Application.builder().token(BOT_TOKEN).build()
    # Add a CommandHandler for the /start command
    app.add_handler(CommandHandler("start", start))
        
    app.add_error_handler(error_handler)
        
    # Add a MessageHandler for handling any  message
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
