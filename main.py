import sys
import random
import math
from collections import deque
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QFileDialog, QColorDialog, QDialog,
    QDialogButtonBox, QLineEdit, QFontComboBox, QSpinBox,
    QLabel, QComboBox, QCheckBox, QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QImage, QPainter, QPen, QBrush, QColor, QAction, QFont, QTransform, QIcon
from PyQt6.QtCore import Qt, QPoint, QRect

class TextDialog(QDialog):
    """Cuadro de diálogo para configurar fuente, tamaño y estilo del texto."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insertar Texto")
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<b>Texto a insertar:</b>"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Escribe aquí...")
        layout.addWidget(self.text_input)

        font_row = QHBoxLayout()
        self.font_combo = QFontComboBox()
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 144)
        self.size_spin.setValue(18)
        self.size_spin.setSuffix(" pt")

        font_row.addWidget(QLabel("Fuente:"))
        font_row.addWidget(self.font_combo, 1)
        font_row.addWidget(QLabel("Tamaño:"))
        font_row.addWidget(self.size_spin)
        layout.addLayout(font_row)

        style_row = QHBoxLayout()
        self.bold_chk = QCheckBox("Negrita")
        self.bold_chk.setStyleSheet("font-weight: bold;")
        self.italic_chk = QCheckBox("Cursiva")
        self.italic_chk.setStyleSheet("font-style: italic;")
        self.underline_chk = QCheckBox("Subrayado")
        self.underline_chk.setStyleSheet("text-decoration: underline;")

        style_row.addWidget(self.bold_chk)
        style_row.addWidget(self.italic_chk)
        style_row.addWidget(self.underline_chk)
        style_row.addStretch()
        layout.addLayout(style_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_text_data(self):
        font = self.font_combo.currentFont()
        font.setPointSize(self.size_spin.value())
        font.setBold(self.bold_chk.isChecked())
        font.setItalic(self.italic_chk.isChecked())
        font.setUnderline(self.underline_chk.isChecked())
        return self.text_input.text(), font


class ResizeDialog(QDialog):
    """Cuadro de diálogo para redimensionar una selección o imagen pegada."""
    def __init__(self, current_w, current_h, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Redimensionar Selección")
        self.orig_w = current_w
        self.orig_h = current_h
        self._updating = False

        layout = QVBoxLayout(self)

        pct_row = QHBoxLayout()
        pct_row.addWidget(QLabel("Escala (%):"))
        self.pct_spin = QSpinBox()
        self.pct_spin.setRange(5, 500)
        self.pct_spin.setValue(100)
        self.pct_spin.setSuffix(" %")
        self.pct_spin.valueChanged.connect(self.on_pct_changed)
        pct_row.addWidget(self.pct_spin)
        layout.addLayout(pct_row)

        px_row = QHBoxLayout()
        self.w_spin = QSpinBox()
        self.w_spin.setRange(5, 4000)
        self.w_spin.setValue(current_w)
        self.w_spin.setSuffix(" px")
        self.w_spin.valueChanged.connect(self.on_w_changed)

        self.h_spin = QSpinBox()
        self.h_spin.setRange(5, 4000)
        self.h_spin.setValue(current_h)
        self.h_spin.setSuffix(" px")
        self.h_spin.valueChanged.connect(self.on_h_changed)

        px_row.addWidget(QLabel("Ancho:"))
        px_row.addWidget(self.w_spin)
        px_row.addWidget(QLabel("Alto:"))
        px_row.addWidget(self.h_spin)
        layout.addLayout(px_row)

        self.aspect_chk = QCheckBox("Mantener relación de aspecto")
        self.aspect_chk.setChecked(True)
        layout.addWidget(self.aspect_chk)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def on_pct_changed(self, pct):
        if self._updating:
            return
        self._updating = True
        self.w_spin.setValue(max(5, int(self.orig_w * pct / 100)))
        self.h_spin.setValue(max(5, int(self.orig_h * pct / 100)))
        self._updating = False

    def on_w_changed(self, new_w):
        if self._updating or not self.aspect_chk.isChecked():
            return
        self._updating = True
        ratio = self.orig_h / max(1, self.orig_w)
        self.h_spin.setValue(max(5, int(new_w * ratio)))
        self._updating = False

    def on_h_changed(self, new_h):
        if self._updating or not self.aspect_chk.isChecked():
            return
        self._updating = True
        ratio = self.orig_w / max(1, self.orig_h)
        self.w_spin.setValue(max(5, int(new_h * ratio)))
        self._updating = False

    def get_new_size(self):
        return self.w_spin.value(), self.h_spin.value()


class CanvasSizeDialog(QDialog):
    """Cuadro de diálogo para cambiar las dimensiones totales del lienzo."""
    def __init__(self, current_w, current_h, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tamaño del Lienzo")
        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        self.w_spin = QSpinBox()
        self.w_spin.setRange(16, 4096)
        self.w_spin.setValue(current_w)
        self.w_spin.setSuffix(" px")

        self.h_spin = QSpinBox()
        self.h_spin.setRange(16, 4096)
        self.h_spin.setValue(current_h)
        self.h_spin.setSuffix(" px")

        row.addWidget(QLabel("Ancho:"))
        row.addWidget(self.w_spin)
        row.addWidget(QLabel("Alto:"))
        row.addWidget(self.h_spin)
        layout.addLayout(row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_size(self):
        return self.w_spin.value(), self.h_spin.value()


class Canvas(QWidget):
    MARGIN = 8

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.zoom_factor = 1.0
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Inicializar atributos antes de llamar a update_widget_size()
        self.canvas_handle = None
        self.preview_canvas_size = None

        # Lienzo en blanco inicial (800 x 550 px)
        self.image = QImage(800, 550, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        self.temp_image = QImage()
        self.update_widget_size()

        # Historial (Ctrl+Z / Ctrl+Y)
        self.undo_stack = []
        self.redo_stack = []

        # Configuración de dibujo
        self.drawing = False
        self.current_tool = "pen"
        self.fill_shapes = False
        self.brush_size = 3
        self.brush_color = QColor("#000000")
        self.start_point = QPoint()
        self.last_point = QPoint()

        # Estado de Selección, Pegado y Redimensionado
        self.selection_rect = QRect()
        self.base_selected_image = QImage()
        self.selected_image = QImage()
        self.moving_selection = False
        self.selection_offset = QPoint()
        self.active_handle = None
        self.resize_orig_rect = QRect()

    def update_widget_size(self):
        img_w = self.preview_canvas_size[0] if self.preview_canvas_size else self.image.width()
        img_h = self.preview_canvas_size[1] if self.preview_canvas_size else self.image.height()
        w = max(1, int(img_w * self.zoom_factor)) + self.MARGIN
        h = max(1, int(img_h * self.zoom_factor)) + self.MARGIN
        self.setFixedSize(w, h)
        self.update()

    def set_zoom(self, factor):
        self.zoom_factor = factor
        self.update_widget_size()
        self.update_status_bar()

    def to_image_coords(self, widget_pt):
        x = int(widget_pt.x() / self.zoom_factor)
        y = int(widget_pt.y() / self.zoom_factor)
        return QPoint(x, y)

    def update_status_bar(self, pt=None):
        pos_str = f"Posición: {pt.x()}, {pt.y()} px  |  " if pt is not None else ""
        zoom_pct = int(self.zoom_factor * 100)
        w, h = self.preview_canvas_size if self.preview_canvas_size else (self.image.width(), self.image.height())
        size_str = f"Lienzo: {w} x {h} px  |  Zoom: {zoom_pct}%"
        if self.has_active_selection():
            sel_str = f"  |  Selección: {self.selection_rect.width()} x {self.selection_rect.height()} px (Arrastra esquinas para redimensionar, Shift mantiene proporción)"
        else:
            sel_str = ""
        self.parent_window.statusBar().showMessage(pos_str + size_str + sel_str)

    def save_state(self):
        self.undo_stack.append(self.image.copy())
        if len(self.undo_stack) > 20:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def has_active_selection(self):
        return not self.selection_rect.isNull() and not self.selected_image.isNull()

    def resize_canvas_to(self, new_w, new_h, record_undo=True):
        new_w = max(16, new_w)
        new_h = max(16, new_h)
        if new_w == self.image.width() and new_h == self.image.height():
            return
        if record_undo:
            self.save_state()
        new_img = QImage(new_w, new_h, QImage.Format.Format_RGB32)
        new_img.fill(Qt.GlobalColor.white)
        painter = QPainter(new_img)
        painter.drawImage(0, 0, self.image)
        self.image = new_img
        self.update_widget_size()
        self.update_status_bar()

    def get_canvas_handle_rects(self):
        z = self.zoom_factor
        w = int(self.image.width() * z)
        h = int(self.image.height() * z)
        s = 7
        return {
            "cr": QRect(w, h // 2 - s // 2, s, s),
            "cb": QRect(w // 2 - s // 2, h, s, s),
            "cbr": QRect(w, h, s, s),
        }

    def hit_test_canvas_handles(self, widget_pt):
        for name, rect in self.get_canvas_handle_rects().items():
            if rect.adjusted(-3, -3, 3, 3).contains(widget_pt):
                return name
        return None

    def get_handle_rects(self):
        if self.selection_rect.isNull():
            return {}
        z = self.zoom_factor
        r = QRect(
            int(self.selection_rect.left() * z),
            int(self.selection_rect.top() * z),
            int(self.selection_rect.width() * z),
            int(self.selection_rect.height() * z)
        )
        s = 8
        hs = s // 2
        cx, cy = r.center().x(), r.center().y()
        return {
            "tl": QRect(r.left() - hs, r.top() - hs, s, s),
            "tc": QRect(cx - hs, r.top() - hs, s, s),
            "tr": QRect(r.right() - hs, r.top() - hs, s, s),
            "ml": QRect(r.left() - hs, cy - hs, s, s),
            "mr": QRect(r.right() - hs, cy - hs, s, s),
            "bl": QRect(r.left() - hs, r.bottom() - hs, s, s),
            "bc": QRect(cx - hs, r.bottom() - hs, s, s),
            "br": QRect(r.right() - hs, r.bottom() - hs, s, s),
        }

    def hit_test_handles(self, widget_pt):
        for name, rect in self.get_handle_rects().items():
            if rect.adjusted(-3, -3, 3, 3).contains(widget_pt):
                return name
        return None

    def update_cursor_for_handle(self, handle, img_pt):
        cursors = {
            "tl": Qt.CursorShape.SizeFDiagCursor,
            "br": Qt.CursorShape.SizeFDiagCursor,
            "cbr": Qt.CursorShape.SizeFDiagCursor,
            "tr": Qt.CursorShape.SizeBDiagCursor,
            "bl": Qt.CursorShape.SizeBDiagCursor,
            "tc": Qt.CursorShape.SizeVerCursor,
            "bc": Qt.CursorShape.SizeVerCursor,
            "cb": Qt.CursorShape.SizeVerCursor,
            "ml": Qt.CursorShape.SizeHorCursor,
            "mr": Qt.CursorShape.SizeHorCursor,
            "cr": Qt.CursorShape.SizeHorCursor,
        }
        if handle in cursors:
            self.setCursor(cursors[handle])
        elif self.current_tool == "select" and self.selection_rect.contains(img_pt):
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)

    def commit_selection(self):
        if self.has_active_selection():
            req_w = max(self.image.width(), self.selection_rect.right() + 1)
            req_h = max(self.image.height(), self.selection_rect.bottom() + 1)
            if req_w > self.image.width() or req_h > self.image.height():
                self.resize_canvas_to(req_w, req_h, record_undo=False)

            painter = QPainter(self.image)
            painter.drawImage(self.selection_rect.topLeft(), self.selected_image)
            self.selection_rect = QRect()
            self.base_selected_image = QImage()
            self.selected_image = QImage()
            self.moving_selection = False
            self.active_handle = None
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.update()
            self.update_status_bar()

    def copy_selection(self):
        if self.has_active_selection():
            QApplication.clipboard().setImage(self.selected_image)

    def delete_selection(self):
        if not self.selection_rect.isNull():
            self.selection_rect = QRect()
            self.base_selected_image = QImage()
            self.selected_image = QImage()
            self.moving_selection = False
            self.active_handle = None
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.update()
            self.update_status_bar()

    def paste_image(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasImage():
            pasted = clipboard.image()
            if not pasted.isNull():
                self.commit_selection()
                self.save_state()
                pasted = pasted.convertToFormat(QImage.Format.Format_RGB32)

                new_w = max(self.image.width(), pasted.width())
                new_h = max(self.image.height(), pasted.height())
                if new_w > self.image.width() or new_h > self.image.height():
                    self.resize_canvas_to(new_w, new_h, record_undo=False)

                self.base_selected_image = pasted.copy()
                self.selected_image = pasted.copy()
                self.selection_rect = QRect(0, 0, pasted.width(), pasted.height())
                self.parent_window.select_tool("select", keep_selection=True)
                self.update()
                self.update_status_bar()
        else:
            QMessageBox.information(self, "Pegar", "No hay ninguna imagen copiada en el portapapeles.")

    def resize_canvas_dialog(self):
        self.commit_selection()
        dlg = CanvasSizeDialog(self.image.width(), self.image.height(), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_w, new_h = dlg.get_size()
            self.resize_canvas_to(new_w, new_h, record_undo=True)

    def resize_selection_dialog(self):
        if not self.has_active_selection():
            QMessageBox.information(self, "Redimensionar", "Primero pega una imagen o selecciona un área.")
            return
        dlg = ResizeDialog(self.selection_rect.width(), self.selection_rect.height(), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_w, new_h = dlg.get_new_size()
            self.selection_rect.setWidth(new_w)
            self.selection_rect.setHeight(new_h)
            self.selected_image = self.base_selected_image.scaled(
                new_w, new_h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            req_w = max(self.image.width(), self.selection_rect.right() + 1)
            req_h = max(self.image.height(), self.selection_rect.bottom() + 1)
            if req_w > self.image.width() or req_h > self.image.height():
                self.resize_canvas_to(req_w, req_h, record_undo=False)
            self.update()
            self.update_status_bar()

    def undo(self):
        self.commit_selection()
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.update_widget_size()
            self.update_status_bar()

    def redo(self):
        self.commit_selection()
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update_widget_size()
            self.update_status_bar()

    def clear_canvas(self):
        self.commit_selection()
        self.save_state()
        self.image.fill(Qt.GlobalColor.white)
        self.update()

    def crop_to_selection(self):
        if self.has_active_selection():
            self.save_state()
            cropped = self.selected_image.copy()
            self.selection_rect = QRect()
            self.base_selected_image = QImage()
            self.selected_image = QImage()
            self.image = cropped
            self.update_widget_size()
            self.update_status_bar()
        else:
            QMessageBox.information(self, "Recortar", "Primero selecciona un área o pega una imagen.")

    def rotate_90(self):
        transform = QTransform().rotate(90)
        if self.has_active_selection():
            self.base_selected_image = self.base_selected_image.transformed(transform)
            self.selected_image = self.selected_image.transformed(transform)
            cx, cy = self.selection_rect.center().x(), self.selection_rect.center().y()
            new_w, new_h = self.selected_image.width(), self.selected_image.height()
            new_x = max(0, cx - new_w // 2)
            new_y = max(0, cy - new_h // 2)
            self.selection_rect = QRect(new_x, new_y, new_w, new_h)
            req_w = max(self.image.width(), self.selection_rect.right() + 1)
            req_h = max(self.image.height(), self.selection_rect.bottom() + 1)
            if req_w > self.image.width() or req_h > self.image.height():
                self.resize_canvas_to(req_w, req_h, record_undo=False)
            self.update()
            self.update_status_bar()
        else:
            self.save_state()
            self.image = self.image.transformed(transform)
            self.update_widget_size()
            self.update_status_bar()

    def flip_image(self, horizontal, vertical):
        if self.has_active_selection():
            self.base_selected_image = self.base_selected_image.mirrored(horizontal, vertical)
            self.selected_image = self.selected_image.mirrored(horizontal, vertical)
            self.update()
        else:
            self.save_state()
            self.image = self.image.mirrored(horizontal, vertical)
            self.update()

    def invert_colors(self):
        if self.has_active_selection():
            self.base_selected_image.invertPixels()
            self.selected_image.invertPixels()
            self.update()
        else:
            self.save_state()
            self.image.invertPixels()
            self.update()

    def spray_paint(self, center_pt):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.brush_color, 1))
        radius = max(8, self.brush_size * 3)
        dots = radius * 2
        for _ in range(dots):
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, radius)
            dx = int(r * math.cos(angle))
            dy = int(r * math.sin(angle))
            painter.drawPoint(center_pt.x() + dx, center_pt.y() + dy)

    def flood_fill(self, start_pt, fill_color):
        w, h = self.image.width(), self.image.height()
        x0, y0 = start_pt.x(), start_pt.y()
        if not (0 <= x0 < w and 0 <= y0 < h):
            return

        target_rgb = self.image.pixel(x0, y0)
        replacement_rgb = fill_color.rgb()
        if target_rgb == replacement_rgb:
            return

        queue = deque([(x0, y0)])
        while queue:
            x, y = queue.popleft()
            if self.image.pixel(x, y) != target_rgb:
                continue

            left = x
            while left > 0 and self.image.pixel(left - 1, y) == target_rgb:
                left -= 1
            right = x
            while right < w - 1 and self.image.pixel(right + 1, y) == target_rgb:
                right += 1

            span_above = False
            span_below = False
            for i in range(left, right + 1):
                self.image.setPixel(i, y, replacement_rgb)

                if y > 0:
                    if self.image.pixel(i, y - 1) == target_rgb:
                        if not span_above:
                            queue.append((i, y - 1))
                            span_above = True
                    else:
                        span_above = False

                if y < h - 1:
                    if self.image.pixel(i, y + 1) == target_rgb:
                        if not span_below:
                            queue.append((i, y + 1))
                            span_below = True
                    else:
                        span_below = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selection()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.commit_selection()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            widget_pt = event.position().toPoint()
            pt = self.to_image_coords(widget_pt)

            if self.current_tool == "select":
                handle = self.hit_test_handles(widget_pt)
                if handle and self.has_active_selection():
                    self.active_handle = handle
                    self.resize_orig_rect = QRect(self.selection_rect)
                    return

                if not self.selection_rect.isNull() and self.selection_rect.contains(pt):
                    self.moving_selection = True
                    self.selection_offset = pt - self.selection_rect.topLeft()
                    self.update()
                    return

            c_handle = self.hit_test_canvas_handles(widget_pt)
            if c_handle:
                self.commit_selection()
                self.canvas_handle = c_handle
                self.preview_canvas_size = (self.image.width(), self.image.height())
                return

            if self.current_tool == "select":
                self.commit_selection()
                self.drawing = True
                self.start_point = pt
                self.selection_rect = QRect(pt, pt)
                self.update()
                return

            self.commit_selection()

            if not self.image.rect().contains(pt):
                return

            if self.current_tool == "bucket":
                self.save_state()
                self.flood_fill(pt, self.brush_color)
                self.update()
            elif self.current_tool == "picker":
                picked = self.image.pixelColor(pt)
                self.parent_window.set_color(picked)
                self.parent_window.select_tool("pen")
            elif self.current_tool == "text":
                dialog = TextDialog(self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    text, chosen_font = dialog.get_text_data()
                    if text:
                        self.save_state()
                        painter = QPainter(self.image)
                        painter.setPen(QPen(self.brush_color))
                        painter.setFont(chosen_font)
                        painter.drawText(pt, text)
                        self.update()
            elif self.current_tool == "spray":
                self.save_state()
                self.drawing = True
                self.spray_paint(pt)
                self.update()
            else:
                self.save_state()
                self.drawing = True
                self.start_point = pt
                self.last_point = pt
                self.temp_image = self.image.copy()

    def mouseMoveEvent(self, event):
        widget_pt = event.position().toPoint()
        pt = self.to_image_coords(widget_pt)
        self.update_status_bar(pt)

        if not (event.buttons() & Qt.MouseButton.LeftButton):
            if self.current_tool == "select" and self.has_active_selection():
                handle = self.hit_test_handles(widget_pt)
                if handle:
                    self.update_cursor_for_handle(handle, pt)
                    return
            c_handle = self.hit_test_canvas_handles(widget_pt)
            if c_handle:
                self.update_cursor_for_handle(c_handle, pt)
            else:
                self.update_cursor_for_handle(None, pt)
            return

        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.canvas_handle:
                new_w, new_h = self.preview_canvas_size
                if self.canvas_handle in ("cr", "cbr"):
                    new_w = max(16, pt.x())
                if self.canvas_handle in ("cb", "cbr"):
                    new_h = max(16, pt.y())
                self.preview_canvas_size = (new_w, new_h)
                self.update_widget_size()
                self.update_status_bar(pt)
                return

            if self.current_tool == "select":
                if self.active_handle and not self.base_selected_image.isNull():
                    r = QRect(self.resize_orig_rect)
                    if "l" in self.active_handle:
                        r.setLeft(min(pt.x(), r.right() - 5))
                    if "r" in self.active_handle:
                        r.setRight(max(pt.x(), r.left() + 5))
                    if "t" in self.active_handle:
                        r.setTop(min(pt.y(), r.bottom() - 5))
                    if "b" in self.active_handle:
                        r.setBottom(max(pt.y(), r.top() + 5))

                    if (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) and len(self.active_handle) == 2:
                        orig_ratio = self.base_selected_image.width() / max(1, self.base_selected_image.height())
                        new_w = r.width()
                        new_h = max(5, int(new_w / orig_ratio))
                        if "t" in self.active_handle:
                            r.setTop(r.bottom() - new_h)
                        else:
                            r.setHeight(new_h)

                    self.selection_rect = r
                    self.selected_image = self.base_selected_image.scaled(
                        r.width(), r.height(),
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.update()
                    return

                if self.moving_selection:
                    self.selection_rect.moveTopLeft(pt - self.selection_offset)
                    self.update()
                elif self.drawing:
                    self.selection_rect = QRect(self.start_point, pt).normalized().intersected(self.image.rect())
                    self.update()
                return

            if self.drawing:
                if self.current_tool in ["pen", "eraser"]:
                    painter = QPainter(self.image)
                    active_color = QColor(Qt.GlobalColor.white) if self.current_tool == "eraser" else self.brush_color
                    pen = QPen(active_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                    painter.setPen(pen)
                    painter.drawLine(self.last_point, pt)
                    self.last_point = pt
                elif self.current_tool == "spray":
                    self.spray_paint(pt)
                elif self.current_tool in ["line", "rect", "ellipse"]:
                    self.image = self.temp_image.copy()
                    self.draw_shape(self.start_point, pt)

                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pt = self.to_image_coords(event.position().toPoint())

            if self.canvas_handle:
                new_w, new_h = self.preview_canvas_size
                self.canvas_handle = None
                self.preview_canvas_size = None
                self.resize_canvas_to(new_w, new_h, record_undo=True)
                return

            if self.current_tool == "select":
                if self.active_handle:
                    self.active_handle = None
                    req_w = max(self.image.width(), self.selection_rect.right() + 1)
                    req_h = max(self.image.height(), self.selection_rect.bottom() + 1)
                    if req_w > self.image.width() or req_h > self.image.height():
                        self.resize_canvas_to(req_w, req_h, record_undo=False)
                    self.update()
                    return
                if self.moving_selection:
                    self.moving_selection = False
                elif self.drawing:
                    self.drawing = False
                    self.selection_rect = QRect(self.start_point, pt).normalized().intersected(self.image.rect())
                    if self.selection_rect.width() > 2 and self.selection_rect.height() > 2:
                        self.save_state()
                        copied = self.image.copy(self.selection_rect)
                        self.base_selected_image = copied.copy()
                        self.selected_image = copied.copy()
                        painter = QPainter(self.image)
                        painter.fillRect(self.selection_rect, Qt.GlobalColor.white)
                    else:
                        self.selection_rect = QRect()
                self.update()
                self.update_status_bar()
                return

            if self.drawing:
                if self.current_tool in ["line", "rect", "ellipse"]:
                    self.image = self.temp_image.copy()
                    self.draw_shape(self.start_point, pt)
                    self.update()
                self.drawing = False

    def draw_shape(self, start, end):
        painter = QPainter(self.image)
        pen = QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        if self.fill_shapes and self.current_tool in ["rect", "ellipse"]:
            painter.setBrush(QBrush(self.brush_color))

        if self.current_tool == "line":
            painter.drawLine(start, end)
        elif self.current_tool == "rect":
            painter.drawRect(QRect(start, end).normalized())
        elif self.current_tool == "ellipse":
            painter.drawEllipse(QRect(start, end).normalized())

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        z = self.zoom_factor
        img_target = QRect(0, 0, int(self.image.width() * z), int(self.image.height() * z))
        canvas_painter.drawImage(img_target, self.image, self.image.rect())

        if self.preview_canvas_size:
            pw, ph = self.preview_canvas_size
            canvas_painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine))
            canvas_painter.setBrush(Qt.BrushStyle.NoBrush)
            canvas_painter.drawRect(0, 0, int(pw * z), int(ph * z))
        else:
            canvas_painter.setPen(QPen(Qt.GlobalColor.black, 1))
            canvas_painter.setBrush(QBrush(Qt.GlobalColor.white))
            for ch_rect in self.get_canvas_handle_rects().values():
                canvas_painter.drawRect(ch_rect)

        if not self.selection_rect.isNull():
            target_rect = QRect(
                int(self.selection_rect.left() * z),
                int(self.selection_rect.top() * z),
                int(self.selection_rect.width() * z),
                int(self.selection_rect.height() * z)
            )
            if not self.selected_image.isNull():
                canvas_painter.drawImage(target_rect, self.selected_image, self.selected_image.rect())

            pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine)
            canvas_painter.setPen(pen)
            canvas_painter.setBrush(Qt.BrushStyle.NoBrush)
            canvas_painter.drawRect(target_rect)

            if self.has_active_selection():
                canvas_painter.setPen(QPen(Qt.GlobalColor.black, 1))
                canvas_painter.setBrush(QBrush(Qt.GlobalColor.white))
                for handle_rect in self.get_handle_rects().values():
                    canvas_painter.drawRect(handle_rect)


class PaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux Paint")
        self.resize(1020, 690)
        self.canvas = Canvas(self)
        self.tool_buttons = {}
        self.zoom_levels = [0.5, 1.0, 2.0, 4.0, 8.0]

        self.init_menu()
        self.init_ui()
        self.canvas.update_status_bar()

    def init_menu(self):
        main_menu = self.menuBar()

        # Menú Archivo
        file_menu = main_menu.addMenu("Archivo")

        new_action = QAction("Nuevo / Limpiar", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.canvas.clear_canvas)
        file_menu.addAction(new_action)

        open_action = QAction("Abrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Guardar...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # Menú Editar
        edit_menu = main_menu.addMenu("Editar")

        undo_action = QAction("Deshacer", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.canvas.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Rehacer", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.canvas.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        copy_action = QAction("Copiar selección", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.canvas.copy_selection)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Pegar imagen", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.canvas.paste_image)
        edit_menu.addAction(paste_action)

        delete_action = QAction("Eliminar selección", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.canvas.delete_selection)
        edit_menu.addAction(delete_action)

        # Menú Ver (Zoom)
        view_menu = main_menu.addMenu("Ver")

        zoom_in_action = QAction("Acercar zoom", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Alejar zoom", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        zoom_100_action = QAction("Tamaño real (100%)", self)
        zoom_100_action.setShortcut("Ctrl+0")
        zoom_100_action.triggered.connect(lambda: self.set_zoom_by_factor(1.0))
        view_menu.addAction(zoom_100_action)

        # Menú Imagen
        img_menu = main_menu.addMenu("Imagen")

        canvas_size_action = QAction("Tamaño del lienzo...", self)
        canvas_size_action.setShortcut("Ctrl+E")
        canvas_size_action.triggered.connect(self.canvas.resize_canvas_dialog)
        img_menu.addAction(canvas_size_action)

        resize_sel_action = QAction("Redimensionar selección / imagen pegada...", self)
        resize_sel_action.setShortcut("Ctrl+R")
        resize_sel_action.triggered.connect(self.canvas.resize_selection_dialog)
        img_menu.addAction(resize_sel_action)

        crop_action = QAction("Recortar a la selección", self)
        crop_action.triggered.connect(self.canvas.crop_to_selection)
        img_menu.addAction(crop_action)

        img_menu.addSeparator()

        rotate_action = QAction("Rotar 90° derecha", self)
        rotate_action.triggered.connect(self.canvas.rotate_90)
        img_menu.addAction(rotate_action)

        flip_h_action = QAction("Voltear horizontalmente", self)
        flip_h_action.triggered.connect(lambda: self.canvas.flip_image(True, False))
        img_menu.addAction(flip_h_action)

        flip_v_action = QAction("Voltear verticalmente", self)
        flip_v_action.triggered.connect(lambda: self.canvas.flip_image(False, True))
        img_menu.addAction(flip_v_action)

        invert_action = QAction("Invertir colores", self)
        invert_action.triggered.connect(self.canvas.invert_colors)
        img_menu.addAction(invert_action)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(6, 6, 6, 6)

        top_layout = QHBoxLayout()

        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setFixedWidth(175)
        sidebar_layout = QVBoxLayout(sidebar)

        lbl_tools = QLabel("<b>Herramientas</b>")
        sidebar_layout.addWidget(lbl_tools)

        tools = [
            ("⬚ Selección", "select"),
            ("✏️ Lápiz", "pen"),
            ("🥫 Aerógrafo", "spray"),
            ("🧽 Goma", "eraser"),
            ("🪣 Relleno", "bucket"),
            ("💧 Cuentagotas", "picker"),
            ("🔤 Texto", "text"),
            ("📏 Línea", "line"),
            ("⬜ Rectángulo", "rect"),
            ("⭕ Elipse", "ellipse")
        ]

        for label, code in tools:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet("text-align: left; padding: 5px;")
            btn.clicked.connect(lambda checked, c=code: self.select_tool(c))
            sidebar_layout.addWidget(btn)
            self.tool_buttons[code] = btn

        self.tool_buttons["pen"].setChecked(True)

        sidebar_layout.addSpacing(10)

        sidebar_layout.addWidget(QLabel("<b>Grosor:</b>"))
        self.size_combo = QComboBox()
        for s in [1, 3, 5, 10, 20]:
            self.size_combo.addItem(f"{s} px", s)
        self.size_combo.setCurrentIndex(1)
        self.size_combo.currentIndexChanged.connect(self.change_size)
        sidebar_layout.addWidget(self.size_combo)

        self.fill_checkbox = QCheckBox("Rellenar figura")
        self.fill_checkbox.toggled.connect(self.toggle_fill)
        sidebar_layout.addWidget(self.fill_checkbox)

        sidebar_layout.addStretch()
        top_layout.addWidget(sidebar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("background-color: #7f7f7f;")
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_area.setWidget(self.canvas)
        top_layout.addWidget(self.scroll_area)

        main_layout.addLayout(top_layout)

        bottom_bar = QFrame()
        bottom_bar.setFrameShape(QFrame.Shape.StyledPanel)
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(8, 4, 8, 4)

        bottom_layout.addWidget(QLabel("<b>Color:</b>"))
        self.active_color_preview = QFrame()
        self.active_color_preview.setFixedSize(36, 36)
        self.active_color_preview.setStyleSheet("background-color: #000000; border: 2px inset gray;")
        bottom_layout.addWidget(self.active_color_preview)

        palette_grid = QGridLayout()
        palette_grid.setSpacing(3)
        colors = [
            "#000000", "#7F7F7F", "#880015", "#ED1C24", "#FF7F27", "#FFF200", "#22B14C", "#00A2E8", "#3F48CC", "#A349A4",
            "#FFFFFF", "#C3C3C3", "#B97A57", "#FFAEC9", "#FFC90E", "#EFE4B0", "#B5E61D", "#99D9EA", "#7092BE", "#C8BFE7"
        ]

        for i, hex_color in enumerate(colors):
            swatch = QPushButton()
            swatch.setFixedSize(24, 24)
            swatch.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #444;")
            swatch.clicked.connect(lambda checked, col=hex_color: self.set_color(QColor(col)))
            palette_grid.addWidget(swatch, i // 10, i % 10)

        bottom_layout.addLayout(palette_grid)

        custom_color_btn = QPushButton("Más colores...")
        custom_color_btn.clicked.connect(self.choose_custom_color)
        bottom_layout.addWidget(custom_color_btn)

        bottom_layout.addStretch()

        bottom_layout.addWidget(QLabel("<b>Zoom:</b>"))
        self.zoom_combo = QComboBox()
        for z in self.zoom_levels:
            self.zoom_combo.addItem(f"{int(z * 100)}%", z)
        self.zoom_combo.setCurrentIndex(1)
        self.zoom_combo.currentIndexChanged.connect(self.on_zoom_combo_changed)
        bottom_layout.addWidget(self.zoom_combo)

        main_layout.addWidget(bottom_bar)

    def on_zoom_combo_changed(self):
        factor = self.zoom_combo.currentData()
        self.canvas.set_zoom(factor)

    def set_zoom_by_factor(self, factor):
        if factor in self.zoom_levels:
            idx = self.zoom_levels.index(factor)
            self.zoom_combo.setCurrentIndex(idx)

    def zoom_in(self):
        idx = self.zoom_combo.currentIndex()
        if idx < len(self.zoom_levels) - 1:
            self.zoom_combo.setCurrentIndex(idx + 1)

    def zoom_out(self):
        idx = self.zoom_combo.currentIndex()
        if idx > 0:
            self.zoom_combo.setCurrentIndex(idx - 1)

    def select_tool(self, tool_code, keep_selection=False):
        if not keep_selection:
            self.canvas.commit_selection()
        self.canvas.current_tool = tool_code
        for code, btn in self.tool_buttons.items():
            btn.setChecked(code == tool_code)

    def change_size(self):
        self.canvas.brush_size = self.size_combo.currentData()

    def toggle_fill(self, checked):
        self.canvas.fill_shapes = checked

    def set_color(self, qcolor):
        self.canvas.brush_color = qcolor
        self.active_color_preview.setStyleSheet(
            f"background-color: {qcolor.name()}; border: 2px inset gray;"
        )
        if self.canvas.current_tool in ["eraser", "picker"]:
            self.select_tool("pen")

    def choose_custom_color(self):
        color = QColorDialog.getColor(self.canvas.brush_color, self, "Seleccionar color")
        if color.isValid():
            self.set_color(color)

    def open_file(self):
        self.canvas.commit_selection()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            loaded_image = QImage(file_path).convertToFormat(QImage.Format.Format_RGB32)
            if not loaded_image.isNull():
                self.canvas.save_state()
                self.canvas.image = loaded_image
                self.canvas.update_widget_size()
                self.canvas.update_status_bar()

    def save_file(self):
        self.canvas.commit_selection()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Imagen", "dibujo.png", "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
        )
        if file_path:
            self.canvas.image.save(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setDesktopFileName("linux-paint")
    app.setWindowIcon(QIcon("/home/aleixandre/linux-paint/icon.svg"))
    window = PaintApp()
    window.show()
    sys.exit(app.exec())
