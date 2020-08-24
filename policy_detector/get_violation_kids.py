#python3
import csv
import os

from profanity import profanity
from better_profanity import profanity as profanity2
from profanityfilter import ProfanityFilter
profanity3 = ProfanityFilter()

import re
import spacy
nlp=spacy.load('/home/song/Downloads/en_core_web_lg-2.2.5/en_core_web_lg/en_core_web_lg-2.2.5')
import string

skills=[]


###################### get output data ################################


#b=os.listdir('outputdata')
number=0
name={}
des={}
des2={}
#note={}
#for i in b:
f=open('outputdata/skill_output.csv','r')
reader=csv.reader(f,delimiter=',')
for row in reader:
	number=number+1
	name[number]=row[1]
	des[number]=row[2]
	des2[number]=row[3]
#	note[number]=row[3]

f.close()

for i in des:
	des[i]=des[i]+'. '+des2[i]

for i in des:
	des[i]=des[i].replace('\n','').lower()

###################### checking profanity ################################

for i in des:
	if profanity.contains_profanity(des[i]) and profanity2.contains_profanity(des[i]) and profanity3.is_profane(des[i]):
		skills.append((i,"contains profanity"))

###################### checking data collection ################################

question_words=['who', 'what', 'when', 'where', 'why','which', 'how', 'is', 'am', 'are', 'was', 'were', 'do', 'does', 'did', 'can', 'may', 'might', 'could', 'will', 'would', 'shall', 'should', 'had', 'has', 'have']

question_words=['who', 'what', 'when', 'where', 'which', 'please']

noun=['address', 'name','first name','last name', 'email', 'birthday', 'age', 'gender', 'location', 'data', 'contact', 'phonebook', 'SMS', 'call', 'profession', 'income', 'ssn','zip code','zipcode']

add_sentences=["how old are you","when were you born","where do you live","where are you from", "what can i call you"]


for i in des:
	sentences = re.split(r' *[\n\,\.!][\'"\)\]]* *', des[i])
	for j in sentences:
		words = re.sub("[^\w]", " ",  j).split()
		if set(words)-(set(words)-set(noun))!=set() and 'your' in words and set(words)-(set(words)-set(question_words))!=set():
			doc=nlp(j)
			for k in doc.noun_chunks:
				if 'your' in k.text and set(noun)-(set(noun)-set(k.text.split())) and (k.root.head.pos_=='AUX' or k.root.head==k.root.head.head):
					print(j)
					print('\n')
					skills.append((i,"contains data collection"))
	for k in add_sentences:
		if k in des[i].translate(str.maketrans('', '', string.punctuation)):
			print(des[i])
			print('\n')
			skills.append((i,"contains data collection"))


for i in des:
	if 'your' in des[i]:
		for j in noun:
			if 'your '+j in des[i]:
				if (i,"contains data collection") not in skills:
					skills.append((i,"contains data collection"))

for i in des:
	for j in add_sentences:
		if j in des[i]:
			skills.append((i,"contains data collection"))
###################### checking general policy ################################

f=open('policy.txt','r')
amazonpolicy=f.read().split('\n')[:-1]
f.close()


policy_content=[]
policy_activity=[]

for i in amazonpolicy:
	doc=nlp(i)
	n=0
	for j in doc:
		if j.pos_=='VERB':
			policy_activity.append(doc)
			n=1
			break
	if n==0:
		policy_content.append(doc)

def getverb(i):
	if i.head.pos_=='VERB':
		return i.head
	elif i.head==i:
		return i
	else:
		return getverb(i.head)

threshold=0.9

for i in des:
	doc=nlp(des[i])
	content=[]
	activity=[]
	for j in doc.noun_chunks:
		content.append(j)
		activity.append(nlp(getverb(j.root).text+' '+j.text))
	for j in content:
		for k in policy_content:
			if j.vector_norm and j.similarity(k)>threshold:
				skills.append((i,"contains "+k.text))
	for j in activity:
		for k in policy_activity:
			if j.vector_norm and j.similarity(k)>threshold:
				skills.append((i,"contains "+k.text))

for i in des:
	if '5 star' in des[i] or 'five star' in des[i]:
		skills.append((i,"contains asking for rating"))

###################### checking advertisement ################################

buy_words=['test','try','buy']

for i in des:
	if 'www.' in des[i] or ('.com' in des[i] and '@' not in des[i]) or 'website' in des[i]:
		skills.append((i,"contains out website"))

for i in des:
	if 'dot' in des[i] and ' com' in des[i]:        
		if 'com' in des[i][des[i].find('dot')-100:des[i].find('dot')+100]:
			skills.append((i,"contains out website"))



for i in des:
	if 'try our' in des[i] and 'you' in des[i]:
		skills.append((i,"contains advertisement"))		

for i in des:
	if 'product' in des[i]:
		des_nlp=nlp(des[i])
		for j in des_nlp:
			if 'product' in j.text and j.head.text in buy_words:
				skills.append((i,"contains advertisement"))


###################### checking illegal ################################

f=open('illegal.txt','r')
illegal=f.read().split('\n')[:-1]
f.close()

for i in des:
	words = re.sub("[^\w]", " ",  des[i]).split()
	if set(words)-(set(words)-set(illegal))!=set():
		print(des[i])
		print('\n')
		skills.append((i,"contains illegal content"))

###################### checking sex ################################

f=open('sex.txt','r')
sex=f.read().split('\n')[:-1]
f.close()

for i in des:
	words = re.sub("[^\w]", " ",  des[i]).split()
	if set(words)-(set(words)-set(sex))!=set():
		print(des[i])
		print('\n')
		skills.append((i,"contains sex content"))

###################### checking violence ################################

f=open('violence.txt','r')
violence=f.read().split('\n')[:-1]
f.close()

for i in des:
	words = re.sub("[^\w]", " ",  des[i]).split()
	if set(words)-(set(words)-set(violence))!=set():
		print(des[i])
		print('\n')
		skills.append((i,"contains violence content"))


skills.sort()
print(len(skills))
print(skills)

########################### write potential violation  #########################


f=open('violation.txt','w')
for i in skills:
	f.write(str(i[0])+'\t'+name[i[0]]+'\t'+des[i[0]]+'\t'+i[1])
	f.write('\n')

f.close()

