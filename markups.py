from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from config import CHANNELS


def showChannels():
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for channel in CHANNELS:
        btn  = InlineKeyboardButton(text=channel[0], url=channel[2])
        keyboard.insert(btn)
        
    btnDoneSub = InlineKeyboardButton(text='Я ПОДПИСАЛСЯ', callback_data="subchannelsdone")   
    keyboard.insert(btnDoneSub)
    return keyboard