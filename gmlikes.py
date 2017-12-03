import requests
import collections
import matplotlib.pyplot as plt
import operator
import sys
import numpy as np

#function to generate url for next batch of messages
def get_url(message_id, group_id, toke):
	#GroupMe limits message batch to 100
	limit = 100
	url = 'https://api.groupme.com/v3/groups/{}/messages?token={}&limit={}&before_id={}'.format(group_id, token, limit, message_id)
	return url

if len(sys.argv) < 3:
	print("Incorrect usage. Try: python analytics.py [group id] [token]")
	sys.exit(0)

#getcommand line args
group_id = sys.argv[1]
token = sys.argv[2]

#print verification of args
print('group id: ' + group_id)
print('token: ' + token)

#count of processed messages
count = 0
#dictionary mapping user ids to like number
senders = collections.defaultdict(int)
#dictionary mapping user id to group nickname
names = dict()

initial_url = 'https://api.groupme.com/v3/groups/{}/messages?token={}&limit=100'.format(group_id, token)
request = requests.get(initial_url)

#exit on invalid token or group id
if request.status_code == 404:
	print("Incorrect token or group id")
	sys.exit(0)

#get json from http request
data = request.json()
count += len(data['response']['messages'])

#use message id of last message if there exists the full batch of messages
if count == 100:
	message_id = data['response']['messages'][99]['id']
else:
	#use the id of first message
	message_id = data['response']['messages'][0]['id']

while 1:
	url = get_url(message_id, group_id, token)
	request = requests.get(url)

	if request.status_code == 304:
		break
		
	data = request.json()
	count += len(data['response']['messages'])
	total = data['response']['count']

	#iterate through messages and add likes to each respective user
	for message in data['response']['messages']:
		for liker in message['favorited_by']:
			senders[liker] += 1
		names[message['sender_id']] = message['name']

	#print progress
	print('Processed {} messages of {}'.format(count, total), end="\r")

	#stop when hit total messages
	batch_count = len(data['response']['messages'])
	if count != total:
		message_id = data['response']['messages'][batch_count-1]['id']
	else:
		break

##### generate matplotlib chart #####

#create list of names
sorted_senders = sorted(senders.items(), key=operator.itemgetter(1))
n = list()
for sender in sorted_senders:
	n.append(names[sender[0]])

y_pos = np.arange(len(n))

plt.figure(figsize=(20, 3))
plt.bar(y_pos, [s[1] for s in sorted_senders], align='edge', width=0.3, alpha=0.5)
plt.xticks(y_pos, n)
plt.ylabel('Likes')
plt.title('Likes By User')

plt.savefig('likes_by_user.png')

print('Created \'likes_by_user.png\'')


