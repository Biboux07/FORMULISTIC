###Theses functions are useful In "Gettinglists.py"###

#Finding the Team Name:

def TeamName(num):

	if num == -1:

		name = "no name"

	if num == 0:

		name = "Mercedes"

	if num == 1:

		name = "Ferrari"
		
	if num == 2:

		name = "Red Bull Racing"
		
	if num == 3:

		name = "Williams"
		
	if num == 4:

		name = "Racing Point"

	if num == 5:

		name = "Renault"
		
	if num == 6:

		name = "AlphaTauri"
		
	if num == 7:

		name = "Haas"
		
	if num == 8:

		name = "McLaren"
		
	if num == 9:

		name = "Alfa Romeo"
		
	#else:

		#name = "Not an F1-2020-car"
		
	return name



#Finding the Track Name:
def TrackName(num):

	if num == -1:

		name = "no name"

	if num == 0:

		name = "Melbourne"

	if num == 1:

		name = "Le Castellet"

	if num == 2:

		name = "Shanghai"

	if num == 3:

		name = "Bahrain"

	if num == 4:

		name = "Barcelona"

	if num == 5:

		name = "Monaco"

	if num == 6:

		name = "Montreal"

	if num == 7:

		name = "Silverstone"

	if num == 8:

		name = "Hungaroring"

	if num == 10:

		name = "Spa"

	if num == 11:

		name = "Monza"

	if num == 12:

		name = "Singapore"

	if num == 13:

		name = "Suzuka"

	if num == 14:

		name = "Abu Dhabi"

	if num == 15:

		name = "Texas"

	if num == 16:

		name = "Brazil"

	if num == 17:

		name = "Austria"

	if num == 18:

		name = "Sochi"

	if num == 19:

		name = "Mexico"

	if num == 20:

		name = "Baku"

	if num == 21:

		name = "Sakhir Short"

	if num == 22:

		name = "Silverstone Short"
	
	if num == 23:

		name = "Texas Short"

	if num == 24:

		name = "Suzuka Short"

	if num == 25:

		name = "Hanoi"

	if num == 26:

		name = "Zandvoort"

	return name


#Finding if the lap is Valid or Not:

def ValidityLap(num):

	if num == -1:
		lap_result = "error"

	if num == 0:
		lap_result = "LAP: VALID"

	if num == 1:
		lap_result = "LAP: INVALID"


	return lap_result


