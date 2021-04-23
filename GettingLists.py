from helper import *
from f1_2020_telemetry.packets import *
from StartEndofLaps import Startend_Lap
from SQLite_connexion import ConnectSQL


def Get_Telemetry (filename):


	#Create all lists needed:
	Car_throttle_list = []
	Car_speed_list = []
	Car_steer_list = []
	Car_brake_list = []
	Car_gear_list = []
	Car_engineRPM_list = []
	CurrentLapTime_List = []
	LapDistance_List = []

	#connection to de Database:
	Car_Data = ConnectSQL(filename)


	#default  car player = 0 :
	num_car = 0


	#Get the biginning of the lap:
	row_start, row_end = Startend_Lap(Car_Data, num_car)


	for row in Car_Data:

		#Unpack les données initiales en bytes:
		Car_Data_Unpack = unpack_udp_packet(row[0])

		#Check the frame:
		Frame_pkt = Car_Data_Unpack.header.frameIdentifier

		if Frame_pkt >= row_start and Frame_pkt < row_end:	



			#Checking what type of packet we are dealing with:
			type_packet = Car_Data_Unpack.header.packetId
	

			#Packetid-1-Session Packet
			if type_packet == 1 :

				#Session_pkt = Car_Data_Unpack


				#Récupérations de toutes les données nécessaires:

				trackId = Car_Data_Unpack.trackId
				track_name = TrackName(trackId)



			#Packetid-2-LAP DATA
			if type_packet == 2 :

				Lap_Data = Car_Data_Unpack.lapData[num_car]


				#Récupérations de toutes les données nécessaires:

				currentLapTime = Lap_Data.currentLapTime
				CurrentLapTime_List.append(currentLapTime)
				
				#Final Lap time(VAR change every time but keep only the last time)
				Final_LapTime = currentLapTime

				lapDistance = Lap_Data.lapDistance
				LapDistance_List.append(lapDistance)

				totalDistance = Lap_Data.totalDistance

				driverStatus = Lap_Data.driverStatus

				currentLapInvalid = Lap_Data.currentLapInvalid
				LapValidity = ValidityLap(currentLapInvalid)


			#Packetid-4-PARTICIPANTS PACKET
			if type_packet == 4 :

				Participant_pkt = Car_Data_Unpack.participants[num_car]


				teamId = Participant_pkt.teamId
				team_name = TeamName(teamId)


				player_name_encode = Participant_pkt.name
				player_name = player_name_encode.decode("utf-8")

			#Packetid-6-CAR-TELEMETRY
			if type_packet == 6 :

				Car_Telemetry = Car_Data_Unpack.carTelemetryData[num_car]


				#Récupérations de toutes les données nécessaires:

				Car_speed = Car_Telemetry.speed
				Car_speed_list.append(Car_speed)

				Car_throttle = Car_Telemetry.throttle
				Car_throttle_list.append(Car_throttle)

				Car_steer = Car_Telemetry.steer
				Car_steer_list.append(Car_steer)

				Car_brake = Car_Telemetry.brake
				Car_brake_list.append(Car_brake)

				Car_gear = Car_Telemetry.gear
				Car_gear_list.append(Car_gear)

				Car_engineRPM = Car_Telemetry.engineRPM
				Car_engineRPM_list.append(Car_engineRPM)



	#Store all variables and lists in a Dictionary and return a result: 

	Final_Car_Data = {
		"track_name": track_name,
		"player_name": player_name,
		"Final_LapTime": Final_LapTime,
		"LapValidity": LapValidity,
		"team_name": team_name,
		"LapDistance_List": LapDistance_List,
		"Car_speed_list": Car_speed_list, 
		"Car_throttle_list": Car_throttle_list,
		"Car_brake_list": Car_brake_list,
		"Car_steer_list": Car_steer_list,
		"Car_gear_list": Car_gear_list,
		"Car_engineRPM_list": Car_engineRPM_list,
		"CurrentLapTime_List": CurrentLapTime_List,
		"lapDistance": lapDistance
	}
	

	return Final_Car_Data


#Theses next functions are used when plotting graphs:

def delta_distance(Data_car1, Data_car2):
    
    delta_dist_list = []
    
    #find the delta time in every packet sent:

    lenthCar1 = len(Data_car1["CurrentLapTime_List"])
    lenthCar2 = len(Data_car2["CurrentLapTime_List"])
    
    if lenthCar1 >= lenthCar2:
        lenthmax = lenthCar2 

    if lenthCar1 < lenthCar2:
        lenthmax = lenthCar1

    print(lenthCar1)
    print(lenthCar2)

    for i in range (0, lenthmax):
        
        
        delta = Data_car1["LapDistance_List"][i] - Data_car2["LapDistance_List"][i]
        delta_dist_list.append(delta)

    return delta_dist_list


def delta_time(Data_car1, Data_car2):
    
    delta_time_list = []
    
    #find the delta time in every packet sent:

    lenthCar1 = len(Data_car1["CurrentLapTime_List"])
    lenthCar2 = len(Data_car2["CurrentLapTime_List"])
    
    if lenthCar1 >= lenthCar2:
        lenthmax = lenthCar2 

    if lenthCar1 < lenthCar2:
        lenthmax = lenthCar1

    print(lenthCar1)
    print(lenthCar2)

    for i in range (0, lenthmax):
        
        
        delta = Data_car1["CurrentLapTime_List"][i] - Data_car2["CurrentLapTime_List"][i]
        delta_time_list.append(delta)

    return delta_time_list