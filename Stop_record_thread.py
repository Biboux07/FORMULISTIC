from sessions.Telemetry_Recorder import *
from f1_2020_telemetry.cli.threading_utils import WaitConsoleThread, Barrier

def close_thread():


    quit_barrier = Barrier()
    quit_barrier.wait()