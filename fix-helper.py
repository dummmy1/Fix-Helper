import os
import sys

from PySide6.QtCore import QProcess
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QProgressBar
)


def unrar_path() -> str:
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'UnRAR.exe')


#app
class FixHelperApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Fix Helper App")

        self.base_dir: str | None = None
        self.part1_rar: str | None = None
        self.fix_repair_rar: str | None = None
        self.final_extract_path: str | None = None

        self.pick_btn = QPushButton("Select directory")
        self.run_btn = QPushButton("Extract And Apply Fix")
        self.run_btn.setEnabled(False)
        self.dir_label = QLabel("Directory: (none)")
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.hide()
        self.log = QPlainTextEdit()

        top = QHBoxLayout()
        top.addWidget(self.pick_btn)
        top.addWidget(self.run_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.dir_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.log)


        self.proc = QProcess(self)
        self.pick_btn.clicked.connect(self.on_pick_directory)
        self.run_btn.clicked.connect(self.on_run_extract)


# select the directory
    def on_pick_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "",
        )

        if not directory:
            return

        if directory:
            self.base_dir = directory
            self.dir_label.setText(f"Directory: {directory}")
            self.run_btn.setEnabled(True)
            self.log.appendPlainText(f"Selected Directory: {directory}")

        for file in os.listdir(directory):
            if file.lower().endswith("part1.rar") or file.lower().endswith("ofme.rar"):
                self.part1_rar = os.path.join(directory, file)
                break

        if not self.part1_rar:
            self.log.appendPlainText("Wrong folder, select a directory with the game's rar file(s)")
            return


        #Find Fix Repair Folder and Rar
        fix_repair_path = os.path.join(directory, "Fix Repair")
        if not os.path.isdir(fix_repair_path):
            self.log.appendPlainText("No Fix Repair Found")
            return
        self.fix_repair_rar = os.listdir(fix_repair_path)[0]

        if self.fix_repair_rar:
            self.log.appendPlainText(f"Fix repair rar found at: {os.path.join(fix_repair_path,self.fix_repair_rar)}")

        self.final_extract_path = os.path.join(directory, os.path.basename(directory))
        os.makedirs(self.final_extract_path, exist_ok=True)
        self.log.appendPlainText(f"Final Game Path: {self.final_extract_path}")
        return



    #start the extraction
    def on_run_extract(self) -> None:

        if not self.part1_rar or not self.final_extract_path or not self.fix_repair_rar or not self.base_dir or not self.dir_label:
            self.log.appendPlainText("Error: Missing required paths")
            return

        final_extract_path = self.final_extract_path
        password = "online-fix.me"
        self.progress.show()
        self.progress.setRange(0, 0)


        #Game files extraction with a moving bar to show it's doing something atleast
        self.proc.finished.disconnect() if self.proc.receivers("finished") else None
        self.proc.finished.connect(lambda *_: (
            self.log.appendPlainText("Game extract successful"),
            self.progress.setRange(0, 1),
            self.progress.setValue(1),
        ))
        self.proc.start(
            unrar_path(),
            ["x","-p"+password, self.part1_rar, self.base_dir]    #extract game first
        )


        #fix repair extraction
        self.proc.finished.disconnect() if self.proc.receivers("finished") else None
        self.proc.finished.connect(lambda *_: (
            self.log.appendPlainText("Fix Repair extract successful"),
            QDesktopServices.openUrl(QUrl.fromLocalFile(final_extract_path))
            ))
        self.proc.start(
            unrar_path(),
            ["x", "-p"+password, "-o+", "-y", self.fix_repair_rar, self.final_extract_path]
        )

        return









if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FixHelperApp()
    w.resize(900, 500)
    w.show()
    raise SystemExit(app.exec())

