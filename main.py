import os
import discord
from dotenv import load_dotenv
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
channelCursor = channelDatabase.cursor()
channelCursor.execute(shyNameSQL)
shyNameRes = channelCursor.fetchall()
for e in shyNameRes:
    db["ShyChannelNameArr"].append(e[0])

torNameSQL = "select * from TorChannel"
channelCursor = channelDatabase.cursor()
channelCursor.execute(shyNameSQL)
TorNameRes = channelCursor.fetchall()
for e in TorNameRes:
    db["TolerantChannelNameArr"].append(e[0])
channelDatabase.close()

helpMsg = '''[종목명] - 현재 KOSPI & KOSDAQ 상장사 전체를 대상으로 서칭합니다. 정확한 대상이 없고 유사결과만 나올 경우 목록을 보여줍니다.\n\n
$주가 보기 [종목명] - 해당 종목의 주가를 표시합니다. 예) 주가 보기 삼성전자보통주\n
$종목번호 보기 [종목명] - 해당 종목의 고유번호를 표시합니다.\n
$내 종목 등록 [종목명] [수량(숫자만)] [평단가(쉼표없이)] - 유저 본인의 주식 정보를 저장합니다. 이 정보는 이 봇이 사용되는 모든곳에서 열람 가능합니다. 예) $내 종목 등록 삼성전자보통주 10 80000\n
$내 종목 보기 - 겁쟁이버전과 사나이버전 등록 채널에 따라 반응해줍니다. 이 정보는 이 봇이 사용되는 모든곳에서 열람 가능합니다. 한 채널에 동시에 두 버전이 연동돼있을 경우 겁쟁이 버전만 동작합니다.\n\n
'''

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

    Database = mysql.connector.connect(
        host="35.233.199.17",
        user = "root",
        passwd = os.environ.get("SQL_PW"),
        database = 'BotDB')
    cursor = Database.cursor()
    if message.content.startswith("$Help"):
        #await message.channel.send(resMsg, file=discord.File('Icon.gif'))
        await message.channel.send(helpMsg)

    elif message.content.startswith("$슈퍼 겁쟁이들의 쉼터 채널명 등록 "):
        db["ShyChannelNameArr"].append(lastToken)
        sql = f"insert into ShyChannel (Name) values('{lastToken}');"
        cursor.execute(sql)
        await message.channel.send(f"슈퍼 겁쟁이들의 쉼터에 '{lastToken}'이 등록 됐습니다.", delete_after=5)

    elif message.content.startswith("$슈퍼 겁쟁이들의 쉼터 채널명 제거 "):
        db["ShyChannelNameArr"].remove(lastToken)
        sql = f"remove from ShyChannel where Name = '{lastToken}';"
        cursor.execute(sql)
        await message.channel.send(f"슈퍼 겁쟁이들의 쉼터에 '{lastToken}'이 제거 됐습니다.", delete_after=5)

    elif message.content.startswith("$사나이 클럽 채널명 등록 "):
        db["TolerantChannelNameArr"].append(lastToken)
        sql = f"insert into TorChannel (Name) values('{lastToken}');"
        cursor.execute(sql)
        await message.channel.send(f"사나이 클럽에 '{lastToken}'이 등록 됐습니다.", delete_after=5)

    elif message.content.startswith("$사나이 클럽 채널명 제거 "):
        db["TolerantChannelNameArr"].remove(lastToken)
        sql = f"remove from TorChannel where Name = '{lastToken}';"
        cursor.execute(sql)
        await message.channel.send(f"사나이 클럽에 '{lastToken}'이 제거 됐습니다.", delete_after=5)

    elif (shyFlag or torFlag) and message.content.startswith("$주가 보기"):
        processingMsg = await message.channel.send("처리중")

        companyKey = NFinance.GetCompanyCode(cursor, lastToken)
        if type(companyKey) is str:
            price = NFinance.GetPrice(companyKey)
            await processingMsg.delete()
            await message.channel.send("확인가격: " + price)
        else:
            fail_msg = GetFailMsg(companyKey)
            await processingMsg.delete()
            await message.channel.send(fail_msg)

    elif (shyFlag or torFlag) and message.content.startswith("$종목번호 보기 "):
        processingMsg = await message.channel.send("처리중")

        companyKey = NFinance.GetCompanyCode(cursor, lastToken)
        if type(companyKey) is str:
            companyCode = NFinance.GetCompanyCode(cursor, lastToken)
            await processingMsg.delete()
            await message.channel.send(companyCode)
        else:
            fail_msg = GetFailMsg(companyKey)
            await processingMsg.delete()
            await message.channel.send(fail_msg)

    elif (shyFlag or torFlag) and message.content.startswith("$내 종목 등록 "):
        processingMsg = await message.channel.send("처리중")

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
            await processingMsg.delete()
            await message.channel.send(f"정보>> {companyName}({companyKey}) {stockCount}주 평단가 {avegCost}로 등록 완료했습니다.")
        else:
            fail_msg = GetFailMsg(companyKey)
            await processingMsg.delete()
            await message.channel.send(fail_msg)

    elif (shyFlag or torFlag) and message.content.startswith("$내 종목 제거 "):
        processingMsg = await message.channel.send("처리중")

        companyKey = NFinance.GetCompanyCode(cursor, lastToken)
        user = str(message.author)
        if type(companyKey) is str:
            if db.__contains__(user):
                del db[user][companyKey]
                await processingMsg.delete()
                await message.channel.send(f"{lastToken} 정보를 저장소에서 성공적으로 제거했습니다.")
            else:
                await processingMsg.delete()
                await message.channel.send(f"{lastToken} 정보는 저장돼있지 않습니다.")
        else:
            fail_msg = GetFailMsg(companyKey)
            await processingMsg.delete()
            await message.channel.send(fail_msg)


    elif (shyFlag or torFlag) and message.content.startswith("$내 종목 보기"):
        if shyFlag:
            keycount = len (db[str(message.author)].keys())
            index = 0
            for elem in db[str(message.author)].keys():
                processingMsg = await message.channel.send(f"처리중{index}/{keycount}")
                price = int(NFinance.GetPrice(elem).replace(',', ''))
                gif = ShyReaction(price, db[str(message.author)][elem][1])

                index += 1
                await processingMsg.delete()
                await message.channel.send(gif)

        elif torFlag:
            print("you die")
        await message.channel.send("정보" + str(db[str(message.author)]))

    # elif message.content.startswith("$"):
    #     await message.channel.send(helpMsg)

def ShyReaction(price, userprice):
    gap = price - userprice
    pfWeight = gap / price
    print(pfWeight)
    return 1

def GetFailMsg(result):
    fail_msg = "주식정보가 없습니다 다음 목록에 나온 이름으로 정확하게 입력하세요 \n------------------\n"
    for stockName in result:
        fail_msg += (stockName + "\n")
    fail_msg += "------------------"
    return fail_msg

client.run(os.environ.get("DISCORD_TOKEN"))
