from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

#時間割
defaultCalendarID = "9ga04rcfpfcme5ksn9cchqobqc@group.calendar.google.com"

def main(calendarID=defaultCalendarID):
	"""Shows basic usage of the Google Calendar API.
	Prints the start and name of the next 10 events on the user's calendar.
	"""

	store = file.Storage('token.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
		creds = tools.run_flow(flow, store)
	service = build('calendar', 'v3', http=creds.authorize(Http()))

	# Call the Calendar API
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

	events_result = service.events().list(calendarId=calendarID, timeMin=now,
										maxResults=9, singleEvents=True,
										orderBy='startTime').execute()
	events = events_result.get('items', [])
	
	#レスポンスを確認する
	# print("{}".format(json.dumps(events,indent=4,ensure_ascii = False)))

	weekday_today = datetime.date.today().weekday() #曜日を取得する
	cal =[]
	for event in events:
		start = event['start'].get('dateTime', event['start'].get('date'))
		end = event['end'].get('dateTime', event['end'].get('date'))
		start = iso_to_hm(start)
		end = iso_to_hm(end)
		if not weekday_today == start[1]:
			cal.append([event['summary'],start[0],end[0]])
		
		print([event['summary'],start[0],end[0]])
	return cal

def iso_to_hm(iso_str):
	import dateutil.parser
	if len(iso_str) == 25:
		time = dateutil.parser.parse(iso_str)
		return time.strftime("%H時%M分"), time.weekday()
	else:
		time = dateutil.parser.parse(iso_str)
		return time.strftime("%m月%d日"), time.weekday()

if __name__ == '__main__':
	main()
