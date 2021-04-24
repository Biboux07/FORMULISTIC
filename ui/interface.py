#Tkinter Imports
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import threading




#Myfiles Imports:
from sessions.Telemetry_Recorder import main as StartRecording
#from sessions.Telemetry_Recorder_Test import stop_thread, main
from f1_2020_telemetry.cli.threading_utils import WaitConsoleThread, Barrier


#Gaphs functions:
from GettingLists import Get_Telemetry
from plot_graphs import Compare_one, Compare_many, Compare_many2, time_dif

#Text import:
from ui.Text_UI import formulistic_description



BIG_TITLE_FONT = ("Arial",40)
BIG_SUB_TITLE_FONT = ("Arial",15)
LARGE_FONT = ("Arial", 12)
NORM_FONT = ("Arial", 10)
COLOR_PAGES = None



#Define some useful functions:

def popupmsg(msg):
    popup = tk.Tk()

    
    popup.wm_title("Oups!")
    label = ttk.Label(popup, text= msg, font= NORM_FONT)
    label.pack(side= "top", padx= 10, pady= 10)


    #Button d'acceptation:
    Button1 = ttk.Button(popup, text= "Okay", command = popup.destroy)
    Button1.pack()
    popup.mainloop()

def compare2_msg(Data_car1, Data_car2):
    popup = tk.Tk()

    #text beeing printed
    deltatime = round(Data_car1["Final_LapTime"]-Data_car2["Final_LapTime"], 3)
    msg1= "Name:", Data_car1["player_name"],"|", Data_car2["player_name"]
    msg2= "Time_Differential:", deltatime
    msg3= "Car:", Data_car1["team_name"],"|", Data_car2["team_name"]
    msg4= "Lap:", Data_car1["LapValidity"],"|", Data_car2["LapValidity"]

    #Label created + packed
    popup.wm_title("Comparaison drivers Infos:")

    label1 = ttk.Label(popup, text= msg1, font= NORM_FONT)
    label1.pack(side= "top", padx= 10, pady= 10)
    label2 = ttk.Label(popup, text= msg2, font= NORM_FONT)
    label2.pack(side= "top", padx= 10, pady= 10)
    label3 = ttk.Label(popup, text= msg3, font= NORM_FONT)
    label3.pack(side= "top", padx= 10, pady= 10)
    label4 = ttk.Label(popup, text= msg4, font= NORM_FONT)
    label4.pack(side= "top", padx= 10, pady= 10)


    #Button d'acceptation:
    Button1 = ttk.Button(popup, text= "Okay", command = popup.destroy)
    Button1.pack()
    popup.mainloop()


def compare1_msg(Data_car1):
    popup = tk.Tk()

    #text beeing printed

    msg1= "Name:", Data_car1["player_name"]
    msg2= "Time:", round(Data_car1["Final_LapTime"],3)
    msg3= "Car:", Data_car1["team_name"]
    msg4= "Lap:", Data_car1["LapValidity"]

    #Label created + packed
    popup.wm_title("Comparaison drivers Infos:")

    label1 = ttk.Label(popup, text= msg1, font= NORM_FONT)
    label1.pack(side= "top", padx= 10, pady= 10)
    label2 = ttk.Label(popup, text= msg2, font= NORM_FONT)
    label2.pack(side= "top", padx= 10, pady= 10)
    label3 = ttk.Label(popup, text= msg3, font= NORM_FONT)
    label3.pack(side= "top", padx= 10, pady= 10)
    label4 = ttk.Label(popup, text= msg4, font= NORM_FONT)
    label4.pack(side= "top", padx= 10, pady= 10)


    #Button d'acceptation:
    Button1 = ttk.Button(popup, text= "Okay", command = popup.destroy)
    Button1.pack()
    popup.mainloop()



class F1_telemetry_app(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        
        #Paramètres général des fenêtres:
        tk.Tk.iconbitmap(self, default= "ui\images\Logo_N1.ico")
        tk.Tk.wm_title(self, "FORMULISTIC")
        tk.Tk.geometry(self, "900x550")
        

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight= 1)
        container.grid_columnconfigure(0, weight= 1)


        #Barre on top
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff= 0)
        filemenu.add_command(label="Test", command = lambda : popupmsg("Unable yet") )
        filemenu.add_separator()
        filemenu.add_command(label= "Exit", command = quit)
        menubar.add_cascade(label= "More",  menu = filemenu)

        tk.Tk.config(self, menu = menubar)


        self.frames = {}

        for F in (
            StartPage, MenuPage, PageOne, CompareOne, PageThree, SessionPageC2, CompareTwo
            ):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row= 0, column= 0, sticky= "nsew")

        self.show_frame(StartPage)


    def show_frame(self, cont):
        
        frame = self.frames[cont]
        frame.tkraise()




class StartPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)


        #Paramètres de la fenêtre:
        tk.Tk.configure(self, background = COLOR_PAGES)

        frame = tk.Frame(self, background = COLOR_PAGES)


        label= tk.Label(frame, text= "FORMULISTIC", font= BIG_TITLE_FONT)
        label.pack()
        label= tk.Label(frame, text= "Start | Connection Page", font= LARGE_FONT)
        label.pack()


        #Buttons:

        button1 = ttk.Button(frame,
        text= "Get Start...",
        command= lambda: controller.show_frame(MenuPage))
        button1.pack(pady=10, fill= tk.X)
        

        frame.pack(expand= True)



class MenuPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)


        #Paramètres de la fenêtre:
        tk.Tk.configure(self, background = COLOR_PAGES)
        frame = tk.Frame(self, background = COLOR_PAGES)

        
        label= tk.Label(frame, text= "MENU PAGE", font= BIG_SUB_TITLE_FONT)
        label.pack()
    

        

        #Buttons:

        button1 = ttk.Button(frame,
        text= "Record Data",
        command= lambda: controller.show_frame(PageOne))
        button1.pack(pady=2, fill= tk.X)

        button2 = ttk.Button(frame,
        text= "Telemetry",
        command= lambda: controller.show_frame(SessionPageC2))
        button2.pack(pady=2, fill= tk.X)

        button3 = ttk.Button(frame,
        text= "Options",
        command= lambda: controller.show_frame(PageThree))
        button3.pack(pady=2, fill= tk.X)

        frame.pack(expand=True)



class PageOne(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)


        #Paramètres de la fenêtre:
        tk.Tk.configure(self, background = COLOR_PAGES)
        frame = tk.Frame(self, background = COLOR_PAGES)

        label1= tk.Label(frame, text= "RECORD DATA", font= LARGE_FONT)
        label1.pack()
        label2 = tk.Label(self, text= "The program will shut down after pressing the stop button. It's normal, your data are saved. Just re-launch the app:)  ")
        label2.pack(side= tk.BOTTOM, pady = 10)

        #Buttons:

        button1 = ttk.Button(frame,
        text= "Back to Home",
        command= lambda: controller.show_frame(MenuPage))
        button1.pack(pady= 2, fill= tk.X)


        button2 = ttk.Button(frame,
        text= "StartRecording",
        command= lambda: threading.Thread(target= StartRecording, daemon=True).start())
        button2.pack(pady= 2, fill= tk.X)


        button3 = ttk.Button(frame,
        text= "StopRecording",
        command= lambda:  quit())
        button3.pack(pady= 2, fill= tk.X)

        #pack frame:
        frame.pack(expand=True)

class PageThree(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)


        #Paramètres de la fenêtre:
        tk.Tk.configure(self, background = COLOR_PAGES)

        label= tk.Label(self, text= "Help page:", font= LARGE_FONT)
        label.pack(pady=10 , padx=10)

        label= tk.Label(self, text= formulistic_description, font= NORM_FONT)
        label.pack(pady=20 , padx=20)

        #Buttons:
        
        button1 = ttk.Button(self,
        text= "Back to Home",
        command= lambda: controller.show_frame(MenuPage))
        button1.pack()





class SessionPageC2(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)


        #Paramètres de la fenêtre:
        tk.Tk.configure(self, background = COLOR_PAGES) 
        frame = tk.Frame(self, background = COLOR_PAGES)
        frame2 = tk.Frame(self, background = COLOR_PAGES)

        #Text\Label 1:
        label1= tk.Label(frame, text= "Your Data | Session Page ", font= BIG_SUB_TITLE_FONT)
        label1.pack(pady=5)

 

        def get_file():
            global Data_car1
            global Data_car2
            
            file_name = None
            file_name = askopenfilename(title= "Select Sessions", filetype=[("Sqlite3 file only", "*.sqlite3")], multiple=True)

            if file_name:

                
                if len(file_name)== 1:

                    Data_car1 = Get_Telemetry(file_name[0])
                    print('new Datacar set')


                    controller.show_frame(CompareOne)


                elif len(file_name)== 2:
                    

                    Data_car1 = Get_Telemetry(file_name[0])
                    Data_car2 = Get_Telemetry(file_name[1])
                    print('new Datacar set')


                    controller.show_frame(CompareTwo)

                else:
                    popupmsg("Too many sessions chosen!")          


        #Buttons:
        button1 = ttk.Button(frame,
        text= "Find Sessions",
        command= lambda: get_file())
        button1.pack(pady=5, fill= tk.X)

        button2 = ttk.Button(frame,
        text= "Previous Page",
        command= lambda: controller.show_frame(MenuPage))
        button2.pack(pady=5, fill= tk.X)


        #Text\Label 2 :
        label2= tk.Label(frame2, text= "Please select one or two sessions that you would like to analyse. \n You will find them in the 'sessions' directory" , font= NORM_FONT)
        label2.pack()

        #pack frame:
        frame.pack(expand=True)
        frame2.pack(expand=True)



class CompareOne(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)


        #Paramètres de la fenêtre:
        tk.Tk.configure(self, background = COLOR_PAGES)
        frame = tk.Frame(self, background = COLOR_PAGES)

        
        #Labels
        label1= tk.Label(frame, text= "ANALYSE DATA OF ONE DRIVER :", font= LARGE_FONT)
        label1.pack()

        
        label2= tk.Label(self, text= "Here are all the information concerning the lap of %s in %s "  %('Data_car1[0]', "Name_track") , font= NORM_FONT)
        label2.pack(side= tk.BOTTOM)




        #Buttons:

        button2 = ttk.Button(frame,
        text= "Open Graph",
        command= lambda: Compare_one(Data_car1))
        button2.pack(pady=5, fill= tk.X)
        
        button3 = ttk.Button(frame,
        text= "Infos",
        command= lambda: compare1_msg(Data_car1))
        button3.pack(pady=5, fill= tk.X)

        button1 = ttk.Button(frame,
        text= "Previous Page",
        command= lambda: controller.show_frame(SessionPageC2))
        button1.pack(pady=5, fill= tk.X)

        #pack frame:
        frame.pack(expand=True)

class CompareTwo(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)


        #Paramètres de la fenêtre:
        tk.Tk.configure(self, background = COLOR_PAGES)
        frame = tk.Frame(self, background = COLOR_PAGES)
        

        #valuable infos:
        

        #Labels
        label1= tk.Label(frame, text= "ANALYSE DATA OF TWO DRIVERS :", font= BIG_SUB_TITLE_FONT)
        label1.pack(pady=10 , padx=10)

        
        label2= tk.Label(self, text= "Here are all the information concerning the lap of %s in %s "  %('name', "Name_track") , font= NORM_FONT)
        label2.pack(side= tk.BOTTOM)




        #Buttons:

        button2 = ttk.Button(frame,
        text= "Open General Graph",
        command= lambda: Compare_many(Data_car1, Data_car2))
        button2.pack(pady=5, fill= tk.X)


        button4 = ttk.Button(frame,
        text= "Distance Differential Graph",
        command= lambda: time_dif(Data_car1, Data_car2))
        button4.pack(pady=5, fill= tk.X)
        
        button3 = ttk.Button(frame,
        text= "Infos",
        command= lambda: compare2_msg(Data_car1, Data_car2))
        button3.pack(pady=5, fill= tk.X)

        button1 = ttk.Button(frame,
        text= "Previous Page",
        command= lambda: controller.show_frame(SessionPageC2))
        button1.pack(pady=5, fill= tk.X)
    

        #pack frame:
        frame.pack(expand=True)

app = F1_telemetry_app()
