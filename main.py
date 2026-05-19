from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Base, engine, get_db
from models import Transaction
from schemas import TransactionCreate, TransactionOut

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PrimeAxis API")

@app.get("/")
def root():
    return {"message": "PrimeAxis API is running"}

@app.post("/transactions", response_model=TransactionOut)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    category = transaction.category.lower()
    if category not in ("income", "expense"):
        raise HTTPException(status_code=400, detail="Category must be 'income' or 'expense'.")

    record = Transaction(
        description=transaction.description,
        amount=transaction.amount,
        category=category
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@app.get("/transactions", response_model=list[TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.created_at.desc()).all()

@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    total_income = db.query(func.coalesce(func.sum(Transaction.amount), 0.0))                .filter(Transaction.category == "income").scalar()
    total_expenses = db.query(func.coalesce(func.sum(Transaction.amount), 0.0))                .filter(Transaction.category == "expense").scalar()

    net_profit = total_income - total_expenses
    tot_tax = total_income * 0.015

    return {
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "net_profit": float(net_profit),
        "tot_tax": float(tot_tax)
    }
