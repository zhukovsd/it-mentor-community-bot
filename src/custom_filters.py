from typing import Optional, Union

from telegram import Update
from telegram.ext._utils.types import FilterDataDict
from telegram.ext.filters import UpdateFilter


class EditedMessage(UpdateFilter):
    def filter(self, update: Update) -> Optional[Union[bool, FilterDataDict]]:
        return update.edited_message is not None


class MessageReaction(UpdateFilter):
    def filter(self, update: Update) -> Optional[Union[bool, FilterDataDict]]:
        return update.message_reaction is not None


EDITED_MESSAGE = EditedMessage(name="custom_filters.EDITED_MESSAGE")
MESSAGE_REACTION = MessageReaction(name="custom_filters.MESSAGE_REACTION")