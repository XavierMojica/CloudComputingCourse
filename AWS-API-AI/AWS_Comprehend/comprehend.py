#*********************************************************************************************************************
# Xavier Mojica
# AWS Comprehend API Demo
# https://docs.aws.amazon.com/comprehend/latest/dg/functionality.html
#*********************************************************************************************************************

import boto3
import json

comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')
text = "Good nature and good sense must ever join; To err is human, to forgive, dive. C'était pour elle une misère noire, la misère en robe de soie. Qué es la vida? Un frenesí. Qué es la vida? Una ilusión, una sombra, una ficción, y el mayor bien es pequeño; que toda la vida es sueño, y los sueñ1os, sueños son. "
#text = "I hate your guts! Why would you ever do that to me!"
#text = "You are my heart, my angel, and my life. I can't live without you being by my side for all of time. I can only think of your sweet words, and beautiful hair"


print("Calling DetectDominantLanguage")
print(json.dumps(comprehend.detect_dominant_language(Text = text), sort_keys=True, indent=4))

print('Calling DetectEntities')
#using English detection,  LanguageCode = 'en'
print(json.dumps(comprehend.detect_entities(Text=text, LanguageCode='en'), sort_keys=True, indent=4))

print('Calling DetectKeyPhrases')
print(json.dumps(comprehend.detect_key_phrases(Text=text, LanguageCode='en'), sort_keys=True, indent=4))

print('Calling DetectSentiment')
print(json.dumps(comprehend.detect_sentiment(Text=text, LanguageCode='en'), sort_keys=True, indent=4))

print('Calling DetectSyntax')
print(json.dumps(comprehend.detect_syntax(Text=text, LanguageCode='en'), sort_keys=True, indent=4))

print('All done\n')

