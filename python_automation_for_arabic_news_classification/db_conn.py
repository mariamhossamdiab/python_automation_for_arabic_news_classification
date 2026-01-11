import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime, date, time, timedelta
import time as time_module

def ccc(input_file):
    # Read CSV and replace textual NaN/NULLs with actual None
    df = pd.read_csv(f"{input_file}")
    df.fillna("unknown", inplace=True)
    #df = df.where(pd.notnull(df), None)
    #print(df)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="news"
    )
    cursor = conn.cursor()
    print("✅ Database connection established")

    inserted_count = 0

    for idx, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO classified_news (
                    Title, Link, website, Article_Text,date,topic,
                   classification, confidence_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
            """, (
                row.get("Title"),
                row.get("Link"),
                row.get("website"),  # ✅ fixed typo here
                row.get("Article_Text"),
                 row.get("date"),
                row.get("topic"),
                row.get("classification"),
                row.get("confidence_score")
               
            ))
            inserted_count += 1
        except Exception as e:
            print(f"⚠️ Failed to insert row {idx}: {e}")
            continue
    cursor.execute("""
        DELETE FROM classified_news
        WHERE date < NOW() - INTERVAL 4 DAY
        """)    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Inserted {inserted_count} rows successfully")

files = [
"classified_data/elshrouk_reality.csv",
 "classified_data/elmasrielyoum_reality.csv",
 "classified_data/elwatan_reality.csv",
 "classified_data/masrawy_reality.csv",
 "classified_data/youm7_reality.csv",
 "classified_data/elbashayer_reality.csv"
]
for file in files:
    ccc(file)

def bbb(input_file):
    wesite_name = input_file.split("/")[2].split("_")[0]
    wesite_name+= ".com"
    # Read CSV and replace textual NaN/NULLs with actual None
    df = pd.read_csv(f"{input_file}")
    #df = df.where(pd.notnull(df), None)
    #print(df)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="news"
    )
    cursor = conn.cursor()
    print("✅ Database connection established")

    inserted_count = 0
    x=datetime.now()
    for idx, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO trend (
                    phrase ,phrase_count , Website ,date)
                
                VALUES (%s, %s, %s, %s)
            """, (
                row.get("phrase"),
                row.get("phrase_count"),
                wesite_name,          # ✅ FIXED
                datetime.now()  
            ))
            inserted_count += 1
        except Exception as e:
            print(f"⚠️ Failed to insert row {idx}: {e}")
            continue
    cursor.execute("""
        DELETE FROM trend 
        WHERE date < NOW() - INTERVAL 120 MINUTE
        """)    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Inserted {inserted_count} rows successfully")

files = [
"my_data/news_insights_output/elshrouknews_ngrams.csv",
 "my_data/news_insights_output/elmasrielyoum_ngrams.csv",
 "my_data/news_insights_output/elwatannews_ngrams.csv",
 "my_data/news_insights_output/masrawy_ngrams.csv",
 "my_data/news_insights_output/youm7_ngrams.csv",
 "my_data/news_insights_output/elbashayer_ngrams.csv"
]
for file in files:
    bbb(file)    