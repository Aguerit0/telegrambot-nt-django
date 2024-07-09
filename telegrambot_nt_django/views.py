import asyncio
import pandas as pd
import requests
import telegram
from django.shortcuts import render, redirect
from .forms import TelegramBotForm

def home(request):
    return render(request, 'bot_previous.html')

def base(request):
    return render(request, 'base.html')

def bot_start(request):
    return render(request, 'bot_start.html')

def bot_success(request):
    return render(request, 'bot_success.html')

# Store running bot tasks
running_tasks = {}

async def send_message(chat_id, bot, text):
    await bot.send_message(chat_id=chat_id, text=text)

async def bot_logic(chat_id, bot_token):
    bot = telegram.Bot(token=bot_token)
    while True:
        response = requests.get("http://127.0.0.1:5000/alerts/rsi")
        alerts_df = pd.DataFrame(response.json()['alerts'], columns=['symbol', 'time', 'value'])
        alerts_df['value'] = alerts_df['value'].astype(int)

        for index, row in alerts_df.iterrows():
            if row['value'] == 1:
                text = f"BUY {row['symbol']}"
                print(text)
                await send_message(chat_id=chat_id, bot=bot, text=text)

            elif row['value'] == 2:
                text = f"SELL {row['symbol']}"
                print(text)
                await send_message(chat_id=chat_id, bot=bot, text=text)

            elif row['value'] == 0:
                text = f"--"
                print(text)
                await send_message(chat_id=chat_id, bot=bot, text=text)

        await asyncio.sleep(5)

def start_bot(request):
    if request.method == 'POST':
        form = TelegramBotForm(request.POST)
        if form.is_valid():
            chat_id = form.cleaned_data['chat_id']
            bot_token = form.cleaned_data['bot_token']
            request.session['chat_id'] = chat_id
            request.session['bot_token'] = bot_token

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Guarda la tarea en running_tasks
            task = loop.create_task(bot_logic(chat_id, bot_token))
            running_tasks[request.user.id] = task
            
            loop.run_until_complete(task)
            
            print("BOT STARTED - Starting asynchronously...")

            return redirect('bot_success')
        else:
            print("FORM NOT VALID")
    else:
        form = TelegramBotForm()

    print("BOT NOT STARTED")

    return render(request, 'bot_start.html', {'form': form})
