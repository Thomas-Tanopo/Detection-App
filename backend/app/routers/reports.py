import json, io
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.detection import Detection
from app.models.user import User
from app.auth_jwt import get_current_user
import openpyxl
from fpdf import FPDF

router = APIRouter()

@router.get("")
def list_detections(start_date: str = Query(""), end_date: str = Query(""), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Detection).order_by(Detection.created_at.desc())
    if start_date:
        q = q.filter(Detection.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        q = q.filter(Detection.created_at <= datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S"))
    dets = q.all()
    result = []
    for d in dets:
        objects = json.loads(d.detected_objects) if d.detected_objects else []
        result.append({
            "id": d.id,
            "image_url": f"/uploads/{d.image_path}" if d.image_path else None,
            "detected_objects": objects,
            "total_objects": len(objects),
            "user": d.user.full_name or d.user.username if d.user else None,
            "created_at": d.created_at.isoformat()
        })
    return result

@router.get("/export/excel")
def export_excel(start_date: str = Query(""), end_date: str = Query(""), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Detection).order_by(Detection.created_at.desc())
    if start_date:
        q = q.filter(Detection.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        q = q.filter(Detection.created_at <= datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S"))
    dets = q.all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Laporan Deteksi"
    ws.append(["ID", "Tanggal", "User", "Objek Terdeteksi"])
    for d in dets:
        nama_user = d.user.full_name or d.user.username if d.user else "-"
        objects = json.loads(d.detected_objects) if d.detected_objects else []
        obj_str = ", ".join([f"{o['label']} ({round(o['confidence']*100,1)}%)" for o in objects]) if objects else "-"
        ws.append([d.id, d.created_at.strftime("%d/%m/%Y %H:%M"), nama_user, obj_str])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            headers={"Content-Disposition": "attachment; filename=laporan_deteksi.xlsx"})

@router.get("/export/pdf")
def export_pdf(start_date: str = Query(""), end_date: str = Query(""), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Detection).order_by(Detection.created_at.desc())
    if start_date:
        q = q.filter(Detection.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        q = q.filter(Detection.created_at <= datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S"))
    dets = q.all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Laporan Deteksi", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(10, 7, "ID", 1)
    pdf.cell(40, 7, "Tanggal", 1)
    pdf.cell(40, 7, "User", 1)
    pdf.cell(100, 7, "Objek Terdeteksi", 1)
    pdf.ln()
    pdf.set_font("Arial", "", 9)
    for d in dets:
        nama_user = d.user.full_name or d.user.username if d.user else "-"
        objects = json.loads(d.detected_objects) if d.detected_objects else []
        obj_str = ", ".join([f"{o['label']} ({round(o['confidence']*100,1)}%)" for o in objects]) if objects else "-"
        pdf.cell(10, 7, str(d.id), 1)
        pdf.cell(40, 7, d.created_at.strftime("%d/%m/%Y %H:%M"), 1)
        pdf.cell(40, 7, nama_user[:18], 1)
        pdf.cell(100, 7, obj_str[:48], 1)
        pdf.ln()
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf",
                            headers={"Content-Disposition": "attachment; filename=laporan_deteksi.pdf"})
