import matplotlib.pyplot as plt
from matplotlib import style
from GettingLists import delta_distance, delta_time

def Compare_one(Data_car1):
    
    #Define Style:
    style.use('ggplot') 


    #Create subplot:
    #Subplot1-Speed:
    g1 = plt.subplot2grid((5,1), (0,0), rowspan=2, colspan=1)
    plt.title('Telemetry of one driver in: %s'  %(Data_car1["track_name"]), 
                fontdict={'family': 'serif', 
                'color' : 'blue',
                'weight': 'bold',
                'size': 18})

    plt.ylabel("Speed [km|h]")
    plt.xlim(0, Data_car1["lapDistance"])
    plt.text(35, 65 , str(Data_car1["LapValidity"]) , fontsize=10)
    g1.axes.get_xaxis().set_visible(False)

    #Subplot2-Gear:
    g2 = plt.subplot2grid((5,1), (2,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Gear")
    g2.axes.get_xaxis().set_visible(False)
    g2.yaxis.set_label_position("right")
    g2.yaxis.tick_right()

    #Subplot3-throttle/brake:
    g3 = plt.subplot2grid((5,1), (3,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Throttle/brake")
    g3.axes.get_xaxis().set_visible(False)

    #Subplot4-Steer:
    g4 = plt.subplot2grid((5,1), (4,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Steer")
    plt.xlabel("Distance [m]")
    g4.axes.get_xaxis().set_visible(True)
    g4.yaxis.set_label_position("right")
    g4.yaxis.tick_right()


    #Plot N1:
    g1.plot(Data_car1["LapDistance_List"] , Data_car1["Car_speed_list"], label= Data_car1["player_name"] , color="dimgrey")
    g1.legend()

    #Plot N2:
    g2.plot(Data_car1["LapDistance_List"] , Data_car1["Car_gear_list"], color="dimgrey")

    #Plot N3:
    g3.plot(Data_car1["LapDistance_List"] , Data_car1["Car_throttle_list"], label= 'Throttle' , color="limegreen")
    g3.plot(Data_car1["LapDistance_List"] , Data_car1["Car_brake_list"], label= 'brake' , color="firebrick")
    g3.legend()
    
    #Plot N4:
    g4.plot(Data_car1["LapDistance_List"] , Data_car1["Car_steer_list"], color="dimgrey")

    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0)
    
    #show
    plt.show()




def time_dif(Data_car1, Data_car2):
    
    #Get Data:
    delta_dist_List = delta_distance(Data_car1, Data_car2)
    delta_time_List = delta_time(Data_car1, Data_car2)

    #Define Style:
    style.use('ggplot') 

    #Create subplot:

    #Subplot1-Speed:
    g1 = plt.subplot2grid((3,1), (0,0), rowspan=2, colspan=1)

    plt.title(f'Differential Analysis:  {Data_car1["track_name"]}', 
                fontdict={'family': 'serif', 
                    'color' : 'blue',
                    'weight': 'bold',
                    'size': 18})

    plt.ylabel("Speed [km|h]")
    plt.xlim(0, Data_car1["lapDistance"])
    g1.axes.get_xaxis().set_visible(False)


    #Subplot3-Distance-Differential:
    g3 = plt.subplot2grid((3,1), (2,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Distance Differential")
    g3.axes.get_xaxis().set_visible(True)


    #Plot N1:
    g1.plot(Data_car2["LapDistance_List"] , Data_car2["Car_speed_list"], label= 'Adversaire: %s'  %(Data_car2["player_name"]), color="lightcoral")
    g1.plot(Data_car1["LapDistance_List"] , Data_car1["Car_speed_list"], label= 'Player: %s'  %(Data_car1["player_name"]) , color="dimgrey") 
    g1.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, borderaxespad=0.)

    #Plot N3:
    g3.plot(Data_car2["LapDistance_List"] , delta_dist_List, color="dimgrey")
    #g3.plot(Data_car1["LapDistance_List"] , Data_car1["CurrentLapTime_List"], color="dimgrey")

    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0)
    plt.show()




def Compare_many (Data_car1, Data_car2):

    #Define Style:
    style.use('ggplot') 

    #Create subplot:
    #Subplot1-Speed:
    g1 = plt.subplot2grid((6,1), (0,0), rowspan=2, colspan=1)

    plt.title(f'Comparasion of two drivers in:  {Data_car1["track_name"]}', 
                fontdict={'family': 'serif', 
                    'color' : 'blue',
                    'weight': 'bold',
                    'size': 18})

    plt.ylabel("Speed [km|h]")
    plt.xlim(0, Data_car1["lapDistance"])
    g1.axes.get_xaxis().set_visible(False)


    #Subplot2-Gear:
    g2 = plt.subplot2grid((6,1), (2,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Gear")
    g2.yaxis.set_ticks(range(9))
    g2.axes.get_xaxis().set_visible(False)
    g2.yaxis.set_label_position("right")
    g2.yaxis.tick_right()


    #Subplot3-throttle:
    g3 = plt.subplot2grid((6,1), (3,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Throttle")
    g3.axes.get_xaxis().set_visible(False)

    #Subplot4-brake:
    g4 = plt.subplot2grid((6,1), (4,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Brake")
    g4.axes.get_xaxis().set_visible(False)
    g4.yaxis.set_label_position("right")
    g4.yaxis.tick_right()

    #Subplot5-Steer:
    g5 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Steer")
    plt.xlabel("Distance [m]")
    g5.axes.get_xaxis().set_visible(True)



    #Plot N1:
    g1.plot(Data_car2["LapDistance_List"] , Data_car2["Car_speed_list"], label= 'Adversaire: %s'  %(Data_car2["player_name"]), color="lightcoral")  #Voiture référence
    g1.plot(Data_car1["LapDistance_List"] , Data_car1["Car_speed_list"], label= 'Player: %s'  %(Data_car1["player_name"]) , color="dimgrey") #Voiture Joueur
    g1.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, borderaxespad=0.)
    #g1.legend(bbox_to_anchor=(0.5, 0., 0.5, 0.5), loc=0, borderaxespad=0.)


    #Plot N2:
    g2.plot(Data_car2["LapDistance_List"] , Data_car2["Car_gear_list"], color="lightcoral")
    g2.plot(Data_car1["LapDistance_List"] , Data_car1["Car_gear_list"], color="dimgrey")


    #Plot N3:
    g3.plot(Data_car2["LapDistance_List"] , Data_car2["Car_throttle_list"], color="lightcoral")
    g3.plot(Data_car1["LapDistance_List"] , Data_car1["Car_throttle_list"], color="dimgrey")
    

    #Plot N4:
    g4.plot(Data_car2["LapDistance_List"] , Data_car2["Car_brake_list"], color="lightcoral")
    g4.plot(Data_car1["LapDistance_List"] , Data_car1["Car_brake_list"], color="dimgrey")
    

    #Plot N5:
    g5.plot(Data_car2["LapDistance_List"] , Data_car2["Car_steer_list"], color="lightcoral")
    g5.plot(Data_car1["LapDistance_List"] , Data_car1["Car_steer_list"], color="dimgrey")
    
    
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0)
    plt.show()



def Compare_many2 (Data_car1, Data_car2):

    #Define Style:
    style.use('ggplot') 

    #Create subplot:
    #Subplot1-Speed:
    g1 = plt.subplot2grid((6,1), (0,0), rowspan=2, colspan=1)

    plt.title(f'Comparasion of two drivers in:  {Data_car1["track_name"]}', 
                fontdict={'family': 'serif', 
                    'color' : 'blue',
                    'weight': 'bold',
                    'size': 18})

    plt.ylabel("Speed [km|h]")
    plt.xlim(0, Data_car1["lapDistance"])
    g1.axes.get_xaxis().set_visible(False)


    #Subplot2-Gear:
    g2 = plt.subplot2grid((7,1), (2,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Gear")
    g2.yaxis.set_ticks(range(9))
    g2.axes.get_xaxis().set_visible(False)
    g2.yaxis.set_label_position("right")
    g2.yaxis.tick_right()


    #Subplot3-throttle:
    g3 = plt.subplot2grid((7,1), (3,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Throttle")
    g3.axes.get_xaxis().set_visible(False)

    #Subplot4-brake:
    g4 = plt.subplot2grid((7,1), (4,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Brake")
    g4.axes.get_xaxis().set_visible(False)
    g4.yaxis.set_label_position("right")
    g4.yaxis.tick_right()

    #Subplot5-Steer:
    g5 = plt.subplot2grid((7,1), (5,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Steer")
    plt.xlabel("Distance [m]")
    g5.axes.get_xaxis().set_visible(False)

    #Subplot6-Time differential:
    Delta_Time_List = delta_time(Data_car1, Data_car2)
    g6 = plt.subplot2grid((7,1), (6,0), rowspan=1, colspan=1, sharex= g1)
    plt.ylabel("Deta/Time")
    plt.xlabel("Distance [m]")
    g5.axes.get_xaxis().set_visible(True)

    #Plot N1:
    g1.plot(Data_car2["LapDistance_List"] , Data_car2["Car_speed_list"], label= 'Adversaire: %s'  %(Data_car2["player_name"]), color="lightcoral")  #Voiture référence
    g1.plot(Data_car1["LapDistance_List"] , Data_car1["Car_speed_list"], label= 'Player: %s'  %(Data_car1["player_name"]) , color="dimgrey") #Voiture Joueur
    g1.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, borderaxespad=0.)
    #g1.legend(bbox_to_anchor=(0.5, 0., 0.5, 0.5), loc=0, borderaxespad=0.)


    #Plot N2:
    g2.plot(Data_car2["LapDistance_List"] , Data_car2["Car_gear_list"], color="lightcoral")
    g2.plot(Data_car1["LapDistance_List"] , Data_car1["Car_gear_list"], color="dimgrey")


    #Plot N3:
    g3.plot(Data_car2["LapDistance_List"] , Data_car2["Car_throttle_list"], color="lightcoral")
    g3.plot(Data_car1["LapDistance_List"] , Data_car1["Car_throttle_list"], color="dimgrey")
    

    #Plot N4:
    g4.plot(Data_car2["LapDistance_List"] , Data_car2["Car_brake_list"], color="lightcoral")
    g4.plot(Data_car1["LapDistance_List"] , Data_car1["Car_brake_list"], color="dimgrey")
    

    #Plot N5:
    g5.plot(Data_car2["LapDistance_List"] , Data_car2["Car_steer_list"], color="lightcoral")
    g5.plot(Data_car1["LapDistance_List"] , Data_car1["Car_steer_list"], color="dimgrey")
    
    #Plot N5:
    g6.plot(Data_car2["LapDistance_List"] , Delta_Time_List, color="lightcoral")
    
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0)
    plt.show()