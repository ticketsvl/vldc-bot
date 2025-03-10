import logging
from datetime import timedelta

from telegram import Update, User
from telegram.ext import Updater, Dispatcher, MessageHandler, Filters, CallbackContext

from mode import Mode
from skills.mute import mute_user_for_time
from utils.voice_recognition import get_text_from_speech

logger = logging.getLogger(__name__)

mode = Mode(mode_name="nastya_mode", default=True)

MAX_VOICE_DURATION = 60  # seconds
VOICE_USER_MUTE_DURATION = timedelta(minutes=10)
EXCLUDING = ["@ravino_doul"]


@mode.add
def add_nastya_mode(upd: Updater, handlers_group: int):
    logger.info("registering nastya handlers")
    dp: Dispatcher = upd.dispatcher

    dp.add_handler(
        MessageHandler(
            Filters.voice & ~Filters.status_update, handle_voice, run_async=True
        ),
        handlers_group,
    )


def handle_voice(update: Update, context: CallbackContext):
    user: User = update.effective_user
    chat_id = update.effective_chat.id
    message = update.message

    if user.name in EXCLUDING:
        return

    voice = message.voice or message.audio
    duration = voice.duration

    if duration > MAX_VOICE_DURATION:
        message_text = f"🤫🤫🤫 @{user.username}! Слишком много наговорил..."
    else:
        file_id = voice.file_id
        logger.info("%s sent voice message!", user.name)
        default_message = f"@{user.username} промямлил что-то невразумительное..."
        recognized_text = None

        try:
            recognized_text = get_text_from_speech(file_id)
        except (AttributeError, ValueError, RuntimeError) as err:
            logger.exception("failed to recognize speech: %s", err)

        if recognized_text is None:
            message_text = default_message
        else:
            message_text = (
                f"🤫🤫🤫 Групповой чат – не место для войсов, @{user.username}!"
                f"\n@{user.username} пытался сказать: {recognized_text}"
            )

    context.bot.send_message(chat_id=chat_id, text=message_text)

    try:
        mute_user_for_time(update, context, user, VOICE_USER_MUTE_DURATION)
    finally:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
