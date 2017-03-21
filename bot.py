import discord
import asyncio
import praw
import datetime
import time

client = discord.Client()
reddit = praw.Reddit(user_agent='USER_AGENT',client_id='CLIENT_ID',client_secret='CLIENT_SECRET',password="PASSWORD",username='USERNAME')
print('Logged in as: '+ str(reddit.user.me()))
loggedin = 0

async def on_reddit():
    stickied = ''
    for submission in reddit.subreddit('SUBREDDIT').hot(limit=None):
        ts = time.time() + 3600
        real_time = submission.created - 25200
        print('System Timestamp: ' + str(ts))
        print('Reddit Timestamp: ' + str(real_time))
        print(datetime.datetime.fromtimestamp(ts))
        if (submission.stickied == True and ts - real_time <= 300): #subtract 25200 because of stupid muricas
            print(submission.title)
            stickied = 'Er is een nieuwe sticky thread: ' + str(submission.title) + ' ' + str(submission.url)
    return stickied

@client.event
async def on_ready():
    global loggedin
    if loggedin == 0:
        print("Logged in as")
        print(client.user.name)
        loggedin = 1
    titel = await on_reddit()
    if titel:
        await client.send_message(client.get_channel('ANNOUNCEMENT_CHANNEL'), titel)
        await delete_annoucements()
    amatext= 'ama'
    if amatext in titel:
        await client.send_message(client.get_channel('ANNOUNCEMENT_CHANNEL'),'@everyone')
    await client.change_presence(game=discord.Game(name='mygame'))
    await asyncio.sleep(300)
    await on_ready()

async def delete_annoucements():
    await asyncio.sleep(43200)
    await client.purge_from(client.get_channel('ANNOUNCEMENT_CHANNEL'), limit=5, check=is_me)
    print('Cleared bot messages')

def is_me(m):
    return m.author == client.user

client.run('DISCORDBOT_TOKEN')
