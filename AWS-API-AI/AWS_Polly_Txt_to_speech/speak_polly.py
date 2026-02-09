# Xavier Mojica
#
#AWS API Polly Demo aka Text to Speach 
# dependencies
# pip3 install pydub
#
# Ensure you have the aws cli installed and configured with default region and access credentials
#
# Visit the url for the different voiceId
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly.html#Polly.Client.synthesize_speech

import boto3
import json
import io
from pydub import AudioSegment
from pydub.playback import play

client = boto3.client('polly')

def playsound(speech, voice='Amy'):
	response = client.synthesize_speech(
		Text=speech,
		TextType='text',
		VoiceId=voice,
		OutputFormat='ogg_vorbis',
		SampleRate='8000',
	)

	print(response)
	audiostream = response['AudioStream'].read()
	audiosegment = AudioSegment.from_file(io.BytesIO(audiostream), format="ogg")
	play(audiosegment)


#playsound('Hi there, how can I help you?')
#playsound("Hi there, how's your day going?", 'Gregory')
playsound("Hey there, today's a new day?", 'Russell')

