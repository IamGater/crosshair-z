import sys
import json
import os
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QSlider, QPushButton, 
                             QColorDialog, QFrame, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QAction, QPainter, QPen, QBrush

class CrosshairOverlay(QWidget):
    def __init__(self):
        super().__init__(None, Qt.WindowType.Window)
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.BypassWindowManagerHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        screen = QApplication.primaryScreen()
        geom = screen.geometry()
        self.setGeometry(geom)

        try:
            try:
                if hasattr(Qt, 'WindowTransparentForInput'):
                    self.setWindowFlag(Qt.WindowTransparentForInput, True)
                elif hasattr(Qt, 'WindowType') and hasattr(Qt.WindowType, 'WindowTransparentForInput'):
                    self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
            except Exception:
                pass

            wh = self.windowHandle()
            if wh is not None:
                try:
                    if hasattr(Qt, 'WindowTransparentForInput'):
                        wh.setFlag(Qt.WindowTransparentForInput, True)
                    elif hasattr(Qt, 'WindowType') and hasattr(Qt.WindowType, 'WindowTransparentForInput'):
                        wh.setFlag(Qt.WindowType.WindowTransparentForInput, True)
                except Exception:
                    pass
        except Exception:
            pass

        self.size = 14
        self.thickness = 2
        self.gap = 4
        self.outline = 1
        self.alpha = 100
        self.style = "Classic (+)"
        self.color = QColor("#00ff66")

    def set_parameters(self, size, thickness, gap, outline, alpha, style, color):
        self.size = size
        self.thickness = thickness
        self.gap = gap
        self.outline = outline
        self.alpha = alpha
        self.style = style
        self.color = QColor(color)
        self.update()

    def set_color(self, color, alpha):
        self.color = QColor(color)
        self.alpha = alpha
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w // 2
        cy = h // 2

        alpha_val = max(0, min(100, int(self.alpha)))
        col = QColor(self.color)
        col.setAlpha(int(alpha_val * 2.55))

        outline_col = QColor(0, 0, 0)
        outline_col.setAlpha(int(alpha_val * 2.55))

        main_pen = QPen(col)
        main_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        main_pen.setWidth(self.thickness)

        outline_pen = QPen(outline_col)
        outline_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        outline_pen.setWidth(max(1, self.thickness + 2 * self.outline))

        if self.style.startswith("Classic"):
            painter.setPen(outline_pen)
            painter.drawLine(cx - self.gap - self.size, cy, cx - self.gap, cy)
            painter.drawLine(cx + self.gap, cy, cx + self.gap + self.size, cy)
            painter.drawLine(cx, cy - self.gap - self.size, cx, cy - self.gap)
            painter.drawLine(cx, cy + self.gap, cx, cy + self.gap + self.size)

            painter.setPen(main_pen)
            painter.drawLine(cx - self.gap - self.size, cy, cx - self.gap, cy)
            painter.drawLine(cx + self.gap, cy, cx + self.gap + self.size, cy)
            painter.drawLine(cx, cy - self.gap - self.size, cx, cy - self.gap)
            painter.drawLine(cx, cy + self.gap, cx, cy + self.gap + self.size)

        elif self.style.startswith("Dot"):
            radius = max(1, self.thickness * 2)
            painter.setBrush(QBrush(outline_col))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(cx - radius - self.outline, cy - radius - self.outline,
                                2 * (radius + self.outline), 2 * (radius + self.outline))
            painter.setBrush(QBrush(col))
            painter.drawEllipse(cx - radius, cy - radius, 2 * radius, 2 * radius)

        elif self.style.startswith("Circle"):
            radius = max(4, self.size // 2)
            painter.setPen(outline_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(cx - radius - self.outline, cy - radius - self.outline,
                                2 * (radius + self.outline), 2 * (radius + self.outline))
            painter.setPen(main_pen)
            painter.drawEllipse(cx - radius, cy - radius, 2 * radius, 2 * radius)

        painter.end()

class ModernHorizontalMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crosshair-Z")
        self.setFixedSize(470, 270)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0c10;
            }
            QFrame.card {
                background-color: #11141a;
                border: 1px solid #1f232d;
                border-radius: 12px;
            }
            QLabel {
                color: #94a3b8;
                font-family: 'Segoe UI', -apple-system, sans-serif;
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QPushButton#combo_style_btn {
                background-color: #1b1f29;
                border: 1px solid #2d3548;
                border-radius: 6px;
                color: #f8fafc;
                padding: 6px 12px;
                min-width: 130px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                text-align: left;
            }
            QPushButton#combo_style_btn:hover {
                background-color: #222733;
                border-color: #3b82f6;
            }
            
            QMenu {
                background-color: #11141a;
                border: 1px solid #1f232d;
                border-radius: 6px;
                padding: 4px 0px;
            }
            QMenu::item {
                color: #f8fafc;
                padding: 6px 14px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
            
            QPushButton#color_btn {
                border-radius: 6px;
                border: 1px solid #2d3548;
                color: #ffffff;
                font-weight: bold;
                font-size: 11px;
                text-transform: uppercase;
                padding: 8px 20px;
                min-width: 90px;
            }
            
            QSlider::groove:vertical {
                background: #1b1f29;
                width: 4px;
                border-radius: 2px;
            }
            QSlider::handle:vertical {
                background: #3b82f6;
                height: 12px;
                width: 12px;
                margin: 0 -4px;
                border-radius: 6px;
            }
            QSlider::handle:vertical:hover {
                background: #60a5fa;
            }
            QSlider::add-page:vertical {
                background: #3b82f6;
                border-radius: 2px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 12, 15, 12)
        main_layout.setSpacing(10)

        self.selected_color = QColor("#00ff66")

        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(10)

        type_card = QFrame()
        type_card.setProperty("class", "card")
        type_layout = QVBoxLayout(type_card)
        type_layout.setContentsMargins(12, 10, 12, 10)
        type_layout.setSpacing(8)
        
        type_title = QLabel("Shape")
        
        self.type_btn = QPushButton("Classic (+)")
        self.type_btn.setObjectName("combo_style_btn")
        
        self.combo_menu = QMenu(self)
        self.combo_menu.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.combo_menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.menu_options = ["Classic (+)", "Dot (•)", "Circle (○)"]
        for option in self.menu_options:
            action = QAction(option, self)
            action.triggered.connect(lambda checked, opt=option: self.handle_menu_selection(opt))
            self.combo_menu.addAction(action)
            
        self.type_btn.clicked.connect(self.show_drop_down_menu)
        
        type_layout.addWidget(type_title, alignment=Qt.AlignmentFlag.AlignTop)
        type_layout.addWidget(self.type_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        type_layout.addStretch()
        top_row_layout.addWidget(type_card)

        color_card = QFrame()
        color_card.setProperty("class", "card")
        color_layout = QVBoxLayout(color_card)
        color_layout.setContentsMargins(12, 10, 12, 10)
        color_layout.setSpacing(8)
        
        color_title = QLabel("Color")
        self.color_btn = QPushButton("Choose")
        self.color_btn.setObjectName("color_btn")
        self.update_color_button_style()
        self.color_btn.clicked.connect(self.choose_color)
        
        color_layout.addWidget(color_title, alignment=Qt.AlignmentFlag.AlignTop)
        color_layout.addWidget(self.color_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        color_layout.addStretch()
        top_row_layout.addWidget(color_card)

        main_layout.addLayout(top_row_layout)

        faders_card = QFrame()
        faders_card.setProperty("class", "card")
        faders_layout = QHBoxLayout(faders_card)
        faders_layout.setContentsMargins(12, 8, 12, 8)
        faders_layout.setSpacing(10)

        self.size_frame, self.size_slider = self.create_fader("Size", 2, 80, 14, "px")
        self.thick_frame, self.thick_slider = self.create_fader("Thickness", 1, 15, 2, "px")
        self.gap_frame, self.gap_slider = self.create_fader("Gap", 0, 40, 4, "px")
        self.outline_frame, self.outline_slider = self.create_fader("Outline", 0, 10, 1, "px")
        self.alpha_frame, self.alpha_slider = self.create_fader("Opacity", 10, 100, 100, "%")

        faders_layout.addWidget(self.size_frame)
        faders_layout.addWidget(self.thick_frame)
        faders_layout.addWidget(self.gap_frame)
        faders_layout.addWidget(self.outline_frame)
        faders_layout.addWidget(self.alpha_frame)
        
        separator = QFrame()
        separator.setFixedWidth(1)
        separator.setStyleSheet("background-color: #1f232d; border: none;")
        faders_layout.addWidget(separator)

        reset_container = QVBoxLayout()
        reset_container.setContentsMargins(0, 0, 0, 0)
        reset_container.addStretch()
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("color_btn")
        self.reset_btn.setFixedSize(80, 30)
        self.reset_btn.clicked.connect(self.reset_parameters)
        
        reset_container.addWidget(self.reset_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        reset_container.addStretch()
        
        faders_layout.addLayout(reset_container)
        main_layout.addWidget(faders_card)

        self.overlay = CrosshairOverlay()

        # connect sliders to update overlay
        self.size_slider.valueChanged.connect(self.update_overlay)
        self.thick_slider.valueChanged.connect(self.update_overlay)
        self.gap_slider.valueChanged.connect(self.update_overlay)
        self.outline_slider.valueChanged.connect(self.update_overlay)
        self.alpha_slider.valueChanged.connect(self.update_overlay)

        # load persisted settings, apply and show overlay
        self.load_settings()
        self.update_overlay()
        self.overlay.show()

    def create_fader(self, label_text, min_val, max_val, default_val, unit):
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        lbl = QLabel(label_text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #64748b; font-size: 8px;")
        
        slider = QSlider(Qt.Orientation.Vertical)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        slider.setMinimumHeight(60)
        
        val_lbl = QLabel(f"{default_val}{unit}")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_lbl.setStyleSheet("color: #f1f5f9; font-size: 9px; font-weight: bold;")
        
        slider.valueChanged.connect(lambda val: val_lbl.setText(f"{val}{unit}"))
        
        layout.addWidget(lbl)
        layout.addWidget(slider, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(val_lbl)
        
        return container, slider

    def show_drop_down_menu(self):
        button_width = self.type_btn.width()
        self.combo_menu.setFixedWidth(button_width)
        
        pos = self.type_btn.mapToGlobal(self.type_btn.rect().bottomLeft())
        self.combo_menu.exec(pos)

    def handle_menu_selection(self, text):
        self.type_btn.setText(text)
        self.update_overlay()

    def choose_color(self):
        color = QColorDialog.getColor(initial=self.selected_color)
        if color.isValid():
            self.selected_color = color
            self.update_color_button_style()
            if hasattr(self, 'overlay'):
                self.overlay.set_color(self.selected_color, self.alpha_slider.value())

    def update_color_button_style(self):
        hex_color = self.selected_color.name()
        brightness = self.selected_color.red() * 0.299 + self.selected_color.green() * 0.587 + self.selected_color.blue() * 0.114
        text_color = "#000000" if brightness > 128 else "#ffffff"
        
        self.color_btn.setStyleSheet(f"""
            QPushButton#color_btn {{
                background-color: {hex_color};
                color: {text_color};
                border: none;
                padding: 8px 20px;
            }}
            QPushButton#color_btn:hover {{
                background-color: {self.selected_color.lighter(115).name()};
            }}
        """)

    def reset_parameters(self):
        self.type_btn.setText("Classic (+)")
        self.selected_color = QColor("#00ff66")
        self.update_color_button_style()
        self.size_slider.setValue(14)
        self.thick_slider.setValue(2)
        self.gap_slider.setValue(4)
        self.outline_slider.setValue(1)
        self.alpha_slider.setValue(100)
        if hasattr(self, 'overlay'):
            self.update_overlay()

    def get_settings_path(self):
        name = "crosshair-z-settings.json"
        tp = tempfile.gettempdir()
        return os.path.join(tp, name)

    def save_settings(self):
        data = {
            "size": self.size_slider.value(),
            "thickness": self.thick_slider.value(),
            "gap": self.gap_slider.value(),
            "outline": self.outline_slider.value(),
            "alpha": self.alpha_slider.value(),
            "style": self.type_btn.text(),
            "color": self.selected_color.name()
        }
        path = self.get_settings_path()
        try:
            tmp_path = path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            Path(tmp_path).replace(path)
        except Exception:
            pass

    def load_settings(self):
        path = self.get_settings_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # block signals while applying
            self.size_slider.blockSignals(True)
            self.thick_slider.blockSignals(True)
            self.gap_slider.blockSignals(True)
            self.outline_slider.blockSignals(True)
            self.alpha_slider.blockSignals(True)

            if "size" in data:
                self.size_slider.setValue(int(data.get("size", 14)))
            if "thickness" in data:
                self.thick_slider.setValue(int(data.get("thickness", 2)))
            if "gap" in data:
                self.gap_slider.setValue(int(data.get("gap", 4)))
            if "outline" in data:
                self.outline_slider.setValue(int(data.get("outline", 1)))
            if "alpha" in data:
                self.alpha_slider.setValue(int(data.get("alpha", 100)))
            if "style" in data:
                self.type_btn.setText(str(data.get("style", "Classic (+)")))
            if "color" in data:
                try:
                    self.selected_color = QColor(str(data.get("color", "#00ff66")))
                    self.update_color_button_style()
                except Exception:
                    pass

            # unblock
            self.size_slider.blockSignals(False)
            self.thick_slider.blockSignals(False)
            self.gap_slider.blockSignals(False)
            self.outline_slider.blockSignals(False)
            self.alpha_slider.blockSignals(False)

            # apply to overlay
            if hasattr(self, 'overlay'):
                self.overlay.set_parameters(size=self.size_slider.value(),
                                            thickness=self.thick_slider.value(),
                                            gap=self.gap_slider.value(),
                                            outline=self.outline_slider.value(),
                                            alpha=self.alpha_slider.value(),
                                            style=self.type_btn.text(),
                                            color=self.selected_color)
        except Exception:
            return

    def update_overlay(self):
        if not hasattr(self, 'overlay'):
            return
        size = self.size_slider.value()
        thickness = self.thick_slider.value()
        gap = self.gap_slider.value()
        outline = self.outline_slider.value()
        alpha = self.alpha_slider.value()
        style = self.type_btn.text()
        color = self.selected_color
        self.overlay.set_parameters(size=size, thickness=thickness, gap=gap,
                                    outline=outline, alpha=alpha,
                                    style=style, color=color)
        # persist settings
        try:
            self.save_settings()
        except Exception:
            pass

    def closeEvent(self, event):
        try:
            self.save_settings()
        except Exception:
            pass
        if hasattr(self, 'overlay'):
            self.overlay.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernHorizontalMenu()
    window.show()
    sys.exit(app.exec())