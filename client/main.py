import sys, struct
from consts import TASK_LIST_MAGIC, SEND_DONE_MAGIC, TASK_STATUS_MAGIC
from setting import SettingsDialog
from serial import Serial
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtCore import QFile, QIODevice, QByteArray

class Main(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial = Serial()
        self.serial.response.readyResponse.connect(self.update_status)

        ui_file_name = "mainwindow.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)

        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        if not self.ui:
            print(loader.errorString())
            sys.exit(-1)

        self.ui.connect_dock.setWidget(SettingsDialog(self.serial))
        self.ui.view_menu.addAction(self.ui.connect_dock.toggleViewAction())
        self.ui.view_menu.addAction(self.ui.task_dock.toggleViewAction())
        self.ui.view_menu.addAction(self.ui.console_dock.toggleViewAction())
        self.ui.show()

    def update_status(self, data):
        ptr = data.indexOf(QByteArray(TASK_LIST_MAGIC))
        if ptr != -1:
            ptr += len(TASK_LIST_MAGIC)
            self.sizeof_int = int.from_bytes(data[ptr])
            self.sizeof_ptr = int.from_bytes(data[ptr+1])
            self.sizeof_pri = int.from_bytes(data[ptr+2])
            self.sizeof_uint = int.from_bytes(data[ptr+3])
            self.sizeof_id = int.from_bytes(data[ptr+4])
            self.sizeof_reltim = int.from_bytes(data[ptr+5])
            self.sizeof_fp = int.from_bytes(data[ptr+6])
            data = data[ptr+7:]
            count, length = struct.unpack_from("<ii", data)
            offset = struct.calcsize("<ii")
            assert(self.sizeof_int * count <= length)
            end_offset = len(SEND_DONE_MAGIC)
            for n, v in enumerate(struct.iter_unpack("<i", data[offset:-end_offset])):
                self.ui.task_list.insertRow(n)
                self.ui.task_list.setItem(n, 0, QTableWidgetItem(str(v[0])))
                self.serial.write(QByteArray(b't' + struct.pack("<i", n)))
                if n >= count - 1:
                    break
        ptr = data.indexOf(QByteArray(TASK_STATUS_MAGIC))
        if ptr != -1:
            ptr += len(TASK_STATUS_MAGIC)
            data = data[ptr:]
            length = struct.unpack_from("<b", data)
            data = data[1:]
            tskid = int.from_bytes(data[:self.sizeof_id], "little")
            data = data[1:]
            data = data[self.sizeof_id:]
            _exinf = data[:self.sizeof_ptr]
            data = data[self.sizeof_ptr:]
            tskpri = data[:self.sizeof_pri]
            self.ui.task_list.setItem(tskid, 1, QTableWidgetItem(str(int.from_bytes(tskpri, "big"))))


def main():
    app = QApplication(sys.argv)
    main = Main()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()