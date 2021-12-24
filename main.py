import discord
from dotenv import load_dotenv
import os
import naverFinance
import mysql.connector
db = {}

load_dotenv()
channelDatabase = mysql.connector.connect(
    host="35.233.199.17",
    user = "root",
    passwd = os.environ.get("SQL_PW"),
    database = 'BotDB'
)

if not db.__contains__("ShyChannelNameArr"):
    db["ShyChannelNameArr"] = []
if not db.__contains__("TolerantChannelNameArr"):
    db["TolerantChannelNameArr"] = []

shyNameSQL = "select * from ShyChannel"
cursor = channelDatabase.cursor()
cursor.execute(shyNameSQL)
shyNameRes = cursor.fetchall()
for e in shyNameRes:
    db["ShyChannelNameArr"].append(e)

torNameSQL = "select * from TorChannel"
cursor = channelDatabase.cursor()
cursor.execute(shyNameSQL)
shyNameRes = cursor.fetchall()
for e in shyNameRes:
    db["ShyChannelNameArr"].append(e)
channelDatabase.close()

client = discord.Client()
NFinance = naverFinance.NaverFinance()


@client.event
async def on_ready():
    print(f"{client.user} logged in now!")


@client.event
async def on_message(message):
    print(f"message from {message.author}: {message.content} at {message.channel}")
    messArr = message.content.split(" ")
    lastToken = messArr[len(messArr) - 1]
    shyFlag = message.channel.name in db["ShyChannelNameArr"]
    torFlag = message.channel.name in db["TolerantChannelNameArr"]
    
    channelDatabase = mysql.connector.connect(
    host="35.233.199.17",
    user = "root",
    passwd = os.environ.get("SQL_PW"),
    database = 'BotDB')
    
    cursor = Database.Cursor()
    if message.content.startswith("$Help"):
        resMsg = '''[종목명] - 현재 KOSPI & KOSDAQ 상장사 전체를 대상으로 서칭합니다. 정확한 대상이 없고 유사결과만 나올 경우 목록을 보여줍니다.\n
$주가 보기 [종목명] - 해당 종목의 주가를 표시합니다.
$종목번호 보기 [종목명] - 해당 종목의 고유번호를 표시합니다.\n

'''
        await message.channel.send(
            resMsg + "https://tenor.com/view/omg-oh-my-god-wow-gif-11411674")

    elif message.content.startswith("$슈퍼 겁쟁이들의 쉼터 채널명 등록 "):
        db["ShyChannelNameArr"].append(lastToken)
        await message.channel.send("슈퍼 겁쟁이들의 쉼터에 '" + lastToken +
                                   "'이 등록 됐습니다.")

    elif message.content.startswith("$슈퍼 겁쟁이들의 쉼터 채널명 제거 "):
        db["ShyChannelNameArr"].remove(lastToken)
        await message.channel.send("슈퍼 겁쟁이들의 쉼터에 '" + lastToken +
                                   "'이 제거 됐습니다.")

    elif message.content.startswith("$사나이 클럽 채널명 등록 "):
        db["TolerantChannelNameArr"].append(lastToken)
        await message.channel.send("사나이 클럽에 '" + lastToken + "'이 등록 됐습니다.")

    elif message.content.startswith("$사나이 클럽 채널명 제거 "):
        db["TolerantChannelNameArr"].remove(lastToken)
        await message.channel.send("사나이 클럽에 '" + lastToken + "'이 제거 됐습니다.")

    elif message.channel.name in db["ShyChannelNameArr"] and message.content.startswith("$주가 보기"):
        result = NFinance.GetCompanyCode(cursor, lastToken)
        if type(result) is str:
            await message.channel.send("확인가격" + NFinance.GetPrice(result))
        else:
            fail_msg = GetFailMsg(result)
            await message.channel.send(fail_msg)

    elif message.channel.name in db["ShyChannelNameArr"] and message.content.startswith("$종목번호 보기 "):
        result = NFinance.GetCompanyCode(cursor, lastToken)
        if type(result) is str:
            await message.channel.send(NFinance.GetCompanyCode(cursor, lastToken))
        else:
            fail_msg = GetFailMsg(result)
            await message.channel.send(fail_msg)
    elif (shyFlag or torFlag) and message.content.startswith("$내 종목 등록 "):
        companyName = messArr[len(messArr) - 3]
        companyKey = NFinance.GetCompanyCode(cursor, companyName)

        stockCount = messArr[len(messArr) - 2]
        avegCost = lastToken
        user = str(message.author)
        if type(companyKey) is str:
            if not db.__contains__(user):
                db[user] = {companyKey: (int(stockCount), int(avegCost))}
            else:
                db[user].update({companyKey: (int(stockCount), int(avegCost))})
            await message.channel.send(f"정보>> {companyName}({companyKey}) {stockCount}주 평단가 {avegCost}로 등록 완료했습니다.")
        else:
            fail_msg = GetFailMsg(result)
            await message.channel.send(fail_msg)

    elif (shyFlag or torFlag) and message.content.startswith("$내 종목 보기"):
      
      if shyFlag:
        for e in db[str(message.author)].keys():
          price = int(NFinance.GetPrice(e).replace(',',''))
          if price > db[str(message.author)][e][1]:
            print("good")
          else:
            print("bad")
        print("haha")
      elif torFlag:
        print("you die")
      await message.channel.send("정보" + str(db[str(message.author)]))
def GetFailMsg(result):
    fail_msg = "주식정보가 없습니다 다음 목록에 나온 이름으로 정확하게 입력하세요 \n------------------\n"
    for e in result:
        fail_msg += (e + "\n")
    fail_msg += "------------------"
    return fail_msg

client.run(os.environ.get("DISCORD_TOKEN"))
