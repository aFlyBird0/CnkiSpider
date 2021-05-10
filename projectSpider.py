import requests

def getJsonOfOneUnitFirstRequest(unit):
    url = "http://kd.nsfc.gov.cn/advancedQuery/data/supportQueryOrgResultsData"
    cookie = "JSESSIONID=909D463F612A9B779F9BEB07A20CB783"
    headers = {'Cookie': cookie, "Content-Type": "application/json;charset=UTF-8", "Connection": "keep-alive"}
    data = {
        "ratifyNo": "",
        "projectName": "",
        "personInCharge": "",
        "dependUnit": "",
        "code": "",
        "projectType": "",
        "subPType": "",
        "psPType": "",
        "keywords": "",
        "ratifyYear": "",
        "conclusionYear": "",
        "adminID": "",
        "beginYear": "",
        "endYear": "",
        "checkDep": "",
        "checkType": "",
        "quickQueryInput": "",
        "ortionID": "76a3a83d9bd32fd90e4908bccdd381cb",
        "pageNum": 95,
        "pageSize": 10,
        "queryType": "input"
    }
    data["dependUnit"] = unit
    r = requests.post(url=url, data=data, headers=headers)
    print(r.text)

if __name__ == '__main__':
    getJsonOfOneUnitFirstRequest("浙江大学")