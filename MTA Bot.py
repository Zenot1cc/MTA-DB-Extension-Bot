import discord
from discord.ext import commands
from discord import *
import random
import datetime
import sqlite3
database = "tutorial.db"
doubleWinRate = 50

#Starting and Connecting to DB
con = sqlite3.connect(database)
cur = con.cursor()
try:
    cur.execute("CREATE TABLE coins(name INTEGER, balance INTEGER)")
    print("Table Created")
    cur.execute(f"INSERT INTO coins VALUES (1072269707614355507, 0)")
    con.commit()
except:
    print("Table Exists")
con.close()

#Starting and Connecting to Discord
intents = discord.Intents().all()
client = commands.Bot(command_prefix = "!", intents = discord.Intents.all())
TOKEN = "MTA3MjI2OTcwNzYxNDM1NTUwNw.GPDDLf.IDkj0lqTdhrXFSVvvbEAtfBw1xrw69WFdiqDWI"
@client.event
async def on_ready():
    print("ready")
    try:
        synced = await client.tree.sync()
        print(f"Synced", len(synced))
        log = open("log.txt", "a")
        log.writelines(f"\nBot Started and Synced Successfully{str(datetime.datetime.now())}")
        log.close()
    except Exception as e:
        print(e)
        log = open("log.txt", "a")
        log.writelines(f"\nBot Started but Unable to sync ({e}) {str(datetime.datetime.now())}")
        log.close()

##############################################################################################################################################################
## Single Player Coinflip
@client.tree.command(name = "doubleornothing")
@app_commands.describe(bet = "Amount To Bet")
async def coinflip(interaction: discord.Interaction, bet: int):
    log = open("log.txt", "a")
    log.writelines(f"\nDouble Or Nothing Attempted By {interaction.user.mention} with a Value of {bet} {str(datetime.datetime.now())}")
    log.close()
    con = sqlite3.connect(database)
    cur = con.cursor()
    hit = [0,0]
    winnings = bet * 2
    userid = interaction.user.id    
    for row in cur.execute("SELECT name, balance FROM coins ORDER BY balance"):

        #Check if user is in database
        if int(userid) == int(row[0]):
            balance = row[1]
            print("old user")
            hit = [userid, balance]
        if int("1072269707614355507") == int(row[0]):
            botBal = int(row[1])
            print(botBal)
    if userid in hit:
        if balance >= bet:
            if botBal > winnings:
                newbal = balance - bet
                cur.execute(f"UPDATE coins SET balance = {newbal} WHERE name = {userid}")
                con.commit()
                dice = random.randint(0,100)
                if dice < doubleWinRate:
                    balance = balance + int(winnings * 0.98)
                    botBal = botBal - int(winnings * 0.98)
                    cur.execute(f"UPDATE coins SET balance = {balance} WHERE name = {userid}")
                    cur.execute(f"UPDATE coins SET balance = {botBal} WHERE name = {1072269707614355507}")
                    con.commit()
                    await interaction.response.send_message(f"You won! Your balance is {balance}:coin:")
                    log = open("log.txt", "a")
                    log.writelines(f"\nDouble Or Nothing Won By {interaction.user.mention} with a Value of {winnings} {str(datetime.datetime.now())}")
#                    log.writelines(f"\nBot won {int(int(bet*2)-winnings)} {str(datetime.datetime.now())}")
                    log.close()
                else:
                    botBal = botBal + int(winnings)
                    cur.execute(f"UPDATE coins SET balance = {botBal} WHERE name = {1072269707614355507}")
                    con.commit()
                    await interaction.response.send_message(f"The house has won. Better luck next time!")
                    log = open("log.txt", "a")
                    log.writelines(f"\nDouble Or Nothing Won By Bot with a Value of {winnings} {str(datetime.datetime.now())}")
                    log.close()
            else:
                await interaction.response.send_message(f"Bot does not have enough :coin: for this action!") 
        else:
            await interaction.response.send_message(f"Not enough :coin: in your account! Use /deposit")

    else:                         
        cur.execute(f"INSERT INTO coins VALUES ({int(userid)}, {0})")
        con.commit()
        print(f"new user {userid}")
        await interaction.response.send_message(f"Not enough :coin: in your account! Use /deposit")
    con.close()        
##############################################################################################################################################################
## DB and C Conversion
@client.tree.command(name = "convert")
@app_commands.describe(ticker = "Ticker", ticker2 = "Ticker 2", convert = "Amount to Convert")
async def convert(interaction: discord.Interaction, ticker: str, ticker2: str, convert: int):
    try:
        ticker = ticker.lower()
        ticker2 = ticker2.lower()
    except:
        await interaction.response.send_message(f"Please Enter Valid Tickers (T1)")
    print(ticker, ticker2, convert)
    if  ticker == "db" and ticker2 == "c":
        convert = convert * 100
# Get Bots Current Balance of C
# Check Bots Current Balance is Enough
# Get Customers Current Balance of DB
# Check Customers Balance is Enough
        print(convert)
        await interaction.response.send_message(f"/send c {interaction.user.mention} {convert}")

    elif ticker == "c" and ticker2 == "db":
# Get Bots current Balance of DB
# Check bots current balance is enough
# Get customers current balance of C
# Check customers Balance is enough
        convert = convert / 100

        if convert < 0.1 or convert == 0:
           await interaction.response.send_message(f"Please enter a value Divisible by 100")
        elif convert > 0:
            await interaction.response.send_message(f"/send db {interaction.user.mention} {convert}")
    else:
        await interaction.response.send_message(f"Please Enter Valid Tickers (T2)")
##############################################################################################################################################################

@client.tree.command(name = "deposit")
@app_commands.describe(ticker = "Ticker", deposit = "Amount to deposit")
async def deposit(interaction: discord.Interaction, ticker: str, deposit: int):
    con = sqlite3.connect(database)
    cur = con.cursor()

    try:
        ticker.lower()
    except:
        await interaction.response.send_message(f"Please Enter a Valid Ticker (T3) ")

    if ticker == "c":
        userid = interaction.user.id
        hit = [0,0]
        for row in cur.execute("SELECT name, balance FROM coins ORDER BY balance"):
            #Check if user is in database
            if int(userid) == int(row[0]):
                balance = row[1]
                print("old user")
                balance = int(row[1]) + int(deposit)
                print(balance)
                hit = [int(interaction.user.id), balance]
            #If they are, Update Records
            if userid in hit:
                cur.execute(f"UPDATE coins SET balance = {balance} WHERE name = {userid}")
                con.commit()
                await interaction.response.send_message(f"Your balance is {balance}:coin:")
                log = open("log.txt", "a")
                log.writelines(f"\n{interaction.user.id} Deposited {deposit} C {str(datetime.datetime.now())}")
                log.close()
            #If not, Create Records
            else:
                cur.execute(f"INSERT INTO coins VALUES ({int(userid)}, {0 + int(deposit)})")
                con.commit()
                print(f"new user {userid}")
                await interaction.response.send_message(f"Your balance is {balance}:coin:")

    elif ticker == "db":
        userid = interaction.user.id
        hit = [0,0]
        for row in cur.execute("SELECT name, balance FROM coins ORDER BY balance"):
            #Check if user is in database
            if int(userid) == int(row[0]):
                balance = row[1]
                print("old user")
                deposit = int(deposit) * 100
                balance = int(row[1]) + int(deposit)
                print(balance)
                hit = [int(interaction.user.id), balance]
            #If they are, Update Records
            if userid in hit:
                cur.execute(f"UPDATE coins SET balance = {balance} WHERE name = {userid}")
                con.commit()
                await interaction.response.send_message(f"Your balance is {balance}:coin:")
                log = open("log.txt", "a")
                log.writelines(f"\n{interaction.user.id} Deposited {deposit} C {str(datetime.datetime.now())}")
                log.close()
            #If not, Create Records
            else:
                cur.execute(f"INSERT INTO coins VALUES ({int(userid)}, {0 + int(deposit)})")
                con.commit()
                print(f"new user {userid}")
                await interaction.response.send_message(f"Your balance is {0 + int(deposit)}:coin:")
    else:
        await interaction.response.send_message(f"Please Enter a Valid Ticker (T4)")            
    con.close()
##############################################################################################################################################################

@client.tree.command(name = "withdraw")
@app_commands.describe(ticker = "Ticker", withdraw = "Amount to Withdaw")
async def withdraw(interaction: discord.Interaction, ticker: str, withdraw: int):
    con = sqlite3.connect(database)
    cur = con.cursor()

    try:
        ticker.lower()
    except:
        await interaction.response.send_message(f"Please Enter a Valid Ticker (T3) ")

    if ticker == "c":
        userid = interaction.user.id
        hit = [0,0]
        for row in cur.execute("SELECT name, balance FROM coins ORDER BY balance"):

            #Check if user is in database
            if int(userid) == int(row[0]):
                balance = row[1]
                print("old user")
                balance = int(balance) - int(withdraw)
                hit = [int(interaction.user.id), balance]

            #If they are, Update Records
            if userid in hit:
                if balance >= 0:
                    cur.execute(f"UPDATE coins SET balance = {balance} WHERE name = {userid}")
                    con.commit()
                    await interaction.response.send_message(f"Your balance is {balance}:coin:")
                    log = open("log.txt", "a")
                    log.writelines(f"\n{interaction.user.id} Withdrew {withdraw} C {str(datetime.datetime.now())}")
                    log.close()
                else:
                    await interaction.response.send_message(f"Not enough :coin: in your account to Withdraw!")

            #If not, Create Records
            else:
                cur.execute(f"INSERT INTO coins VALUES ({int(userid)}, {0})")
                con.commit()
                print(f"new user {userid}")
                await interaction.response.send_message(f"Not enough :coin: in your account to Withdraw!")

    elif ticker == "db":
        userid = interaction.user.id
        hit = [0,0]
        for row in cur.execute("SELECT name, balance FROM coins ORDER BY balance"):

            #Check if user is in database
            if int(userid) == int(row[0]):
                balance = row[1]
                print("old user")
                withdraw = withdraw * 100
                balance = int(balance) - int(withdraw)
                hit = [int(interaction.user.id), balance]

        #If they are, Update Records
        if userid in hit:
            if balance >= 0:
                cur.execute(f"UPDATE coins SET balance = {balance} WHERE name = {userid}")
                con.commit()
                await interaction.response.send_message(f"Your balance is {balance}:coin:")
                log = open("log.txt", "a")
                log.writelines(f"\n{interaction.user.id} Withdrew {withdraw} C {str(datetime.datetime.now())}")
                log.close()
            else:
                await interaction.response.send_message(f"Not enough :coin: in your account to Withdraw!")

        #If not, Create Records
        else:
            cur.execute(f"INSERT INTO coins VALUES ({int(userid)}, {0})")
            con.commit()
            print(f"new user {userid}")
            await interaction.response.send_message(f"Not enough :coin: in your account to Withdraw!")
    else:
        await interaction.response.send_message(f"Please Enter a Valid Ticker (T4)")            
    con.close()        

#####################################################################################################################################

@client.tree.command()
async def cbalance(interaction: discord.Interaction):
    con = sqlite3.connect(database)
    cur = con.cursor()
    hit = [0,0]
    for row in cur.execute("SELECT name, balance FROM coins ORDER BY balance"):
        if interaction.user.id == row[0]:
            balance = row[1]
            hit = [interaction.user.id, balance]
        if interaction.user.id in hit:
            await interaction.response.send_message(f"Your balance is {balance}:coin")
        else:
            cur.execute(f"INSERT INTO coins VALUES ({interaction.user.id}, {int(0)})")           
            await interaction.response.send_message(f"Your balance is 0:coin:")
    con.close()














#@client.tree.command(name= "auctioncreate")
#@app_commands.describe(command = "What would you like to do? (/auction help)", name = "What are you selling?", length = "How long will the auction last?", starting_bid = "Starting bid of the auction", buyout = "What amount would you ideally like to sell this item for?")
#async def auction(interaction: discord.Interaction, name: str, length: int, starting_bid: int, buyout: int):
#    try:
#        channel = "1082099666243551292"
#        print(f"Making an auction{str(name), str(length), str(starting_bid), str(buyout)}" )
#        await channel.create_thread(name = name, type=ChannelType.public_thread )
#        await interaction.response.send_message(f"I have created your auction")

#    except:
#        await interaction.response.send_message(f"Please ensure you have all the required information for your Auction. Use /auctionhelp for help")
#        print(name)



    



client.run(TOKEN)
