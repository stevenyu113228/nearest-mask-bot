from flask import Flask,request


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage
)


import pandas
from geopy.distance import geodesic

import urllib.parse

global df1
df1 = pandas.read_csv("https://raw.githubusercontent.com/kiang/pharmacies/master/data.csv")

def get_mask(my_x,my_y,adult = True):
    global df1
    df = pandas.read_csv("https://data.nhi.gov.tw/resource/mask/maskdata.csv")
    df1 = df1[['醫事機構代碼','TGOS X','TGOS Y']]
    df2 = df.set_index('醫事機構代碼').join(df1.set_index('醫事機構代碼'), lsuffix='_caller', rsuffix='_other')
    df2 = df2.dropna(subset=['TGOS X'])
    df2 = df2.reset_index()
    
    k = '成人口罩總剩餘數' if adult == True else '兒童口罩剩餘數'
    available = df2[df2[k]>0]
    
    distance  = []
    for _, row in available.iterrows():
        distance.append(geodesic((my_y,my_x), (row['TGOS Y'],row['TGOS X'])).m)
        
    available  = available.assign(dist = distance)
    return available.sort_values(by='dist')


line_bot_api = LineBotApi('')
handler = WebhookHandler('')

# one_data =  




app = Flask(__name__)

@app.route('/',methods = ['GET','POST'])
def root():
    if request.method == 'POST':
        print(request.json)
        for event in request.json['events']:
            if event['message']['type'] == 'location':
                my_y = event['message']['latitude']
                my_x = event['message']['longitude']
                sorted_available = get_mask(my_x,my_y,True)
                d = sorted_available[:10].to_dict('records')

                flex_dict = {
                "type": "carousel",
                "contents": []
                }

                # c = []
                for i in d:
                    flex_dict['contents'].append({
                    "type": "bubble",
                    "size": "micro",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": i['醫事機構名稱'],
                            "weight": "bold",
                            "size": "md",
                            "wrap": True,
                            "align": "center"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                            {
                                "type": "text",
                                "text": "地址：",
                                "wrap": True,
                                "color": "#8c8c8c",
                                "size": "xs",
                                "flex": 5,
                                "contents": [
                                {
                                    "type": "span",
                                    "text": "地址：",
                                    "color": "#000000"
                                },
                                {
                                    "type": "span",
                                    "text": i['醫事機構地址']
                                }
                                ],
                                "align": "start",
                                "gravity": "top",
                                "margin": "lg"
                            },
                            {
                                "type": "text",
                                "text": "地址：",
                                "wrap": True,
                                "color": "#8c8c8c",
                                "size": "xs",
                                "flex": 5,
                                "contents": [
                                {
                                    "type": "span",
                                    "text": "距離：",
                                    "color": "#000000"
                                },
                                {
                                    "type": "span",
                                    "text": str(int(i['dist'])) + ' m'
                                }
                                ],
                                "margin": "md"
                            },
                              {
                                "type": "text",
                                "text": "電話：",
                                "wrap": True,
                                "color": "#8c8c8c",
                                "size": "xs",
                                "flex": 5,
                                "contents": [
                                {
                                    "type": "span",
                                    "text": "電話：",
                                    "color": "#000000"
                                },
                                {
                                    "type": "span",
                                    "text": i['醫事機構電話']
                                }
                                ],
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "地址：",
                                "wrap": True,
                                "color": "#8c8c8c",
                                "size": "xs",
                                "flex": 5,
                                "contents": [
                                {
                                    "type": "span",
                                    "text": "成人口罩數量：",
                                    "color": "#000000"
                                },
                                {
                                    "type": "span",
                                    "text": str(i['成人口罩總剩餘數'])
                                }
                                ],
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "地址：",
                                "wrap": True,
                                "color": "#8c8c8c",
                                "size": "xs",
                                "flex": 5,
                                "contents": [
                                {
                                    "type": "span",
                                    "text": "兒童口罩數量：",
                                    "color": "#000000"
                                },
                                {
                                    "type": "span",
                                    "text": str(i['兒童口罩剩餘數'])
                                }
                                ],
                                "margin": "md"
                            }
                            ],
                            "margin": "lg"
                        }
                        ],
                        "spacing": "sm",
                        "paddingAll": "13px"
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "button",
                            "action": {
                            "type": "uri",
                            "label": "電話",
                            "uri": 'tel:' + i['醫事機構電話'].replace('(','').replace(')','')
                            }
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "uri",
                            "label": "導航",
                            "uri": "http://www.google.com.tw/maps/search/" + urllib.parse.quote(i['醫事機構地址'])
                            }
                        }
                        ],
                        "spacing": "sm",
                        "paddingAll": "13px"
                    }
                    })

                line_bot_api.reply_message(
                event['replyToken'],
                FlexSendMessage(alt_text="喵",
                contents=flex_dict))
            else:
                line_bot_api.reply_message(
                    event['replyToken'],
                    TextSendMessage(text='發定位給我LA\nQQ\n喵喵')
                )
    return '1'

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',port = 5463)