import logging

from telegram import Update, User
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackContext

logger = logging.getLogger(__name__)

MSG = (
    "Would you like to make PR for this?\n"
    "You can start by forking me at https://github.com/vldc-hq/vldc-bot\n"
    "💪😎"
)


def add_pr(upd: Updater, handlers_group: int):
    logger.info("registering PR handler")
    dp: Dispatcher = upd.dispatcher
    dp.add_handler(CommandHandler("pr", _pr, run_async=True), handlers_group)


def _pr(update: Update, context: CallbackContext):
    user: User = (
        update.message.reply_to_message.from_user
        if update.message.reply_to_message
        else None
    )
    msg = f"@{user.username} " + MSG if user else MSG
    context.bot.send_message(update.effective_chat.id, msg)
