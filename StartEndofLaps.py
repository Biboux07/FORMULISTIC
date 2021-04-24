from f1_2020_telemetry.packets import *




def Startend_Lap(Car_Data, num_car):

	lapStart_List = []
	i = 0
	previousLapStart = 0


	for row in Car_Data:

		#Unpack les données initiales en bytes:
		Car_Data_Unpack = unpack_udp_packet(row[0])


		#Checking what type of packet we are dealing with:
		type_packet = Car_Data_Unpack.header.packetId

		Frame_pkt = Car_Data_Unpack.header.frameIdentifier


		#Packetid-2-LAP DATA
		if type_packet == 2 :

			Lap_Data = Car_Data_Unpack.lapData[num_car]


			#Récupérations de toutes les données nécessaires:

			currentLapTime = Lap_Data.currentLapTime
			

			#Spot de beginnig of the Lap:

			if currentLapTime >= 0 and currentLapTime <= 1:

				currentlapStart = i

				

				#Take only the first frame per lap (Because many frame are between 0 and 0.1)
				if currentlapStart - previousLapStart > 400:

					lapStart_List.append(Frame_pkt)

				previousLapStart = currentlapStart


		i += 1
	
	
	#take on consideration only the last lap:
	lenlist= len(lapStart_List)
	
	#Send result:
	row_start = lapStart_List[lenlist-2]
	row_end = lapStart_List[lenlist-1]-1


	return row_start, row_end
	

