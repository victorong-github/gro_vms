from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from psycopg2.extras import RealDictCursor

app = FastAPI()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}


class PORecord(BaseModel):
    identifier: str
    po_number: str
    service_month_year: str
    acknowledgement: str
    billable_days: int
    non_billable_days: int
    service_start_date: str
    service_end_date: str
    calculated_amount: float
    name: str
    status: str

# Request model for updating acknowledgement
class AcknowledgementUpdate(BaseModel):
    acknowledgement: str

@app.get("/po/{identifier}")
def get_po(identifier: str):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("SELECT * FROM po_records WHERE identifier = %s", (identifier,))
    record = cur.fetchone()
    cur.close()
    conn.close()
    
    if not record:
        raise HTTPException(status_code=404, detail="PO not found")
    
    return dict(zip([desc[0] for desc in cur.description], record))

@app.post("/po/upload")
def upload_po(po: PORecord):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO po_records (identifier, po_number, service_month_year, acknowledgement, billable_days, non_billable_days, 
                               service_start_date, service_end_date, calculated_amount, name, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (po.identifier, po.po_number, po.service_month_year, po.acknowledgement, po.billable_days, po.non_billable_days,
          po.service_start_date, po.service_end_date, po.calculated_amount, po.name, po.status))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "PO uploaded successfully"}

@app.put("/po/approve/{identifier}")
def approve_po(identifier: str):
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("UPDATE po_records SET status = 'approved' WHERE identifier = %s", (identifier,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "PO approved successfully"}

@app.put("/update-acknowledgement/{identifier}")
def update_acknowledgement(identifier: str, data: AcknowledgementUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update record
        cursor.execute("UPDATE po_records SET acknowledgement = %s WHERE identifier = %s RETURNING *;",
                       (data.acknowledgement, identifier))
        updated_row = cursor.fetchone()

        if not updated_row:
            raise HTTPException(status_code=404, detail="PO Record not found")

        conn.commit()  # Ensure changes are saved
        return {"message": "Acknowledgement updated successfully"}

    except Exception as e:
        print(f"Error: {e}")  # Log error
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        cursor.close()
        conn.close()
