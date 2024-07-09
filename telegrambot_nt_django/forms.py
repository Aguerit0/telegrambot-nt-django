# apps/telegrambot/forms.py
from django import forms

class TelegramBotForm(forms.Form):
    chat_id = forms.CharField(max_length=100)
    bot_token = forms.CharField(max_length=100)
