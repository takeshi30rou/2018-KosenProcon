# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json

import dateutil.parser

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
										maxResults=5, singleEvents=True,
										orderBy='startTime').execute()
	events = events_result.get('items', [])
	
	#レスポンスを確認する
	# print("{}".format(json.dumps(events,indent=4,ensure_ascii = False)))

	cal =[]
	for event in events:
		start = event['start'].get('dateTime', event['start'].get('date'))
		end = event['end'].get('dateTime', event['end'].get('date'))
		r = arrangeArrange(start, end)
		if datetime.datetime.now().weekday() == r[2]:
			cal.append([event['summary'],r[0],r[1]])
	return cal

def arrangeArrange(startTime, endTime):
	
	start = dateutil.parser.parse(startTime)
	end = dateutil.parser.parse(endTime)

	returnStart = start.strftime("%H時%M分")
	returnEnd = end.strftime("%H時%M分")
	if not start.strftime("%d") == end.strftime("%d"):
		returnEnd = end.strftime("%d日%H時%M分")
	if not start.strftime("%m") == end.strftime("%m"):
		returnEnd = end.strftime("%m月%d日%H時%M分")
	if not start.strftime("%Y") == end.strftime("%Y"):
		returnEnd = end.strftime("%Y年%m月%d日%H時%M分")
	return returnStart, returnEnd, start.weekday()

if __name__ == '__main__':
	main()
