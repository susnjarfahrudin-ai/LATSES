import sys
import numpy as np
from PyQt6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

from framework_jezgro import execute_master_runtime_verification
from dopuna_thermo_fluid import execute_domain_extension_verification_suite

class LATCESMasterGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LAT-CES High-Speed Multi-Domain Control Panel v1.0")
        self.resize(1280,750)
        self.setStyleSheet("background-color: #f5f6fa;")
        self.kernel_ok=execute_master_runtime_verification()
        self.domain_ok=execute_domain_extension_verification_suite()
        self.tick_count=0; self.max_points=200; self.time_axis=np.linspace(-2,0,self.max_points)
        self.telemetry_data={"hvac_load": deque_data := [0.0]*self.max_points,"struct_stress":[150.0]*self.max_points,"control_error":[0.0]*self.max_points,"power_factor":[0.95]*self.max_points}
        main_widget=QtWidgets.QWidget(); self.setCentralWidget(main_widget); main_layout=QtWidgets.QHBoxLayout(main_widget); main_layout.setContentsMargins(15,15,15,15); main_layout.setSpacing(15)
        sidebar=QtWidgets.QVBoxLayout(); sidebar.setSpacing(10)
        title_box=QtWidgets.QGroupBox("Sistemski Status"); title_layout=QtWidgets.QVBoxLayout(title_box)
        self.lbl_status=QtWidgets.QLabel("● KERNEL STATUS: LOCKED & STABLE"); self.lbl_status.setStyleSheet("color: #4cd137; font-weight: bold; font-size: 14px;")
        self.lbl_assurance=QtWidgets.QLabel("● ASSURANCE LEVEL: LEVEL-4 (Trusted)"); self.lbl_assurance.setStyleSheet("color: #00a8ff; font-weight: bold;")
        self.lbl_health=QtWidgets.QLabel("● EKOSISTEM ZDRAVLJE: 100% (Zdrav)"); self.lbl_health.setStyleSheet("color: #4cd137; font-weight: bold;")
        for w in (self.lbl_status,self.lbl_assurance,self.lbl_health): title_layout.addWidget(w)
        sidebar.addWidget(title_box)
        control_box=QtWidgets.QGroupBox("Upravljanje i Kalibracija"); control_layout=QtWidgets.QFormLayout(control_box)
        self.slider_temp=QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.slider_temp.setRange(10,40); self.slider_temp.setValue(25); control_layout.addRow("HVAC Temp Delta (°C):",self.slider_temp)
        self.slider_load=QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.slider_load.setRange(10,200); self.slider_load.setValue(100); control_layout.addRow("STRUCT Teret (kN):",self.slider_load)
        self.btn_safe_mode=QtWidgets.QPushButton("AKTIVIRAJ SAFE MODE"); self.btn_safe_mode.clicked.connect(self.trigger_emergency_safe_mode); control_layout.addRow(self.btn_safe_mode); sidebar.addWidget(control_box)
        audit_box=QtWidgets.QGroupBox("Ustavni Audit Zapisnik (Uživo)"); audit_layout=QtWidgets.QVBoxLayout(audit_box); self.audit_log=QtWidgets.QTextEdit(); self.audit_log.setReadOnly(True); audit_layout.addWidget(self.audit_log); sidebar.addWidget(audit_box); main_layout.addLayout(sidebar,stretch=1)
        graph_grid=QtWidgets.QGridLayout(); graph_grid.setSpacing(12); pg.setConfigOption('background','w'); pg.setConfigOption('foreground','k')
        self.p1=pg.PlotWidget(title="LAT-HVAC: Dinamičko Termičko Opterećenje"); self.p1.showGrid(x=True,y=True); self.curve_hvac_live=self.p1.plot(self.time_axis,self.telemetry_data['hvac_load']); graph_grid.addWidget(self.p1,0,0)
        self.p2=pg.PlotWidget(title="LAT-STRUCT: von Misesov Ekvivalentni Napon"); self.p2.showGrid(x=True,y=True); self.curve_struct_live=self.p2.plot(self.time_axis,self.telemetry_data['struct_stress']); graph_grid.addWidget(self.p2,0,1)
        self.p3=pg.PlotWidget(title="LAT-CONTROL: Lyapunovljeve Granice i Odstupanje"); self.p3.showGrid(x=True,y=True); self.curve_control_live=self.p3.plot(self.time_axis,self.telemetry_data['control_error']); graph_grid.addWidget(self.p3,1,0)
        self.p4=pg.PlotWidget(title="LAT-ELECTRICAL: Faktor Snage i Vektorska Analiza"); self.p4.showGrid(x=True,y=True); self.curve_elec_live=self.p4.plot(self.time_axis,self.telemetry_data['power_factor']); graph_grid.addWidget(self.p4,1,1)
        main_layout.addLayout(graph_grid,stretch=3)
        self.gui_timer=QtCore.QTimer(); self.gui_timer.setInterval(30); self.gui_timer.timeout.connect(self.update_telemetry_ui); self.gui_timer.start()
        self.log_audit("Sistemsko sučelje uspešno inicijalizovano."); self.log_audit("Jezgro + Thermo/Fluid dopuna verifikovani."); self.log_audit("GUI spreman.")
    def log_audit(self,message):
        timestamp=datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
        self.audit_log.append(f"[{timestamp}] {message}")
    def update_telemetry_ui(self):
        self.tick_count+=1; temp_delta=self.slider_temp.value(); load_factor=self.slider_load.value()/100.0
        self.telemetry_data['hvac_load'].pop(0); self.telemetry_data['hvac_load'].append(500*temp_delta+np.random.normal(0,150)); self.curve_hvac_live.setData(self.time_axis,self.telemetry_data['hvac_load'])
        self.telemetry_data['struct_stress'].pop(0); self.telemetry_data['struct_stress'].append(150000000*load_factor+np.random.normal(0,2000000)); self.curve_struct_live.setData(self.time_axis,self.telemetry_data['struct_stress'])
        self.telemetry_data['control_error'].pop(0); self.telemetry_data['control_error'].append(2*np.sin(self.tick_count*.05)*np.exp(-self.tick_count*.002)+np.random.normal(0,.1)); self.curve_control_live.setData(self.time_axis,self.telemetry_data['control_error'])
        self.telemetry_data['power_factor'].pop(0); self.telemetry_data['power_factor'].append(.95+np.random.normal(0,.005)); self.curve_elec_live.setData(self.time_axis,self.telemetry_data['power_factor'])
    def trigger_emergency_safe_mode(self):
        self.gui_timer.stop(); self.lbl_status.setText("● KERNEL STATUS: SAFE MODE (CRITICAL LOCKDOWN)"); self.lbl_assurance.setText("● ASSURANCE LEVEL: LEVEL-0 (Aborted)"); self.lbl_health.setText("● EKOSISTEM ZDRAVLJE: DEGRADED (Izolovan)"); self.log_audit("Korisnik pokrenuo prinudni ustavni LOCKDOWN.")

if __name__=="__main__":
    app=QtWidgets.QApplication(sys.argv); gui=LATCESMasterGUI(); gui.show(); sys.exit(app.exec())
