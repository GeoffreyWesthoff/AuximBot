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
    amatext= 'ama'
    if amatext in titel:
        await client.send_message(client.get_channel('ANNOUNCEMENT_CHANNEL'),'@everyone')
    await asyncio.sleep(300)
    await on_ready()

client.run('DISCORDBOT_TOKEN')
