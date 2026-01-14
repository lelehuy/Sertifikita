from __future__ import annotations

import os, json, re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Callable

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import (
    QPixmap, QFont, QColor, QAction, QPen, QPalette, QIcon, QPainter, QBrush
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsTextItem, QGraphicsRectItem, QSpinBox, QComboBox, QLineEdit,
    QMessageBox, QColorDialog, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QCheckBox, QStyle, QToolBar, QGroupBox, QSlider,
    QFormLayout, QFontComboBox, QFrame, QSizePolicy, QSplitter, QGraphicsDropShadowEffect
)

from renderer import draw_certificate, render_to_image


# ===================== Model =====================
@dataclass
class TextField:
    name: str
    x: float
    y: float
    size: int = 32
    color: str = "#000000"
    align: str = "left"
    font_family: str = ""
    font_path: str = ""
    box_width: int = 0


def qfont_from_field(f: TextField) -> QFont:
    fam = f.font_family.strip() if f.font_family else ""
    if not fam and f.font_path:
        fam = os.path.splitext(os.path.basename(f.font_path))[0]
    return QFont(fam or "Arial", f.size)


# ------------- font resolver -------------
_FONT_CACHE: Dict[str, str] = {}
def _font_dirs() -> List[str]:
    dirs = [
        "/System/Library/Fonts", "/System/Library/Fonts/Supplemental",
        "/Library/Fonts", os.path.expanduser("~/Library/Fonts"),
        "/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
    ]
    win = os.environ.get("WINDIR") or os.environ.get("SystemRoot")
    if win: dirs.append(os.path.join(win, "Fonts"))
    return [d for d in dirs if os.path.isdir(d)]
def _simp(s: str) -> str: return "".join(ch.lower() for ch in s if ch.isalnum())
def resolve_font_path(family: str) -> str:
    if not family: return ""
    key=_simp(family)
    if key in _FONT_CACHE: return _FONT_CACHE[key]
    cand=[]
    for d in _font_dirs():
        for root,_,files in os.walk(d):
            for fn in files:
                if not fn.lower().endswith((".ttf",".otf")): continue
                if _simp(family) in _simp(os.path.splitext(fn)[0]):
                    cand.append(os.path.join(root,fn))
    best=""
    if cand:
        pref=[p for p in cand if "regular" in _simp(os.path.basename(p)) or "book" in _simp(os.path.basename(p))]
        best=pref[0] if pref else cand[0]
    _FONT_CACHE[key]=best
    return best


# ===================== Theme =====================
def build_fresh_stylesheet(mode="dark")->str:
    if mode=="light":
        bg,card,text,sub="#F7F8FA","#FFFFFF","#0F172A","#475569"
        border,input_bg,input_border="#E5E7EB","#FFFFFF","#CBD5E1"
        accent,view_bg,hdr,hover="#4F46E5","#F3F4F6","#F1F5F9","#EEF2FF"
    else:
        bg,card,text,sub="#0B0F19","#0F172A","#E5E7EB","#94A3B8"
        border,input_bg,input_border="#1F2937","#111827","#374151"
        accent,view_bg,hdr,hover="#6366F1","#0B1220","#111827","#1E293B"
    return f"""
    QMainWindow {{ background:{bg}; color:{text}; }}
    QLabel {{ color:{text}; font-size:12.5pt; }}
    QGroupBox {{ border:1px solid {border}; border-radius:12px; margin-top:12px; padding:12px; background:{card}; }}
    QGroupBox::title {{ left:10px; padding:0 4px; color:{sub}; font-weight:600; }}
    QLineEdit, QSpinBox, QComboBox {{
        background:{input_bg}; border:1px solid {input_border}; border-radius:10px; padding:7px 10px; color:{text}; font-size:12.5pt;
    }}
    QFontComboBox {{ background:{input_bg}; border:1px solid {input_border}; border-radius:10px; padding:4px 8px; color:{text}; font-size:12.5pt; }}
    QComboBox QAbstractItemView {{ background:{card}; color:{text}; border:1px solid {border}; selection-background-color:{hover}; }}
    QTableWidget {{ background:{card}; color:{text}; gridline-color:{border}; border:1px solid {border}; border-radius:10px; }}
    QHeaderView::section {{ background:{hdr}; color:{sub}; border:0; padding:8px 10px; font-weight:600; }}
    QPushButton {{ background:{card}; border:1px solid {border}; color:{text}; border-radius:10px; padding:8px 12px; font-weight:600; }}
    QPushButton:hover {{ border-color:{input_border}; background:{hover}; }}
    QPushButton#primary {{ background:{accent}; border:0; color:white; }}
    QPushButton#danger {{ background:#EF4444; border:0; color:white; }}
    QGraphicsView {{ background:{view_bg}; border:1px solid {border}; border-radius:14px; }}
    QToolBar {{ background:transparent; border:0; spacing:8px; }}
    QToolButton {{ background:{card}; border:1px solid {border}; padding:7px 10px; border-radius:10px; color:{text}; }}
    QToolButton:hover {{ border-color:{input_border}; background:{hover}; }}
    QSlider::groove:horizontal {{ height:6px; background:{border}; border-radius:3px; }}
    QSlider::handle:horizontal {{ width:18px; height:18px; margin:-7px 0; border-radius:9px; background:{accent}; }}
    """

def apply_fresh_theme(app: QApplication, mode="dark"):
    app.setStyle("Fusion")
    try: app.setFont(QFont("SF Pro Text",12))
    except Exception: app.setFont(QFont("Arial",12))
    pal=app.palette()
    if mode=="dark":
        pal.setColor(QPalette.Window,QColor("#0B0F19"))
        pal.setColor(QPalette.WindowText,QColor("#E5E7EB"))
        pal.setColor(QPalette.Base,QColor("#0F172A"))
        pal.setColor(QPalette.AlternateBase,QColor("#111827"))
        pal.setColor(QPalette.Text,QColor("#E5E7EB"))
        pal.setColor(QPalette.Button,QColor("#0F172A"))
        pal.setColor(QPalette.ButtonText,QColor("#E5E7EB"))
        pal.setColor(QPalette.Highlight,QColor("#6366F1"))
        pal.setColor(QPalette.HighlightedText,QColor("#FFFFFF"))
    app.setPalette(pal)

    # Try loading from file first
    qss_path = os.path.join(os.path.dirname(__file__), "resources", "qss", f"fresh_{mode}.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        app.setStyleSheet(build_fresh_stylesheet(mode))


# --------------- Color chip ---------------
class ColorChip(QFrame):
    colorChanged = Signal(str)
    def __init__(self,start="#000000",parent=None):
        super().__init__(parent); self._color=start
        self.setFixedSize(28,24); self.setFrameShape(QFrame.StyledPanel); self.setCursor(Qt.PointingHandCursor)
        self.setAutoFillBackground(True); self._apply()
    def _apply(self):
        pal=self.palette(); pal.setColor(QPalette.Window,QColor(self._color)); self.setPalette(pal)
    def setColor(self,c:str):
        self._color=c; self._apply(); self.colorChanged.emit(self._color)
    def mousePressEvent(self,e):
        col=QColorDialog.getColor(QColor(self._color),self,"Pick Color")
        if col.isValid(): self.setColor(col.name())


# --------------- Overlay (resize width) ---------------
class ResizeOverlay(QGraphicsRectItem):
    EDGE=8
    def __init__(self, field:TextField, sf:float, on_resize:Optional[Callable[[int],None]]=None):
        super().__init__(0,0,40,20); self.field=field; self.sf=sf; self.on_resize=on_resize
        self._resizing=False; self._start_scene_x=0.0; self._start_w=40.0
        self.setPen(QPen(QColor("#1e90ff"),1,Qt.DashLine)); self.setBrush(Qt.NoBrush); self.setZValue(1000)
        self.setAcceptedMouseButtons(Qt.LeftButton); self.setAcceptHoverEvents(True); self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
    def _on_right_edge(self,pos):
        r=self.rect(); return (r.width()-self.EDGE)<=pos.x()<=(r.width()+self.EDGE) and 0<=pos.y()<=r.height()
    def hoverMoveEvent(self,ev):
        self.setCursor(Qt.SizeHorCursor if self._on_right_edge(ev.pos()) else Qt.ArrowCursor); super().hoverMoveEvent(ev)
    def mousePressEvent(self,ev):
        if self._on_right_edge(ev.pos()):
            self._resizing=True; self._start_scene_x=ev.scenePos().x(); self._start_w=self.rect().width(); ev.accept(); return
        super().mousePressEvent(ev)
    def mouseMoveEvent(self,ev):
        if self._resizing:
            dx=ev.scenePos().x()-self._start_scene_x
            new_w=max(40.0,self._start_w+dx)
            r=self.rect(); self.setRect(0,0,new_w,r.height())
            self.field.box_width=int(new_w/self.sf)
            if self.on_resize: self.on_resize(self.field.box_width)
            ev.accept(); return
        super().mouseMoveEvent(ev)
    def mouseReleaseEvent(self,ev):
        self._resizing=False; super().mouseReleaseEvent(ev)


# --------------- CanvasView (arrow nudge) ---------------
class CanvasView(QGraphicsView):
    def __init__(self,scene,nudge_cb:Callable[[int,int],None]):
        super().__init__(scene); self.nudge_cb=nudge_cb; self.setFocusPolicy(Qt.StrongFocus)
    def keyPressEvent(self,e):
        step=10 if (e.modifiers() & Qt.ShiftModifier) else 1
        if e.key()==Qt.Key_Left: self.nudge_cb(-step,0); return
        if e.key()==Qt.Key_Right: self.nudge_cb(+step,0); return
        if e.key()==Qt.Key_Up: self.nudge_cb(0,-step); return
        if e.key()==Qt.Key_Down: self.nudge_cb(0,+step); return
        super().keyPressEvent(e)

    def wheelEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:
            f = 1.15 if e.angleDelta().y() > 0 else (1/1.15)
            self.window()._change_zoom(f)
            e.accept()
        else:
            super().wheelEvent(e)


# --------------- EnterAdvancingTable ---------------
class EnterAdvancingTable(QTableWidget):
    def keyPressEvent(self,e):
        key,mods=e.key(),e.modifiers()
        if key in (Qt.Key_Return,Qt.Key_Enter) and not (mods & (Qt.ControlModifier|Qt.AltModifier)):
            r,c=self.currentRow(),self.currentColumn()
            if mods & Qt.ShiftModifier: nr=max(0,r-1)
            else:
                nr=r+1
                if nr>=self.rowCount():
                    self.insertRow(self.rowCount())
                    for k in range(self.columnCount()):
                        if not self.item(nr,k): self.setItem(nr,k,QTableWidgetItem(""))
            self.setCurrentCell(nr,c)
            it=self.item(nr,c) or QTableWidgetItem("")
            self.setItem(nr,c,it); self.editItem(it); return
        super().keyPressEvent(e)


# --------------- DraggableText ---------------
class DraggableText(QGraphicsTextItem):
    def __init__(self, field:TextField, sf:float, moved_cb:Optional[Callable[['DraggableText'],None]]=None):
        super().__init__(f"{{{{{field.name}}}}}")
        self.field=field; self.sf=sf; self.moved_cb=moved_cb
        self.setDefaultTextColor(QColor(field.color)); self.setFont(qfont_from_field(field))
        self.setFlag(QGraphicsTextItem.ItemIsMovable,True); self.setFlag(QGraphicsTextItem.ItemIsSelectable,True)
        self.setPos(self.field.x*self.sf,self.field.y*self.sf)
    def mouseReleaseEvent(self,ev):
        super().mouseReleaseEvent(ev)
        p=self.pos(); self.field.x=p.x()/self.sf; self.field.y=p.y()/self.sf
        if self.moved_cb: self.moved_cb(self)

    def hoverEnterEvent(self, ev):
        self.setOpacity(0.8)
        super().hoverEnterEvent(ev)

    def hoverLeaveEvent(self, ev):
        self.setOpacity(1.0)
        super().hoverLeaveEvent(ev)


# --------------- ManageDataDialog ---------------
class ManageDataDialog(QDialog):
    def __init__(self,parent,keys:List[str],dataset:List[Dict[str,str]]):
        super().__init__(parent); self.setWindowTitle("Manage Data"); self.resize(900,520)
        self.keys=list(keys)
        self.dataset=[{k:r.get(k,"") for k in self.keys} for r in (dataset or [])] or [{k:"" for k in self.keys}]
        self.table=EnterAdvancingTable(self); self.table.setColumnCount(len(self.keys))
        self.table.setHorizontalHeaderLabels(self.keys); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.btn_add, self.btn_del = QPushButton("+ Add Row"), QPushButton("Delete Row")
        self.btn_import, self.btn_export = QPushButton("Import CSV"), QPushButton("Export CSV")
        self.btn_ok, self.btn_cancel = QPushButton("OK"), QPushButton("Cancel")
        main=QVBoxLayout(self); main.addWidget(self.table)
        r=QHBoxLayout(); r.addWidget(self.btn_add); r.addWidget(self.btn_del); r.addStretch(); r.addWidget(self.btn_import); r.addWidget(self.btn_export); main.addLayout(r)
        r2=QHBoxLayout(); r2.addStretch(); r2.addWidget(self.btn_cancel); r2.addWidget(self.btn_ok); main.addLayout(r2)
        self.btn_add.clicked.connect(self._add); self.btn_del.clicked.connect(self._del)
        self.btn_import.clicked.connect(self._imp); self.btn_export.clicked.connect(self._exp)
        self.btn_ok.clicked.connect(self.accept); self.btn_cancel.clicked.connect(self.reject)
        self._reload()
    def _reload(self):
        self.table.setColumnCount(len(self.keys)); self.table.setHorizontalHeaderLabels(self.keys)
        self.table.setRowCount(len(self.dataset))
        for r,row in enumerate(self.dataset):
            for c,k in enumerate(self.keys): self.table.setItem(r,c,QTableWidgetItem(row.get(k,"")))
    def _sync(self):
        out=[]; 
        for r in range(self.table.rowCount()):
            row={}
            for c,k in enumerate(self.keys):
                it=self.table.item(r,c); row[k]=it.text() if it else ""
            out.append(row)
        self.dataset=out
    def _add(self):
        self._sync(); self.dataset.append({k:"" for k in self.keys}); self._reload()
        nr=self.table.rowCount()-1
        if nr>=0: self.table.setCurrentCell(nr,0); it=self.table.item(nr,0) or QTableWidgetItem(""); self.table.setItem(nr,0,it); self.table.editItem(it)
    def _del(self):
        sel = sorted([i.row() for i in self.table.selectionModel().selectedRows()], reverse=True) or []
        self._sync()
        for i in sel:
            if 0<=i<len(self.dataset): self.dataset.pop(i)
        if not self.dataset: self.dataset=[{k:"" for k in self.keys}]
        self._reload()
    def _imp(self):
        path,_=QFileDialog.getOpenFileName(self,"Import CSV","","CSV (*.csv)")
        if not path: return
        import csv
        try:
            with open(path,"r",encoding="utf-8-sig") as f:
                rdr=csv.DictReader(f); self.dataset=[{k:rec.get(k,"") for k in self.keys} for rec in rdr] or [{k:"" for k in self.keys}]
            self._reload()
        except Exception as e: QMessageBox.critical(self,"CSV error",str(e))
    def _exp(self):
        path,_=QFileDialog.getSaveFileName(self,"Export CSV","dataset.csv","CSV (*.csv)")
        if not path: return
        import csv
        self._sync()
        try:
            with open(path,"w",encoding="utf-8",newline="") as f:
                w=csv.DictWriter(f,fieldnames=self.keys); w.writeheader(); [w.writerow(row) for row in self.dataset]
            QMessageBox.information(self,"Saved",f"Exported to {path}")
        except Exception as e: QMessageBox.critical(self,"CSV error",str(e))
    def get_dataset(self)->List[Dict[str,str]]: self._sync(); return self.dataset


# --------------- Preview ---------------
class PreviewDialog(QDialog):
    def __init__(self,pixmap:QPixmap,parent=None):
        super().__init__(parent); self.setWindowTitle("Preview"); self.resize(1000,700)
        lbl=QLabel(); lbl.setPixmap(pixmap); lbl.setAlignment(Qt.AlignCenter)
        sc=QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(lbl)
        lay=QVBoxLayout(self); lay.addWidget(sc)


# ================= Main =================
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sertifikita"); self.resize(1280,860)

        self.template_path=""; self.img_w=self.img_h=1; self.sf=1.0; self.view_zoom=1.0
        self.fields: List[TextField]=[]; self.dataset: List[Dict[str,str]]=[]
        self.overlay_box=None; self.bg_item=None

        self.setAcceptDrops(True)
        self._build_menu()

        self.scene=QGraphicsScene(self)
        self.scene.selectionChanged.connect(self._on_selection_changed)
        self.view=CanvasView(self.scene,self._on_nudge)
        hqa=getattr(QPainter,"HighQualityAntialiasing",None)
        hints=QPainter.Antialiasing|QPainter.TextAntialiasing|QPainter.SmoothPixmapTransform
        if hqa is not None: hints|=hqa
        self.view.setRenderHints(hints)
        self.view.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.view.setCacheMode(QGraphicsView.CacheBackground)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        # ---- Field group ----
        grp_field=QGroupBox("Field Properties")
        self.fld_name=QLineEdit("")
        self.fld_size=QSpinBox(); self.fld_size.setRange(6,300); self.fld_size.setValue(32)

        self.fld_color=QLineEdit("#000000")
        self.fld_color.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.color_chip=ColorChip("#000000")
        row_color=QHBoxLayout(); row_color.setContentsMargins(0,0,0,0); row_color.setSpacing(8)
        row_color.addWidget(self.fld_color,1); row_color.addWidget(self.color_chip,0)
        w_color=QWidget(); w_color.setLayout(row_color); w_color.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

        self.fld_align=QComboBox(); self.fld_align.addItems(["left","center","right"])
        self.font_combo=QFontComboBox(); self.font_combo.setEditable(False)
        self.font_combo.setFontFilters(QFontComboBox.ScalableFonts|QFontComboBox.MonospacedFonts|QFontComboBox.ProportionalFonts)
        self.fld_boxw=QSpinBox(); self.fld_boxw.setRange(0,10000); self.fld_boxw.setEnabled(False)

        form_field=QFormLayout(grp_field)
        form_field.setLabelAlignment(Qt.AlignRight|Qt.AlignVCenter)
        form_field.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_field.setHorizontalSpacing(12); form_field.setVerticalSpacing(10)
        
        row_size_align = QHBoxLayout()
        row_size_align.addWidget(self.fld_size, 1)
        row_size_align.addWidget(QLabel("Align"))
        row_size_align.addWidget(self.fld_align, 1)
        w_size_align = QWidget(); w_size_align.setLayout(row_size_align)

        form_field.addRow("Field Name", self.fld_name)
        form_field.addRow("Font Size", w_size_align)
        form_field.addRow("Color (#RRGGBB)", w_color)
        form_field.addRow("Font Family", self.font_combo)
        form_field.addRow("Box Width", self.fld_boxw)

        # ---- Placement ----
        grp_place=QGroupBox("Placement")
        self.spin_x=QSpinBox(); self.spin_x.setRange(0,10000)
        self.spin_y=QSpinBox(); self.spin_y.setRange(0,10000)
        self.chk_snap=QCheckBox("Snap 5px"); self.chk_snap.setChecked(True)
        form_place=QFormLayout(grp_place)
        form_place.setLabelAlignment(Qt.AlignRight|Qt.AlignVCenter)
        form_place.addRow("X", self.spin_x); form_place.addRow("Y", self.spin_y); form_place.addRow("", self.chk_snap)

        # ---- Template & Controls ----
        grp_tpl=QGroupBox("Template Controls")
        self.btn_loadtpl=QPushButton("Load Template")
        self.btn_add_text=QPushButton("+ Add Dynamic Text")
        self.btn_delete_text=QPushButton("Delete Selected"); self.btn_delete_text.setObjectName("danger")
        self.btn_save_fields=QPushButton("Save Fields JSON")
        lt=QVBoxLayout(grp_tpl); lt.addWidget(self.btn_loadtpl)
        fr=QHBoxLayout(); fr.addWidget(self.btn_add_text); fr.addWidget(self.btn_delete_text); lt.addLayout(fr)
        lt.addWidget(self.btn_save_fields)

        # ---- Data & Export ----
        grp_data=QGroupBox("Data Export")
        self.btn_manage_data=QPushButton("Manage Data")
        self.filename_field=QComboBox()
        self.pattern_edit=QLineEdit("{index}_{Text-1}")
        self.pattern_help=QLabel("Pattern: gunakan {index} / {index:03} / {FieldName}."); self.pattern_help.setStyleSheet("color:#94A3B8; font-size:11pt;")
        self.pattern_preview=QLabel("Preview: -"); self.pattern_preview.setStyleSheet("color:#94A3B8; font-size:11pt;")
        self.format_combo=QComboBox(); self.format_combo.addItems(["png","pdf"])
        self.btn_preview=QPushButton("Preview"); self.btn_preview.setObjectName("primary")
        self.btn_generate=QPushButton("Generate"); self.btn_generate.setObjectName("primary")

        ld=QVBoxLayout(grp_data)
        ld.addWidget(self.btn_manage_data)
        rowp=QFormLayout(); rowp.setLabelAlignment(Qt.AlignRight|Qt.AlignVCenter)
        rowp.addRow("Filename field", self.filename_field)
        rowp.addRow("Filename pattern", self.pattern_edit)
        ld.addLayout(rowp)
        ld.addWidget(self.pattern_help)
        ld.addWidget(self.pattern_preview)
        bot=QHBoxLayout(); bot.addWidget(QLabel("Format")); bot.addWidget(self.format_combo); ld.addLayout(bot)
        ld.addWidget(self.btn_preview); ld.addWidget(self.btn_generate)

        # Toolbar
        tb=QToolBar("Toolbar"); tb.setMovable(False); tb.setIconSize(QSize(18,18))
        act_open=QAction(self.style().standardIcon(QStyle.SP_DialogOpenButton),"Open Template",self); act_open.triggered.connect(self.load_template)
        act_zoom_in=QAction(self.style().standardIcon(QStyle.SP_ArrowUp),"Zoom In",self); act_zoom_in.triggered.connect(lambda: self._change_zoom(1.15))
        act_zoom_out=QAction(self.style().standardIcon(QStyle.SP_ArrowDown),"Zoom Out",self); act_zoom_out.triggered.connect(lambda: self._change_zoom(1/1.15))
        act_zoom_reset=QAction(QIcon(),"Reset Zoom",self); act_zoom_reset.triggered.connect(self._fit_to_view)
        act_prev=QAction(self.style().standardIcon(QStyle.SP_FileDialogContentsView),"Preview",self); act_prev.triggered.connect(self.preview_dialog)
        act_gen=QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton),"Generate",self); act_gen.triggered.connect(self.generate_all)
        for a in (act_open,): tb.addAction(a)
        tb.addSeparator(); [tb.addAction(a) for a in (act_zoom_out,act_zoom_reset,act_zoom_in)]
        tb.addSeparator(); [tb.addAction(a) for a in (act_prev,act_gen)]
        self.addToolBar(tb)

        # Zoom slider
        self.zoom_slider=QSlider(Qt.Horizontal); self.zoom_slider.setRange(10,300); self.zoom_slider.setValue(int(self.view_zoom*100))
        self.zoom_slider.valueChanged.connect(lambda v: self._set_zoom(v/100.0))

        # Right column (scrollable)
        right=QVBoxLayout(); [right.addWidget(w) for w in (grp_field,grp_place,grp_tpl,grp_data)]; right.addStretch()
        rw=QWidget(); rw.setLayout(right)
        right_scroll=QScrollArea(); right_scroll.setWidgetResizable(True); right_scroll.setFrameShape(QFrame.NoFrame)
        right_scroll.setWidget(rw); right_scroll.setMinimumWidth(440); right_scroll.setMaximumWidth(560)

        # Left column
        leftcol=QVBoxLayout(); leftcol.addWidget(self.view,1); leftcol.addWidget(self.zoom_slider); lw=QWidget(); lw.setLayout(leftcol)

        # Splitter
        splitter=QSplitter(Qt.Horizontal); splitter.addWidget(lw); splitter.addWidget(right_scroll)
        splitter.setCollapsible(0,False); splitter.setCollapsible(1,False); splitter.setSizes([900,480])

        container=QWidget(); lay=QVBoxLayout(container); lay.setContentsMargins(0,0,0,0); lay.addWidget(splitter); self.setCentralWidget(container)

        # Shortcuts
        self.shortcut_open = QAction(self); self.shortcut_open.setShortcut("Ctrl+O"); self.shortcut_open.triggered.connect(self.load_template); self.addAction(self.shortcut_open)
        self.shortcut_save = QAction(self); self.shortcut_save.setShortcut("Ctrl+S"); self.shortcut_save.triggered.connect(self.save_fields); self.addAction(self.shortcut_save)
        self.shortcut_gen = QAction(self); self.shortcut_gen.setShortcut("Ctrl+G"); self.shortcut_gen.triggered.connect(self.generate_all); self.addAction(self.shortcut_gen)
        self.shortcut_del = QAction(self); self.shortcut_del.setShortcuts(["Delete", "Backspace"]); self.shortcut_del.triggered.connect(self.delete_selected); self.addAction(self.shortcut_del)

        # Signals
        self.btn_loadtpl.clicked.connect(self.load_template)
        self.btn_add_text.clicked.connect(self.add_text)
        self.btn_delete_text.clicked.connect(self.delete_selected)
        self.btn_save_fields.clicked.connect(self.save_fields)
        self.btn_preview.clicked.connect(self.preview_dialog)
        self.btn_generate.clicked.connect(self.generate_all)
        self.btn_manage_data.clicked.connect(self.open_manage_data)

        self.fld_name.textEdited.connect(self._panel_changed)
        self.fld_size.valueChanged.connect(self._panel_changed)
        self.fld_align.currentTextChanged.connect(self._panel_changed)
        self.font_combo.currentFontChanged.connect(lambda _f: self._panel_changed())
        self.spin_x.valueChanged.connect(self._spins_changed)
        self.spin_y.valueChanged.connect(self._spins_changed)
        self.fld_color.textEdited.connect(self._on_color_text)
        self.color_chip.colorChanged.connect(lambda s: (self.fld_color.setText(s), self._panel_changed()))
        self.pattern_edit.textEdited.connect(lambda _ : self._update_filename_preview())
        self.filename_field.currentTextChanged.connect(lambda _ : self._update_filename_preview())
        self.format_combo.currentTextChanged.connect(lambda _ : self._update_filename_preview())

        self.statusBar().showMessage("Tip: Enter = baris baru; Shift+Enter = baris atas. Drag file template atau CSV langsung ke sini!")
        self._refresh_filename_choices(); self._update_filename_preview()

        # Empty state label
        self.empty_overlay = QLabel("No Template Loaded\nClick 'Load Template' or drag image here", self.view)
        self.empty_overlay.setAlignment(Qt.AlignCenter)
        self.empty_overlay.setStyleSheet("color: #64748B; font-size: 16pt; font-weight: 500; background: transparent;")
        self.empty_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._update_empty_overlay()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_empty_overlay()

    def _update_empty_overlay(self):
        if hasattr(self, 'empty_overlay'):
            self.empty_overlay.setVisible(not bool(self.template_path))
            self.empty_overlay.setGeometry(self.view.viewport().rect())

    # ---------- drag/drop ----------
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            urls = e.mimeData().urls()
            if any(u.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.csv')) for u in urls):
                e.acceptProposedAction()

    def dropEvent(self, e):
        for u in e.mimeData().urls():
            path = u.toLocalFile()
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                self.set_template(path)
                break # only one template
            elif path.lower().endswith('.csv'):
                self._import_csv_direct(path)
                break

    def _import_csv_direct(self, path):
        import csv
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                rdr = csv.DictReader(f)
                names = self._field_names() or ["Text-1"]
                self.dataset = [{k: rec.get(k, "") for k in names} for rec in rdr] or [{k: "" for k in names}]
                self._update_filename_preview()
                QMessageBox.information(self, "CSV Imported", f"Imported {len(self.dataset)} rows from {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "CSV error", str(e))

    # ---------- menu ----------
    def _build_menu(self):
        fm=self.menuBar().addMenu("&File")
        act_open=QAction("Open Template…",self); act_open.triggered.connect(self.load_template); fm.addAction(act_open)
        fm.addSeparator(); act_quit=QAction("Quit",self); act_quit.triggered.connect(self.close); fm.addAction(act_quit)

    # ---------- zoom ----------
    def _apply_view_transform(self):
        self.view.resetTransform(); self.view.scale(self.view_zoom,self.view_zoom)
        it=self._selected_item()
        if it: self._update_overlay_for_item(it)
    def _set_zoom(self,z:float):
        self.view_zoom=max(0.1,min(8.0,z)); self.zoom_slider.blockSignals(True); self.zoom_slider.setValue(int(self.view_zoom*100)); self.zoom_slider.blockSignals(False); self._apply_view_transform()
    def _change_zoom(self,f): self._set_zoom(self.view_zoom*f)
    def _fit_to_view(self):
        if not self.bg_item: return
        vw=max(10,self.view.viewport().width()-24); vh=max(10,self.view.viewport().height()-24)
        self._set_zoom(min(vw/self.img_w, vh/self.img_h))

    # ---------- template ----------
    def load_template(self):
        path,_=QFileDialog.getOpenFileName(self,"Choose template image","","Images (*.png *.jpg *.jpeg *.webp)")
        if path: self.set_template(path)
    def set_template(self,path:str):
        self.template_path=path; pm=QPixmap(path)
        self.img_w,self.img_h=pm.width(),pm.height(); self.sf=1.0
        self.scene.clear(); self._clear_overlay()
        paper=QGraphicsRectItem(0,0,self.img_w,self.img_h); paper.setBrush(QBrush(Qt.white)); paper.setPen(QPen(QColor("#D1D5DB"),1)); self.scene.addItem(paper)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setXOffset(0); shadow.setYOffset(4)
        shadow.setColor(QColor(0,0,0,60))
        
        self.bg_item=QGraphicsPixmapItem(pm)
        try: self.bg_item.setTransformationMode(Qt.SmoothTransformation)
        except Exception: pass
        self.bg_item.setZValue(1); self.scene.addItem(self.bg_item)
        
        # Apply shadow to both paper and pixmap via a container if needed, 
        # but GraphicsItem shadow is tricky. Apply to the pixmap item for now.
        self.bg_item.setGraphicsEffect(shadow)

        for f in self.fields:
            it=DraggableText(f,self.sf,self._on_item_moved); it.setZValue(2); self.scene.addItem(it); self._apply_canvas_alignment(it)
        self.scene.setSceneRect(-50,-50,self.img_w+100,self.img_h+100); self._fit_to_view()
        self._update_empty_overlay()

    # ---------- overlay ----------
    def _clear_overlay(self):
        if self.overlay_box: self.scene.removeItem(self.overlay_box); self.overlay_box=None
    def _show_overlay_for(self,it:DraggableText):
        self._clear_overlay(); f=it.field
        scene_w=(f.box_width*self.sf) if (f.box_width and f.box_width>0) else int(it.boundingRect().width())+12
        h=max(20,int(it.boundingRect().height())); x=it.pos().x(); y=it.pos().y()
        box=ResizeOverlay(f,self.sf,on_resize=lambda bw:(self.fld_boxw.setValue(int(bw)), self._apply_canvas_alignment(it)))
        box.setRect(0,0,max(40,int(scene_w)),h); box.setPos(x,y); self.scene.addItem(box); self.overlay_box=box; self.fld_boxw.setValue(int(f.box_width))
    def _update_overlay_for_item(self,it:DraggableText):
        if not self.overlay_box or self._selected_item() is not it: return
        f=it.field; scene_w=(f.box_width*self.sf) if (f.box_width and f.box_width>0) else int(it.boundingRect().width())+12
        h=max(20,int(it.boundingRect().height())); self.overlay_box.setRect(0,0,max(40,int(scene_w)),h)
        self.overlay_box.setPos(it.pos().x(), it.pos().y()); self.fld_boxw.setValue(int(f.box_width)); self._apply_canvas_alignment(it)

    # ---------- align kanvas ----------
    def _apply_canvas_alignment(self,it:QGraphicsTextItem):
        f:TextField=it.field
        width_scene=float(f.box_width*self.sf) if (f.box_width and f.box_width>0) else -1.0
        it.setTextWidth(width_scene)
        doc=it.document(); opt=doc.defaultTextOption()
        a=(f.align or "left").lower()
        opt.setAlignment(Qt.AlignHCenter if a=="center" else (Qt.AlignRight if a=="right" else Qt.AlignLeft))
        doc.setDefaultTextOption(opt); it.setFont(qfont_from_field(f)); it.setDefaultTextColor(QColor(f.color)); it.update()

    # ---------- helpers ----------
    def _field_names(self)->List[str]: return [f.name for f in self.fields]
    def _refresh_filename_choices(self):
        cur=self.filename_field.currentText(); self.filename_field.clear()
        names=self._field_names() or ["Text-1"]; self.filename_field.addItems(names)
        if cur and cur in names: self.filename_field.setCurrentText(cur)
    def _ensure_dataset_columns(self):
        if not self.dataset: return
        names=self._field_names()
        for r in self.dataset:
            for n in names:
                if n not in r: r[n]=""
    def _rename_dataset_column(self,old,new):
        if old==new: return
        for r in self.dataset:
            if old in r and new not in r: r[new]=r.pop(old)
            else: r.pop(old, None)

    # ---------- sink panel → field ----------
    def _push_selected_panel_to_field(self):
        it=self._selected_item()
        if not it: return
        f=it.field; old=f.name
        f.name=self.fld_name.text().strip() or old
        f.size=self.fld_size.value()
        f.color=self.fld_color.text().strip() or "#000000"
        f.align=self.fld_align.currentText().strip().lower()
        f.font_family=self.font_combo.currentFont().family(); f.font_path=resolve_font_path(f.font_family)
        f.x, f.y = self.spin_x.value(), self.spin_y.value()
        it.setPlainText(f"{{{{{f.name}}}}}"); it.setFont(qfont_from_field(f)); it.setDefaultTextColor(QColor(f.color)); it.setPos(f.x*self.sf, f.y*self.sf)
        if old!=f.name: self._rename_dataset_column(old,f.name); self._ensure_dataset_columns(); self._refresh_filename_choices()
        self._update_overlay_for_item(it); self._update_filename_preview()

    # ---------- fields ----------
    def _next_field_name(self)->str:
        i, used = 1, set(self._field_names())
        while True:
            n=f"Text-{i}"
            if n not in used: return n
            i+=1
    def add_text(self):
        if not self.template_path:
            QMessageBox.warning(self,"No template","Silakan load template dulu."); return
        name=self.fld_name.text().strip() or self._next_field_name()
        fam=self.font_combo.currentFont().family()
        f=TextField(name=name,x=100,y=100,size=self.fld_size.value(),
                    color=self.fld_color.text().strip() or "#000000",
                    align=self.fld_align.currentText(), font_family=fam, font_path=resolve_font_path(fam), box_width=0)
        self.fields.append(f)
        it=DraggableText(f,self.sf,self._on_item_moved); it.setZValue(3)
        self.scene.addItem(it); self._apply_canvas_alignment(it)
        it.setSelected(True); self._on_selection_changed(); self.view.centerOn(it)
        self._ensure_dataset_columns(); self._refresh_filename_choices(); self._update_filename_preview()
    def delete_selected(self):
        sel=[it for it in self.scene.selectedItems() if isinstance(it,DraggableText)]
        if not sel: return
        for it in sel:
            name=it.field.name; self.scene.removeItem(it)
            self.fields=[f for f in self.fields if f.name!=name]
            for r in self.dataset: r.pop(name, None)
        self._clear_overlay(); self._refresh_filename_choices(); self._update_filename_preview()
    def _selected_item(self)->Optional[DraggableText]:
        for it in self.scene.selectedItems():
            if isinstance(it,DraggableText): return it
        return None
    def _on_selection_changed(self):
        it=self._selected_item(); self._clear_overlay()
        if not it: return
        f=it.field
        self.fld_name.setText(f.name); self.fld_size.setValue(f.size)
        self.fld_color.setText(f.color); self.color_chip.setColor(f.color)
        self.fld_align.setCurrentText(f.align if f.align in ["left","center","right"] else "left")
        if f.font_family: self.font_combo.setCurrentFont(QFont(f.font_family))
        self.spin_x.blockSignals(True); self.spin_y.blockSignals(True)
        self.spin_x.setValue(int(f.x)); self.spin_y.setValue(int(f.y))
        self.spin_x.blockSignals(False); self.spin_y.blockSignals(False)
        self._show_overlay_for(it); self._apply_canvas_alignment(it)

    # ---------- panel change ----------
    def _panel_changed(self,*args):
        self._push_selected_panel_to_field()
    def _on_color_text(self,s:str):
        if QColor.isValidColor(s): self.color_chip.setColor(s)
        self._panel_changed()

    # ---------- fields JSON ----------
    def save_fields(self):
        if not self.fields: QMessageBox.information(self,"Empty","Belum ada field."); return
        out,_=QFileDialog.getSaveFileName(self,"Save fields.json","fields.json","JSON (*.json)")
        if not out: return
        with open(out,"w",encoding="utf-8") as fp: json.dump([asdict(f) for f in self.fields], fp, indent=2, ensure_ascii=False)
        QMessageBox.information(self,"Saved",out)

    # ---------- data ----------
    def open_manage_data(self):
        names=self._field_names() or ["Text-1"]; self._ensure_dataset_columns()
        dlg=ManageDataDialog(self,names,self.dataset)
        if dlg.exec(): self.dataset=dlg.get_dataset(); self._update_filename_preview()

    # ---------- pilih folder (tanpa Save As) ----------
    def _select_output_dir(self)->str:
        # pakai dialog khusus folder; tombol biasanya "Open/Choose" (tanpa kolom file name)
        path=QFileDialog.getExistingDirectory(self,"Choose output folder","")
        return path or ""

    # ---------- filename pattern ----------
    def _render_filename_from_pattern(self, row: Dict[str,str], idx:int, fallback_field:str)->str:
        pat = (self.pattern_edit.text() or "").strip()
        if not pat:
            return row.get(fallback_field, f"row_{idx}") or f"row_{idx}"

        # {index} or {index:03}
        def repl_index(m):
            pad = m.group(1)
            return f"{idx:0{int(pad)}d}" if pad else str(idx)
        s = re.sub(r"\{index(?::(\d+))?\}", repl_index, pat)

        # {FieldName}
        def repl_field(m):
            key = m.group(1)
            return str(row.get(key, "")).strip()
        s = re.sub(r"\{([^{}:]+)\}", repl_field, s)

        s = s or f"row_{idx}"
        safe = "".join(c for c in s if c.isalnum() or c in "-_ ").strip().replace(" ","_")
        return safe or f"row_{idx}"

    def _update_filename_preview(self):
        if not self.dataset:
            self.pattern_preview.setText("Preview: (isi data dulu)")
            return
        field = self.filename_field.currentText().strip() or (self._field_names()[0] if self.fields else "Text-1")
        name = self._render_filename_from_pattern(self.dataset[0], 1, field)
        ext = self.format_combo.currentText().lower()
        self.pattern_preview.setText(f"Preview: {name}.{ext}")

    # ---------- preview / generate ----------
    def preview_dialog(self):
        if not self.template_path: QMessageBox.warning(self,"No template","Silakan load template dulu."); return
        if not self.dataset: QMessageBox.information(self,"Data kosong","Isi data di Manage Data."); return
        self._push_selected_panel_to_field()
        try:
            img=render_to_image(self.template_path,[asdict(f) for f in self.fields], self.dataset[0])
            from PIL.ImageQt import ImageQt
            qimg=ImageQt(img); pix=QPixmap.fromImage(qimg); PreviewDialog(pix,self).exec()
        except Exception as e: QMessageBox.critical(self,"Error",str(e))

    def generate_all(self):
        if not self.template_path: QMessageBox.warning(self,"No template","Silakan load template dulu."); return
        if not self.dataset: QMessageBox.information(self,"Data kosong","Isi data di Manage Data."); return
        self._push_selected_panel_to_field()

        out_dir=self._select_output_dir()
        if not out_dir: return

        fmt=self.format_combo.currentText().lower().strip()
        fallback_field=self.filename_field.currentText().strip() or (self._field_names()[0] if self.fields else "output")
        fields=[asdict(f) for f in self.fields]; cnt=0
        for idx,row in enumerate(self.dataset, start=1):
            base=self._render_filename_from_pattern(row, idx, fallback_field)
            out=os.path.join(out_dir, f"{base}.pdf" if fmt=="pdf" else f"{base}.png")
            try: draw_certificate(self.template_path, fields, row, out, fmt=fmt); cnt+=1
            except Exception as e: QMessageBox.warning(self,"Render error",f"Row {idx}: {e}")
        QMessageBox.information(self,"Selesai",f"Generated {cnt} file(s) ke:\n{out_dir}")

    # ---------- presisi ----------
    def _apply_snap(self,x,y):
        if self.chk_snap.isChecked(): x=round(x/5)*5; y=round(y/5)*5
        return x,y
    def _on_item_moved(self,it:DraggableText):
        x,y=self._apply_snap(it.field.x,it.field.y); it.field.x, it.field.y = x,y
        it.setPos(x*self.sf,y*self.sf)
        self.spin_x.blockSignals(True); self.spin_y.blockSignals(True)
        self.spin_x.setValue(int(x)); self.spin_y.setValue(int(y))
        self.spin_x.blockSignals(False); self.spin_y.blockSignals(False)
        self._update_overlay_for_item(it)
    def _spins_changed(self):
        it=self._selected_item()
        if not it: return
        x,y=self._apply_snap(self.spin_x.value(), self.spin_y.value())
        it.field.x, it.field.y = x,y; it.setPos(x*self.sf,y*self.sf); self._update_overlay_for_item(it)
    def _on_nudge(self,dx,dy):
        it=self._selected_item()
        if not it: return
        x,y=self._apply_snap(it.field.x+dx, it.field.y+dy)
        it.field.x, it.field.y = x,y; it.setPos(x*self.sf,y*self.sf)
        self.spin_x.blockSignals(True); self.spin_y.blockSignals(True)
        self.spin_x.setValue(int(x)); self.spin_y.setValue(int(y))
        self.spin_x.blockSignals(False); self.spin_y.blockSignals(False)
        self._update_overlay_for_item(it)


def main():
    import sys
    app=QApplication(sys.argv)
    apply_fresh_theme(app, mode="dark")
    w=Main(); w.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
