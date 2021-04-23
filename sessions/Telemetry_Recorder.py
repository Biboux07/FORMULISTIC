#! /usr/bin/env python3

"""This script captures F1 2019 telemetry packets (sent over UDP) and stores them into SQLite3 database files.

One database file will contain all packets from one session.

From UDP packet to database entry
---------------------------------

The data flow of UDP packets into the database is managed by 2 threads.

PacketReceiver thread:

  (1) The PacketReceiver thread does a select() to wait on incoming packets in the UDP socket.
  (2) When woken up with the notification that a UDP packet is available for reading, it is actually read from the socket.
  (3) The receiver thread calls the recorder_thread.record_packet() method with a TimedPacket containing
      the reception timestamp and the packet just read.
  (4) The recorder_thread.record_packet() method locks its packet queue, inserts the packet there,
      then unlocks the queue. Note that this method is only called from within the receiver thread!
  (5) repeat from (1).

PacketRecorder thread:

  (1) The PacketRecorder thread sleeps for a given period, then wakes up.
  (2) It locks its packet queue, moves the queue's packets to a local variable, empties the packet queue,
      then unlocks the packet queue.
  (3) The packets just moved out of the queue are passed to the 'process_incoming_packets' method.
  (4) The 'process_incoming_packets' method inspects the packet headers, and converts the packet data
      into SessionPacket instances that are suitable for inserting into the database.
      In the process, it collects packets from the same session. After collecting all
      available packets from the same session, it passed them on to the
      'process_incoming_same_session_packets' method.
  (5) The 'process_incoming_same_session_packets' method makes sure that the appropriate SQLite database file
      is opened (i.e., the one with matching sessionUID), then writes the packets into the 'packets' table.

By decoupling the packet capture and database writing in different threads, we minimize the risk of
dropping UDP packets. This risk is real because SQLite3 database commits can take a considerable time.
"""

import argparse
import sys
import time
import socket
import sqlite3
import threading
import logging
import ctypes
import selectors

from collections import namedtuple

from f1_2020_telemetry.cli.threading_utils import WaitConsoleThread, Barrier
from f1_2020_telemetry.packets import (
    PacketHeader,
    PacketID,
    HeaderFieldsToPacketType,
    unpack_udp_packet,
)

# The type used by the PacketReceiverThread to represent incoming telemetry packets, with timestamp.
TimestampedPacket = namedtuple("TimestampedPacket", "timestamp, packet")

# The type used by the PacketRecorderThread to represent incoming telemetry packets for storage in the SQLite3 database.
SessionPacket = namedtuple(
    "SessionPacket",
    "timestamp, packetFormat, gameMajorVersion, gameMinorVersion, packetVersion, packetId, sessionUID, sessionTime, frameIdentifier, playerCarIndex, packet",
)


class PacketRecorder:
    """The PacketRecorder records incoming packets to SQLite3 database files.

    A single SQLite3 file stores packets from a single session.
    Whenever a new session starts, any open file is closed, and a new database file is created.
    """

    # The SQLite3 query that creates the 'packets' table in the database file.
    _create_packets_table_query = """
        CREATE TABLE packets (
            pkt_id            INTEGER  PRIMARY KEY, -- Alias for SQLite3's 'rowid'.
            timestamp         REAL     NOT NULL,    -- The POSIX time right after capturing the telemetry packet.
            packetFormat      INTEGER  NOT NULL,    -- Header field: packet format.
            gameMajorVersion  INTEGER  NOT NULL,    -- Header field: game major version.
            gameMinorVersion  INTEGER  NOT NULL,    -- Header field: game minor version.
            packetVersion     INTEGER  NOT NULL,    -- Header field: packet version.
            packetId          INTEGER  NOT NULL,    -- Header field: packet type ('packetId' is a bit of a misnomer).
            sessionUID        CHAR(16) NOT NULL,    -- Header field: unique session id as hex string.
            sessionTime       REAL     NOT NULL,    -- Header field: session time.
            frameIdentifier   INTEGER  NOT NULL,    -- Header field: frame identifier.
            playerCarIndex    INTEGER  NOT NULL,    -- Header field: player car index.
            packet            BLOB     NOT NULL     -- The packet itself
        );
        """

    # The SQLite3 query that inserts packet data into the 'packets' table of an open database file.
    _insert_packets_query = """
        INSERT INTO packets(
            timestamp,
            packetFormat, gameMajorVersion, gameMinorVersion, packetVersion, packetId, sessionUID,
            sessionTime, frameIdentifier, playerCarIndex,
            packet) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

    def __init__(self):
        self._conn = None
        self._cursor = None
        self._filename = None
        self._sessionUID = None

    def close(self):
        """Make sure that no database remains open."""
        if self._conn is not None:
            self._close_database()

    def _open_database(self, sessionUID: str):
        """Open SQLite3 database file and make sure it has the correct schema."""
        assert self._conn is None
        filename = f"Formulistic_{sessionUID}.sqlite3"
        logging.info("Opening file %s", filename)
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()

        # Get rid of indentation and superfluous newlines in the 'CREATE TABLE' command.
        query = "".join(
            line[8:] + "\n"
            for line in PacketRecorder._create_packets_table_query.split("\n")[
                1:-1
            ]
        )

        # Try to execute the 'CREATE TABLE' statement. If it already exists, this will raise an exception.
        try:
            cursor.execute(query)
        except sqlite3.OperationalError:
            logging.info("    (Appending to existing file.)")
        else:
            logging.info("    (Created new file.)")

        self._conn = conn
        self._cursor = cursor
        self._filename = filename
        self._sessionUID = sessionUID

    def _close_database(self):
        """Close SQLite3 database file."""
        assert self._conn is not None
        logging.info("Closing file %s", self._filename)
        self._cursor.close()
        self._cursor = None
        self._conn.close()
        self._conn = None
        self._filename = None
        self._sessionUID = None

    def _insert_and_commit_same_session_packets(self, same_session_packets):
        """Insert session packets to database and commit."""
        assert self._conn is not None
        self._cursor.executemany(
            PacketRecorder._insert_packets_query, same_session_packets
        )
        self._conn.commit()

    def _process_same_session_packets(self, same_session_packets):
        """Insert packets from the same session into the 'packets' table of the appropriate database file.

        Precondition: all packets in 'same_session_packets' are from the same session (identical 'sessionUID' field).

        We need to handle four different cases:

        (1) 'same_session_packets' is empty:

            --> return (no-op).

        (2) A database file is currently open, but it stores packets with a different session UID:

            --> Close database;
            --> Open database with correct session UID;
            --> Insert 'same_session_packets'.

        (3) No database file is currently open:

            --> Open database with correct session UID;
            --> Insert 'same_session_packets'.

        (4) A database is currently open, with correct session UID:

            --> Insert 'same_session_packets'.
        """

        if not same_session_packets:
            # Nothing to insert.
            return

        if (
            self._conn is not None
            and self._sessionUID != same_session_packets[0].sessionUID
        ):
            # Close database if it's recording a different session.
            self._close_database()

        if self._conn is None:
            # Open database with the correct sessionID.
            self._open_database(same_session_packets[0].sessionUID)

        # Write packets.
        self._insert_and_commit_same_session_packets(same_session_packets)

    def process_incoming_packets(self, timestamped_packets):
        """Process incoming packets by recording them into the correct database file.

        The incoming 'timestamped_packets' is a list of timestamped raw UDP packets.

        We process them to a variable 'same_session_packets', which is a list of consecutive
        packets having the same 'sessionUID' field. In this list, each packet is a 11-element tuple
        that can be inserted into the 'packets' table of the database.

        The 'same_session_packets' are then passed on to the '_process_same_session_packets'
        method that writes them into the appropriate database file.
        """

        t1 = time.monotonic()

        # Invariant to be guaranteed: all packets in 'same_session_packets' have the same 'sessionUID' field.
        same_session_packets = []

        for (timestamp, packet) in timestamped_packets:

            if len(packet) < ctypes.sizeof(PacketHeader):
                logging.error(
                    "Dropped bad packet of size {} (too short).".format(
                        len(packet)
                    )
                )
                continue

            header = PacketHeader.from_buffer_copy(packet)

            packet_type_tuple = (
                header.packetFormat,
                header.packetVersion,
                header.packetId,
            )

            packet_type = HeaderFieldsToPacketType.get(packet_type_tuple)
            if packet_type is None:
                logging.error(
                    "Dropped unrecognized packet (format, version, id) = %r.",
                    packet_type_tuple,
                )
                continue

            if len(packet) != ctypes.sizeof(packet_type):
                logging.error(
                    "Dropped packet with unexpected size; "
                    "(format, version, id) = %r packet, size = %d, expected %d.",
                    packet_type_tuple,
                    len(packet),
                    ctypes.sizeof(packet_type),
                )
                continue

            if header.packetId == PacketID.EVENT:  # Log Event packets
                event_packet = unpack_udp_packet(packet)
                logging.info(
                    "Recording event packet: %s",
                    event_packet.eventStringCode.decode(),
                )

            # NOTE: the sessionUID is not reliable at the start of a session (in F1 2018, need to check for F1 2019).
            # See: http://forums.codemasters.com/discussion/138130/bug-f1-2018-pc-v1-0-4-udp-telemetry-bad-session-uid-in-first-few-packets-of-a-session

            # Create an INSERT-able tuple for the data in this packet.
            #
            # Note that we convert the sessionUID to a 16-digit hex string here.
            # SQLite3 can store 64-bit numbers, but only signed ones.
            # To prevent any issues, we represent the sessionUID as a 16-digit hex string instead.

            session_packet = SessionPacket(
                timestamp,
                header.packetFormat,
                header.gameMajorVersion,
                header.gameMinorVersion,
                header.packetVersion,
                header.packetId,
                f"{header.sessionUID:016x}",
                header.sessionTime,
                header.frameIdentifier,
                header.playerCarIndex,
                packet,
            )

            if (
                len(same_session_packets) > 0
                and same_session_packets[0].sessionUID
                != session_packet.sessionUID
            ):
                # Write 'same_session_packets' collected so far to the correct session database, then forget about them.
                self._process_same_session_packets(same_session_packets)
                same_session_packets.clear()

            same_session_packets.append(session_packet)

        # Write 'same_session_packets' to the correct session database, then forget about them.
        # The 'same_session_packets.clear()' is not strictly necessary here, because 'same_session_packets' is about to
        #   go out of scope; but we make it explicit for clarity.

        self._process_same_session_packets(same_session_packets)
        same_session_packets.clear()

        t2 = time.monotonic()

        duration = t2 - t1

        logging.info(
            "Recorded %d packets in %.3f ms.",
            len(timestamped_packets),
            duration * 1000.0,
        )

    def no_packets_received(self, age: float) -> None:
        """No packets were received for a considerable time. If a database file is open, close it."""
        if self._conn is None:
            logging.info("No packets to record for %.3f seconds.", age)
        else:
            logging.info(
                "No packets to record for %.3f seconds; closing file due to inactivity.",
                age,
            )
            self._close_database()


class PacketRecorderThread(threading.Thread):
    """The PacketRecorderThread writes telemetry data to SQLite3 files."""

    def __init__(self, record_interval):
        super().__init__(name="recorder")
        self._record_interval = record_interval
        self._packets = []
        self._packets_lock = threading.Lock()
        self._socketpair = socket.socketpair()

    def close(self):
        for sock in self._socketpair:
            sock.close()

    def run(self):
        """Receive incoming packets and hand them over the the PacketRecorder.

        This method runs in its own thread.
        """

        selector = selectors.DefaultSelector()
        key_socketpair = selector.register(
            self._socketpair[0], selectors.EVENT_READ
        )

        recorder = PacketRecorder()

        packets = []

        logging.info("Recorder thread started.")

        quitflag = False
        inactivity_timer = time.time()
        while not quitflag:

            # Calculate the timeout value that will bring us in sync with the next period.
            timeout = (-time.time()) % self._record_interval
            # If the timeout interval is too short, increase its length by 1 period.
            if timeout < 0.5 * self._record_interval:
                timeout += self._record_interval

            for (key, events) in selector.select(timeout):
                if key == key_socketpair:
                    quitflag = True

            # Swap packets, so the 'record_packet' method can be called uninhibited as soon as possible.
            with self._packets_lock:
                (packets, self._packets) = (self._packets, packets)

            if len(packets) != 0:
                inactivity_timer = packets[-1].timestamp
                recorder.process_incoming_packets(packets)
                packets.clear()
            else:
                t_now = time.time()
                age = t_now - inactivity_timer
                recorder.no_packets_received(age)
                inactivity_timer = t_now

        recorder.close()

        selector.close()

        logging.info("Recorder thread stopped.")

    def request_quit(self):
        """Request termination of the PacketRecorderThread.

        Called from the main thread to request that we quit.
        """
        self._socketpair[1].send(b"\x00")

    def record_packet(self, timestamped_packet):
        """Called from the receiver thread for every UDP packet received."""
        with self._packets_lock:
            self._packets.append(timestamped_packet)


class PacketReceiverThread(threading.Thread):
    """The PacketReceiverThread receives incoming telemetry packets via the network and passes them to the PacketRecorderThread for storage."""

    def __init__(self, udp_port, recorder_thread):
        super().__init__(name="receiver")
        self._udp_port = udp_port
        self._recorder_thread = recorder_thread
        self._socketpair = socket.socketpair()

    def close(self):
        for sock in self._socketpair:
            sock.close()

    def run(self):
        """Receive incoming packets and hand them over to the PacketRecorderThread.

        This method runs in its own thread.
        """

        udp_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )

        # Allow multiple receiving endpoints.
        if sys.platform in ["darwin"]:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        elif sys.platform in ["linux", "win32"]:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Accept UDP packets from any host.
        address = ("", self._udp_port)
        udp_socket.bind(address)

        selector = selectors.DefaultSelector()

        key_udp_socket = selector.register(udp_socket, selectors.EVENT_READ)
        key_socketpair = selector.register(
            self._socketpair[0], selectors.EVENT_READ
        )

        logging.info(
            "Receiver thread started, reading UDP packets from port %d",
            self._udp_port,
        )

        quitflag = False
        while not quitflag:
            for (key, events) in selector.select():
                timestamp = time.time()
                if key == key_udp_socket:
                    # All telemetry UDP packets fit in 2048 bytes with room to spare.
                    packet = udp_socket.recv(2048)
                    timestamped_packet = TimestampedPacket(timestamp, packet)
                    self._recorder_thread.record_packet(timestamped_packet)
                elif key == key_socketpair:
                    quitflag = True

        selector.close()
        udp_socket.close()
        for sock in self._socketpair:
            sock.close()

        logging.info("Receiver thread stopped.")

    def request_quit(self):
        """Request termination of the PacketReceiverThread.

        Called from the main thread to request that we quit.
        """
        self._socketpair[1].send(b"\x00")


def main():
    """Record incoming telemetry data until the user presses enter."""

    # Configure logging.

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-23s | %(threadName)-10s | %(levelname)-5s | %(message)s",
    )
    logging.Formatter.default_msec_format = "%s.%03d"

    # Parse command line arguments.

    parser = argparse.ArgumentParser(
        description="Record F1 2019 telemetry data to SQLite3 files."
    )

    parser.add_argument(
        "-p",
        "--port",
        default=20777,
        type=int,
        help="UDP port to listen to (default: 20777)",
        dest="port",
    )
    parser.add_argument(
        "-i",
        "--interval",
        default=1.0,
        type=float,
        help="interval for writing incoming data to SQLite3 file, in seconds (default: 1.0)",
        dest="interval",
    )

    args = parser.parse_args()

    # Start recorder thread first, then receiver thread.

    quit_barrier = Barrier()

    recorder_thread = PacketRecorderThread(args.interval)
    recorder_thread.start()

    receiver_thread = PacketReceiverThread(args.port, recorder_thread)
    receiver_thread.start()

    wait_console_thread = WaitConsoleThread(quit_barrier)
    wait_console_thread.start()

    # Recorder, receiver, and wait_console threads are now active. Run until we're asked to quit.

    quit_barrier.wait()

    # Stop threads.

    wait_console_thread.request_quit()
    wait_console_thread.join()
    wait_console_thread.close()

    receiver_thread.request_quit()
    receiver_thread.join()
    receiver_thread.close()

    recorder_thread.request_quit()
    recorder_thread.join()
    recorder_thread.close()

    # All done.

    logging.info("All done.")


if __name__ == "__main__":
    main()

