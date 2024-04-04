import telebot as tl
from g4f.client import Client
from g4f.Provider import Liaobots, You, Gemini, ChatgptNext, ChatForAi, Vercel, Theb, ChatgptAi, Bing, ChatgptX, Chatgpt4Online, GptTalkRu, Raycast, ChatBase, Poe, FreeGpt, FlowGpt

token = 'your_token'

context = {}
commands = ['/start', '/ask', '/reset']

bot = tl.TeleBot(token)
print('bot polling')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,'Вопрос: /ask')

@bot.message_handler(commands=['ask'])
def ask_message(message):
    bot.send_message(message.chat.id, 'Введите ваш вопрос или сообщение:')
    bot.register_next_step_handler(message, process_ask_command)

def send_chunks(chat_id, text):
    chunks = [text[i:i + 4096] for i in range(0, len(text), 4096)]
    for chunk in chunks:
        bot.send_message(chat_id, chunk, parse_mode='Markdown')

def process_ask_command(message):
    user_input = message.text
    search = bot.send_message(message.chat.id, 'Идет генерация...')
    
    while True:
        client = Client(
            provider=ChatgptNext,
            image_provider=Gemini
        )
        try:
            if message.chat.id not in context.keys():
                response = client.chat.completions.create(
                    model="gpt-3.5",
                    messages=[{"role": "user", "content": user_input}],
                    auth = True,
                )
                generated_text = response.choices[0].message.content
                bot.delete_message(message.chat.id, search.message_id)
                context[message.chat.id] = [{"role": "user", "content": user_input}, {"role": "assistant", "content": generated_text}]
                send_chunks(message.chat.id, generated_text)
                bot.register_next_step_handler(message, process_user_response)  
                print(context)
                print()
                break
            else:
                context[message.chat.id].append({"role": "user", "content": user_input})
                response = client.chat.completions.create(
                    model="gpt-3.5",
                    messages=context[message.chat.id],
                )
                bot.send_chat_action(message.chat.id, "typing", 600)
                generated_text = response.choices[0].message.content
                bot.delete_message(message.chat.id, search.message_id)
                context[message.chat.id].append({"role": "assistant", "content": generated_text})
                send_chunks(message.chat.id, generated_text)
                bot.register_next_step_handler(message, process_user_response)  
                print(context)
                print()
                break
        except Exception as e:
            print(e)
            continue

def process_user_response(message):
    user_input = message.text
    search = bot.send_message(message.chat.id, 'Идет генерация...')
    while True:
        client = Client(
            provider=Liaobots,
            image_provider=Gemini
        )
        try:
            context[message.chat.id].append({"role": "user", "content": user_input})
            response = client.chat.completions.create(
                model="gpt-3.5",
                messages=context[message.chat.id],
            )
            bot.send_chat_action(message.chat.id, "typing", 600)
            generated_text = response.choices[0].message.content
            bot.delete_message(message.chat.id, search.message_id)
            send_chunks(message.chat.id, generated_text)
            context[message.chat.id].append({"role": "assistant", "content": generated_text})
            bot.register_next_step_handler(message, process_user_response)
            print(context)
            print()  
        except Exception as e:
            print(e)
            continue
    

bot.polling()