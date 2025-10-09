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
    QMessageBox, QTabWidget, QPushButton, QFileDialog, QFrame, QListWidget, QListWidgetItem, QLabel, QStyle
)
from PySide6.QtGui import QIcon
from windows_tasks import enforce_password_history, backup_password_policy, restore_password_policy


# ----------------------- Central Logging -----------------------
class ActionLogger:
    def __init__(self):
        self.actions = []  # list of dicts: {timestamp, action, details}
        self.compliance_records = []  # list of dicts: {parameter, previous, current, status, severity, timestamp}
        self.rollback_records = []  # list of dicts: {timestamp, parameter, backup_path}

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
        self.rollback_records.clear()

    def add_rollback(self, parameter: str, backup_path: str):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.rollback_records.append({
            "timestamp": ts,
            "parameter": parameter,
            "backup_path": backup_path,
        })


action_logger = ActionLogger()

class WorkerSignals(QObject):
    log = Signal(str)
    progress = Signal(int)
    finished = Signal()

class TaskWorker(threading.Thread):
    def __init__(self, tasks: List[QTreeWidgetItem], signals: WorkerSignals, stop_event: threading.Event, tasks_hierarchy: List[dict]):
        super().__init__(daemon=True)
        self.tasks = tasks
        self.signals = signals
        self.stop_event = stop_event
        self.tasks_hierarchy = tasks_hierarchy

    def run(self):
        total = len(self.tasks)
        for i, item in enumerate(self.tasks, start=1):
            if self.stop_event.is_set():
                self.signals.log.emit("Execution stopped by user.")
                break

            task_name = item.text(0)
            self.signals.log.emit(f"Starting: {task_name}")

            # Find script_key from tasks_hierarchy
            script_key = None
            for task in self.tasks_hierarchy:
                if task.get("title") == task_name:
                    script_key = task.get("script_key")
                    break

            # (Backup is now created once at run start)

            # Execute corresponding function
            result_text = ""
            if script_key:
                func = globals().get(script_key)
                if func:
                    try:
                        result = func()
                        
                        # Handle both string and dictionary returns
                        if isinstance(result, dict):
                            result_text = result.get("message", str(result))
                            previous_value = result.get("previous", "Unknown")
                            current_value = result.get("current", "Unknown")
                            status = "Executed" if result.get("status") == "success" else "Failed"
                        else:
                            result_text = str(result)
                            previous_value = "Unknown"
                            current_value = str(result)
                            status = "Executed"
                        
                        self.signals.log.emit(result_text)
                        action_logger.add_compliance(
                            parameter=task_name,
                            previous=previous_value,
                            current=current_value,
                            status=status,
                            severity="High"
                        )
                    except Exception as e:
                        self.signals.log.emit(f"❌ Error executing '{task_name}': {str(e)}")

            # Simulate progress while executing (optional)
            for step in range(10):
                if self.stop_event.is_set():
                    self.signals.log.emit(f"Task '{task_name}' interrupted.")
                    break
                time.sleep(0.05)
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
                # Headings are checkable but not auto-tristate to avoid confusion
                heading_item.setFlags(heading_item.flags() | Qt.ItemIsUserCheckable)
                heading_item.setCheckState(0, Qt.Unchecked)
                heading_map[heading] = {"item": heading_item, "subheadings": {}}

            heading_entry = heading_map[heading]
            if subheading not in heading_entry["subheadings"]:
                sub_item = QTreeWidgetItem(heading_entry["item"])
                sub_item.setText(0, subheading)
                # Subheadings are checkable but not auto-tristate
                sub_item.setFlags(sub_item.flags() | Qt.ItemIsUserCheckable)
                sub_item.setCheckState(0, Qt.Unchecked)
                heading_entry["subheadings"][subheading] = sub_item

            task_item = QTreeWidgetItem(heading_entry["subheadings"][subheading])
            task_item.setText(0, title)
            task_item.setData(0, Qt.UserRole, details)
            # Individual tasks are checkable
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
                item.setHidden(not (text in item.text(0).lower()))

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
        
        # If this item has children (heading or subheading), propagate to children
        if item.childCount() > 0:
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, state)
                # If child also has children, propagate to grandchildren
                if child.childCount() > 0:
                    for j in range(child.childCount()):
                        grandchild = child.child(j)
                        grandchild.setCheckState(0, state)
        
        # Update toggle select button label based on overall state
        self._update_toggle_button_text()

    def _update_toggle_button_text(self):
        """Update the toggle select button text based on current selection state"""
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
        # Create a single backup of current policy before executing tasks
        try:
            backup_path, backup_msg = backup_password_policy()
            if backup_path:
                self.append_log(f"Backup created: {backup_path}")
                action_logger.add_rollback(parameter="Batch Run", backup_path=backup_path)
                # Refresh rollback list in Backup tab
                try:
                    main_window = self.window()
                    if hasattr(main_window, 'backup_tab'):
                        main_window.backup_tab.refresh_task_rollbacks()
                except Exception:
                    pass
            elif backup_msg:
                self.append_log(f"Backup warning: {backup_msg}")
        except Exception as e:
            self.append_log(f"Backup error: {e}")

        self.append_log("Starting execution...")
        self.worker = TaskWorker(tasks, self.signals, self.stop_event, self.tasks_hierarchy)
        self.worker.start()

    def stop(self):
        if not self.worker or not self.worker.is_alive():
            self.append_log("No running job to stop.")
            return
        self.append_log("Stopping execution...")
        self.stop_event.set()

    def on_worker_finished(self):
        self.append_log("Execution finished.")
        # Refresh reporting tab if it exists
        try:
            # Find the main window and refresh the reporting tab
            main_window = self.window()
            if hasattr(main_window, 'logging_tab'):
                main_window.logging_tab.refresh_compliance_display()
        except:
            pass  # Silently fail if we can't refresh

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

        # (Top controls removed; actions are in the left backup panel toolbar)

        # ---------------- Log console ----------------
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log, 1)

        # ---------------- Two-column layout: Left Backup | Right Rollback ----------------
        main_row = QHBoxLayout()
        main_row.setContentsMargins(0, 0, 0, 0)
        main_row.setSpacing(8)

        # Left: Backup panel (50%)
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(0, 0, 0, 0)
        left_panel.setSpacing(6)

        # Top controls for backup (useful buttons)
        backup_controls = QHBoxLayout()
        backup_controls.setContentsMargins(0, 0, 0, 0)
        backup_controls.setSpacing(6)
        self.btn_backup_refresh = QPushButton()
        self.btn_backup_refresh.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.btn_backup_refresh.setToolTip("Refresh backups")
        self.btn_backup_refresh.clicked.connect(self.refresh_backups)
        backup_controls.addWidget(self.btn_backup_refresh)

        self.btn_backup_restore = QPushButton()
        self.btn_backup_restore.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        self.btn_backup_restore.setToolTip("Restore selected backup")
        self.btn_backup_restore.clicked.connect(self.restore_policy)
        self.btn_backup_restore.setEnabled(False)
        backup_controls.addWidget(self.btn_backup_restore)

        self.btn_backup_delete = QPushButton()
        self.btn_backup_delete.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.btn_backup_delete.setToolTip("Delete selected backup")
        self.btn_backup_delete.clicked.connect(self.delete_selected_backup)
        self.btn_backup_delete.setEnabled(False)
        backup_controls.addWidget(self.btn_backup_delete)

        self.btn_backup_open = QPushButton()
        self.btn_backup_open.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.btn_backup_open.setToolTip("Open backup folder")
        self.btn_backup_open.clicked.connect(self.open_backup_folder)
        backup_controls.addWidget(self.btn_backup_open)

        backup_controls.addStretch(1)

        # Top section (30%): Rollbacks
        rollback_label = QLabel("Rollbacks")
        rollback_label.setStyleSheet("font-weight: bold; margin: 0 0 4px 0;")
        left_panel.addWidget(rollback_label)
        self.rollback_list = QListWidget()
        self.rollback_list.setStyleSheet(
            "QListWidget::item:hover { background-color: #eeeeee; }\n"
            "QListWidget::item:selected { background-color: #dddddd; color: black; }"
        )
        left_panel.addWidget(self.rollback_list, stretch=3)
        rollback_actions = QHBoxLayout()
        self.btn_rollback_selected = QPushButton("Rollback Selected")
        self.btn_rollback_selected.setToolTip("Applies the saved INF for the selected task")
        self.btn_rollback_selected.clicked.connect(self.rollback_selected_task)
        self.btn_rollback_selected.setVisible(True)
        self.btn_rollback_selected.setEnabled(False)
        rollback_actions.addWidget(self.btn_rollback_selected)
        rollback_actions.addStretch(1)
        left_panel.addLayout(rollback_actions)

        # Bottom section (70%): Backups list + controls
        backups_label = QLabel("Backups")
        backups_label.setStyleSheet("font-weight: bold; margin: 8px 0 4px 0;")
        left_panel.addWidget(backups_label)
        # Place toolbar just below heading
        left_panel.addLayout(backup_controls)
        self.backup_list = QListWidget()
        self.backup_list.itemSelectionChanged.connect(self._on_backup_selection_changed)
        self.backup_list.setStyleSheet(
            "QListWidget::item:hover { background-color: #eeeeee; }\n"
            "QListWidget::item:selected { background-color: #dddddd; color: black; }"
        )
        # Allow double-click restore
        self.backup_list.itemDoubleClicked.connect(lambda _: self.restore_policy())
        left_panel.addWidget(self.backup_list, stretch=7)

        main_row.addLayout(left_panel, stretch=1)

        # Right: Backup Content (100%)
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(6)
        content_label = QLabel("Backup Content")
        content_label.setStyleSheet("font-weight: bold; margin: 0 0 4px 0;")
        right_panel.addWidget(content_label)
        self.backup_content = QPlainTextEdit()
        self.backup_content.setReadOnly(True)
        self.backup_content.setPlaceholderText("Select a backup to view contents...")
        try:
            from PySide6.QtGui import QFontDatabase
            fixed = QFontDatabase.systemFont(QFontDatabase.FixedFont)
            self.backup_content.setFont(fixed)
        except Exception:
            pass
        self.backup_content.setLineWrapMode(QPlainTextEdit.NoWrap)
        right_panel.addWidget(self.backup_content, stretch=1)

        main_row.addLayout(right_panel, stretch=1)
        layout.addLayout(main_row)

        # ---------------- Bottom: Log area with Export/Clear ----------------
        log_section = QVBoxLayout()
        log_header = QHBoxLayout()
        log_title = QLabel("Backup & Rollback Log")
        log_title.setStyleSheet("font-weight: bold;")
        log_header.addWidget(log_title)

        btn_export_log = QPushButton()
        btn_export_log.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        btn_export_log.setToolTip("Export log to a text file")
        btn_export_log.clicked.connect(self.export_backup_log)
        log_header.addWidget(btn_export_log)

        btn_clear_log = QPushButton()
        btn_clear_log.setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        btn_clear_log.setToolTip("Clear log")
        btn_clear_log.clicked.connect(self.clear_backup_log)
        log_header.addWidget(btn_clear_log)

        log_header.addStretch(1)
        log_section.addLayout(log_header)

        # Use the existing attribute name `self.log` to keep prior calls working
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Operational messages will appear here...")
        log_section.addWidget(self.log, stretch=1)

        layout.addLayout(log_section)

        # Legacy top controls removed; handled by toolbar buttons above the backup list

        # Initial load
        self.refresh_backups()


    # def backup_policy(self):
    #     path, msg = backup_password_policy()
    #     if path:
    #         self.log.appendPlainText(f"✅ Backup created at: {path}")
    #         self.refresh_backups()
    #     else:
    #         self.log.appendPlainText(f"❌ Backup failed: {msg}")

    def restore_policy(self):
        item = self.backup_list.currentItem()
        if not item:
            return
        path = item.data(Qt.UserRole)
        if not path:
            return
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Confirm Restore", 
            f"Are you sure you want to restore policy from:\n{path}\n\nThis will overwrite current security settings!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log.appendPlainText(f"🔄 Restoring policy from: {path}")
            msg = restore_password_policy(path)
            self.log.appendPlainText(msg)
        else:
            self.log.appendPlainText("❌ Policy restore cancelled by user.")

    def _on_backup_selection_changed(self):
        has_selection = self.backup_list.currentItem() is not None
        # Enable/disable icon buttons
        self.btn_backup_restore.setEnabled(has_selection)
        self.btn_backup_delete.setEnabled(has_selection)
        # Load content preview
        self.load_selected_backup_content()

        # Also update rollback button enabled state
        has_rb = self.rollback_list.currentItem() is not None
        self.btn_rollback_selected.setEnabled(has_rb)

        # Ensure selection change on rollback list toggles enable state
        self.rollback_list.itemSelectionChanged.connect(self._on_rollback_selection_changed)
        # Double-click to rollback
        self.rollback_list.itemDoubleClicked.connect(lambda _: self.rollback_selected_task())

    def _on_rollback_selection_changed(self):
        self.btn_rollback_selected.setEnabled(self.rollback_list.currentItem() is not None)

    def refresh_backups(self):
        try:
            from pathlib import Path
            backup_dir = Path(__file__).resolve().parent / "backup"
            backup_dir.mkdir(parents=True, exist_ok=True)
            files = sorted(backup_dir.glob("*.inf"), key=lambda p: p.stat().st_mtime, reverse=True)
            self.backup_list.clear()
            for p in files:
                item = QListWidgetItem(p.name)
                item.setData(Qt.UserRole, str(p))
                self.backup_list.addItem(item)
            # Refresh task rollback list from in-memory records
            self.refresh_task_rollbacks()
            # Update content preview for first item
            if self.backup_list.count() > 0:
                self.backup_list.setCurrentRow(0)
                self.load_selected_backup_content()
        except Exception as e:
            self.log.appendPlainText(f"❌ Failed to load backups list: {e}")

    def load_selected_backup_content(self):
        item = self.backup_list.currentItem()
        if not item:
            self.backup_content.clear()
            return
        path = item.data(Qt.UserRole)
        if not path:
            self.backup_content.clear()
            return
        # Try multiple encodings to render content properly
        for enc in ("utf-8-sig", "utf-16", "mbcs", "latin-1"):
            try:
                with open(path, "r", encoding=enc) as f:
                    text = f.read()
                # Show file path as header for clarity
                self.backup_content.setPlainText(f"{path}\n\n{text}")
                return
            except Exception:
                continue
        # Final fallback: binary read and decode best-effort
        try:
            with open(path, "rb") as f:
                raw = f.read()
            self.backup_content.setPlainText(f"{path}\n\n" + raw.decode("latin-1", errors="ignore"))
        except Exception as e:
            self.backup_content.setPlainText(f"Failed to read file:\n{e}")

    def refresh_task_rollbacks(self):
        try:
            self.rollback_list.clear()
            for rec in reversed(action_logger.rollback_records):
                text = f"{rec['parameter']}  |  {rec['timestamp']}"
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, rec['backup_path'])
                self.rollback_list.addItem(item)
        except Exception as e:
            self.log.appendPlainText(f"❌ Failed to load rollback list: {e}")

    def rollback_selected_task(self):
        item = self.rollback_list.currentItem()
        if not item:
            return
        path = item.data(Qt.UserRole)
        if not path:
            return
        # Confirm and apply
        reply = QMessageBox.question(
            self,
            "Confirm Rollback",
            f"Are you sure you want to rollback using:\n{path}\n\nThis will overwrite current security settings!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        msg = restore_password_policy(path)
        self.log.appendPlainText(msg)

    def delete_selected_backup(self):
        item = self.backup_list.currentItem()
        if not item:
            return
        path = item.data(Qt.UserRole)
        if not path:
            return
        try:
            import os
            os.remove(path)
            self.log.appendPlainText(f"🗑️ Deleted backup: {path}")
            self.refresh_backups()
        except Exception as e:
            self.log.appendPlainText(f"❌ Failed to delete backup: {e}")

    def open_backup_folder(self):
        try:
            import os
            from pathlib import Path
            backup_dir = Path(__file__).resolve().parent / "backup"
            backup_dir.mkdir(parents=True, exist_ok=True)
            os.startfile(str(backup_dir))
        except Exception as e:
            self.log.appendPlainText(f"❌ Failed to open folder: {e}")

    def export_backup_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Log", "backup_rollback_log.txt", "Text Files (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log.toPlainText())
            QMessageBox.information(self, "Export Log", f"Log exported successfully to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Log", f"Failed to export log:\n{str(e)}")

    def clear_backup_log(self):
        self.log.clear()


class LoggingReportingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Create two main sections
        main_splitter = QFrame()
        main_splitter.setFrameStyle(QFrame.StyledPanel)
        main_layout = QHBoxLayout(main_splitter)

        # Left section - Create Reports
        left_section = QVBoxLayout()
        left_section.setContentsMargins(10, 10, 5, 10)
        
        # Create report section
        create_group = QFrame()
        create_group.setFrameStyle(QFrame.StyledPanel)
        create_group.setMaximumHeight(200)
        create_layout = QVBoxLayout(create_group)
        
        create_title = QPushButton("📊 Create New Report")
        create_title.setStyleSheet("QPushButton { font-weight: bold; font-size: 14px; padding: 10px; background-color: #3498db; color: white; border: none; border-radius: 5px; }")
        create_title.clicked.connect(self.create_new_report)
        create_layout.addWidget(create_title)
        
        # Report name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Report Name:"))
        self.report_name_input = QLineEdit()
        self.report_name_input.setPlaceholderText("Enter report name...")
        self.report_name_input.setText(f"Compliance_Report_{time.strftime('%Y%m%d_%H%M%S')}")
        name_layout.addWidget(self.report_name_input)
        create_layout.addLayout(name_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_create_html = QPushButton("Create HTML Report")
        self.btn_create_html.clicked.connect(self.create_html_report)
        btn_layout.addWidget(self.btn_create_html)
        
        self.btn_create_pdf = QPushButton("Create PDF Report")
        self.btn_create_pdf.clicked.connect(self.create_pdf_report)
        btn_layout.addWidget(self.btn_create_pdf)
        
        create_layout.addLayout(btn_layout)
        left_section.addWidget(create_group)
        
        # Compliance results display
        results_label = QLabel("Compliance Results:")
        results_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        left_section.addWidget(results_label)
        
        self.compliance_display = QPlainTextEdit()
        self.compliance_display.setReadOnly(True)
        self.compliance_display.setPlaceholderText("Compliance results will appear here after running hardening tasks...")
        left_section.addWidget(self.compliance_display, 1)
        
        main_layout.addLayout(left_section, 1)

        # Right section - Report List
        right_section = QVBoxLayout()
        right_section.setContentsMargins(5, 10, 10, 10)
        
        # Report list section
        list_group = QFrame()
        list_group.setFrameStyle(QFrame.StyledPanel)
        list_layout = QVBoxLayout(list_group)
        
        list_title = QPushButton("📋 Generated Reports")
        list_title.setStyleSheet("QPushButton { font-weight: bold; font-size: 14px; padding: 10px; background-color: #27ae60; color: white; border: none; border-radius: 5px; }")
        list_title.clicked.connect(self.refresh_report_list)
        list_layout.addWidget(list_title)
        
        # Report list
        self.report_list = QListWidget()
        self.report_list.setAlternatingRowColors(True)
        list_layout.addWidget(self.report_list, 1)
        
        # Action buttons for report list (icon-only)
        action_buttons = QHBoxLayout()

        # Shared icon-only style with grey hover
        icon_btn_style = (
            "QPushButton { background-color: transparent; border: 1px solid #ccc; padding: 6px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #eee; }"
        )

        refresh_btn = QPushButton()
        refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_btn.setToolTip("Refresh")
        refresh_btn.setStyleSheet(icon_btn_style)
        refresh_btn.clicked.connect(self.refresh_report_list)
        action_buttons.addWidget(refresh_btn)

        delete_all_btn = QPushButton()
        delete_all_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_all_btn.setToolTip("Delete All Reports")
        delete_all_btn.setStyleSheet(icon_btn_style)
        delete_all_btn.clicked.connect(self.delete_all_reports)
        action_buttons.addWidget(delete_all_btn)

        list_layout.addLayout(action_buttons)
        
        right_section.addWidget(list_group)
        main_layout.addLayout(right_section, 1)

        layout.addWidget(main_splitter)

        # Create reports directories
        self.create_report_directories()
        
        # Refresh display on load
        self.refresh_compliance_display()
        self.refresh_report_list()

    def create_report_directories(self):
        """Create the reports directories if they don't exist"""
        try:
            from pathlib import Path
            base_dir = Path(__file__).resolve().parent
            html_dir = base_dir / "reports" / "html"
            pdf_dir = base_dir / "reports" / "pdf"
            html_dir.mkdir(parents=True, exist_ok=True)
            pdf_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating report directories: {e}")

    def create_new_report(self):
        """Generate a new report name with timestamp"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        self.report_name_input.setText(f"Compliance_Report_{timestamp}")

    def create_html_report(self):
        """Create HTML report and save to reports/html directory"""
        report_name = self.report_name_input.text().strip()
        if not report_name:
            QMessageBox.warning(self, "No Name", "Please enter a report name.")
            return
        
        try:
            from pathlib import Path
            base_dir = Path(__file__).resolve().parent
            html_dir = base_dir / "reports" / "html"
            html_dir.mkdir(parents=True, exist_ok=True)
            
            # Ensure .html extension
            if not report_name.endswith('.html'):
                report_name += '.html'
            
            html_path = html_dir / report_name
            html_content = self._build_html_report()
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            QMessageBox.information(self, "Report Created", f"HTML report saved to:\n{html_path}")
            self.refresh_report_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create HTML report:\n{str(e)}")

    def create_pdf_report(self):
        """Create PDF report and save to reports/pdf directory"""
        report_name = self.report_name_input.text().strip()
        if not report_name:
            QMessageBox.warning(self, "No Name", "Please enter a report name.")
            return
        
        try:
            from pathlib import Path
            base_dir = Path(__file__).resolve().parent
            pdf_dir = base_dir / "reports" / "pdf"
            pdf_dir.mkdir(parents=True, exist_ok=True)
            
            # Ensure .pdf extension
            if not report_name.endswith('.pdf'):
                report_name += '.pdf'
            
            pdf_path = pdf_dir / report_name
            self._build_pdf_report(str(pdf_path))
            
            QMessageBox.information(self, "Report Created", f"PDF report saved to:\n{pdf_path}")
            self.refresh_report_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create PDF report:\n{str(e)}")

    def refresh_report_list(self):
        """Refresh the list of generated reports"""
        try:
            from pathlib import Path
            base_dir = Path(__file__).resolve().parent
            html_dir = base_dir / "reports" / "html"
            pdf_dir = base_dir / "reports" / "pdf"
            
            self.report_list.clear()
            
            # Get all HTML reports
            if html_dir.exists():
                for html_file in sorted(html_dir.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True):
                    self._add_report_item(html_file, "HTML")
            
            # Get all PDF reports
            if pdf_dir.exists():
                for pdf_file in sorted(pdf_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True):
                    self._add_report_item(pdf_file, "PDF")
                    
        except Exception as e:
            print(f"Error refreshing report list: {e}")

    def _add_report_item(self, file_path, report_type):
        """Add a report item to the list with view buttons"""
        from pathlib import Path
        file_name = file_path.name
        file_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_path.stat().st_mtime))
        
        # Create custom widget for the list item
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        # Report info
        info_layout = QVBoxLayout()
        name_label = QLabel(file_name)
        name_label.setStyleSheet("font-weight: bold;")
        time_label = QLabel(f"Created: {file_time}")
        time_label.setStyleSheet("color: #666; font-size: 11px;")
        type_label = QLabel(f"Type: {report_type}")
        type_label.setStyleSheet("color: #666; font-size: 11px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(time_label)
        info_layout.addWidget(type_label)
        item_layout.addLayout(info_layout, 1)
        
        # Action buttons (icon-only)
        buttons_layout = QHBoxLayout()

        # Shared icon-only style with grey hover
        icon_btn_style = (
            "QPushButton { background-color: transparent; border: 1px solid #ccc; padding: 6px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #eee; }"
        )

        # View button
        view_btn = QPushButton()
        view_btn.setStyleSheet(icon_btn_style)
        view_btn.setToolTip("View Report")
        if report_type == "HTML":
            view_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            view_btn.clicked.connect(lambda checked, path=str(file_path): self.view_html_report(path))
        else:  # PDF
            view_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
            view_btn.clicked.connect(lambda checked, path=str(file_path): self.view_pdf_report(path))

        # Download button
        download_btn = QPushButton()
        download_btn.setStyleSheet(icon_btn_style)
        download_btn.setToolTip("Download Report")
        download_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        download_btn.clicked.connect(lambda checked, path=str(file_path): self.download_report(path))

        # Delete button
        delete_btn = QPushButton()
        delete_btn.setStyleSheet(icon_btn_style)
        delete_btn.setToolTip("Delete Report")
        delete_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_btn.clicked.connect(lambda checked, path=str(file_path): self.delete_report(path))

        buttons_layout.addWidget(view_btn)
        buttons_layout.addWidget(download_btn)
        buttons_layout.addWidget(delete_btn)

        item_layout.addLayout(buttons_layout)
        
        # Create list item and set custom widget
        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())
        self.report_list.addItem(list_item)
        self.report_list.setItemWidget(list_item, item_widget)

    def view_html_report(self, file_path):
        """Open HTML report in default browser"""
        try:
            import webbrowser
            import os
            webbrowser.open(f"file://{os.path.abspath(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open HTML report:\n{str(e)}")

    def view_pdf_report(self, file_path):
        """Open PDF report in default PDF viewer"""
        try:
            import webbrowser
            import os
            webbrowser.open(f"file://{os.path.abspath(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open PDF report:\n{str(e)}")

    def download_report(self, file_path):
        """Download report to user's chosen location"""
        try:
            from pathlib import Path
            import shutil
            
            file_path = Path(file_path)
            if not file_path.exists():
                QMessageBox.warning(self, "File Not Found", f"Report file not found:\n{file_path}")
                return
            
            # Get download location
            download_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Report As", 
                str(file_path.name),
                f"{file_path.suffix.upper()} Files (*{file_path.suffix})"
            )
            
            if download_path:
                # Copy file to chosen location
                shutil.copy2(file_path, download_path)
                QMessageBox.information(self, "Download Complete", f"Report saved to:\n{download_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download report:\n{str(e)}")

    def delete_report(self, file_path):
        """Delete report file with confirmation"""
        try:
            from pathlib import Path
            
            file_path = Path(file_path)
            if not file_path.exists():
                QMessageBox.warning(self, "File Not Found", f"Report file not found:\n{file_path}")
                return
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete this report?\n\n{file_path.name}\n\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                file_path.unlink()  # Delete the file
                QMessageBox.information(self, "Deleted", f"Report deleted successfully:\n{file_path.name}")
                # Refresh the report list
                self.refresh_report_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete report:\n{str(e)}")

    def delete_all_reports(self):
        """Delete all reports with confirmation"""
        try:
            from pathlib import Path
            
            base_dir = Path(__file__).resolve().parent
            html_dir = base_dir / "reports" / "html"
            pdf_dir = base_dir / "reports" / "pdf"
            
            # Count total files
            total_files = 0
            if html_dir.exists():
                total_files += len(list(html_dir.glob("*.html")))
            if pdf_dir.exists():
                total_files += len(list(pdf_dir.glob("*.pdf")))
            
            if total_files == 0:
                QMessageBox.information(self, "No Reports", "No reports found to delete.")
                return
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Confirm Delete All",
                f"Are you sure you want to delete ALL reports?\n\nThis will delete {total_files} report(s) from both HTML and PDF directories.\n\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                deleted_count = 0
                
                # Delete HTML reports
                if html_dir.exists():
                    for html_file in html_dir.glob("*.html"):
                        html_file.unlink()
                        deleted_count += 1
                
                # Delete PDF reports
                if pdf_dir.exists():
                    for pdf_file in pdf_dir.glob("*.pdf"):
                        pdf_file.unlink()
                        deleted_count += 1
                
                QMessageBox.information(self, "Deleted", f"Successfully deleted {deleted_count} report(s).")
                # Refresh the report list
                self.refresh_report_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete all reports:\n{str(e)}")

    def refresh_compliance_display(self):
        """Display compliance results in a readable format"""
        if not action_logger.compliance_records:
            self.compliance_display.setPlainText("No compliance results available. Run some hardening tasks to see results here.")
            return
        
        lines = []
        lines.append("COMPLIANCE RESULTS")
        lines.append("=" * 50)
        lines.append("")
        
        for record in action_logger.compliance_records:
            lines.append(f"Parameter: {record['parameter']}")
            lines.append(f"Previous: {record['previous']}")
            lines.append(f"Current: {record['current']}")
            lines.append(f"Status: {record['status']}")
            lines.append(f"Severity: {record['severity']}")
            lines.append(f"Timestamp: {record['timestamp']}")
            lines.append("-" * 30)
            lines.append("")
        
        self.compliance_display.setPlainText("\n".join(lines))


    def _build_html_report(self) -> str:
        # Calculate summary statistics
        total_actions = len(action_logger.actions)
        total_compliance = len(action_logger.compliance_records)
        high_severity = len([r for r in action_logger.compliance_records if r['severity'].upper() == 'HIGH'])
        medium_severity = len([r for r in action_logger.compliance_records if r['severity'].upper() == 'MEDIUM'])
        low_severity = len([r for r in action_logger.compliance_records if r['severity'].upper() == 'LOW'])
        
        # Build compliance rows with severity color coding
        rows = []
        for r in action_logger.compliance_records:
            severity_class = "severity-high" if r['severity'].upper() == 'HIGH' else "severity-medium" if r['severity'].upper() == 'MEDIUM' else "severity-low"
            rows.append(f"<tr><td>{r['parameter']}</td><td>{r['previous']}</td><td>{r['current']}</td><td>{r['status']}</td><td class='{severity_class}'>{r['severity']}</td><td>{r['timestamp']}</td></tr>")
        
        rows_html = "\n".join(rows)
        
        # Build action logs
        logs = "\n".join(f"<li><strong>[{a['timestamp']}]</strong> {a['action']}: {a['details']}</li>" for a in action_logger.actions)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>System Hardening Compliance Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }}
    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
    h1 {{ color: #2c3e50; margin: 0 0 10px 0; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
    h2 {{ color: #34495e; margin: 20px 0 10px 0; }}
    h3 {{ color: #7f8c8d; margin: 15px 0 5px 0; }}
    .summary {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }}
    .summary-item {{ display: inline-block; margin: 5px 20px 5px 0; font-weight: bold; }}
    .summary-high {{ color: #e74c3c; }}
    .summary-medium {{ color: #f39c12; }}
    .summary-low {{ color: #27ae60; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    th, td {{ border: 1px solid #bdc3c7; padding: 8px 12px; text-align: left; }}
    th {{ background: #34495e; color: white; font-weight: bold; }}
    tr:nth-child(even) {{ background-color: #f8f9fa; }}
    tr:hover {{ background-color: #e8f4f8; }}
    .severity-high {{ color: #e74c3c; font-weight: bold; }}
    .severity-medium {{ color: #f39c12; font-weight: bold; }}
    .severity-low {{ color: #27ae60; font-weight: bold; }}
    ul {{ margin-top: 6px; }}
    li {{ margin: 5px 0; }}
    .audit-trail {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #bdc3c7; color: #7f8c8d; font-size: 0.9em; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>System Hardening Compliance Report</h1>
    <p><strong>Generated:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Report ID:</strong> {hash(time.strftime('%Y%m%d%H%M%S')) % 10000:04d}</p>
    
    <div class="summary">
      <h3>Executive Summary</h3>
      <div class="summary-item">Total Actions: {total_actions}</div>
      <div class="summary-item">Compliance Records: {total_compliance}</div>
      <div class="summary-item summary-high">High Severity: {high_severity}</div>
      <div class="summary-item summary-medium">Medium Severity: {medium_severity}</div>
      <div class="summary-item summary-low">Low Severity: {low_severity}</div>
    </div>
    
    <div class="audit-trail">
      <h2>Audit Trail - Actions Log</h2>
      <p>Complete chronological log of all actions performed during the hardening process:</p>
      <ul>
        {logs if logs else "<li>No actions recorded.</li>"}
      </ul>
    </div>
    
    <h2>Compliance Results with Severity Ratings</h2>
    <p>Detailed compliance results showing parameter changes and severity levels:</p>
    <table>
      <thead>
        <tr>
          <th>Parameter</th>
          <th>Previous Value</th>
          <th>Current Value</th>
          <th>Status</th>
          <th>Severity</th>
          <th>Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {rows_html if rows_html else "<tr><td colspan='6'>No compliance records available.</td></tr>"}
      </tbody>
    </table>
    
    <div class="footer">
      <p>Report generated by System Hardening Tool</p>
      <p>This report provides a comprehensive audit trail of system hardening activities and compliance results.</p>
    </div>
  </div>
</body>
</html>
"""
        return html

    def _build_pdf_report(self, path: str):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
        except Exception as e:
            raise RuntimeError("ReportLab is not installed. Please install reportlab.") from e

        doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        story = []

        # Title and header
        story.append(Paragraph("System Hardening Compliance Report", styles['Title']))
        story.append(Paragraph(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Report ID: {hash(time.strftime('%Y%m%d%H%M%S')) % 10000:04d}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        total_actions = len(action_logger.actions)
        total_compliance = len(action_logger.compliance_records)
        high_severity = len([r for r in action_logger.compliance_records if r['severity'].upper() == 'HIGH'])
        medium_severity = len([r for r in action_logger.compliance_records if r['severity'].upper() == 'MEDIUM'])
        low_severity = len([r for r in action_logger.compliance_records if r['severity'].upper() == 'LOW'])
        
        summary_text = f"""
        <b>Total Actions Performed:</b> {total_actions}<br/>
        <b>Compliance Records:</b> {total_compliance}<br/>
        <b>High Severity Issues:</b> {high_severity}<br/>
        <b>Medium Severity Issues:</b> {medium_severity}<br/>
        <b>Low Severity Issues:</b> {low_severity}<br/>
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 12))

        # Actions Log with timestamps
        story.append(Paragraph("Audit Trail - Actions Log", styles['Heading2']))
        story.append(Paragraph("All actions performed during the hardening process with timestamps:", styles['Normal']))
        story.append(Spacer(1, 6))
        
        if action_logger.actions:
            for i, a in enumerate(action_logger.actions, 1):
                action_text = f"<b>[{a['timestamp']}]</b> {a['action']}"
                if a['details']:
                    action_text += f": {a['details']}"
                story.append(Paragraph(f"{i}. {action_text}", styles['Normal']))
        else:
            story.append(Paragraph("No actions recorded.", styles['Normal']))
        
        story.append(PageBreak())

        # Compliance Results with Severity Ratings
        story.append(Paragraph("Compliance Results with Severity Ratings", styles['Heading2']))
        story.append(Paragraph("Detailed compliance results showing parameter changes and severity levels:", styles['Normal']))
        story.append(Spacer(1, 12))

        if action_logger.compliance_records:
            # Group by severity for better organization
            severity_groups = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
            for r in action_logger.compliance_records:
                severity = r['severity'].upper()
                if severity in severity_groups:
                    severity_groups[severity].append(r)
                else:
                    severity_groups['LOW'].append(r)

            for severity, records in severity_groups.items():
                if records:
                    # Severity header with color coding
                    color = colors.red if severity == 'HIGH' else colors.orange if severity == 'MEDIUM' else colors.green
                    story.append(Paragraph(f"<font color='{color.hexval()}'><b>{severity} SEVERITY ISSUES ({len(records)})</b></font>", styles['Heading3']))
                    
                    for r in records:
                        story.append(Paragraph(f"<b>Parameter:</b> {r['parameter']}", styles['Normal']))
                        story.append(Paragraph(f"<b>Previous Value:</b> {r['previous']}", styles['Normal']))
                        story.append(Paragraph(f"<b>Current Value:</b> {r['current']}", styles['Normal']))
                        story.append(Paragraph(f"<b>Status:</b> {r['status']}", styles['Normal']))
                        story.append(Paragraph(f"<b>Severity:</b> {r['severity']}", styles['Normal']))
                        story.append(Paragraph(f"<b>Timestamp:</b> {r['timestamp']}", styles['Normal']))
                        story.append(Spacer(1, 6))
                    
                    story.append(Spacer(1, 12))

            # Summary table
            story.append(Paragraph("Compliance Summary Table", styles['Heading3']))
            data = [["Parameter", "Previous", "Current", "Status", "Severity", "Timestamp"]]
            for r in action_logger.compliance_records:
                # Color code severity in the table
                severity_color = colors.red if r['severity'].upper() == 'HIGH' else colors.orange if r['severity'].upper() == 'MEDIUM' else colors.green
                data.append([
                    r['parameter'], 
                    r['previous'], 
                    r['current'], 
                    r['status'], 
                    f"<font color='{severity_color.hexval()}'>{r['severity']}</font>", 
                    r['timestamp']
                ])

            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No compliance records available.", styles['Normal']))

        # Footer
        story.append(Spacer(1, 24))
        story.append(Paragraph("End of Report", styles['Normal']))
        story.append(Paragraph(f"Report generated by System Hardening Tool on {time.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

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
        tabs.addTab(self.logging_tab, "Reporting")
        main_layout.addWidget(tabs)
        self.setCentralWidget(main)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
