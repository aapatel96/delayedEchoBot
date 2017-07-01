##import urllib
##import telegram
##import tweepy
##
##bot = telegram.Bot(token='297497718:AAFEZdRe7tbkt6z2Brb4tepPPCn5uNkrLlA')
##
##updates = bot.getUpdates()
##print updates

'''
Have to change the set function to new reading Function so that you give /newReading <dueDate> <reading>
and it splits the readings and starts sending messages
'''

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job, JobQueue, RegexHandler,ConversationHandler
import telegram.replykeyboardmarkup
import telegram.keyboardbutton
import telegram.ext
import logging
import json
import os
import requests


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


users = []


# Enable logging


SETTIME,TYPING_CHOICE=range(2)


#classes

class User:
    def __init__(self,user_id):
        self.currentTask = None
        self.user_id = user_id


        
class special:
    def __init__(self,uid,message):
        self.message = message
        self.id = uid



def find_user(users, user_id):
    """
    Returns the user object with given user_id

    Args:
         users:   The list of user instances to search through.
         user_id: The ID of the user to find.

    Returns:
            The 'user' object with user_id.
    """
    for i in range(len(users)):
        if users[i].user_id == user_id:
            return users[i]

    return None




def start(bot, update, job_queue):
    update.message.reply_text("Yo")
    users.append(User(update.message.from_user.id))   
    job_queue.run_once(herokualarm,15*60,context=job_queue)
    

def herokualarm(bot,job):
    requests.post("https://telegramnewsbot.herokuapp.com/",data={"ping":"ping"})
    requests.post("https://bowdoinmenu.herokuapp.com/",data={"ping":"ping"})
    job_queue.run_once(herokualarm,15*60,context=job_queue)



def help(bot, update):
    update.message.reply_text(' newtask <taskname:priority:duedate> to create a task'+ '\n'
                              + ' mytasks to show tasks'+'\n'+ ' newhabit <habitname:priority>'+'\n'+ ' myhabits to show tasks'+'\n'+ ' deltask <taskid> to delete task by task id (you can find this out using /mytasks command)'
                              +'fintask ,<taskid> to delete task by task id (you can find this out using /mytasks command'+ '\n' +'delthabit <habitid> to delete habit by habit id (you can find this out using /myhabits command)' +"/help to get command list")



def alarm(bot,job):
    userid = job.context.id
    userfind = find_user(users,userid)
    message = job.context.message
    if userfind == None:
        update.message.reply_text("Please type /start and then resend command")
        return

    bot.sendMessage(userid,message)
    return 

    

def apiaif(bot,update):
    userfind = find_user(users,update.message.from_user.id)
    if userfind == None:
        update.message.reply_text("Please type /start and then resend command")
        return ConversationHandler.END
    if update.message.text == "What do you think about the government?":
        update.message.reply_text("yeh government bik gayi hai")
        return ConversationHandler.END
    else:
        userfind.currentTask = update.message.text
        update.message.reply_text("In how many minutes do you want me to remind you?")
        return SETTIME
    
def setTime(bot,update, job_queue):
    userfind = find_user(users,update.message.from_user.id)
    if userfind == None:
        update.message.reply_text("Please type /start and then resend command")
        return ConversationHandler.END
    if update.message.text == "What do you think about the government?":
        update.message.reply_text("yeh government bik gayi hai")
        return ConversationHandler.END
    else:
        try:
            time = float(update.message.text)
            timeSeconds = time * 60.0
        except:
            update.message.reply_text("Sorry could you just give me a number?")
            return SETTIME
        print timeSeconds
        alarm2 = Job(alarm,
            timeSeconds,
            repeat=False,
            context=special(update.message.chat_id,userfind.currentTask))
        job_queue.put(alarm2)
        update.message.reply_text("Thanks! I will remind you in a bit")
        return ConversationHandler.END


def cancel(bot, update):
    print "r"
    userfind = find_user(users,update.message.from_user.id)
    if userfind == None:
        update.message.reply_text("Please type /start and then resend command")
        return ConversationHandler.END
    logger.info("User %s canceled the conversation." % update.message.from_user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.')
    userfind.currentTask = None
    return ConversationHandler.END
    
 
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    TOKEN = "372334539:AAGjvW77FYjFWBxBVodvrDOLrGEWsvH0Djg"
    updater = Updater(TOKEN)
    PORT = int(os.environ.get('PORT', '5000'))
    # job_q= updater.job_queue

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, pass_job_queue=True))
    dp.add_handler(CommandHandler("help", help))

    #task handling
    


    ai_task_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text,apiaif)],
    states={


        SETTIME: [RegexHandler('^cancel$',
                                cancel),
                    MessageHandler(Filters.text,
                                   setTime,
                                   pass_job_queue=True)

                  ],
        TYPING_CHOICE: [RegexHandler('^cancel$', cancel),
                        MessageHandler(Filters.text,
                               start),

                        
                ],

        
    },

    fallbacks=[RegexHandler('^cancel$', cancel)]
    )

    dp.add_handler(ai_task_conv_handler)

    #easter egg




    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.set_webhook("https://delayedecho.herokuapp.com/" + TOKEN)
##    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
