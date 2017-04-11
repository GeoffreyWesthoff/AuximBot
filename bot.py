import discord
import asyncio
import praw
import datetime
import time
import os
import sys
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

user_agent = config['REDDIT']['user_agent']
username = config['REDDIT']['username']
password = config['REDDIT']['password']
client_id = config['REDDIT']['client_id']
client_secret = config['REDDIT']['client_secret']
subreddit = config['REDDIT']['subreddit']
check_time = config['REDDIT']['check_time']
reddit_time_delta = config['REDDIT']['reddit_time_delta']
system_time_delta = config['REDDIT']['system_time_delta']
sticky_title = config['REDDIT']['sticky_title']

leave_message = config['PERSONALISATION']['leave_message']
message_failed = config['PERSONALISATION']['message_failed']
message_received = config['PERSONALISATION']['message_received']
pm_title = config['PERSONALISATION']['pm_title']
mygame = config['PERSONALISATION']['mygame']

bot_id = config['DISCORD']['bot_id']
raw_announcement_channel = config['DISCORD']['announcement_channel']
raw_mod_channel = config['DISCORD']['mod_channel']
raw_report_channel = config['DISCORD']['report_channel']

moderators_list = config['LISTS']['moderators']
blacklist_list = config['LISTS']['blacklist']

report_channel = str(raw_report_channel)
announcement_channel = str(raw_announcement_channel)
mod_channel = str(raw_mod_channel)
moderators = moderators_list.split(',')
blacklist = blacklist_list.split(',')


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
        real_time = submission.created - int(reddit_time_delta) #fuck zomertijd
        print('System Timestamp: ' + str(ts))
        print('Reddit Timestamp: ' + str(real_time))
        print(datetime.datetime.fromtimestamp(ts))
        print(datetime.datetime.fromtimestamp(real_time))
        if (submission.stickied == True and ts - real_time <= int(check_time)): #subtract 25200 because of stupid muricas
            print(submission.title)
            stickied = str(sticky_title) + str(submission.title) + ' ' + str(submission.url)
    return stickied

async def time_reddit():
    reddit_time = ''
    for submission in reddit.subreddit(subreddit).hot(limit=2):
        if submission.stickied == True:
            reddit_time = submission.created - int(reddit_time_delta)
    return reddit_time

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
    everyonetexts = ['ama', 'exchange']
    for everyonetext in everyonetexts:
        if everyonetext in titel:
            await client.send_message(client.get_channel(announcement_channel),'@everyone')
    await client.change_presence(game=discord.Game(name='Reddit en Reports'))
    sys_time = time.time()
    f = open('posttimes.txt', 'r')
    if float(sys_time) - float(f.read()) >= 43200:
        await client.purge_from(client.get_channel(announcement_channel), limit=5, check=is_me)
        print('Cleared bot messages')
    f.close()
    await asyncio.sleep(600)
    await on_check()

@client.event
async def on_message(message):
    author = message.author
    for moderator in moderators:
        if str(moderator) == str(author):
            if message.content.startswith('$restart'):
                await client.send_message(client.get_channel(mod_channel), leave_message)
                os.execv(sys.executable, ['bot.py'] + sys.argv)
            if message.content.startswith('$r'):
                half_reply = message.content.rsplit(' ', 1)[0]
                reply = half_reply.split(' ', 1)[1]
                print(reply)
                pm_author = message.content.rsplit(' ', 1)[1]
                print(pm_author)
                try:
                    send_author = await client.get_user_info(pm_author)
                    print(send_author)
                    await client.send_message(send_author, reply) #allows moderators to send a reply
                except Exception as e:
                    await client.send_message(client.get_channel(report_channel), message_failed)
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
