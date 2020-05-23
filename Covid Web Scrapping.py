import pandas as pd
import requests
import numpy as np
import pyttsx3
import speech_recognition as sr
import re


web=requests.get("https://www.worldometers.info/coronavirus/")
dfs=pd.read_html(web.text)
data=dfs[0]
data.to_csv("datafile1.csv",index=False)
df = pd.read_csv ('covid_data.csv')
df.drop(df.index[216])
df.replace(np.NaN,"NIL",inplace=True)
#print(df.head())

def get_total_cases(df):
    return float(df['TotalCases'][0])

def get_total_deaths(df):
    return float(df['TotalDeaths'][0])

def get_country_data(df,country):
    ind=0
    info={}
    for c in df['Country,Other']:
        if c.lower()==country:
            break
        ind+=1
    country_info={'Country':country.upper(),'TotalCases':float(df['TotalCases'][ind]),'NewCases':(df['NewCases'][ind])[1:],'TotalDeaths':float(df['TotalDeaths'][ind]),'TotalRecovered':float(df['TotalRecovered'][ind]), }    
    return country_info 

country_list=[]

def get_country_list(df):
    for c in df['Country,Other']:
        country_list.append(c.lower())
    return country_list


def speak(text):
    engine=pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
   
def get_audio():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
        said=""

        try:
            said=r.recognize_google(audio)
        except Exception as e:
            print("Exception:",str(e))

    return said.lower()

def main():
    print("Started Program")
    END_PHRASE="stop"
    result=None
    country_list=set(get_country_list(df))


    TOTAL_PATTERNS= {
                   re.compile("[\w\s]+ total [\w\s]+ cases"):get_total_cases,
                   re.compile("[\w\s]+ total cases"):get_total_cases,
                   re.compile("[\w\s]+ total [\w\s]+ deaths"):get_total_deaths,
                   re.compile("[\w\s]+ total deaths"):get_total_deaths
                   }
    COUNTRY_PATTERNS = {
                re.compile("[\w\s]+ cases [\w\s]+") :lambda df,country:get_country_data(df,country)['TotalCases'],
                re.compile("[\w\s]+ deaths [\w\s]+"):lambda df,country:get_country_data(df,country)['TotalDeaths'],
                re.compile("[\w\s]+ new cases [\w\s]+") :lambda df,country:get_country_data(df,country)['NewCases'],
                re.compile("[\w\s]+ total recovered [\w\s]+") :lambda df,country:get_country_data(df,country)['TotalRecovered']

                }


    while True:
        print("Listening...")
        text=get_audio()
        print(text)
        result=None


        for pattern,func in COUNTRY_PATTERNS.items():
            if pattern.match(text.lower()):
                words=set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result=func(df,country)
                        break


        for pattern,func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result=func(df)
                break

        if result:
            speak(result)

        if text.find(END_PHRASE)!=-1:
            speak('see you later')  #Say stop to come out of the application
            break

main()

