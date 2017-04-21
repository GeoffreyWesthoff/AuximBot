import discord
import asyncio
import praw
import datetime
import time
import os
import sys
import configparser

config = configparser.ConfigParser()
strikes_config = configparser.ConfigParser()
config.read('config.ini')

language = config['GENERAL']['language']

if language == 'english':
    sticky_title = 'A new sticky thread was posted'
    leave_message = 'Goodbye. Be right back...'
    message_failed = 'Message could not be send'
    message_received = 'Message sent to moderators :postbox:'
    message_send = 'Message has been send succesfully.'
    pm_title = 'A PM was send:'
    mygame = 'Reddit and Modmail'
    has = 'has'
    strike_text = 'strikes'
    strike_added = 'Strike added to'
    strike_removed= 'Strike taken from'
    hasnow = 'He/she now has'
    print('Language is set to English')
elif language == 'dutch':
    sticky_title = 'Er is een nieuwe sticky thread:'
    leave_message = 'Toedeloe heren. Tot zo...'
    message_failed = 'Bericht kon niet worden verzonden'
    message_received = 'Bericht bezorgd bij de moderators :postbox:'
    message_send = 'Bericht is met succes verzonden'
    pm_title = 'Een PM is verstuurd:'
    mygame = 'Reddit en Modmail'
    has = 'heeft'
    strike_text = 'strikes'
    strike_added = 'Strike gegeven aan'
    strike_removed= 'Strike afgenomen van'
    hasnow = 'Hij/zij heeft nu'
    print('Taal is ingesteld op Nederlands')

elif language == 'custom':
    sticky_title = config['CUSTOM']['sticky_title']
    leave_message = config['CUSTOM']['leave_message']
    message_failed = config['CUSTOM']['message_failed']
    message_received = config['CUSTOM']['message_received']
    pm_title = config['CUSTOM']['pm_title']
    mygame = config['CUSTOM']['mygame']
    has = config['CUSTOM']['has']
    strike_text = config['CUSTOM']['strike_text']
    strike_added = config['CUSTOM']['strike_added']
    hasnow = config['CUSTOM']['hasnow']
    strike_removed = config['CUSTOM']['strike_removed']
    print('Bot is now using custom strings')

user_agent = config['REDDIT']['user_agent']
username = config['REDDIT']['username']
password = config['REDDIT']['password']
client_id = config['REDDIT']['client_id']
client_secret = config['REDDIT']['client_secret']
subreddit = config['REDDIT']['subreddit']
check_time = config['REDDIT']['check_time']
check_time_ama = config['REDDIT']['check_time_ama']
reddit_time_delta = config['REDDIT']['reddit_time_delta']
system_time_delta = config['REDDIT']['system_time_delta']


bot_id = config['DISCORD']['bot_id']
raw_announcement_channel = config['DISCORD']['announcement_channel']
raw_mod_channel = config['DISCORD']['mod_channel']
raw_report_channel = config['DISCORD']['report_channel']
command_prefix = config['DISCORD']['command_prefix']

moderators_list = config['LISTS']['moderators']
blacklist_list = config['LISTS']['blacklist']
everyonetexts_list = config['LISTS']['everyonetexts']

report_channel = str(raw_report_channel)
announcement_channel = str(raw_announcement_channel)
mod_channel = str(raw_mod_channel)
moderators = moderators_list.split(',')
blacklist = blacklist_list.split(',')
everyonetexts = everyonetexts_list.split(',')

client = discord.Client()
reddit = praw.Reddit(user_agent=user_agent,client_id=client_id,client_secret=client_secret,password=password,username=username)
print('Logged in as: '+ str(reddit.user.me()))
computer_time = time.time()
f = open('posttimes.txt', 'w')
f.write(str(computer_time))
f.close()

async def on_reddit():
    stickied = ''
    for submission in reddit.subreddit(subreddit).hot(limit=2):
        ts = time.time() + int(system_time_delta)
        flair_text = submission.link_flair_text
        real_time = submission.created - int(reddit_time_delta) #fuck zomertijd
        print('System Timestamp: ' + str(ts))
        print('Reddit Timestamp: ' + str(real_time))
        print(datetime.datetime.fromtimestamp(ts))
        print(datetime.datetime.fromtimestamp(real_time))
        if (submission.stickied == True and ts - real_time <= int(check_time)) and flair_text != 'AMA': #subtract 25200 because of stupid muricas
            print(submission.title)
            stickied = str(sticky_title) + str(submission.title) + ' ' + str(submission.url)
        elif (submission.stickied == True) and ts - real_time <= int(check_time_ama) and flair_text == 'AMA':
            print(submission.title)
            stickied = str(sticky_title) + str(submission.title) + ' ' + str(submission.url) + ' @everyone'
    return stickied

async def time_reddit():
    reddit_time = ''
    for submission in reddit.subreddit(subreddit).hot(limit=2):
        if submission.stickied == True:
            reddit_time = submission.created - int(reddit_time_delta)
    return reddit_time

async def flair_text():
    for submission in reddit.subreddit(subreddit).hot(limit=2):
        flair_text_check = submission.link_flair_text
    return flair_text_check

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    await on_check()

def is_me(m):
    return m.author == client.user

async def on_check():
    try:
        titel = await on_reddit()
    except Exception as e:
        print(e)
        await on_check()
    if titel:
        await client.send_message(client.get_channel(announcement_channel), titel)
        f = open('posttimes.txt', 'w')
        f.write(str(await time_reddit()))
        f.close()
    for everyonetext in everyonetexts:
        if everyonetext in titel:
            await client.send_message(client.get_channel(announcement_channel),'@everyone')
    await client.change_presence(game=discord.Game(name=mygame))
    sys_time = time.time()
    f = open('posttimes.txt', 'r')
    if float(sys_time) - float(f.read()) >= 43200:
        await client.purge_from(client.get_channel(announcement_channel), limit=5, check=is_me)
        print('Cleared bot messages')
    f.close()
    if await flair_text() == 'AMA':
        print('Waiting 1800 seconds')
        await asyncio.sleep(int(check_time_ama))
        await on_check()
    else:
        print('Waiting 600 seconds')
        await asyncio.sleep(int(check_time))
        await on_check()

@client.event
async def on_message(message):
    author = message.author
    for moderator in moderators:
        if str(moderator) == str(author):
            if message.content.startswith(command_prefix + 'restart'):
                await client.send_message(client.get_channel(mod_channel), leave_message)
                os.execv(sys.executable, ['bot.py'] + sys.argv)
            if message.content.startswith(command_prefix + 'r'):
                half_reply = message.content.rsplit(' ', 1)[0]
                reply = half_reply.split(' ', 1)[1]
                print(reply)
                pm_author = message.content.rsplit(' ', 1)[1]
                print(pm_author)
                #try:
                send_author = await client.get_user_info(pm_author)
                print(send_author)
                await client.send_message(send_author, reply) #allows moderators to send a reply
                confirmation = await client.send_message(client.get_channel(report_channel),message_send)
                await asyncio.sleep(3)
                await client.delete_message(confirmation)
                #except Exception as e:
                #    await client.send_message(client.get_channel(report_channel), message_failed)
            if message.content.startswith(command_prefix + 'checkstrike'):
                strike_check = message.content.rsplit(' ', 1)[1]
                strike_check_user = await client.get_user_info(strike_check)
                string_strike_check_user = str(strike_check_user)
                strikes_config.read('strikes.ini')
                if string_strike_check_user not in strikes_config:
                    strikes_config.add_section(string_strike_check_user)
                    strikes_config.set(string_strike_check_user,'strikes','0')
                strikes = strikes_config.get(string_strike_check_user,'strikes')
                with open('strikes.ini','w') as configfile:
                    strikes_config.write(configfile)
                await client.send_message(client.get_channel(report_channel),strike_check_user.mention + ' ' + has + ' ' + str(strikes) + ' ' + strike_text)
            if message.content.startswith(command_prefix + 'strike'):
                strike = message.content.rsplit(' ', 1)[1]
                strike_user = await client.get_user_info(strike)
                print(strike_user)
                strikes_config.read('strikes.ini')
                string_strike_user = str(strike_user)
                if string_strike_user not in strikes_config:
                    strikes_config.add_section(string_strike_user)
                    strikes_config.set(string_strike_user,'strikes', '0')
                strikes = strikes_config.get(string_strike_user,'strikes')
                strikes = int(strikes)+1
                strikes_config.set(string_strike_user,'strikes',str(strikes))
                with open('strikes.ini','w') as configfile:
                    strikes_config.write(configfile)
                await client.send_message(client.get_channel(report_channel), strike_added + ' ' + strike_user.mention + '. ' + hasnow + ' ' + str(strikes) + ' ' + strike_text)
            if message.content.startswith(command_prefix + 'deletestrike'):
                    r_strike = message.content.rsplit(' ', 1)[1]
                    r_strike_user = await client.get_user_info(r_strike)
                    strikes_config.read('strikes.ini')
                    string_r_strike_user = str(r_strike_user)
                    if string_r_strike_user not in strikes_config:
                        strikes_config.add_section(string_r_strike_user)
                        strikes_config.set(string_r_strike_user,'strikes', '0')
                    r_strikes = strikes_config.get(string_r_strike_user,'strikes')
                    r_strikes = int(r_strikes)-1
                    strikes_config.set(string_r_strike_user,'strikes',str(r_strikes))
                    with open('strikes.ini','w') as configfile:
                        strikes_config.write(configfile)
                    await client.send_message(client.get_channel(report_channel), strike_removed + ' ' + r_strike_user.mention + '. ' + hasnow + ' ' + str(r_strikes) + ' ' + strike_text)
    if message.channel.is_private and author != client.user:
        for blacklisted in blacklist:
            if str(blacklisted) != str(author):
                message_timestamp = message.timestamp + datetime.timedelta(hours=2)
                em = discord.Embed(title = pm_title, description = message.content, colour=0xFF9900)
                em.set_author(name=author, icon_url=author.avatar_url)
                em.set_footer(text= 'ID: ' + str(author.id) + ' | ' + str(message_timestamp))
                await client.send_message(client.get_channel(report_channel), embed=em)
                await client.send_message(author, message_received)
                print(author)

client.run(bot_id)
