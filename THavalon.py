#!/usr/bin/env python3

import copy
import os
import random
import shutil
import sys

def main():
	if not (6 <= len(sys.argv) <= 11):
		print("Invalid number of players")
		exit(1)

	players = sys.argv[1:]
	num_players = len(players)
	players = set(players) # use as set to avoid duplicate players
	players = list(players) # convert to list
	random.shuffle(players) # ensure random order, though set should already do that
	if len(players) != num_players:
		print("No duplicate player names")
		exit(1)

	# choose 3 players
	three_players = random.sample(players, 3)

	# first two proppose for the first mission, last is starting player of second round
	first_mission_proposers = three_players[:2]
	second_mission_starter = three_players[2]

	all_good_roles_in_order = ["Percival", "Merlin", "Tristan", "Iseult", "Arthur", "Lancelot", "Guinevere", "Gawain", "Titania", "Galahad"]
	all_evil_roles_in_order = ["Mordred", "Morgana", "Maelegant", "Agravaine", "Colgrevance", "Oberon"]

	# assign the roles in the game
	good_roles = ["Merlin", "Percival", "Guinevere", "Lancelot", "Lovers"]
	evil_roles = ["Mordred", "Morgana", "Maelegant", "Oberon"]

	if num_players >= 7:
		# good_roles.append("Guinevere")
		good_roles.append("Arthur")
		good_roles.append("Titania")
		# evil_roles.append("Oberon")

	if num_players >= 8: 
		evil_roles.append("Agravaine")
		
	if num_players == 10:
		good_roles.append("Gawain")
		evil_roles.append("Colgrevance")

	# shuffle the roles
	random.shuffle(good_roles)
	random.shuffle(evil_roles)

	# determine the number of roles in the game
	if num_players == 10:
		num_evil = 4
		num_good = 6
	elif num_players == 9:
		num_evil  = 3
		num_good = 4
	elif num_players == 7 or num_players == 8:
		num_evil = 3
		num_good = num_players - num_evil 
	else: # 5 or 6
		num_evil = 2
		num_good = num_players - num_evil 

	# assign players to teams
	assignments = {}
	reverse_assignments = {}
	good_roles_in_game = set()
	evil_roles_in_game = set()
	roles_in_game = set()

	if num_players == 9:
		pelinor = players[8]
		assignments[pelinor] = "Pelinor"
		reverse_assignments["Pelinor"] = pelinor

		questing_beast = players[7]
		assignments[questing_beast] = "Questing Beast"
		reverse_assignments["Questing Beast"] = questing_beast

	good_players = players[:num_good]
	evil_players = players[num_good:num_good + num_evil]


	# assign good roles
	for good_player in good_players:
		player_role = good_roles.pop()
		assignments[good_player] = player_role
		reverse_assignments[player_role] = good_player
		good_roles_in_game.add(player_role)
		roles_in_game.add(player_role)

	# assign evil roles
	for evil_player in evil_players:
		player_role = evil_roles.pop()
		assignments[evil_player] = player_role
		reverse_assignments[player_role] = evil_player
		evil_roles_in_game.add(player_role)
		roles_in_game.add(player_role)

	if "Lovers" in good_roles_in_game: 
		good_roles_in_game.remove("Lovers")
		# lovers -> tristan
		good_roles_in_game.add("Tristan")
		good_roles_in_game.add("Iseult")
		tristan_player = reverse_assignments["Lovers"]
		assignments[tristan_player] = "Tristan" 
		del reverse_assignments["Lovers"]
		reverse_assignments["Tristan"] = tristan_player
		# random other good -> iseult
		good_players_no_tristan = list(set(good_players)) 
		good_players_no_tristan.remove(tristan_player)
		iseult_player = str(random.sample(good_players_no_tristan, 1)[0])
		old_role_iseult = assignments[iseult_player]
		del reverse_assignments[old_role_iseult]
		good_roles_in_game.remove(old_role_iseult)
		assignments[iseult_player] = "Iseult" 
		reverse_assignments["Iseult"] = iseult_player
		
	# lone percival -> galahad
	if ("Percival" in good_roles_in_game and "Merlin" not in good_roles_in_game and "Morgana" not in evil_roles_in_game and num_players >= 7):
		good_roles_in_game.remove("Percival")
		good_roles_in_game.add("Galahad")
		percival_player = reverse_assignments["Percival"]
		assignments[percival_player] = "Galahad" 
		del reverse_assignments["Percival"]
		reverse_assignments["Galahad"] = percival_player
	
	# missing roles
	missing_roles_good = list(set(good_roles) - set(good_roles_in_game))
	missing_roles_evil = list(set(evil_roles) - set(evil_roles_in_game))
	# print(missing_roles_good)
	# print(missing_roles_evil)
	
	oberon_target_role = ""
	oberon_seen = ""
	if ("Oberon" in evil_roles_in_game):
		good_roles_for_oberon = list(set(good_roles_in_game))  
		if "Lancelot" in good_roles_in_game:
			good_roles_for_oberon.remove("Lancelot") 
		if "Titania" in good_roles_in_game:
			good_roles_for_oberon.remove("Titania") 
		if "Gawain" in good_roles_in_game:
			good_roles_for_oberon.remove("Gawain") 
		random.shuffle(good_roles_for_oberon)
		oberon_target_role = good_roles_for_oberon[0] 
	
	titania_target_role = ""
	titania_seen = ""
	if ("Titania" in good_roles_in_game):
		evil_roles_for_titania = list(set(evil_roles_in_game))  
		random.shuffle(evil_roles_for_titania)
		titania_target_role = evil_roles_for_titania[0] 
		
	# delete and recreate game directory
	if os.path.isdir("game"):
		shutil.rmtree("game")
	os.mkdir("game")

	# make every role's file

	# Merlin sees: Morgana, Maelegant, Oberon, Agravaine, Colgrevance, Lancelot* as evil 
	if "Merlin" in good_roles_in_game:
		player_name = reverse_assignments["Merlin"]
		# determine who Merlin sees
		seen = []
		for evil_player in evil_players:
			if assignments[evil_player] != "Mordred":
				seen.append(evil_player)
		if "Lancelot" in good_roles_in_game:
			seen.append(reverse_assignments["Lancelot"])
					
		# oberon 
		if oberon_target_role == "Merlin": 
			unseen = [player for player in players if player not in seen]
			if (player_name in unseen):
				unseen.remove(player_name)
			random.shuffle(unseen)
			oberon_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)
		
		# and write this info to Merlin's file
		
		filename = "game/" + player_name
		with open(filename, "w") as file:
			file.write("You are Merlin.\n")
			if oberon_target_role == "Merlin": 
				file.write("\nYOU HAVE BEEN OBERONED.\nYou see one additional person who is neither Evil nor Lancelot.\n\n")
			for seen_player in seen:
				file.write("You see " + seen_player + " as evil (or Lancelot).\n")
		

	# Percival sees Merlin, Morgana* as Merlin
	if "Percival" in good_roles_in_game:
		player_name = reverse_assignments["Percival"]
		# determine who Percival sees
		seen = []
		if "Merlin" in good_roles_in_game:
			seen.append(reverse_assignments["Merlin"])
		if "Morgana" in evil_roles_in_game:
			seen.append(reverse_assignments["Morgana"])
		# oberon 
		if oberon_target_role == "Percival": 
			unseen = [player for player in players if player not in seen]
			if (player_name in unseen):
				unseen.remove(player_name)
			random.shuffle(unseen)
			oberon_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)
		

		# and write this info to Percival's file
		filename = "game/" + player_name
		with open(filename, "w") as file:
			file.write("You are Percival.\n")
			if oberon_target_role == "Percival": 
				file.write("\nYOU HAVE BEEN OBERONED.\nYou see one additional person who is neither Merlin nor Morgana.\n\n")
			for seen_player in seen:
				file.write("You see " + seen_player + " as Merlin (or Morgana).\n")
			if len(seen) == 0:
				file.write("\nFin.\n");

	if "Tristan" in good_roles_in_game:
		# write the info to Tristan's file
		player_name = reverse_assignments["Tristan"]
		filename = "game/" + player_name
		seen = []
		if "Iseult" in good_roles_in_game:
			seen.append(reverse_assignments["Iseult"])
		# oberon 
		if oberon_target_role == "Tristan": 
			unseen = [player for player in players if player not in seen]
			if (player_name in unseen):
				unseen.remove(player_name)
			random.shuffle(unseen)
			oberon_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)

		with open(filename, "w") as file:
			file.write("You are Tristan.\n")
			# write Iseult's info to file
			if oberon_target_role == "Tristan": 
				file.write("YOU HAVE BEEN OBERONED.\nYou see one additional person who is not your lover.\n")
			for seen_player in seen:
				file.write("You see " + seen_player + " as your luxurious lover Iseult.\n")
			if len(seen) == 0:
				file.write("Nobody loves you. Not even your cat.\n")

	if "Iseult" in good_roles_in_game:
		# write this info to Iseult's file
		player_name = reverse_assignments["Iseult"]
		filename = "game/" + player_name
		seen = []
		if "Tristan" in good_roles_in_game:
			seen.append(reverse_assignments["Tristan"])
		# oberon 
		if oberon_target_role == "Iseult": 
			unseen = [player for player in players if player not in seen]
			if (player_name in unseen):
				unseen.remove(player_name)
			random.shuffle(unseen)
			oberon_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)

		with open(filename, "w") as file:
			file.write("You are Iseult.\n")
			# write Iseult's info to file
			if oberon_target_role == "Iseult": 
				file.write("\nYOU HAVE BEEN OBERONED.\nYou see one additional person who is not your lover.\n\n")
			for seen_player in seen:
				file.write("You see " + seen_player + " as your luscious lover Tristan.\n")
			if len(seen) == 0:
				file.write("Nobody loves you.\n")

	if "Lancelot" in good_roles_in_game: 
		# write ability to Lancelot's file 
		player_name = reverse_assignments["Lancelot"] 
		filename = "game/" + player_name 
		with open(filename, "w") as file:
			file.write("You are Lancelot. You are on the Good team. \n\n") 
			file.write("Ability: Reversal \n")	
			file.write("You are able to play Reversal cards while on missions. A Reversal card inverts the result of a mission; a mission that would have succeeded now fails and vice versa. \n \n")
			file.write("Note: In games with at least 7 players, a Reversal played on the 4th mission results in a failed mission if there is only one Fail card, and otherwise succeeds. Reversal does not interfere with Agravaine's ability to cause the mission to fail\n")

	if "Guinevere" in good_roles_in_game:
		# guinevere sees two random "rumors"
		# rumors currently are only player knowledge (e.g. A sees B)

		player_name = reverse_assignments["Guinevere"]
		rumors = []
		truths = []
		lies = []
		connections = [] 
		
		not_guin = list(set(players) - set([reverse_assignments["Guinevere"]]))
		if "Mordred" in evil_roles_in_game:
			not_guin.remove(reverse_assignments["Mordred"]) 
		
		for player in not_guin:
			other_players = list(set(not_guin)-set([player])) 
			for other_player in other_players: 
				connections.append([player,other_player])
		
		
		#lies = list(set(connections)-set(truths))
		#lies = connections.remove(set(truths))
		
		evil_players_no_obemord = list(set(evil_players)) 
		evil_players_no_mordred = list(set(evil_players)) 
		if "Mordred" in evil_roles_in_game:
			evil_players_no_obemord.remove(reverse_assignments["Mordred"]) 
			evil_players_no_mordred.remove(reverse_assignments["Mordred"]) 
		if "Colgrevance" in evil_roles_in_game:
			evil_players_no_obemord.remove(reverse_assignments["Colgrevance"]) 
		# rumor generation here
		for evil_player in evil_players_no_obemord:
			other_evil_players = list(set(evil_players_no_obemord) - set([evil_player]))
			for evil_player_two in other_evil_players: 
				truths.append([evil_player,evil_player_two])
		if "Colgrevance" in evil_roles_in_game:
			oberon = reverse_assignments["Colgrevance"]
			for evil_player_not_oberon in evil_players_no_obemord: 
				truths.append([oberon,evil_player_not_oberon])
		if "Merlin" in good_roles_in_game:
			merlin = reverse_assignments["Merlin"]
			for evil_player_not_mordred in evil_players_no_mordred: 
				truths.append([merlin,evil_player_not_mordred])
			if "Lancelot" in good_roles_in_game: 
				lancelot = reverse_assignments["Lancelot"]
				truths.append([merlin,lancelot])
		if "Percival" in good_roles_in_game: 
			percival = reverse_assignments["Percival"]
			if "Merlin" in good_roles_in_game: 
				merlin = reverse_assignments["Merlin"]
				truths.append([percival,merlin])
			if "Morgana" in evil_roles_in_game: 
				morgana = reverse_assignments["Morgana"]
				truths.append([percival,morgana])
		if "Tristan" in good_roles_in_game: 
			tristan = reverse_assignments["Tristan"]
			if "Iseult" in good_roles_in_game: 
				iseult = reverse_assignments["Iseult"]
				truths.append([tristan,iseult])
				truths.append([iseult,tristan])
		if "Arthur" in good_roles_in_game: 
			arthur = reverse_assignments["Arthur"]
			guinevere = reverse_assignments["Guinevere"]
			good_players_no_arthur = list(set(good_players) - set([arthur,guinevere])) 
			for good_player in good_players_no_arthur:
				truths.append([arthur,good_player])
		if "Galahad" in good_roles_in_game: 
			galahad = reverse_assignments["Galahad"]
			for evil_player in evil_players_no_mordred:
				truths.append([galahad,evil_player])
		
		lies = [lie for lie in connections if lie not in truths]
		random.shuffle(truths)
		random.shuffle(lies)
		
		guin_truths = []
		guin_lies = []
		if len(truths) > 0: 
			new_truth = truths.pop(0)
			converse_truth = [new_truth[1],new_truth[0]]
			lies = [lie for lie in lies if lie != converse_truth]
			truths = [truth for truth in truths if truth != converse_truth]
			rumors.append(new_truth)
			guin_truths.append(new_truth)
			new_lie = lies.pop(0)
			converse_lie = [new_lie[1],new_lie[0]]
			lies = [lie for lie in lies if lie != converse_lie]
			truths = [truth for truth in truths if truth != converse_lie]
			rumors.append(new_lie)
			guin_lies.append(new_lie)

		guin_real_truths = copy.deepcopy(guin_truths)
		guin_real_lies = copy.deepcopy(guin_lies)
			
		if oberon_target_role == "Guinevere" and len(rumors) > 0: 
			element = random.randint(0,1) 
			index = random.randint(0,1)
			rumor = rumors[element]
			if index == 0:
				oberon_seen = "<¿" + rumor[0] + "? -> " + rumor[1] + ">"
			if index == 1:
				oberon_seen = "<" + rumor[0] + " -> ¿" + rumor[1] + "?>"
			rumor[index] = "???"
		random.shuffle(rumors)

		# and write this info to Guinevere's file
		filename = "game/" + player_name
		with open(filename, "w") as file:
			file.write("You are Guinevere.\n\n")
			if oberon_target_role == "Guinevere": 
				file.write("\nYOU HAVE BEEN OBERONED.\nOne of your rumors has been corrupted.\n\n")
			for rumor in rumors: 
				file.write("{} knows something about {}.\n".format(rumor[0],rumor[1]))
	
	if "Titania" in good_roles_in_game: 
		# write ability to Titania's file 
		player_name = reverse_assignments["Titania"] 
		filename = "game/" + player_name 
		with open(filename, "w") as file:
			file.write("You are Titania.\n\n")	
			file.write("You have added false information to the player with the role of " + titania_target_role + "\n")
			if "Oberon" in evil_roles_in_game:
				file.write("There is an Oberon in the game.\n")
			
	
	if "Arthur" in good_roles_in_game:
		# determine which roles Arthur sees
		player_name = reverse_assignments["Arthur"]
		seen = []
		for good_role in good_roles_in_game:
			seen.append(good_role)
		# oberon 
		if oberon_target_role == "Arthur": 
			unseen = [role for role in good_roles if role not in good_roles_in_game or role != "Arthur"]
			random.shuffle(unseen)
			oberon_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)

		# and write this info to Arthur's file
		filename = "game/" + player_name
		with open(filename, "w") as file:
			file.write("You are Arthur.\n\n")
			if oberon_target_role == "Arthur": 
				file.write("\nYOU HAVE BEEN OBERONED.\nYou see an additional good role that is not in the game.\n\n")
			file.write("The following good roles are in the game:\n")
			for seen_role in seen:
				if seen_role != "Arthur":
					file.write(seen_role + "\n")
			file.write("\n")
			file.write("Ability: Proclamation\n")
			file.write("If two missions have failed, you may formally reveal that you are Arthur, establishing that you are Good for the remainder of the game. You may still propose and vote on missions, as well as be chosen to be part of a mission team, as per usual.\n")
	
	if "Gawain" in good_roles_in_game:
		player_name = reverse_assignments["Gawain"]
		filename = "game/" + player_name
		with open(filename, "w") as file:
			file.write("You are Gawain.\n")
			file.write("\nAbility: Once per game, after the 1st mission and before there are two missions with the same outcome (Pass or Fail), after the cards are chosen but before they are shuffled together, you may declare as Gawain. By doing so, you may collect the cards played by everyone except for the mission leader, shuffle them together and select one to remove. You then return the remaining cards to the mission leader, who shuffles the played cards and reveals the result. The card you removed does not affect the mission, but the next time you go on a mission, you must play the card you removed, even if you normally couldn't play it.\n\n") 
			file.write("\nNote: If you remove a single Fail card, and Agravaine is on the mission, then Agravaine may declare and cause the mission to fail anyway. If Agravaine does this, you are no longer required to play a Fail card.\n\n")

	if "Galahad" in good_roles_in_game:
		# determine which roles Galahad sees
		seen = []
		for evil_role in evil_roles_in_game:
			seen.append(evil_role)
		random.shuffle(seen)
		if oberon_target_role == "Galahad": 
			unseen = [role for role in evil_roles if role not in evil_roles_in_game]
			random.shuffle(unseen)
			oberon_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)
	
		# and write this info to Arthur's file
		player_name = reverse_assignments["Galahad"]
		filename = "game/" + player_name
		with open(filename, "w") as file:
			file.write("You are Galahad.\n\n")
			if oberon_target_role == "Galahad": 
				file.write("\nYOU HAVE BEEN OBERONED.\nYou see an additional evil role that is not in the game.\n\n")
			
			file.write("The following evil roles are in the game:\n")
			for seen_role in seen:
					file.write(seen_role + "\n")
			file.write("\n(The following roles are not in the game: Percival, Merlin, and Morgana.)\n")
	
	# make list of evil players seen to other evil
	if "Colgrevance" in evil_roles_in_game:
		evil_players_no_oberon = list(set(evil_players) - set([reverse_assignments["Colgrevance"]]))
	else: 
		evil_players_no_oberon = list(set(evil_players))
		
	random.shuffle(evil_players_no_oberon)

	if "Mordred" in evil_roles_in_game:
		player_name = reverse_assignments["Mordred"]
		filename = "game/" + player_name
		seen = []
		for evil_player in evil_players:
			if assignments[evil_player] != "Colgrevance":
				seen.append(evil_player)
		
		# titania 
		if titania_target_role == "Mordred": 
			unseen = [player for player in players if player not in seen]
			if (player_name in unseen):
				unseen.remove(player_name)
			random.shuffle(unseen)
			titania_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)
				
		with open(filename, "w") as file:
			file.write("You are Mordred. (Join us, we have jackets and meet on Thursdays. ~ Andrew and Kath)\n")
			if titania_target_role == "Mordred": 
				file.write("\nYOU HAVE BEEN TITANIA'D.\nYou see one additional person who is not Evil.\n\n")
			for seen_player in seen:
				if seen_player != player_name:
					file.write(seen_player + " is a fellow member of the evil council.\n")
			if "Colgrevance" in evil_roles_in_game:
				file.write("There is a Colgrevance lurking in the shadows.\n")

	if "Morgana" in evil_roles_in_game:
		player_name = reverse_assignments["Morgana"]
		filename = "game/" + player_name
		seen = []
		for evil_player in evil_players:
			if assignments[evil_player] != "Colgrevance":
				seen.append(evil_player)
		
		# titania 
		if titania_target_role == "Morgana": 
			unseen = [player for player in players if player not in seen]
			if (player_name in unseen):
				unseen.remove(player_name)
			random.shuffle(unseen)
			titania_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)
		
		with open(filename, "w") as file:
			file.write("You are Morgana.\n")
			if titania_target_role == "Morgana": 
				file.write("\nYOU HAVE BEEN TITANIA'D.\nYou see one additional person who is not Evil.\n\n")
			
			for seen_player in seen:
				if seen_player != player_name:
					file.write(seen_player + " is a fellow member of the evil council.\n")
			if "Colgrevance" in evil_roles_in_game:
				file.write("There is an Colgrevance lurking in the shadows.\n")
			file.write("\nAbility: Once per game, when you would propose a mission team, you may declare as Morgana and permanently reverse mission order. The next proposal is granted to the person sitting next to the first proposer of the round. Morgana may NOT use this ablity if they have the last proposal of a round.\n");

	if "Oberon" in evil_roles_in_game:
		player_name = reverse_assignments["Oberon"]
		filename = "game/" + player_name
		seen = []
		for evil_player in evil_players:
			if assignments[evil_player] != "Colgrevance":
				seen.append(evil_player)
		
		# titania 
		if titania_target_role == "Oberon": 
			unseen = [player for player in players if player not in seen]
			if (player_name in unseen):
				unseen.remove(player_name)
			random.shuffle(unseen)
			titania_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)
		
		with open(filename, "w") as file:
			file.write("You are Oberon.\n")
			if titania_target_role == "Oberon": 
				file.write("\nYOU HAVE BEEN TITANIA'D.\nYou see one additional person who is not Evil.\n\n")
			
			for seen_player in seen:
				if seen_player != player_name:
					file.write(seen_player + " is a fellow member of the evil council.\n")
				
			file.write("You have added false information to a good player. ")
			
	if "Agravaine" in evil_roles_in_game:
		player_name = reverse_assignments["Agravaine"]
		filename = "game/" + player_name
		seen = []
		for evil_player in evil_players:
			if assignments[evil_player] != "Colgrevance":
				seen.append(evil_player)
		# titania 
		if titania_target_role == "Agravaine": 
			unseen = [player for player in players if player not in seen]
			if (player_name in unseen):
				unseen.remove(player_name)
			random.shuffle(unseen)
			titania_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)
		with open(filename, "w") as file:
			file.write("You are Agravaine.\n")
			if titania_target_role == "Agravaine": 
				file.write("\nYOU HAVE BEEN TITANIA'D.\nYou see one additional person who is not Evil.\n\n")
			
			for seen_player in seen:
				if seen_player != player_name:
					file.write(seen_player + " is a fellow member of the evil council.\n")
			if "Colgrevance" in evil_roles_in_game:
				file.write("There is a Colgrevance lurking in the shadows.\n")
				
			file.write("\nAbility: On any mission you are on, after the mission cards have been revealed, should the mission not result in a Fail (such as via a Reversal, requiring 2 fails, or other mechanics), you may formally declare as Agravaine to force the mission to Fail anyway.\n\n");
			file.write("Drawback: You may only play Fail cards while on missions.\n");
			
				
	if "Maelegant" in evil_roles_in_game: 
		# write ability to Lancelot's file 
		player_name = reverse_assignments["Maelegant"] 
		filename = "game/" + player_name 
		seen = []
		for evil_player in evil_players:
			if assignments[evil_player] != "Colgrevance":
				seen.append(evil_player)
		# titania 
		if titania_target_role == "Maelegant": 
			unseen = [player for player in players if player not in seen]
			if (player_name in unseen):
				unseen.remove(player_name)
			random.shuffle(unseen)
			titania_seen = unseen[0]
			seen.append(unseen[0])
		random.shuffle(seen)	
		
		with open(filename, "w") as file:
			file.write("You are Maelegant. \n\n") 
			if titania_target_role == "Maelegant": 
				file.write("\nYOU HAVE BEEN TITANIA'D.\nYou see one additional person who is not Evil.\n\n")
			
			for seen_player in seen:
				if seen_player != player_name:
					file.write(seen_player + " is a fellow member of the evil council.\n")
			if "Colgrevance" in evil_roles_in_game:
				file.write("There is a Colgrevance lurking in the shadows.\n")
			file.write("\nAbility: Reversal \n")	
			file.write("You are able to play Reversal cards while on missions. A Reversal card inverts the result of a mission; a mission that would have succeeded now fails and vice versa. \n \n")
			file.write("Note: In games with at least 7 players, a Reversal played on the 4th mission results in a failed mission if there is only one Fail card, and otherwise succeeds. Reversal does not interfere with Agravaine's ability to cause the mission to fail.")
			
				
	if "Colgrevance" in evil_roles_in_game:
		player_name = reverse_assignments["Colgrevance"]
		filename = "game/" + player_name
		seen = []
		for evil_player in evil_players:
			if assignments[evil_player] != "Colgrevance":
				seen.append(evil_player)
		titania_colgrevance_player = ""
		# titania 
		if titania_target_role == "Colgrevance": 
			if (player_name in seen):
				seen.remove(player_name)
			random.shuffle(seen)
			titania_seen = seen[0]
			titania_colgrevance_player = seen[0]
		random.shuffle(seen)
		
		with open(filename, "w") as file:
			file.write("You are Colgrevance.\n")
			if titania_target_role == "Colgrevance": 
				file.write("\nYOU HAVE BEEN TITANIA'D.\nOne of your teammate's roles has been obscured.\n\n")
			
			for seen_player in seen:
				if seen_player != player_name:
					if seen_player != titania_colgrevance_player:
						file.write(seen_player + " is " + assignments[seen_player] + ".\n")
					else: 
						file.write(seen_player + " is ???.\n")

	# TODO: pelinor + questing beast
	if num_players == 9:
		# write pelinor's information
		pelinor_filename = "game/" + pelinor
		with open(pelinor_filename, "w") as file:
			file.write("You are Pelinor.\n\n")
			file.write("You win if one of the following conditions are met:\n")
			file.write("[1]: No Questing Beast Was Here cards are played.\n")
			file.write("[2]: You are on a mission where a Questing Beast Was Here Card is played, and three missions succeed.\n")
			file.write("[3]: If neither of the previous two conditions are met at the end of the game, you declare as Pelinor prior to Assassination and name the person you believe to be the Questing Beast. You are told if you are correct at the conclusion of any other post-game phases. If you are correct, you win.\n")

		questing_beast_filename = "game/" + questing_beast
		with open(questing_beast_filename, "w") as file:
			file.write("You are the Questing Beast.\n")
			file.write("You must play the 'Questing Beast Was Here' card on missions. Once per game, you can play a Success card instead of a Questing Beast Was Here card.\n\n")
			file.write("You win if all of the following conditions are met:\n")
			file.write("[1]: You play at least one Questing Beast Was Here card.\n")
			file.write("[2]: Either a) Pelinor is never on a mission where a Questing Beast Was Here card is played; or b) 3 Quests fail.\n\n")
			file.write("[3]: Pelinor fails to identify you after the conclusion of the game.\n\n")
			file.write(pelinor + " is Pelinor.\n")

	# hijack 
	bonus_ability_hijack = 0
	if (num_players >= 7): 
		if "Mordred" in evil_roles_in_game:
			evil_players_no_mordred = list(set(evil_players) - set([reverse_assignments["Mordred"]]))
		else: 
			evil_players_no_mordred = list(set(evil_players))
		random.shuffle(evil_players_no_mordred)
		bonus_ability_hijack = evil_players_no_mordred[0] 
		bonus_hijack_filename = "game/" + bonus_ability_hijack 
		with open(bonus_hijack_filename, "a") as file: 
			file.write("\n \n \nYou also have the following ability, in addition to any other abilities you may possess.")
			file.write("\nAbility: Should any mission get to the last proposal of the round, after the people on the mission have been named, you may declare as Evil to replace one person on that mission with yourself.\n\n")
			file.write("Note: You may not use this ability after two missions have already failed. Furthermore, you may only use this ability once per game.\n"); 
				
	# write start file
	with open("game/start", "w") as file:
		file.write("The players proposing teams for the first mission are:\n")
		for first_mission_proposer in first_mission_proposers:
			file.write(first_mission_proposer + "\n")
		file.write("\n" + second_mission_starter + " is the starting player of the 2nd round.\n")

	# write do not open
	with open("game/DoNotOpen", "w") as file:
		file.write("Player -> Role\n\nGOOD TEAM:\n")
		for role in all_good_roles_in_order:
			if role in reverse_assignments:
				file.write(reverse_assignments[role] + " -> " + role + "\n")
		file.write("\n\nEVIL TEAM:\n")
		for role in all_evil_roles_in_order:
			if role in reverse_assignments:
				file.write(reverse_assignments[role] + " -> " + role + "\n")
		file.write("\n\nMISCELLANEOUS:\n")
		file.write("[Mission 1] {}, {}\n".format(first_mission_proposers[0],first_mission_proposers[1]))
		file.write("[Mission 2] {} \n".format(second_mission_starter))
		if bonus_ability_hijack: 
			file.write("[Hijack] " + bonus_ability_hijack + "\n") 
		if "Guinevere" in good_roles_in_game: 
			for truth in guin_real_truths: 
				file.write("[Guinevere: Truth] {} -> {}\n".format(truth[0],truth[1]))
			for lie in guin_real_lies: 
				file.write("[Guinevere: Lie] {} -> {}\n".format(lie[0],lie[1]))
		if "Oberon" in evil_roles_in_game: 
			file.write("[Oberon] (" + oberon_target_role + ") " + reverse_assignments[oberon_target_role] + " -> " + oberon_seen + "\n")
		if "Titania" in good_roles_in_game: 
			file.write("[Titania] (" + titania_target_role + ") " + reverse_assignments[titania_target_role] + " -> " + titania_seen + "\n")
			
				
if __name__ == "__main__":
	main()
