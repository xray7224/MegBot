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

import re, urllib2, traceback

def main(connection, line):
	if len(line.split()) <= 4:
		line = line + " " + line.split()[0].split("!")[0][1:]
	try:
		i = urllib2.urlopen("http://identi.ca/%s" % line.split()[-1])
		data = i.read()
		last = re.findall("<p class=\"entry-content\">(.+?)</p>", data)[0]
		name = re.findall("<title>(.+?) ", data)[0]
		time = re.findall("> a (.+?) ago </addr>", data)
		if not time:
			time = re.findall(">about (.+?) ago</abbr>", data)[0]
		else:
			time = "a %s ago" % time[0]
		identification = re.findall("<li class=\"hentry notice\" id=\"notice-(.+?)\">", data)[0]
		
		#Fixes tagging
		last = re.sub("<span class=\"tag\"><a href=.*? rel=\"tag\">(.+?)</a></span>", "\g<1>", last)
		#checks for url's
		last = re.sub("<span class=\"vcard\">.*?<span class=\"fn nickname\">(.+?)</span></a></span>", "\g<1>", last)
		last = re.sub("<a href=\"(.+?)\".*?>.*?<\/a>", "\g<1>", last)
		last = re.sub("<span class=\"(.+?)\".*?>.*?<\/span>", "", last)
		last = last.replace("&quot;", "\"").replace("&gt;", ">").replace("&lt;", "<")
		connection.core["privmsg"].main(connection, line.split()[2], "\002[%s]\017 %s - \002Aprox: %s\017 - http://www.identi.ca/notice/%s" % (name, last, time, identification))
	except:
		traceback.print_exc()
		connection.core["privmsg"].main(connection, line.split()[2], "An error has occured")
		