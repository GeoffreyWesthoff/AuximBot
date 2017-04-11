import discord
import asyncio
import praw
import datetime
import time
import os
import sys

client = discord.Client()
reddit = praw.Reddit(user_agent='USER_AGENT',client_id='CLIENT_ID',client_secret='CLIENT_SECRET',password="PASSWORD",username='USERNAME') #The bot needs an ID, User Agent(self identification), the secret and a Reddit account. The secret and ID can be obtained by making a new app on Reddit.
print('Logged in as: '+ str(reddit.user.me()))
computer_time = time.time()
f = open('posttimes.txt', 'w')
f.write(str(computer_time))
f.close()

async def on_reddit():
    stickied = ''
    for submission in reddit.subreddit('SUBREDDIT').hot(limit=2): #choose a subreddit to read from
        ts = time.time() + 7200
        real_time = submission.created - 21600
        print('System Timestamp: ' + str(ts))
        print('Reddit Timestamp: ' + str(real_time))
        print(datetime.datetime.fromtimestamp(ts))
		print(datetime.datetime.fromtimestam(real_time))
        if (submission.stickied == True and ts - real_time <= 300): #subtract 25200 because of stupid muricas
            print(submission.title)
            stickied = 'Er is een nieuwe sticky thread: ' + str(submission.title) + ' ' + str(submission.url)
    return stickied

async def time_reddit():
    reddit_time = ''
    for submission in reddit.subreddit('SUBREDDIT').hot(limit=2): #check submission time
        if submission.stickied == True:
            reddit_time = submission.created - 25200
    return reddit_time

@client.event #Login message in console
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    await on_check()

def is_me(m):
    return m.author == client.user #Check if message is by bot himself

async def on_check(): #Post the sticky to Discord, if there is one
    try:
        titel = await on_reddit()
    except Exception as e:
        print(e)
        await on_check()
    if titel:
        await client.send_message(client.get_channel('ANNOUCEMENT_CHANNEL'), titel)
        f = open('posttimes.txt', 'w')
        f.write(str(await time_reddit()))
        f.close()
    everyonetexts = ['ama', 'exchange']
    for everyonetext in everyonetexts:
        if everyonetext in titel:
            await client.send_message(client.get_channel('ANNOUCEMENT_CHANNEL'),'@everyone')
    await client.change_presence(game=discord.Game(name='MYGAME'))
    sys_time = time.time()
    f = open('posttimes.txt', 'r')
    if float(sys_time) - float(f.read()) >= 43200:
        await client.purge_from(client.get_channel('ANNOUCEMENT_CHANNEL'), limit=5, check=is_me)
        print('Cleared bot messages')
    f.close()
    await asyncio.sleep(300)
    await on_check()

@client.event #When a message is received
async def on_message(message):
    moderators = ['MODS']
    author = message.author
    for moderator in moderators:
        if str(moderator) == str(author):
            if message.content.startswith('$restart'):
                await client.send_message(client.get_channel('MOD_CHANNEL'), 'LEAVE_MESSAGE') #Message in the mod channel indicating a restart
                os.execv(sys.executable, ['bot.py'] + sys.argv)
            if message.content.startswith('$r'): #usage $r [MESSAGE] [ID]
                half_reply = message.content.rsplit(' ', 1)[0]
                reply = half_reply.split(' ', 1)[1]
                print(reply)
                pm_author = message.content.rsplit(' ', 1)[1]
                print(pm_author)
                send_author = await client.get_user_info(pm_author)
                print(send_author)
                await client.send_message(send_author, reply) #allows moderators to send a reply
    if message.channel.is_private and author != client.user:
        blacklist = ['']
        for blacklisted in blacklist:
            if str(blacklisted) != str(author):
                message_time = datetime.datetime.fromtimestamp(float(message.timestamp))
                em = discord.Embed(title = 'A PM was sent:', description = message.content, colour=0xFF9900, footer=message_time)
                em.set_author(name=author, icon_url=author.avatar_url)
                em.set_footer(text=author.id + ' | ' + message_timestamp)
                await client.send_message(client.get_channel('REPORT_CHANNEL'), embed=em) #Send content of message to the report channel
                await client.send_message(author, "MESSAGE_RECEIVED") #PM's user with confirmation of delivery
                print(author)

client.run('BOT_ID')
