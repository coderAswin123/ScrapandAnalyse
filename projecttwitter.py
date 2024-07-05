import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import getpass
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
#from wordcloud import WordCloud
#import matplotlib.pyplot as plt
#import matplotlib.ticker as mtick
#import seaborn as sns
import streamlit as st

st.title("Twitter Analysis")
my_user = st.text_input(label="UserName",placeholder="Enter UserName") 
my_pass = st.text_input(label="Password",placeholder="Enter Password",type="password") 
search_item= st.text_input(label="About What",placeholder="Enter Search Item") 
if st.button("Analyse"):
    #PATH ="chromedriver.exe"
    driver = webdriver.Chrome()
    driver.get("https://twitter.com/i/flow/login")
    # driver.maximize_window()
    sleep(5)

    user_id=driver.find_element(By.XPATH,"//input[@type='text']")
    user_id.send_keys(my_user)
    user_id.send_keys(Keys.ENTER)
    sleep(5)

    password = driver.find_element(By.XPATH,"//input[@type='password']")
    password.send_keys(my_pass)
    password.send_keys(Keys.ENTER)
    sleep(8)

    search_box = driver.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']")
    search_box.send_keys(search_item)
    search_box.send_keys(Keys.ENTER)
    sleep(8)

    all_tweets = set()
    tweets = driver.find_elements(By.XPATH,"//div[@data-testid='tweetText']")
    while True:
        for tweet in tweets:
            all_tweets.add(tweet.text)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(5)
        tweets = driver.find_elements(By.XPATH,"//div[@data-testid='tweetText']")
        if len(all_tweets)>20:
            break
            
    driver.quit()
    all_tweets = list(all_tweets)
    print(all_tweets[0])

    pd.options.display.max_colwidth = 1000
    stp_words=stopwords.words('english')
    print(stp_words)
    df = pd.DataFrame(all_tweets,columns=['tweets'])
    print(df.head())
    one_tweet=df.iloc[0]['tweets']
    print(one_tweet)

    def TweetCleaning(tweet):
        cleanTweet = re.sub(r"@[a-zA-Z0-9]+","",tweet)
        cleanTweet = re.sub(r"#","",cleanTweet)
        cleanTweet = re.sub(r"\n"," ",cleanTweet)
        cleanTweet = ' '.join(word for word in cleanTweet.split() if word not in stp_words)
        return cleanTweet

    def calPolarity(tweet):
        return TextBlob(tweet).sentiment.polarity

    def calSubjectivity(tweet):
        return TextBlob(tweet).sentiment.subjectivity

    def segmentation(tweet):
        if tweet > 0:
            return "positive"
        if tweet == 0:
            return "neutral"
        else:
            return "negative"
    
    df['cleanedTweets'] = df['tweets'].apply(TweetCleaning)
    df['tPolarity'] = df['cleanedTweets'].apply(calPolarity)
    df['tSubjectivity'] = df['cleanedTweets'].apply(calSubjectivity)
    df['segmentation'] = df['tPolarity'].apply(segmentation)
    print(df.head())
    print(df.pivot_table(index=['segmentation'],aggfunc={'segmentation':'count'}))
    #top 3 most positive
    print(df.sort_values(by=['tPolarity'],ascending=False).head(3))
    # top 3 most negative
    print(df.sort_values(by=['tPolarity'],ascending=True).head(3))
    # 3 neutral
    print(df[df.tPolarity==0].head(3))

    consolidated = ' '.join(word for word in df['cleanedTweets'])

    #wordCloud = WordCloud(width=400, height=200, random_state=20, max_font_size=119).generate(consolidated)
    #plt.imshow(wordCloud, interpolation='bilinear')
    #plt.axis('off')
    #plt.show()

    print(df.groupby('segmentation').count())

    #plt.figure(figsize=(10,5))
    #sns.set_style("whitegrid")
    #sns.scatterplot(data=df, x='tPolarity',y='tSubjectivity',s=100,hue='segmentation')

    #plt.figure(figsize=(10,5))
    #sns.countplot(data=df,x='segmentation')

    positive = round(len(df[df.segmentation == 'positive'])/len(df)*100,1)
    negative = round(len(df[df.segmentation == 'negative'])/len(df)*100,1)
    neutral = round(len(df[df.segmentation == 'neutral'])/len(df)*100,1)

    responses = [positive, negative, neutral]
    print(responses)

    response = {'response': ['Positive', 'Negative', 'Neutral'], 'percentage':[positive, negative, neutral]}
    resdf=pd.DataFrame(response)
    resdf.set_index('response',inplace=True)
    print(resdf)
    st.dataframe(resdf)
    st.bar_chart(resdf)



