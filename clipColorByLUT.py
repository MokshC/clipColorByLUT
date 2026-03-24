#!/usr/bin/env python

# Created by: Moksh Chitkara
# Last Update: Mar 24th 2026
# v0.1.0
# Copyright (C) 2026  Moksh Chitkara
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime

# Global Variables
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()

class ColorRef():

	def __init__(self):
		self.availColor = ["Orange", "Apricot", "Yellow", "Lime", "Olive", "Green", "Teal", "Navy", "Blue", "Purple", "Violet", "Pink", "Tan", "Beige", "Brown", "Chocolate"]
		self.usedColor = []
		self.dict = {}

	def __str__(self):
		if not self.dict:
			return "No Colors Assigned Yet."
		line = ""
		for key in self.dict:
			line += str(self.dict[key]) + ": " + str(key) + "\n"
		return line
		
	def addKey(self, key):
		if (self.availColor) and (key not in self.dict):
			usingColor = self.availColor.pop(0)
			self.usedColor.append(usingColor)
			self.dict[key] = usingColor
			return True
		else:
			return False

################################################################################################
# Window creation #
###################
def main_ui():
	# vertical group
	window = [ui.VGroup({"Spacing": 15,},[
			# horizontal groups
			# button for export
			ui.Button({"ID": "Start", "Text": "Start Coloring!", "Weight": 0}),
			#
			ui.TextEdit({"ID": "textbox", "Text": 
"""
This script will color clips based on the first LUT found on the color page.
This WILL overwrite existing clip colors.
""", 
			
			"Weight": 1})
			]) 
		]
	return window

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Color by LUT",
			"ID": "CCBLWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [1500,500,700,250], # x-position, y-position, width, height
			}, 
			main_ui())

itm = window.GetItems() # Grabs all UI elements to be manipulated
################################################################################################
# Functions #
#############

def log(info, level = 1):

	if level == 1:
		level = "INFO"
	elif level == 2:
		level = "WARN"
	else:
		level = "EROR"
		
	time = datetime.datetime.now()
	
	fullLog = [str(time), level, info]
	print(" | ".join(fullLog))	

def _main(ev):

	itm['Start'].Enabled = False
	itm['Start'].Text = "Starting..."
	
	log("Start Clicked")
	
	ref_main = ColorRef()
	timeline = project.GetCurrentTimeline()

	log("Main Ref Created")

	track_range = reversed(range(1, timeline.GetTrackCount("video")+1))
	for track in track_range:
		log("Starting on track: " + str(track))
		track_items = timeline.GetItemListInTrack("video",track)
		total = len(track_items)
		prog = 0
		for item in track_items:
			prog += 1
			loading = "{:.2%}".format(float(prog)/float(total))
			itm['Start'].Text = "Matching Track {}: {}".format(track, loading)
			nodes = item.GetNodeGraph(1)	# get nodes
			if nodes != None:
				for node_idx in range(1, nodes.GetNumNodes() + 1):
					tools = nodes.GetToolsInNode(node_idx)
					if tools:
						for tool in tools:
							if 'LUT:' in tool:
								ref_main.addKey(tool[5:])
								colorName = ref_main.dict[tool[5:]]
								item.SetClipColor(colorName)
								log(str(item.GetName()) + ": Found LUT " + str(tool[5:]) + " and set color to " + str(colorName))
								itm['textbox'].Text = str(ref_main)
								break
			else:
				log(str(item.GetName()) + " Nodes == None", 2)
			
	itm['Start'].Text = "Start Coloring!"
	itm['Start'].Enabled = True
	
# needed to close window
def _close(ev):
	disp.ExitLoop()

################################################################################################
# GUI Elements #
# manipulations
# button presses
window.On.Start.Clicked = _main
window.On.CCBLWin.Close = _close
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################
