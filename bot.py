import discord
import asyncio
import praw
import datetime
import time

client = discord.Client()
reddit = praw.Reddit(user_agent='USER_AGENT',client_id='CLIENT_ID',client_secret='CLIENT_SECRET',password="PASSWORD",username='USERNAME')
print('Logged in as: '+ str(reddit.user.me()))
loggedin = 0
computer_time = time.time()
f = open('posttimes.txt', 'w')
f.write(str(computer_time))
f.close()

async def on_reddit():
    stickied = ''
    for submission in reddit.subreddit('SUBREDDIT').hot(limit=2):
        ts = time.time() + 3600
        real_time = submission.created - 25200
        print('System Timestamp: ' + str(ts))
        print('Reddit Timestamp: ' + str(real_time))
        print(datetime.datetime.fromtimestamp(ts))
        if (submission.stickied == True and ts - real_time <= 300): #subtract 25200 because of stupid muricas
            print(submission.title)
            stickied = 'Er is een nieuwe sticky thread: ' + str(submission.title) + ' ' + str(submission.url)
    return stickied

async def time_reddit():
    reddit_time = ''
    for submission in reddit.subreddit('SUBREDDIT').hot(limit=2):
        if submission.stickied == True:
            reddit_time = submission.created - 25200
    return reddit_time

@client.event
async def on_ready():
    global loggedin
    if loggedin == 0:
        print("Logged in as")
        print(client.user.name)
        loggedin = 1
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
        await client.send_message(client.get_channel('CHANNEL'), titel)
        f = open('posttimes.txt', 'w')
        f.write(str(await time_reddit()))
        f.close()
    amatext= 'ama'
    if amatext in titel:
        await client.send_message(client.get_channel('CHANNEL'),'@everyone')
    await client.change_presence(game=discord.Game(name='MYGAME'))
    sys_time = time.time()
    f = open('posttimes.txt', 'r')
    if float(sys_time) - float(f.read()) >= 43200:
        await client.purge_from(client.get_channel('CHANNEL'), limit=5, check=is_me)
        print('Cleared bot messages')
    f.close()
    await asyncio.sleep(300)
    await on_check()

client.run('BOT_ID')
