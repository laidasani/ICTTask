# importing libraries 
import os 
import shutil
import sys
from pythonlibraries.pydub import AudioSegment
from pythonlibraries.pydub.silence import split_on_silence 
from pythonlibraries import speech_recognition as sr

# Function that splits the audio file into chunks, by breaking them through silence, to get the number of silences in the audio.
# This function also applies speech recognition to each chunk to get words per minute and word frequency. 
def helper(inputFilePath): 

	# Open the audio file (.wav) that is passed as an argument to command line 
	inputAudio = AudioSegment.from_wav(inputFilePath) 

	# stores the length of the audio in milli seconds
	lenthAudio=len(inputAudio)

	#JUST FOR TESTING: Writes the audio to a text file after speech conversion
	#fh = open("audio.txt", "w+") 
		
	# Split track where silence is 1.5 seconds or more, and audio threshold is less than -30DBFS.
	# keep_silence keeps silence of 3000ms i.e 1500ms to start and end of the chunk. 
	chunks = split_on_silence(inputAudio, min_silence_len = 1500, silence_thresh = -30, keep_silence=3000) 

	try: 
		#Creating temporary directory to temporarily store audio chunks
		os.mkdir('AudioChunks') 
	except(FileExistsError): 
		pass

	os.chdir('AudioChunks') 

	i = 1
	numberOfSilences=0
	wordCount=0
	wordDict={}

	for chunk in chunks: 
		# Create 1 second silence chunk.
		silentChunk = AudioSegment.silent(duration = 1000) 

		# Add 1 second silence to beginning and end of audio chunk. 
		audioChunk = silentChunk + chunk + silentChunk 		

		# Export audio chunk and save it in the current directory. 
		audioChunk.export("./chunk{0}.wav".format(i), bitrate ='192k', format ="wav") 

		# The name of the newly created chunk.
		file = 'chunk'+str(i)+'.wav'

		#Creating speech recognition object
		r = sr.Recognizer() 
 
		with sr.AudioFile(file) as source: 
			audioRecorded = r.record(source) 

		try: 
			#use recognize_google method of the library to convert speech to text
			audioText = r.recognize_google(audioRecorded) 

			#JUST FOR TESTING: Writing each chunk to text file
			#fh.write(audioText+". ") 

			#Split words to individual word and make a mapping for word frequency.
			words = audioText.split()
			for word in words:
				word=word.lower()
				wordCount+=1
				if(word in wordDict.keys()):
					wordDict[word]=wordDict[word]+1
				else:
					wordDict[word]=1

		#Print this to console if the particular chunk was clear to understand for coversion from speech to text.
		except sr.UnknownValueError: 
			print("Could not understand audio for chunk number "+str(i)) 

		#Print this to console if any other error like Internet Connection Issue (recognize_google() requires internet connection)
		except sr.RequestError as e: 
			print("Could not request results. check your internet connection") 

		i += 1

	os.chdir('..') 

	#PRINTING RESULTS TO CONSOLE	
	if(len(chunks)==0):
		numberOfSilences=len(chunks)
	else:
		numberOfSilences=len(chunks)-1

	WPM=(wordCount*60)*1000/lenthAudio

	print("Number of silences: "+str(numberOfSilences))
	print("Words Per Minute: "+str(WPM))
	print("Word Frequency List: "+str(wordDict))

	#Removing the temporary directory and all the audio chunks
	shutil.rmtree('AudioChunks')

if __name__ == '__main__':

	inputFile = sys.argv[1]
	helper(inputFile) 