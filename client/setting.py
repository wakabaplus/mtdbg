import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QComboBox, QVBoxLayout, QMessageBox
from PySide6.QtCore import QFile, QIODevice, QIODeviceBase
from PySide6.QtSerialPort import QSerialPortInfo, QSerialPort

class SettingsDialog(QWidget):

    def __init__(self, serial, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial = serial

        ui_file_name = "settingwindow.ui"
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

        self.ui.baudrate_box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.ui.connect_button.clicked.connect(self.connect)
        self.ui.refresh_button.clicked.connect(self.send_request)
        self.ui.refresh_button.hide()
        self.ui.port_list.currentIndexChanged.connect(self.showPortInfo)

        self.fill_ports_parameters()
        self.fill_ports_info()
        self.update_settings()

        l = QVBoxLayout()
        l.addWidget(self.ui)
        self.setLayout(l)

    def showPortInfo(self, idx):
        if idx == -1:
            return

        data = self.ui.port_list.itemData(idx)
        self.ui.description_label.setText(f"Description: {data[1]}")
        self.ui.manufacturer_label.setText(f"Manufacturer: {data[2]}")

    def connect(self):
        if self.serial.isOpen():
            self.parent().parent().task_list.setRowCount(0)
            self.ui.connect_button.setText("Connect")
            self.ui.refresh_button.hide()
            self.serial.close()
        else:
            self.ui.connect_button.setText("Disconnect")
            self.ui.refresh_button.show()
            self.update_settings()
            self.open_serial()
            self.send_request()

    def send_request(self):
        self.serial.write("T".encode())

    def open_serial(self):
        name = self.serial.name

        if self.serial.open(QIODeviceBase.OpenModeFlag.ReadWrite):
            self.parent().parent().statusBar().showMessage(f"Connected to {name}")
        else:
            QMessageBox.critical(self, "Error", self.serial.errorString())
            self.parent().parent().statusBar().showMessage(f"Error occurred while connecting to {name}")

    def fill_ports_parameters(self):
        self.ui.baudrate_box.addItem("9600", QSerialPort.Baud9600)
        self.ui.baudrate_box.addItem("19200", QSerialPort.Baud19200)
        self.ui.baudrate_box.addItem("38400", QSerialPort.Baud38400)
        self.ui.baudrate_box.addItem("115200", QSerialPort.Baud115200)
        self.ui.baudrate_box.setCurrentIndex(3)

        self.ui.databits_box.addItem("5", QSerialPort.Data5)
        self.ui.databits_box.addItem("6", QSerialPort.Data6)
        self.ui.databits_box.addItem("7", QSerialPort.Data7)
        self.ui.databits_box.addItem("8", QSerialPort.Data8)
        self.ui.databits_box.setCurrentIndex(3)

        self.ui.parity_box.addItem("None", QSerialPort.NoParity)
        self.ui.parity_box.addItem("Even", QSerialPort.EvenParity)
        self.ui.parity_box.addItem("Odd", QSerialPort.OddParity)
        self.ui.parity_box.addItem("Mark", QSerialPort.MarkParity)
        self.ui.parity_box.addItem("Space", QSerialPort.SpaceParity)

        self.ui.stopbits_box.addItem("1", QSerialPort.OneStop)
        self.ui.stopbits_box.addItem("1.5", QSerialPort.OneAndHalfStop)
        self.ui.stopbits_box.addItem("2", QSerialPort.TwoStop)

        self.ui.flowcontrol_box.addItem("None", QSerialPort.NoFlowControl)
        self.ui.flowcontrol_box.addItem("RTS/CTS", QSerialPort.HardwareControl)
        self.ui.flowcontrol_box.addItem("XON/XOFF", QSerialPort.SoftwareControl)

    def fill_ports_info(self):
        self.ui.port_list.clear()
        infos = QSerialPortInfo.availablePorts()

        for info in infos:
            data = []
            description = info.description()
            manufacturer = info.manufacturer()
            data.append(info.portName())
            if description:
                data.append(description)
            else:
                data.append("")
            if manufacturer:
                data.append(manufacturer)
            else:
                data.append("")

            self.ui.port_list.addItem(data[0], data)

    def update_settings(self):
        self.serial.name = self.ui.port_list.currentText()

        baudrate = self.ui.baudrate_box.currentData()
        self.serial.baudRate = QSerialPort.BaudRate(baudrate)

        databits = self.ui.databits_box.currentData()
        self.serial.dataBits = QSerialPort.DataBits(databits)

        parity = self.ui.parity_box.currentData()
        self.serial.parity = QSerialPort.Parity(parity)

        stopbits = self.ui.stopbits_box.currentData()
        self.serial.stopBits = QSerialPort.StopBits(stopbits)

        flowcontrol = self.ui.flowcontrol_box.currentData()
        self.serial.flowControl = QSerialPort.FlowControl(flowcontrol)