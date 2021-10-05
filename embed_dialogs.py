"A wrapper to create nice-looking embed-style messages"
from nextcord import Embed, Colour

uiEmoji = {
	#Reason      Which emoji to use   The colour of the accent on the left
    "Warn"    : [":warning:",         Colour.yellow()],
	"Error"   : [":no_entry_sign:",   Colour.red()],
    "Playing" : [":arrow_forward:",   Colour.from_rgb(6, 227, 164)],
    "Queued"  : [":speech_balloon:",  Colour.from_rgb(6, 227, 164)],
    "Version" : [":green_heart:",     Colour.from_rgb(6, 227, 164)],
	"Debug"   : [":gear:",            Colour.lighter_grey()]
}

def DialogBox(messageEmoji, messageTitle, messageContent=False):
	if not messageContent:
		embed = Embed(
			title = "{emoji}  {title}".format(emoji=uiEmoji[messageEmoji][0], title=messageTitle),
			colour = uiEmoji[messageEmoji][1]
		)
	else:
		embed = Embed(
			title = "{emoji}  {title}".format(emoji=uiEmoji[messageEmoji][0], title=messageTitle),
			description = messageContent,
			colour = uiEmoji[messageEmoji][1]
		)
	return embed
