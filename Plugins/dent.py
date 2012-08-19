##
#This file is part of MegBot.
#
#   MegBot is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   MegBot is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with MegBot.  If not, see <http://www.gnu.org/licenses/>.
##

import json, urllib2, traceback, time

def main(connection, line):
	if len(line.split()) <= 4:
		line = Raw2Nick(line)
	try:
		i = urllib2.urlopen("http://identi.ca/api/statuses/user_timeline.json?screen_name=%s" % line.split()[-1])
		data = i.read()
		data = json.loads(data)
		if data and not ("-g" in line.split() or "-group" in line.split()):
			# this is from the http://status.net/wiki/Twitter-compatible_API
			name = data[0]["user"]["screen_name"]
			cid = data[0]["id"]
			status = data[0]["text"]
			time = Helper.HumanTime(float(data[0]["created_at"]))
			
		else:
			i = urllib2.urlopen("http://identi.ca/api/statusnet/groups/timeline/%s.json" % line.split()[-1])
			data = i.read()
			data = json.loads(data)
			if data:
				name = data[0]["user"]["screen_name"]
				cid = data[0]["id"]
				status = data[0]["text"]
				time = Helper.HumanTime(float(data[0]["created_at"]))
			else:
				Channel.send("Sorry, they haven't posted on identi.ca")
				return
	except:
		traceback.print_exc()
		Channel.send("An error has occured")
	Channel.send("\002[%s]\017 %s - \002Approx:\017 %s ago - \002Link:\017http://www.identi.ca/notice/%s" % (name, status, time, cid))

help = "Gets the last dent from a specific user/group (or tries your nickname if non is given) from identi.ca (for group support use -g or -group)"
