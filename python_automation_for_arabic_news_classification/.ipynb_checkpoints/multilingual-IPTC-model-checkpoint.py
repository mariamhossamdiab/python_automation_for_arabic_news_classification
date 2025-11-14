from transformers import pipeline
import pandas as pd

# Load the multilingual news topic classifier
classifier = pipeline(
    "text-classification",
    model="classla/multilingual-IPTC-news-topic-classifier",
    max_length=128,
    truncation=True
)

# Read the uploaded Excel file
df = pd.read_excel("elshrouk.xlsx")

# Select the first 5 articles
x = df['Article_Text'][0:5]
my_list = x.tolist()

# Run classification
results = classifier(my_list)
# Display results
for i, result in enumerate(results):
    print(f"Article {i+1}: {result}")
import joblib
model = joblib.load("RandomForestClassifier_model.joblib")
my_list = x.tolist()
# Get prediction
prediction = model.predict(my_list)
for i, result in enumerate(prediction):
    print(f"Article {i+1}: {result}")