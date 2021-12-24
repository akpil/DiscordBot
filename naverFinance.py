#BeautifulSoup == markup parser
#To setup bs4 type pip install bs4
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import mysql.connector

class NaverFinance:
    def GetHtmlData(self, company_code):
        url = "https://finance.naver.com/item/main.naver?code=" + company_code
        ua = UserAgent()

        headers = { "User-agent" : ua.ie }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    
    def GetPrice(self, company_code):
        if company_code == None or company_code == "":
            return ""
        soup = self.GetHtmlData(company_code)

        no_today = soup.select_one("p.no_today")
        blind = no_today.select_one("span.blind")
        print(blind.text.replace(',',''))
        return blind.text

    def GetComapnyName(self, cursor, company_code):
        sql = f"Select Name from StockData where StockID = '{company_code}'"
        cursor.execute(sql)
        result = cursor.fetchall()

        if len(result) == 1:
            return result[0][0]
        else:
            return "wrong sotck name"

    def GetCompanyCode(self, cursor, company_name):
        sql = f"Select Name, StockID from StockData where Name like '%{company_name}%'"
        cursor.execute(sql)
        result = cursor.fetchall()

        if len(result) == 1:
            return result[0][1]
        else:
            res = []
            for e in result:
                res.append(e[0])
            return res
