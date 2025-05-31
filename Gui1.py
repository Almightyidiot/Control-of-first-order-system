import sys
import serial
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

class RealTimePlot(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super(RealTimePlot, self).__init__(parent)
        title = "<span style='color: black;font-weight: bold;'>Real-Time PID Data</span>"
        self.plot = self.addPlot(title=title)
        self.plot.addLegend()
        self.plot.setLabel('left', '<span style="font-weight: bold; color: black;">Voltage (V)</span>')
        self.plot.setLabel('bottom', '<span style="font-weight: bold; color: black;">Time (s)</span>')
        self.plot.showGrid(x=True, y=True)
        self.plot.getAxis('left').setPen(color='black')
        self.plot.getAxis('bottom').setPen(color='black') 
        self.plot.getAxis('left').setTextPen('black')  
        self.plot.getAxis('bottom').setTextPen('black')

        # Set background color to white for the plot area
        self.plot.getViewBox().setBackgroundColor('w')
        self.setBackground('#f0f0f0')
        # Crosshair cursor to show coordinates
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen='k')
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen='k')
        self.plot.addItem(self.vLine, ignoreBounds=True)
        self.plot.addItem(self.hLine, ignoreBounds=True)

        # Label for displaying coordinates
        self.coordLabel = pg.TextItem(anchor=(0,1),color='k')
        self.plot.addItem(self.coordLabel, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        # Initialize plot lines
        self.line_system_output = self.plot.plot([], [], pen=pg.mkPen('g', width=2), name='<span style="color: green;font-weight: bold;">System Output (°C)</span>')
        self.line_control_output = self.plot.plot([], [], pen=pg.mkPen('r', width=2), name='<span style="color: red;font-weight: bold;">Control Signal (V)</span>')
        self.line_setpoint = self.plot.plot([], [], pen=pg.mkPen('b', width=2), name='<span style="color: blue;font-weight: bold;">Setpoint (°C)</span>')
        
        self.x = []
        self.y_setpoint = []
        self.y_control_output = []
        self.y_system_output = []

        self.outputVoltageLabel = QtWidgets.QLabel("<span style='font-size: 16pt; color: Red;'>Current Temperature: 0.00 °C</span>", self)
        
    def update_plot(self, time, setpoint, control_output, system_output):
        self.x.append(time)
        self.y_setpoint.append(setpoint)
        self.y_control_output.append(control_output)
        self.y_system_output.append(system_output)
        
        self.line_setpoint.setData(self.x, self.y_setpoint)
        self.line_control_output.setData(self.x, self.y_control_output)
        self.line_system_output.setData(self.x, self.y_system_output)
        self.update_voltage_display(system_output)

    def update_voltage_display(self, voltage):
            self.outputVoltageLabel.setText(f"<span style='font-size: 16pt; color: black;'>Current Temperature: {voltage:.2f} °C</span>")

    def mouseMoved(self, evt):
        pos = evt[0]  # Using signal proxy turns original arguments into a tuple
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.vb.mapSceneToView(pos)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
            # Update the label with the current cursor position
            self.coordLabel.setText(f"Time={mousePoint.x():.2f}, Voltage={mousePoint.y():.2f}")
            self.coordLabel.setPos(mousePoint.x(), mousePoint.y())

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.plot = RealTimePlot(self)
        self.serial_port = self.setup_serial_connection()
        self.init_ui() 
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # 100ms interval
        self.timer.timeout.connect(self.read_serial_data)
        self.is_paused = False
        self.timer.start()

    def setup_serial_connection(self):
        specified_port = 'COM1'
        baud_rate = 9600
        try:
            arduino = serial.Serial(specified_port, baud_rate, timeout=1)
            print(f"Connected to Arduino via port {arduino.port}")
            return arduino
        except serial.SerialException as e:
            error_message = f"Error: Unable to connect to Arduino on port {specified_port}. {str(e)}"
            QtWidgets.QMessageBox.critical(self, "Connection Error", error_message)
            sys.exit(1)

    def init_ui(self):
        self.setWindowTitle('PID Controller GUI')
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)
        controls_layout = QtWidgets.QGridLayout()
        
        # UI controls for PID parameters
        self.setpoint = self.create_double_spin_box(2.5)
        self.kp = self.create_double_spin_box(0.17)
        self.ki = self.create_double_spin_box(0.3)
        self.kd = self.create_double_spin_box(0.06)

        self.update_button = QtWidgets.QPushButton('Update PID')
        self.reset_button = QtWidgets.QPushButton('Reset PID')
        self.reset_view_button = QtWidgets.QPushButton('Reset View') 
        controls_layout.addWidget(QtWidgets.QLabel("Setpoint:"), 0, 0, QtCore.Qt.AlignRight)
        controls_layout.addWidget(self.setpoint, 0, 1)
        controls_layout.addWidget(QtWidgets.QLabel("Kp:"), 1, 0, QtCore.Qt.AlignRight)
        controls_layout.addWidget(self.kp, 1, 1)
        controls_layout.addWidget(self.update_button, 1, 2, QtCore.Qt.AlignLeft)
        controls_layout.addWidget(QtWidgets.QLabel("Ki:"), 2, 0, QtCore.Qt.AlignRight)
        controls_layout.addWidget(self.ki, 2, 1)
        controls_layout.addWidget(self.reset_button, 2, 2, QtCore.Qt.AlignLeft)
        controls_layout.addWidget(QtWidgets.QLabel("Kd:"), 3, 0, QtCore.Qt.AlignRight)
        controls_layout.addWidget(self.kd, 3, 1)
        controls_layout.addWidget(self.reset_view_button, 3, 2, QtCore.Qt.AlignLeft)  
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.plot)

        self.update_button.clicked.connect(self.send_parameters)
        self.reset_button.clicked.connect(self.reset_plot)
        self.reset_view_button.clicked.connect(self.reset_view)  

    def create_double_spin_box(self, value):
        spin_box = QtWidgets.QDoubleSpinBox()
        spin_box.setRange(0, 10e10)
        spin_box.setDecimals(2)
        spin_box.setSingleStep(0.5)
        spin_box.setValue(value)
        spin_box.setAlignment(QtCore.Qt.AlignCenter)
        spin_box.setFixedSize(150, 30)
        return spin_box

    def send_parameters(self):
        params = f"{self.setpoint.value():.2f},{self.kp.value():.2f},{self.ki.value():.2f},{self.kd.value():.2f}\n"
        self.serial_port.write(params.encode())
        print(f"Sent PID parameters to Arduino: {params}")

    def reset_plot(self):
        self.serial_port.write(b'RESET\n')
        print("Sent reset command to Arduino.")
        # Clear data lists
        self.plot.x = []
        self.plot.y_setpoint = []
        self.plot.y_control_output = []
        self.plot.y_system_output = []

        # Update plot lines
        self.plot.line_setpoint.setData(self.plot.x, self.plot.y_setpoint)
        self.plot.line_control_output.setData(self.plot.x, self.plot.y_control_output)
        self.plot.line_system_output.setData(self.plot.x, self.plot.y_system_output)

    def reset_view(self):
        # Reset the plot view to show all the data with proper scaling
        self.plot.plot.enableAutoRange()

    def read_serial_data(self):
        while self.serial_port.in_waiting > 0:
            data = self.serial_port.readline().decode().strip()
            print("Received:", data)
            if data:
                try:
                    time, setpoint, control_output, system_output = map(float, data.split(','))
                    self.plot.update_plot(time, setpoint, control_output, system_output)
                except ValueError:
                    print("Received malformed data:", data)
                except Exception as e:
                    print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QLabel { color: black; }")
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
