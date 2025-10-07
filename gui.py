#!/usr/bin/env python3

import sys
import time
import threading
import platform
import json
from typing import List

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QProgressBar, QPlainTextEdit,
    QMessageBox, QTabWidget, QPushButton, QFileDialog, QFrame
)

# ----------------------- Central Logging -----------------------
class ActionLogger:
    def __init__(self):
        self.actions = []  # list of dicts: {timestamp, action, details}
        self.compliance_records = []  # list of dicts: {parameter, previous, current, status, severity, timestamp}

    def log(self, action: str, details: str = ""):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.actions.append({"timestamp": ts, "action": action, "details": details})

    def add_compliance(self, parameter: str, previous: str, current: str, status: str, severity: str):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.compliance_records.append({
            "timestamp": ts,
            "parameter": parameter,
            "previous": previous,
            "current": current,
            "status": status,
            "severity": severity,
        })

    def clear(self):
        self.actions.clear()
        self.compliance_records.clear()


action_logger = ActionLogger()

class WorkerSignals(QObject):
    log = Signal(str)
    progress = Signal(int)
    finished = Signal()

class TaskWorker(threading.Thread):
    def __init__(self, tasks: List[QTreeWidgetItem], signals: WorkerSignals, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.tasks = tasks
        self.signals = signals
        self.stop_event = stop_event

    def run(self):
        total = len(self.tasks)
        for i, item in enumerate(self.tasks, start=1):
            if self.stop_event.is_set():
                self.signals.log.emit("Execution stopped by user.")
                break
            task_name = item.text(0)
            self.signals.log.emit(f"Starting: {task_name}")
            for step in range(10):
                if self.stop_event.is_set():
                    self.signals.log.emit(f"Task '{task_name}' interrupted.")
                    break
                time.sleep(0.08)
                progress_pct = int(((i - 1) + (step + 1) / 10) / total * 100)
                self.signals.progress.emit(progress_pct)
            self.signals.log.emit(f"Completed: {task_name}")
        self.signals.progress.emit(100)
        self.signals.finished.emit()

def detect_os():
    system = platform.system()
    release = platform.release()
    version = platform.version()
    return system, release, version

def load_tasks_for_os(os_name: str):
    filename = f"{os_name.lower()}_tasks.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []
    return tasks

class HardeningTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stop_event = threading.Event()
        self.worker = None
        self.signals = WorkerSignals()
        self.signals.log.connect(self.append_log)
        self.signals.progress.connect(self.set_progress)
        self.signals.finished.connect(self.on_worker_finished)

        layout = QVBoxLayout(self)

        # Top: Filter & Select/Clear All & Toggle View
        top_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter tasks...")
        self.search_input.textChanged.connect(self.filter_tasks)
        top_row.addWidget(self.search_input)

        # Select/Clear toggle now moved inline with list controls

        self.view_hierarchy = True
        self.btn_toggle_view = QPushButton("List View")
        self.btn_toggle_view.clicked.connect(self.toggle_view)

        # Toggle select/clear all
        self.btn_toggle_select = QPushButton("Select All")
        self.btn_toggle_select.clicked.connect(self.toggle_select_all)

        # Track whether the tree is currently expanded
        self.is_tree_expanded = True
        self.btn_toggle_expand = QPushButton("Collapse All")
        self.btn_toggle_expand.clicked.connect(self.toggle_expand_collapse)
        # Visible only in hierarchy view
        self.btn_toggle_expand.setVisible(self.view_hierarchy)

        layout.addLayout(top_row)

        # Middle: Task tree + Details
        mid = QHBoxLayout()
        list_panel = QVBoxLayout()

        view_row = QHBoxLayout()
        view_row.addWidget(self.btn_toggle_select)
        view_row.addWidget(self.btn_toggle_view)
        view_row.addWidget(self.btn_toggle_expand)
        view_row.addStretch(1)
        list_panel.addLayout(view_row)

        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderHidden(True)
        self.task_tree.itemSelectionChanged.connect(self.on_task_selected)
        self.task_tree.itemChanged.connect(self.on_item_changed)
        self.task_tree.setFrameShape(QFrame.NoFrame)

        tree_frame = QFrame()
        tree_frame.setFrameShape(QFrame.StyledPanel)
        tree_frame.setFrameShadow(QFrame.Plain)
        tree_frame.setLineWidth(1)

        tree_wrap = QVBoxLayout(tree_frame)
        tree_wrap.setContentsMargins(2, 5, 2, 5)  # left, top, right, bottom
        tree_wrap.addWidget(self.task_tree, 1)
        list_panel.addWidget(tree_frame, 1)
        mid.addLayout(list_panel, 2)

        right_panel = QVBoxLayout()
        self.task_details = QPlainTextEdit()
        self.task_details.setReadOnly(True)
        self.task_details.setPlaceholderText("Select a task to see details...")
        right_panel.addWidget(self.task_details, 3)

        action_row = QHBoxLayout()
        self.btn_run_selected = QPushButton("Run Selected")
        self.btn_run_selected.clicked.connect(self.run_selected_tasks)
        action_row.addWidget(self.btn_run_selected)

        self.btn_run_all = QPushButton("Run All")
        self.btn_run_all.clicked.connect(self.run_all_tasks)
        action_row.addWidget(self.btn_run_all)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop)
        action_row.addWidget(self.btn_stop)

        right_panel.addLayout(action_row)
        mid.addLayout(right_panel, 3)
        layout.addLayout(mid)

        # Bottom: Progress + Execution log + Export/Clear buttons
        bottom = QVBoxLayout()

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        bottom.addWidget(self.progress)

        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        bottom.addWidget(self.log_console, 2)

        log_buttons = QHBoxLayout()
        self.btn_export_log = QPushButton("Export Log")
        self.btn_export_log.clicked.connect(self.export_log)
        log_buttons.addWidget(self.btn_export_log)

        self.btn_clear_log = QPushButton("Clear Log")
        self.btn_clear_log.clicked.connect(self.clear_log)
        log_buttons.addWidget(self.btn_clear_log)
        bottom.addLayout(log_buttons)

        layout.addLayout(bottom)

        self.populate_tasks_for_current_os()

    # ----------------------- Populate Tasks -----------------------
    def populate_tasks_for_current_os(self):
        system, release, version = detect_os()
        self.append_log(f"Detected OS: {system} {release} ({version})")
        self.tasks_hierarchy = load_tasks_for_os(system)
        self.populate_tasks_hierarchy()

    def populate_tasks_hierarchy(self):
        self.task_tree.clear()
        heading_map = {}
        for task in self.tasks_hierarchy:
            heading = task.get("heading", "General")
            subheading = task.get("subheading", "")
            title = task.get("title", "")
            details = task.get("details", "")

            if heading not in heading_map:
                heading_item = QTreeWidgetItem(self.task_tree)
                heading_item.setText(0, heading)
                heading_item.setFlags(heading_item.flags() | Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable)
                heading_item.setCheckState(0, Qt.Unchecked)
                heading_map[heading] = {"item": heading_item, "subheadings": {}}

            heading_entry = heading_map[heading]
            if subheading not in heading_entry["subheadings"]:
                sub_item = QTreeWidgetItem(heading_entry["item"])
                sub_item.setText(0, subheading)
                sub_item.setFlags(sub_item.flags() | Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable)
                sub_item.setCheckState(0, Qt.Unchecked)
                heading_entry["subheadings"][subheading] = sub_item

            task_item = QTreeWidgetItem(heading_entry["subheadings"][subheading])
            task_item.setText(0, title)
            task_item.setData(0, Qt.UserRole, details)
            task_item.setFlags(task_item.flags() | Qt.ItemIsUserCheckable)
            task_item.setCheckState(0, Qt.Unchecked)

        self.task_tree.expandAll()
        self.is_tree_expanded = True
        if hasattr(self, 'btn_toggle_expand'):
            self.btn_toggle_expand.setText("Collapse All")

    def populate_tasks_flat(self):
        self.task_tree.clear()
        for task in self.tasks_hierarchy:
            title = task.get("title", "")
            details = task.get("details", "")
            task_item = QTreeWidgetItem(self.task_tree)
            task_item.setText(0, title)
            task_item.setData(0, Qt.UserRole, details)
            task_item.setFlags(task_item.flags() | Qt.ItemIsUserCheckable)
            task_item.setCheckState(0, Qt.Unchecked)
        self.task_tree.expandAll()
        self.is_tree_expanded = True
        if hasattr(self, 'btn_toggle_expand'):
            self.btn_toggle_expand.setText("Collapse All")

    # ----------------------- Filter Tasks -----------------------
    def filter_tasks(self, text: str):
        text = text.lower().strip()
        for i in range(self.task_tree.topLevelItemCount()):
            item = self.task_tree.topLevelItem(i)
            if self.view_hierarchy:
                heading_visible = False
                for j in range(item.childCount()):
                    sub_item = item.child(j)
                    sub_visible = False
                    for k in range(sub_item.childCount()):
                        task_item = sub_item.child(k)
                        match = text in task_item.text(0).lower()
                        task_item.setHidden(not match)
                        sub_visible |= match
                    sub_item.setHidden(not sub_visible)
                    heading_visible |= sub_visible
                item.setHidden(not heading_visible)
            else:
                match = text in item.text(0).lower()
                item.setHidden(not match)

    # ----------------------- Toggle View -----------------------
    def toggle_view(self):
        self.view_hierarchy = not self.view_hierarchy
        if self.view_hierarchy:
            self.btn_toggle_view.setText("List View")
            self.populate_tasks_hierarchy()
        else:
            self.btn_toggle_view.setText("Hierarchy View")
            self.populate_tasks_flat()
        # Show expand/collapse toggle only in hierarchy view
        self.btn_toggle_expand.setVisible(self.view_hierarchy)

    def toggle_expand_collapse(self):
        if self.is_tree_expanded:
            self.task_tree.collapseAll()
            self.btn_toggle_expand.setText("Expand All")
            self.is_tree_expanded = False
        else:
            self.task_tree.expandAll()
            self.btn_toggle_expand.setText("Collapse All")
            self.is_tree_expanded = True

    # ----------------------- Logging -----------------------
    def append_log(self, text: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_console.appendPlainText(f"[{timestamp}] {text}")
        action_logger.log("Hardening", text)

    def set_progress(self, value: int):
        self.progress.setValue(value)

    def export_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Log", "hardening_log.txt", "Text Files (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.log_console.toPlainText())
                QMessageBox.information(self, "Export Log", f"Log exported successfully to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Log", f"Failed to export log:\n{str(e)}")

    def clear_log(self):
        self.log_console.clear()

    # ----------------------- Task Selection -----------------------
    def on_item_changed(self, item, column):
        state = item.checkState(0)
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
        # Update toggle select button label based on overall state
        all_checked = True
        for i in range(self.task_tree.topLevelItemCount()):
            if self.task_tree.topLevelItem(i).checkState(0) != Qt.Checked:
                all_checked = False
                break
        if hasattr(self, 'btn_toggle_select'):
            self.btn_toggle_select.setText("Clear All" if all_checked else "Select All")

    def select_all(self):
        for i in range(self.task_tree.topLevelItemCount()):
            self.task_tree.topLevelItem(i).setCheckState(0, Qt.Checked)

    def clear_all(self):
        for i in range(self.task_tree.topLevelItemCount()):
            self.task_tree.topLevelItem(i).setCheckState(0, Qt.Unchecked)

    def toggle_select_all(self):
        # Determine current aggregate state
        any_unchecked = False
        for i in range(self.task_tree.topLevelItemCount()):
            if self.task_tree.topLevelItem(i).checkState(0) != Qt.Checked:
                any_unchecked = True
                break

        if any_unchecked:
            self.select_all()
            self.btn_toggle_select.setText("Clear All")
        else:
            self.clear_all()
            self.btn_toggle_select.setText("Select All")

    def _gather_checked_tasks(self):
        checked = []
        def recursive_collect(item):
            for i in range(item.childCount()):
                child = item.child(i)
                if child.childCount() == 0 and child.checkState(0) == Qt.Checked:
                    checked.append(child)
                else:
                    recursive_collect(child)
        for i in range(self.task_tree.topLevelItemCount()):
            item = self.task_tree.topLevelItem(i)
            if item.childCount() == 0 and item.checkState(0) == Qt.Checked:
                checked.append(item)
            else:
                recursive_collect(item)
        return checked

    def run_selected_tasks(self):
        tasks = self._gather_checked_tasks()
        if not tasks:
            QMessageBox.warning(self, "No tasks", "Please select one or more tasks to run.")
            return
        self.start_worker(tasks)

    def run_all_tasks(self):
        for i in range(self.task_tree.topLevelItemCount()):
            self.task_tree.topLevelItem(i).setCheckState(0, Qt.Checked)
        tasks = self._gather_checked_tasks()
        self.start_worker(tasks)

    def start_worker(self, tasks):
        if self.worker and self.worker.is_alive():
            QMessageBox.warning(self, "Already running", "A run is already in progress.")
            return
        self.stop_event.clear()
        self.progress.setValue(0)
        self.append_log("Starting execution...")
        self.worker = TaskWorker(tasks, self.signals, self.stop_event)
        self.worker.start()

    def stop(self):
        if not self.worker or not self.worker.is_alive():
            self.append_log("No running job to stop.")
            return
        self.append_log("Stopping execution...")
        self.stop_event.set()

    def on_worker_finished(self):
        self.append_log("Execution finished.")

    def on_task_selected(self):
        sel_items = self.task_tree.selectedItems()
        details = []
        for item in sel_items:
            d = item.data(0, Qt.UserRole)
            if d:
                details.append(f"{item.text(0)}\n{d}\n")
        self.task_details.setPlainText("\n".join(details))


class BackupRollbackTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        self.btn_backup = QPushButton("Backup")
        self.btn_backup.clicked.connect(self.backup)
        controls.addWidget(self.btn_backup)

        self.btn_restore = QPushButton("Restore")
        self.btn_restore.clicked.connect(self.restore)
        controls.addWidget(self.btn_restore)

        controls.addStretch(1)
        layout.addLayout(controls)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log, 1)

    def backup(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Backup", "hardening_backup.json", "JSON (*.json)")
        if not path:
            return
        try:
            data = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "note": "Placeholder backup"}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.log.appendPlainText(f"Saved backup to: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup", f"Failed to save backup:\n{str(e)}")

    def restore(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Backup", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.log.appendPlainText(f"Loaded backup from: {path}\n{json.dumps(data, indent=2)}")
        except Exception as e:
            QMessageBox.critical(self, "Restore", f"Failed to load backup:\n{str(e)}")


class LoggingReportingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Controls
        controls = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Logs")
        self.btn_refresh.clicked.connect(self.refresh_logs)
        controls.addWidget(self.btn_refresh)

        self.btn_export_html = QPushButton("Export Report (HTML)")
        self.btn_export_html.clicked.connect(self.export_html)
        controls.addWidget(self.btn_export_html)

        self.btn_export_pdf = QPushButton("Export Report (PDF)")
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        controls.addWidget(self.btn_export_pdf)

        controls.addStretch(1)
        layout.addLayout(controls)

        # Logs console
        self.logs_console = QPlainTextEdit()
        self.logs_console.setReadOnly(True)
        layout.addWidget(self.logs_console, 2)

        # Placeholder to show how compliance rows look
        hint = QPlainTextEdit()
        hint.setReadOnly(True)
        hint.setPlainText("Report columns: Parameter | Previous | Current | Status | Severity")
        layout.addWidget(hint, 1)

        self.refresh_logs()

    def refresh_logs(self):
        lines = [f"[{a['timestamp']}] {a['action']}: {a['details']}".rstrip(': ') for a in action_logger.actions]
        self.logs_console.setPlainText("\n".join(lines))

    def export_html(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export HTML Report", "compliance_report.html", "HTML Files (*.html)")
        if not path:
            return
        try:
            html = self._build_html_report()
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            QMessageBox.information(self, "Export", f"HTML report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export", f"Failed to create HTML report:\n{str(e)}")

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF Report", "compliance_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return
        try:
            self._build_pdf_report(path)
            QMessageBox.information(self, "Export", f"PDF report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export", f"Failed to create PDF report:\n{str(e)}")

    def _build_html_report(self) -> str:
        rows = "\n".join(
            f"<tr><td>{r['parameter']}</td><td>{r['previous']}</td><td>{r['current']}</td><td>{r['status']}</td><td>{r['severity']}</td><td>{r['timestamp']}</td></tr>"
            for r in action_logger.compliance_records
        )
        logs = "\n".join(f"<li>[{a['timestamp']}] {a['action']}: {a['details']}</li>" for a in action_logger.actions)
        html = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>Compliance Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    h1, h2 {{ margin: 0 0 10px 0; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    ul {{ margin-top: 6px; }}
  </style>
  </head>
  <body>
    <h1>Compliance Report</h1>
    <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <h2>Actions Log</h2>
    <ul>
      {logs}
    </ul>
    <h2>Compliance Results</h2>
    <table>
      <thead>
        <tr>
          <th>Parameter</th><th>Previous</th><th>Current</th><th>Status</th><th>Severity</th><th>Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </body>
</html>
"""
        return html

    def _build_pdf_report(self, path: str):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
        except Exception as e:
            raise RuntimeError("ReportLab is not installed. Please install reportlab.") from e

        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Compliance Report", styles['Title']))
        story.append(Paragraph(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Actions log
        story.append(Paragraph("Actions Log", styles['Heading2']))
        for a in action_logger.actions:
            story.append(Paragraph(f"[{a['timestamp']}] {a['action']}: {a['details']}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Compliance table
        story.append(Paragraph("Compliance Results", styles['Heading2']))
        data = [["Parameter", "Previous", "Current", "Status", "Severity", "Timestamp"]]
        for r in action_logger.compliance_records:
            data.append([r['parameter'], r['previous'], r['current'], r['status'], r['severity'], r['timestamp']])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(table)

        doc.build(story)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Hardening Tool")
        self.resize(1000, 700)
        main = QWidget()
        main_layout = QVBoxLayout(main)
        tabs = QTabWidget()
        self.hardening_tab = HardeningTab()
        tabs.addTab(self.hardening_tab, "Hardening")
        self.backup_tab = BackupRollbackTab()
        tabs.addTab(self.backup_tab, "Backup && Rollback")
        self.logging_tab = LoggingReportingTab()
        tabs.addTab(self.logging_tab, "Logging && Reporting")
        main_layout.addWidget(tabs)
        self.setCentralWidget(main)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
