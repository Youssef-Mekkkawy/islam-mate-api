import requests



session = requests.Session()
content = session.get("https://qul.tarteel.ai/resources/recitation")

with open("file.html", 'w', encoding="utf-8") as file:
    file.write(content.text)