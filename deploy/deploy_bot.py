#
# These are the libraries needed by this application
#!pip install scikit-learn
#!pip install nltk
#!pip install json
#
import random
import nltk
import json
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression, RidgeClassifier, SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

#
# load the file into sample_data on the left hand pane
#
with open('/usr/src/app/AIML_BOT.json', 'r') as f:
  BOT_CONFIG = json.load(f)

#with open('/content/test.txt', 'w') as f:
#   f.write('test text')

#
# clean the text roman or cyrillic alphabet
#
def clean(text):
  return ''.join([simbol for simbol in text.lower() if simbol in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz '])

#
# use nltk to suggest the word match (close to words)
#
def match(example, text):
  return nltk.edit_distance(clean(text), clean(example)) / len(example) < BOT_CONFIG['threshold'] if len(example) > 0 else False
  # return nltk.edit_distance(clean(text), clean(example)) / len(example) < BOT_CONFIG['threshold']

#def get_intent(text):
#  for intent, value in BOT_CONFIG['intents'].items():
#    print("intent was %s" % intent)
#    if 'examples' in value and not intent.find(text) == -1:
#        for example in value['examples']:
#          if match(example, text):
#              return intent
#          else:
#              return 'not found in examples'
#    elif 'inc_examples' in value and not intent.find(text):
#        for example in value['inc_examples']:
#            if match(example, text):
#              return intent
#            else:
#              return 'not known from inc_examples'        
#  return 'no config found'

# clean the text up (remove punctuation) and convert to lower case 
#
def cleaner(text): # clean the text up
    cleaned_text = ''
    for ch in text.lower():
        if ch in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz ':
            cleaned_text = cleaned_text + ch
    return cleaned_text

def get_intent(text):
  for intent in BOT_CONFIG['intents'].keys():
    for example in BOT_CONFIG['intents'][intent]['examples']:
      cleaned_example = clean(example)
      cleaned_text = clean(text)
      if nltk.edit_distance(cleaned_example, cleaned_text) / max(len(cleaned_example), len(cleaned_text), 1) < BOT_CONFIG['threshold']:
        return intent
  #return 'unknown_intent'

#X = []
#y = []

#for intent, value in BOT_CONFIG['intents'].items():
#    if 'inc_examples' in value:
#      examples = list(set([example.lower() for example in value['inc_examples']]))
#    else:
#      examples = list(set([example.lower() for example in value['examples']]))
#    X += examples
#    y += [intent] * len(examples)

X = []
y = []
for intent in BOT_CONFIG['intents']:
  for example in BOT_CONFIG['intents'][intent]['examples']:
    X.append(example)
    y.append(intent)

#X = []
#y = []
#for intent in BOT_CONFIG['intents']:
#     if 'examples' in BOT_CONFIG['intents'][intent]:
#          X += BOT_CONFIG['intents'][intent]['examples']
#          y += [intent for i in range(len(BOT_CONFIG['intents'][intent]['examples']))]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

#
# most models use this TfidVectoriser
#
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1,3))                #CountVectorizer(analyzer='char', ngram_range=(1,3), preprocessor=clean)
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

#
# count vectoriser is used by SGD classification
#
vectorizer2 = CountVectorizer(analyzer='char', preprocessor=cleaner, ngram_range=(1,3), stop_words=['а', 'и'])
vectorizer2.fit(X)
X_vect3 = vectorizer2.transform(X)
X_train_vect3, X_test_vect3, y_train3, y_test3 = train_test_split(X_vect3, y, test_size=0.3)
#sgd = SGDClassifier()                                                           # SGD model
#sgd.fit(X_vect3, y)                                                             # Train the model
#sgd.score(X_vect3, y)                                                           # check score

# ======================================================================================== 
# different methods gave various answers so we collated the answers and selected variants
# ========================================================================================

#
# use ridge classifier and TfidVectoriser
#
clf = RidgeClassifier()                                                         # model examples RandomForestClassifier() #RidgeClassifier() #LogisticRegression()
clf.fit(X_train_vectorized, y_train)
clf.score(X_train_vectorized, y_train), clf.score(X_test_vectorized, y_test)

#
# use random forrest classifier and TfidVectoriser
#
clf2 = RandomForestClassifier()                                                 
clf2.fit(X_train_vectorized, y_train)
clf2.score(X_train_vectorized, y_train), clf2.score(X_test_vectorized, y_test)

#
# this is an alternative method using random forrest with a differnt test/train split but still using the TfidVectoriser
#
vectorizer2 = TfidfVectorizer()
X_transformed2 = vectorizer.fit_transform(X)

X_train2, X_test2, y_train2, y_test2 = train_test_split(X_transformed2, y, test_size=0.2, random_state=42)

classifier = RandomForestClassifier()
classifier.fit(X_train2, y_train2)

#
# SGDClassifier with CountVectoriser
#
sgd = SGDClassifier()                                                           # stochastic gradient descent
sgd.fit(X_vect3, y)
sgd.score(X_vect3, y)                                                           # We look at the quality of the classification

#
# test the bot reader and nltk here
#
question = input()
answer = get_intent(question)
print(answer)

# get intent using ridge classifier model1
#
def get_intent_by_rc_model1(text):
  vectorized_text = vectorizer.transform([text])
  return clf.predict(vectorized_text)[0]
  
# get intent using random forrest model 1
#
def get_intent_by_rf_model1(text):
  vectorized_text = vectorizer.transform([text])
  return clf2.predict(vectorized_text)[0]
  
# get intent using random forrest model 2
#
def get_intent_by_rf_model2(text):
  return classifier.predict(vectorizer.transform([text]))[0]

# get intent using sgd classification and countVectoriser
#
def get_intent_by_sgd_model1(text): # Функция определяющая интент текста с помощью ML-модели
     return sgd.predict(vectorizer.transform([text]))[0]

#
# use the ridge classifier model 1
#
def bot_rc_ml1(text):

  intent = get_intent(text)                                                     # 1. try to understand the intention by comparison according to Levinstein

  if intent is None:
    intent = get_intent_by_rc_model1(text)                                      # use ridge classifier

  if 'inc_response' in BOT_CONFIG['intents'][intent]:
      return random.choice(BOT_CONFIG['intents'][intent]['inc_response']) 
  else: 
      return random.choice(BOT_CONFIG['intents'][intent]['responses'])

#
# use the random forrest model 1
#
def bot_rf_ml1(text):

  intent = get_intent(text)                                                     # 1. try to understand the intention by comparison according to Levinstein

  if intent is None:
    intent = get_intent_by_rf_model1(text)                                      # 2. use random forrest 1

  if 'inc_response' in BOT_CONFIG['intents'][intent]:
      return random.choice(BOT_CONFIG['intents'][intent]['inc_response']) 
  else: 
      return random.choice(BOT_CONFIG['intents'][intent]['responses'])

#
# use the random forrest model 2
#
def bot_rf_ml2(text):

  intent = get_intent(text)                                                     # 1. try to understand the intention by comparison according to Levinstein

  if intent is None:
    intent = get_intent_by_rf_model2(text)                                      # 2. use random forrest 2

  if 'inc_response' in BOT_CONFIG['intents'][intent]:
      return random.choice(BOT_CONFIG['intents'][intent]['inc_response']) 
  else: 
      return random.choice(BOT_CONFIG['intents'][intent]['responses'])

#
# use the sgd model 1
#
def bot_sgd_ml1(text):

  intent = get_intent(text)                                                     # 1. try to understand the intention by comparison according to Levinstein
                                                                                # when multiple phrases are found in many sections i might reverse this
  if intent is None:
    intent = get_intent_by_sgd_model1(text)                                     # 2. use the SGD model

  if 'inc_response' in BOT_CONFIG['intents'][intent]:
      return random.choice(BOT_CONFIG['intents'][intent]['inc_response']) 
  else: 
      return random.choice(BOT_CONFIG['intents'][intent]['responses'])    

#
# this is test we run each ml model in alternating sequence
# so we can look and analyse how it parsed the json file
#
choiceVar = 0
question = ''
while question != 'exit':
  question = input()
  if question.find(cleaner('exit')) == -1:       
    if choiceVar == 0:
      print("bot1 ridgeclassifier ml1")
      response = bot_rc_ml1(question)
    elif choiceVar == 1:
      print("bot2 random forrest ml1")
      response = bot_rf_ml1(question)
    elif choiceVar == 2:
      print("bot3 random forrest ml2")
      response = bot_rf_ml2(question)
    else:
      print("bot4 sgd ml1")
      response = bot_sgd_ml1(question)
    choiceVar = choiceVar + 1
    choiceVar = choiceVar % 4
    print(response)
    
#
# This is the bot which will run the AIML for the messanger
# we run all the machine learning models we developed and make a choice from there
# results
#
def bot(question):

  if question.find(cleaner('exit')) == -1:
    response = []       
    print("bot1 rcml1")
    try:
      response.append( bot_rc_ml1(question) )                                   # ridge classifier model
    except:
      print("bot1 rcml1 fail")
    print("bot2 rfml1")
    try:
      response.append( bot_rf_ml1(question) )                                   # random forrest model1
    except:
      print("bot2 rfml1 fail")
    print("bot3 rfml2")
    try:
      response.append( bot_rf_ml2(question) )                                   # random forrest model2
    except:
      print("bot3 rfml2 fail")
    print("bot4 sgdml1")
    try:
      response.append( bot_sgd_ml1(question) )                                  # sgd stochastic gradient desent
    except:
      print("bot4 sgdm1 fail") 
    return random.choice(response)                                              # make a random chocie from the machine learning models results (some always look at various sections so this way we see them all)
    #return response                                                            # if you want to look at the result list
  else:
    return 'exit'
    
import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
questions = []

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    reply = 'list :: house, garage, future garage, cartoon, anime, hip hop etc..'
    update.message.reply_text(reply)


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    question = update.message.text
    questions.append(question)
    if question.find(cleaner('exit')) == -1:       
      response = bot(question)
      if not response.find("65536") == -1:                                      # we did find in list
        reply = "list :: house, garage, future garage, cartoon, anime, hip hop, modern art etc.. \n try entering just the word"
      else:
        reply = response
      #print("the response %s" % reply)
    else:
      reply = 'exit' 
    # to send a file ..... reply = 'https://colab.research.google.com/drive/1Azj_M62pXee_7DlknRx7nEqEB2j7SoFp#scrollTo=zuaT9rmGkjZw'
    if not reply.find("list") == -1 or not reply.find("reply") == -1:
        update.message.reply_text(reply)
    else:
        replyurl = reply
        update.message.reply_text(replyurl)      

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1778043544:AAE7NZYNTOqLMWmSFB0jGIv2-vFuNxgBz68")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    
#
# run communication to the botFather
#
main()
