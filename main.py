import os
import discord
from dotenv import load_dotenv
import naverFinance
import mysql.connector
import random
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
channelCursor.execute(torNameSQL)
TorNameRes = channelCursor.fetchall()
for e in TorNameRes:
    db["TolerantChannelNameArr"].append(e[0])
channelDatabase.close()

helpMsg = '''봇 명령어 설명\n\n
$주가 보기 [종목명] - 해당 종목의 주가를 표시합니다. \n예) $주가 보기 삼성전자보통주\n
$종목 번호 보기 [종목명] - 해당 종목의 고유번호를 표시합니다. \n예) $종목 번호 삼성전자보통주\n
$내 종목 등록 [종목명] [수량(숫자만)] [평단가(쉼표없이)] - 유저 본인의 주식 정보를 저장합니다. 이 정보는 이 봇이 사용되는 모든곳에서 열람 가능합니다. \n예) $내 종목 등록 삼성전자보통주 10 80000\n
$내 종목 제거 [종목명] - 유저 본인의 주식 정보를 제거합니다. 이 작업은 되돌릴 수 없습니다.\n예) $내 종목 제거 삼성전자보통주\n
$내 종목 완전 제거 - 유저 본인의 주식 정보를 완전히 제거합니다. 이 작업은 되돌릴 수 없습니다.\n
$내 종목 보기 - 겁쟁이버전과 사나이버전 등록 채널에 따라 반응해줍니다. 이 정보는 이 봇이 사용되는 모든곳에서 열람 가능합니다. 한 채널에 동시에 두 버전이 연동돼있을 경우 겁쟁이 버전만 동작합니다.\n
$마법의 소라고동 매수 - 마법의 소라고동님에게 매수할지 말지를 물어봅니다. 주식명은 본인 마음속에 있습니다.\n
$마법의 소라고동 손절 - 마법의 소라고동님에게 손절해야할지를 물어봅니다
'''

client = discord.Client()
NFinance = naverFinance.NaverFinance()


@client.event
async def on_ready():
    print(f"{client.user} logged in now!")
    

@client.event
async def on_message(message):
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
    if message.content.startswith("$Help") or message.content.startswith("$help"):
        #await message.channel.send(resMsg, file=discord.File('Icon.gif'))
        await message.channel.send(helpMsg)

    elif message.content.startswith("$슈퍼 겁쟁이 쉼터 채널명 등록 "):
        db["ShyChannelNameArr"].append(lastToken)
        sql = f"insert into ShyChannel (Name) values('{lastToken}');"
        cursor.execute(sql)
        await message.channel.send(f"슈퍼 겁쟁이 쉼터에 '{lastToken}'이 등록 됐습니다.", delete_after=5)
        message.delete()

    elif message.content.startswith("$슈퍼 겁쟁이 쉼터 채널명 제거 "):
        db["ShyChannelNameArr"].remove(lastToken)
        sql = f"delete from ShyChannel where Name = '{lastToken}';"
        cursor.execute(sql)
        await message.channel.send(f"슈퍼 겁쟁이 쉼터에 '{lastToken}'이 제거 됐습니다.", delete_after=5)
        message.delete()

    elif message.content.startswith("$사나이클럽 채널명 등록 "):
        db["TolerantChannelNameArr"].append(lastToken)
        sql = f"insert into TorChannel (Name) values('{lastToken}');"
        cursor.execute(sql)
        await message.channel.send(f"사나이클럽에 '{lastToken}'이 등록 됐습니다.", delete_after=5)
        message.delete()

    elif message.content.startswith("$사나이클럽 채널명 제거 "):
        db["TolerantChannelNameArr"].remove(lastToken)
        sql = f"delete from TorChannel where Name = '{lastToken}';"
        cursor.execute(sql)
        await message.channel.send(f"사나이클럽에 '{lastToken}'이 제거 됐습니다.", delete_after=5)
        message.delete()

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

    elif (shyFlag or torFlag) and message.content.startswith("$종목 번호 보기 "):
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
        avegCostStr = "{:,}".format(int(avegCost))
        user = str(message.author)
        if type(companyKey) is str:
            sql = f"select Count, EvalCost from UserData where ID = '{user}' and StockID = '{companyKey}';"
            cursor.execute(sql)
            storedDatas = cursor.fetchall()
            if len(storedDatas) == 0:
                query = f"insert into UserData (ID, StockID, Count, EvalCost) values('{user}', '{companyKey}', {stockCount}, {avegCost});"
                cursor.execute(query)
                await processingMsg.delete()
                await message.channel.send(f"정보>> {companyName}({companyKey}) {stockCount}주 평단가 {avegCostStr}로 등록 완료했습니다.")
            else:
                await processingMsg.delete()
                avegCostStr = "{:,}".format(storedDatas[0][1])
                await message.channel.send(f"이미 정보가 저장돼있습니다. {companyName} {storedDatas[0][0]}주 평단가 {avegCostStr}")
        else:
            fail_msg = GetFailMsg(companyKey)
            await processingMsg.delete()
            await message.channel.send(fail_msg)

    elif (shyFlag or torFlag) and message.content.startswith("$내 종목 제거 "):
        processingMsg = await message.channel.send("처리중")

        companyKey = NFinance.GetCompanyCode(cursor, lastToken)
        user = str(message.author)
        if type(companyKey) is str:
            sql = f"select Count, EvalCost from UserData where ID = '{user}' and StockID = '{companyKey}';"
            cursor.execute(sql)
            storedDatas = cursor.fetchall()
            if len(storedDatas) == 1:
                sql = f"delete from UserData where ID = '{user}' and StockID = '{companyKey}';"
                cursor.execute(sql)
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
        user = str(message.author)
        sql = f"select StockID, Count, EvalCost from UserData where ID = '{user}';"
        cursor.execute(sql)
        storedDatas = cursor.fetchall()
        func = ShyReaction
        if shyFlag:
            func = ShyReaction
        elif torFlag:
            func = TorReaction
        keycount = len (storedDatas)
        index = 1
        for elem in storedDatas:
            processingMsg = await message.channel.send(f"처리중{index}/{keycount}")
            await message.channel.send("--" + NFinance.GetComapnyName(cursor, elem[0]))
            price = int(NFinance.GetPrice(elem[0]).replace(',', ''))
            res = func(price, elem[2], elem[1])
            index += 1
            await processingMsg.delete()
            await message.channel.send(res)
    elif (shyFlag or torFlag) and message.content.startswith("$마법의 소라고동 매수"):
        await message.channel.send(TrumpetShellAskBuy())
    elif (shyFlag or torFlag) and message.content.startswith("$마법의 소라고동 손절"):
        await message.channel.send(TrumpetShellAskSell())
    elif message.content.startswith("$"):
        await message.channel.send(helpMsg)
    Database.commit()
    Database.close()

def ShyReaction(price, userprice, count):
    gap = userprice - price
    pfWeight = gap / price
    
    if pfWeight > 0.03:
        return "https://tenor.com/view/john-jonah-jameson-lol-laughing-hysterically-laughing-out-loud-funny-gif-17710543"
    elif pfWeight > 0.01:
        return "https://tenor.com/view/shaq-shaquille-o-neal-wiggle-evil-smile-gif-15358842"
    elif pfWeight > -0.01:
        return "https://tenor.com/view/i-mav3riq-imaveriq-eh-meh-gif-9056024"
    elif pfWeight > -0.03:
        return "https://discord.com/channels/921005414710128670/922386044094148648/923872420903923712"
    else:
        return "https://tenor.com/view/sad-blackish-anthony-anderson-tears-upset-gif-4988274"

def TorReaction(price, userprice, count):
    currency = "{:,}".format(price)
    gap = (userprice - price) * count
    gapCurrency = "{:,}".format(gap)
    gbp = gap / 7000
    gbpCount = "{:,.2f}".format(abs(gbp))

    return f"현재 주가는 '{currency}'원 입니다.\n 현재 손익은 '{gapCurrency}'원 입니다.\n그돈이면 국밥(7,000원)을 약 {gbpCount} 그릇 사 먹을 수 있습니다."


def GetFailMsg(result):
    fail_msg = "주식정보가 없습니다 다음 목록에 나온 이름으로 정확하게 입력하세요 \n------------------\n"
    for stockName in result:
        fail_msg += (stockName + "\n")
    fail_msg += "------------------"
    return fail_msg

def TrumpetShellAskBuy():
    value = random.randrange(0, 2)
    resStr = "마법의 소라고동님께 이 주식을 살지 여쭤봅니다.\n마법의 소라고동님이 답합니다.\n"
    if value == 0:
        resStr += '"사"'
    else:
        resStr += '"사지마"'
    resStr += "\n ** 해당 기능은 전적으로 재미를 위해 만들어졌으며 답변을 통한 선택에 대해 본 봇과 개발자는 아무런 책임을 지지 않습니다."
    return resStr
def TrumpetShellAskSell():
    value = random.randrange(0, 3)
    resStr = "마법의 소라고동님께 이 주식을 살지 여쭤봅니다.\n마법의 소라고동님이 답합니다.\n"
    if value == 0:
        resStr += '"존버해"'
    elif value == 1:
        resStr += '"손절해"'
    else:
        resStr += '"추가 매수해"'
    resStr += "\n ** 해당 기능은 전적으로 재미를 위해 만들어졌으며 답변을 통한 선택에 대해 본 봇과 개발자는 아무런 책임을 지지 않습니다."
    return resStr

client.run(os.environ.get("DISCORD_TOKEN"))
