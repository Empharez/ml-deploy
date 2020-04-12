from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import text
from sqlalchemy import func, and_
from datetime import datetime
import json
from config import app

db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    referenceNumber = db.Column(db.String(12),  primary_key=True, nullable=False)
    step = db.Column(db.Integer, nullable=False)
    paymentMode = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.String(80), nullable=False)
    funderAcct = db.Column(db.String(80), nullable=False)
    oldFunderBalance = db.Column(db.String(80), nullable=False)
    newFunderBalance = db.Column(db.String(80), nullable=False)
    benefAcct = db.Column(db.String(80), nullable=False)
    oldBenefBalance = db.Column(db.String(80), nullable=False)
    newBenefBalance = db.Column(db.String(80), nullable=False)
    prediction = db.Column(db.Integer, nullable=True)
    fraudStatus = db.Column(db.Enum('normal', 'suspected', 'confirmed', 'dismissed', name='fraud_status'), default='normal', nullable=True)


    def json(self):
        return {
                'referenceNumber': self.referenceNumber,
                'step': self.step,
                'paymentMode': self.paymentMode, 
                'amount': self.amount,
                'funderAcct': self.funderAcct,
                'oldFunderBalance': self.oldFunderBalance,
                'newFunderBalance': self.newFunderBalance,
                'benefAcct': self.benefAcct, 
                'oldBenefBalance': self.oldBenefBalance,
                'newBenefBalance': self.newBenefBalance,
                'fraudStatus': self.fraudStatus
                }

    def get_by_reference(_refNo):
        return Transaction.json(Transaction.query.filter_by(referenceNumber=_refNo).first())

    def get_transactions(fraudStatus=None, paymentMode=None, page=None):
        res = Transaction.query

        if fraudStatus is not None:
            res = res.filter(Transaction.fraudStatus == fraudStatus)
        if paymentMode is not None:
            res = res.filter(Transaction.paymentMode == paymentMode)
        return [Transaction.json(transaction) for transaction in res.paginate(page, 10, False).items]

    def update_transaction(_refNo, _status, _prediction):
        transaction = Transaction.query.filter_by(referenceNumber=_refNo).first()
        transaction.fraudStatus = _status
        transaction.prediction = _prediction
        db.session.commit()


    def change_status(_refNo, _status):
        transaction =  Transaction.query.filter_by(referenceNumber=_refNo).first()
        transaction.fraudStatus = _status
        db.session.commit()


    def __repr__(self):
        transaction = {
            'referenceNumber': self.referenceNumber,
            'step': self.step,
            'paymentMode': self.paymentMode, 
            'amount': self.amount,
            'funderAcct': self.funderAcct,
            'oldFunderBalance': self.oldFunderBalance,
            'newFunderBalance': self.newFunderBalance,
            'benefAcct': self.benefAcct, 
            'oldBenefBalance': self.oldBenefBalance,
            'newBenefBalance': self.newBenefBalance,
            'fraudStatus': self.fraudStatus
            }
        return str(transaction)
