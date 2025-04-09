#Tsports Cookie Updater Script
#By JESHAN AKAND
#Date 16/12/23
#Last Update 5/4/25


import requests,json,os,urllib3
from urllib.parse import urlparse
urllib3.disable_warnings()

#Environment Variables
api_live_matches=os.environ["api_live_matches"]
file_password=os.environ["file_password"]
api_proxies=os.environ["API_PROXIES"]

def load_proxies(api:str) -> list:
	proxy_list=requests.get(api).text.splitlines()
	for index,proxy in enumerate(proxy_list):
		proxy_list[index] = (lambda p: f"socks5://{p.split(':')[2]}:{p.split(':')[3]}@{p.split(':')[0]}:{p.split(':')[1]}" if len(p.split(':')) == 4 else None)(proxy)
	return proxy_list
    
def update_time():
    from datetime import datetime, timedelta
    import time
    import pytz

    IST = pytz.timezone('Asia/Dhaka')   
    today_date = datetime.now(IST).strftime("%d-%m-%Y") #Current Date
    curr_time = datetime.now(IST).strftime("%H:%M:%S")   #Current time
    
    if int(datetime.now(IST).strftime("%H"))>=5 and int(datetime.now(IST).strftime("%H"))<18:
        emoji="🌞"
    else:
        emoji="🌙"
    if datetime.now(IST).strftime("%H")<"12":
    	curr_time=curr_time+" AM "+emoji
    else:
    	curr_hour=int(datetime.now(IST).strftime("%H"))-12
    	curr_min=datetime.now(IST).strftime("%M")
    	curr_sec=datetime.now(IST).strftime("%S")
    	curr_time=str(curr_hour)+":"+curr_min+":"+curr_sec
    	curr_time=curr_time+" PM "+emoji
    return curr_time,today_date


def update_live_event_info():
    from decode import deecb
    headers={
    "Host":"mapi-cdn.tsports.com",
    "user-agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }
    proxy_list=load_proxies(api_proxies)
    if len(proxy_list)!=0:
        for proxy_url in proxy_list:
            req=requests.get(api_live_matches,headers,proxies = {'http': proxy_url,'https': proxy_url},verify=False)
            if req.status_code==200:break
    else:
        req=requests.get(api_live_matches,headers, verify=False)
    all_data=[]
    decode=json.loads(deecb(req.text))
    print(decode)
    if "contents" in decode["data"]:
        for event in decode["data"]["contents"]:
            name=event["contentName"]
            categoryname=event["categoryName"]
            logo=event["mobileLogo"]
            if len(event["playingMetaData"])!=0 or event["contentAes128HlsUrl"]!=None:
                stream_url=event["contentAes128HlsUrl"] if event["contentAes128HlsUrl"]!=None else event["playingMetaData"][0]["mediaUrl"]
                try:cookie = event["playingMetaData"][0].get("signedCookie", "")
                except:cookie=""
                data={
                        "category_name":categoryname,
                        "name":name,
                        "logo":logo,
                        "link":stream_url,
                        "headers":{
                        "Cookie":cookie,
                        "Host":urlparse(stream_url).netloc,
                        "User-agent":"https://github.com/byte-capsule (Linux;Android 14)"}}
                all_data.append(data)
                
        
    return all_data



def unzip_password_protected_zip(zip_file_path, output_path, password):
    import pyzipper
    try:
        with pyzipper.AESZipFile(zip_file_path) as z:
            z.extractall(output_path, pwd=password.encode('utf-8'))
        return True
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def json_formater(name, output_file_name,data):
    date_time_info=update_time()
    date_time=date_time_info[1]+" on "+date_time_info[0]
    
    data={
    "name":name,
    "owner":"Byte Capsule \nTelegram: https://t.me/J_9X_H_9X_N\nGithub:https://github.com/byte-capsule",
    "channels_amount":len(data),
    "updated_on":date_time,
    "channels":data
    }
    
    
    with open(output_file_name,"w") as w:
        json.dump(data,w,indent=2)
def ns_player_playlist_converter(output_file_name,json_data):
    all_data_ns=[]
    for data in json_data:
        data={
        "name":data["name"],
        "link":data["link"],
        "logo":data["logo"],
        "origin":"https://"+data["headers"]["Host"],
        "referrer":"https://"+data["headers"]["Host"],
        "userAgent":"Tsports (Linux; Telegram:https://t.me/J_9X_H_9X_N) Github:https://github.com/byte-capsule AndroidXMedia3/1.1.1/64103898/4d2ec9b8c7534adc",
        "cookie":data["headers"]["Cookie"],
        "drmScheme":"",
        "drmLicense":""}
        all_data_ns.append(data)
        
    with open(output_file_name,"w") as w:
        json.dump(all_data_ns,w,indent=2)
def ott_negivator_playlist_converter(output_file_name,json_data):
    final_text=""
    for content in json_data:
        final_text+=f'#EXTINF:-1 group-title="{content["category_name"]}" tvg-chno="" tvg-id="" tvg-logo="{content["logo"]}", {content["name"]}'
        final_text+='\n'+f'#EXTVLCOPT:http-user-agent={content["headers"]["User-agent"]}'
        final_text+='\n'+'#EXTHTTP:{"cookie":"'+content["headers"]["Cookie"]+'"}'
        final_text+='\n'+f'{content["link"]}'+"\n"
    with open(output_file_name,"w") as w:
        w.write(final_text)
            
            
if __name__=="__main__":
    
    #Extract Password protected Code File
    unzip_password_protected_zip("enc-cracker.py","",file_password)
    #Update Live Event Data
    data=update_live_event_info()
    
    #Remove Temporary Files 
    os.remove("decode.py")
    
    #Conver in Json Format
    json_formater("TSports App All Live Matches Data in Json","TSports_m3u8_headers.Json",data)
    #Convert Ns Player PlayList 
    ns_player_playlist_converter("NS_Player_Tsports_live.m3u",data)
    #Convert OTT_Navigator PlayList 
    ott_negivator_playlist_converter("OTT_Navigator_Tspots_live.m3u",data)
    
