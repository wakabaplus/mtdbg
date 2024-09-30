from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QByteArray, Signal, QObject
from consts import SEND_DONE_MAGIC

class Serial(QSerialPort):
    class SerialResponse(QObject):
        readyResponse = Signal(QByteArray)
        _data = QByteArray()

        def __init__(self):
            super().__init__()

        @property
        def data(self):
            return self._data

        @data.setter
        def data(self, res):
            self._data += res
            if self._data.indexOf(QByteArray(SEND_DONE_MAGIC)) != -1:
                self.readyResponse.emit(self._data)
                self._data.clear()

    _name = ""
    _baudRate = QSerialPort.BaudRate.Baud115200
    _dataBits = QSerialPort.DataBits.Data8
    _parity = QSerialPort.Parity.NoParity
    _stopBits = QSerialPort.StopBits.OneStop
    _flowControl = QSerialPort.FlowControl.NoFlowControl
    response = SerialResponse()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readyRead.connect(self.read)

    @property
    def name(self):
        return self._name

    @property
    def baudRate(self):
        return self._baudRate

    @property
    def dataBits(self):
        return self._dataBits

    @property
    def parity(self):
        return self._parity

    @property
    def stopBits(self):
        return self._stopBits

    @property
    def flowControl(self):
        return self._flowControl

    @name.setter
    def name(self, value):
        super().setPortName(value)
        self._name = value

    @baudRate.setter
    def baudRate(self, value):
        self.setBaudRate(value)
        self._baudRate = value

    @dataBits.setter
    def dataBits(self, value):
        self.setDataBits(value)
        self._dataBits = value

    @parity.setter
    def parity(self, value):
        self.setParity(value)
        self._parity = value

    @stopBits.setter
    def stopBits(self, value):
        self.setStopBits(value)
        self._stopBits = value

    @flowControl.setter
    def flowControl(self, value):
        self.setFlowControl(value)
        self._flowControl = value

    def read(self):
        self.response.data = self.readAll()