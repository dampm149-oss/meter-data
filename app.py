#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Backend API cho Meter Data
Deploy lên: Vercel, Railway, PythonAnywhere, etc.

Cài đặt:
pip install flask flask-cors supabase-py python-dotenv requests openpyxl

Chạy locally:
python3 app.py
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import requests
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

load_dotenv()

app = Flask(__name__)
CORS(app)

# ========== CONFIG ==========
API_BASE_URL = "http://14.225.244.63:8899/api"
USERNAME = os.getenv("METER_USERNAME", "verdant")
PASSWORD = os.getenv("METER_PASSWORD", "verdantenergy@2026")

# Danh sách công tơ
METERS = [
    {"stt": 1, "meter_no": "2410770895", "site": "VN1-YISHENG", "site_id": "VD016"},
    {"stt": 2, "meter_no": "2411320841", "site": "VN2-RK RESOURCES", "site_id": "VD019"},
    {"stt": 3, "meter_no": "2411320925", "site": "VN2-RK RESOURCES", "site_id": "VD019"},
    {"stt": 4, "meter_no": "2411320957", "site": "VN2-RK RESOURCES", "site_id": "VD019"},
    {"stt": 5, "meter_no": "2410770947", "site": "VN1-DELSON_S1", "site_id": "VD011"},
    {"stt": 6, "meter_no": "2410770496", "site": "VN1-DELSON_S1", "site_id": "VD011"},
    {"stt": 7, "meter_no": "2410770519", "site": "VN1-WEISHENG", "site_id": "VD015"},
    {"stt": 8, "meter_no": "2410770533", "site": "VN1-KINGDOM", "site_id": "VD014"},
    {"stt": 9, "meter_no": "2410770525", "site": "VN1-KINGDOM", "site_id": "VD014"},
    {"stt": 10, "meter_no": "2410770851", "site": "VN1-JIANG MEN", "site_id": "VD013"},
    {"stt": 11, "meter_no": "2410770894", "site": "VN1-GREAT PROCESS", "site_id": "VD012"},
    {"stt": 12, "meter_no": "2411320920", "site": "VN2-MOCAL CREATIVE", "site_id": "VD018"},
    {"stt": 13, "meter_no": "2411320977", "site": "VN2-MOCAL CREATIVE", "site_id": "VD018"},
    {"stt": 14, "meter_no": "2410717617", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 15, "meter_no": "2410770552", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 16, "meter_no": "2410770558", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 17, "meter_no": "2410770588", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 18, "meter_no": "2410770598", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 19, "meter_no": "2410770614", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 20, "meter_no": "2410770628", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 21, "meter_no": "2410770631", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 22, "meter_no": "2410770637", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 23, "meter_no": "2410770640", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 24, "meter_no": "2410770720", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 25, "meter_no": "2410770737", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 26, "meter_no": "2510014176", "site": "VN2-ChengShin Rubber", "site_id": "VD017"},
    {"stt": 27, "meter_no": "2510696851", "site": "VN3-Alena-1A", "site_id": "VD020"},
    {"stt": 28, "meter_no": "2510696860", "site": "VN3-Alena-1A", "site_id": "VD020"},
    {"stt": 29, "meter_no": "2510223457", "site": "VN3-Amara-1A", "site_id": "VD021"},
    {"stt": 30, "meter_no": "2510697069", "site": "VN3-Amara-1A", "site_id": "VD021"},
]

# ========== HELPER FUNCTIONS ==========

def get_token():
    """Lấy token từ API"""
    try:
        login_url = f"{API_BASE_URL}/Login?UserAccount={USERNAME}&Password={PASSWORD}"
        response = requests.get(login_url, timeout=10)
        data = response.json()
        if data.get('CODE') == '1' or data.get('CODE') == 1:
            return data.get('TOKEN')
    except Exception as e:
        print(f"Error getting token: {str(e)}")
    return None

def fetch_meter_data(meter_no, start_date, end_date, token):
    """Lấy dữ liệu công tơ từ API"""
    try:
        url = f"{API_BASE_URL}/GetMeterDataByDate?MeterNo={meter_no}&StartDate={start_date}&EndDate={end_date}&Token={token}"
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error fetching meter {meter_no}: {str(e)}")
    return []

def calculate_daily_consumption(meter_data):
    """Tính sản lượng ngày từ first và last record"""
    if not meter_data or len(meter_data) == 0:
        return {}
    
    first = meter_data[0]
    last = meter_data[-1]
    
    result = {
        'first_time': first.get('DATE_TIME'),
        'last_time': last.get('DATE_TIME'),
        'records_count': len(meter_data)
    }
    
    # Tính delta cho các field số
    for key in first.keys():
        if key not in ['METER_NO', 'DATE_TIME', 'RESERVE1', 'RESERVE2']:
            try:
                first_val = float(first.get(key, 0))
                last_val = float(last.get(key, 0))
                delta = last_val - first_val
                result[key] = round(delta, 2)
            except:
                pass
    
    return result

# ========== API ROUTES ==========

@app.route('/', methods=['GET'])
def index():
    """Home page"""
    return jsonify({
        'name': 'Meter Data API',
        'version': '1.0',
        'endpoints': {
            '/api/meters': 'Get list of all meters',
            '/api/data/today': 'Get today meter data',
            '/api/data/yesterday': 'Get yesterday meter data',
            '/api/data/<meter_no>/<date>': 'Get specific meter data (date: YYYY-MM-DD)',
            '/api/export/excel': 'Export data to Excel',
        }
    })

@app.route('/api/meters', methods=['GET'])
def get_meters():
    """Danh sách tất cả công tơ"""
    return jsonify({
        'total': len(METERS),
        'meters': METERS
    })

@app.route('/api/data/yesterday', methods=['GET'])
def get_yesterday_data():
    """Lấy dữ liệu hôm qua"""
    target_date = datetime.now() - timedelta(days=1)
    start_date = target_date.strftime("%Y%m%d000000")
    end_date = target_date.strftime("%Y%m%d235959")
    
    token = get_token()
    if not token:
        return jsonify({'error': 'Cannot get token'}), 401
    
    results = []
    for meter_info in METERS:
        meter_data = fetch_meter_data(
            meter_info['meter_no'],
            start_date,
            end_date,
            token
        )
        
        if meter_data:
            consumption = calculate_daily_consumption(meter_data)
            result = {
                **meter_info,
                **consumption
            }
            results.append(result)
    
    return jsonify({
        'date': target_date.strftime('%Y-%m-%d'),
        'total_meters': len(results),
        'data': results
    })

@app.route('/api/data/today', methods=['GET'])
def get_today_data():
    """Lấy dữ liệu hôm nay"""
    target_date = datetime.now()
    start_date = target_date.strftime("%Y%m%d000000")
    end_date = target_date.strftime("%Y%m%d235959")
    
    token = get_token()
    if not token:
        return jsonify({'error': 'Cannot get token'}), 401
    
    results = []
    for meter_info in METERS:
        meter_data = fetch_meter_data(
            meter_info['meter_no'],
            start_date,
            end_date,
            token
        )
        
        if meter_data:
            consumption = calculate_daily_consumption(meter_data)
            result = {
                **meter_info,
                **consumption
            }
            results.append(result)
    
    return jsonify({
        'date': target_date.strftime('%Y-%m-%d'),
        'total_meters': len(results),
        'data': results
    })

@app.route('/api/data/<meter_no>/<date_str>', methods=['GET'])
def get_specific_meter_data(meter_no, date_str):
    """Lấy dữ liệu công tơ cụ thể theo ngày"""
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        start_date = target_date.strftime("%Y%m%d000000")
        end_date = target_date.strftime("%Y%m%d235959")
    except:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    token = get_token()
    if not token:
        return jsonify({'error': 'Cannot get token'}), 401
    
    meter_data = fetch_meter_data(meter_no, start_date, end_date, token)
    
    if not meter_data:
        return jsonify({'error': 'No data found'}), 404
    
    meter_info = next((m for m in METERS if m['meter_no'] == meter_no), None)
    
    return jsonify({
        'date': date_str,
        'meter': meter_info,
        'records_count': len(meter_data),
        'consumption': calculate_daily_consumption(meter_data),
        'raw_data': meter_data
    })

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    """Export dữ liệu hôm qua sang Excel"""
    date_param = request.args.get('date')
    
    if date_param:
        try:
            target_date = datetime.strptime(date_param, '%Y-%m-%d')
        except:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    else:
        target_date = datetime.now() - timedelta(days=1)
    
    start_date = target_date.strftime("%Y%m%d000000")
    end_date = target_date.strftime("%Y%m%d235959")
    
    token = get_token()
    if not token:
        return jsonify({'error': 'Cannot get token'}), 401
    
    # Fetch all data
    results = []
    for meter_info in METERS:
        meter_data = fetch_meter_data(
            meter_info['meter_no'],
            start_date,
            end_date,
            token
        )
        
        if meter_data:
            consumption = calculate_daily_consumption(meter_data)
            result = {
                **meter_info,
                **consumption
            }
            results.append(result)
    
    # Create Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Meter Data"
    
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Headers
    headers = ['STT', 'Công tơ', 'Site', 'Site ID', 'Số record', 'Giờ đầu', 'Giờ cuối']
    
    # Find all delta fields
    delta_fields = set()
    for result in results:
        for key in result.keys():
            if key not in ['stt', 'meter_no', 'site', 'site_id', 'first_time', 'last_time', 'records_count']:
                delta_fields.add(key)
    
    delta_fields = sorted(list(delta_fields))
    headers.extend(delta_fields)
    
    # Write headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = border
    
    # Write data
    for row_idx, result in enumerate(results, 2):
        ws.cell(row=row_idx, column=1).value = result.get('stt')
        ws.cell(row=row_idx, column=2).value = result.get('meter_no')
        ws.cell(row=row_idx, column=3).value = result.get('site')
        ws.cell(row=row_idx, column=4).value = result.get('site_id')
        ws.cell(row=row_idx, column=5).value = result.get('records_count')
        ws.cell(row=row_idx, column=6).value = result.get('first_time')
        ws.cell(row=row_idx, column=7).value = result.get('last_time')
        
        for col_idx, field in enumerate(delta_fields, 8):
            value = result.get(field, '')
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.value = value
            if value != '':
                cell.number_format = '#,##0.00'
            cell.border = border
    
    # Save to BytesIO
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    filename = f"meter_data_{target_date.strftime('%Y%m%d')}.xlsx"
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

# ========== RUN ==========

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
