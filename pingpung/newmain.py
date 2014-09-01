import sys

from PyQt4 import QtCore, QtGui

from pplib import pping, audio, maingui, pptab


class PingThread(QtCore.QThread):
    """ A QThread subclass for running the pings.

    Args:
        ip - the IP address or domain name of the target to ping
        ping_count - how many times to run this ping before the thread terminates
        interval - the time to sleep between pings
        packet_size - number of bytes to send per ping
        tab_id - the ID number of the tab which started the thread.
            This is used to match ping response to the correct tab.

    The results of a ping are sent via Qt Signals.  Errors initializing the ping are sent with a string describing the
    error, while the complete ping signal (including timeouts and such) includes a dictionary with the detailed results,
    as provided by the ping library in use.
    """

    def __init__(self, ip, ping_count, interval, packet_size, tab_id):
        self.ip = ip
        self.ping_count = ping_count
        self.interval = interval
        self.packet_size = packet_size
        self.tab_id = tab_id
        super(PingThread, self).__init__()

    def run(self):
        pcount = 0
        while (pcount < self.ping_count) or (self.ping_count == 0):
            pcount += 1
            # Cannot accept sequence number > 65535.  This resets seq number but does not affect stats totals
            if pcount > 65535:
                pcount = 0
            try:
                self.result = pping.ping(self.ip, 1000, pcount, self.packet_size)
            except pping.SocketError:
                self.emit(QtCore.SIGNAL('error'), "Socket error.  Verify that program is running as root/admin.")
                break
            except pping.AddressError:
                self.emit(QtCore.SIGNAL('error'), "Address error.  Bad IP address or domain name.")
                break
            else:
                self.result["tabID"] = self.tab_id
                self.emit(QtCore.SIGNAL('complete'), self.result)
                time.sleep(self.interval)


class PingPung(QtGui.QMainWindow):
    def __init__(self):
        app = QtGui.QApplication(sys.argv)
        super(PingPung, self).__init__()

        self.ui = maingui.Ui_MainWindow()
        self.ui.setupUi(self)

        # Hack until I can get Designer to only start with 1 tab
        self.ui.tab_bar.removeTab(0)
        self.ui.tab_bar.removeTab(0)

        self.new_tab()


        self.show()
        sys.exit(app.exec_())

    def new_tab(self, name="New Tab"):
        # Tab contents are in their own object, as each tab needs to operate independently of the others in all cases
        tab_ui = pptab.Ui_tab_container()
        new_tab_object = QtGui.QWidget()
        tab_ui.setupUi(new_tab_object)
        self.ui.tab_bar.addTab(new_tab_object, "New Tab")

    def connect_keys(self):
        #self.ui.ip_box.returnPressed.connect(self.start_ping)
        #self.ui.session_box.returnPressed.connect(self.start_ping)
        pass


    def start_ping(self):
        ip = self.ui
        ping_thread = PingThread()
        print("Start signal Acquired!")


if __name__ == '__main__':
    PingPung()