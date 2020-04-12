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


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    funderAcct = db.Column(db.String(80), nullable=False)
    benefAcct = db.Column(db.String(80), nullable=False)
    paymentMode = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.String(80), nullable=False)
    prediction = db.Column(db.Integer, nullable=False)
    transactionDate = db.Column(db.DateTime())
    fraudStatus = db.Column(db.Enum('normal', 'suspected', 'confirmed', 'dismissed', name='fraud_status'), default='normal')

    def json(self):
        return {
                'id': self.id,
                'amount': self.amount,
                'benefAcct': self.benefAcct, 
                'funderAcct': self.funderAcct, 
                'paymentMode': self.paymentMode, 
                'prediction': self.prediction,
                'transactionDate': self.transactionDate,
                'fraudStatus': self.fraudStatus
                }

    def add_report(_funderAcct, _benefAcct, _paymentMode, _amount, _prediction, _transactionDate, _fraudStatus):
        new_report = Report(
            funderAcct=_funderAcct,
            benefAcct=_benefAcct, 
            paymentMode=_paymentMode,
            amount=_amount,
            prediction=_prediction,
            transactionDate = _transactionDate,
            fraudStatus=_fraudStatus)
        db.session.add(new_report)
        db.session.commit()

    def get_reports():
        return [Report.json(report) for report in Report.query.all()]

    def get_all_good_reports():
        return [Report.json(report) for report in Report.query.filter_by(prediction=0).all()]


    def get_all_bad_reports():
        return [Report.json(report) for report in Report.query.filter_by(prediction=1).all()]      

    def get_all_reports(prediction=None, paymentMode=None, fromDate=None, toDate=None):
        res = Report.query

        if prediction is not None:
            res = res.filter(Report.prediction == prediction)
        if paymentMode is not None:
            res = res.filter(Report.paymentMode == paymentMode)
        if fromDate and toDate is not None:
            res = res.filter(and_(func.date(Report.transactionDate) >= fromDate, func.date(Report.transactionDate) <= toDate))
        return [Report.json(report) for report in res.all()]

    def confirm_fraud(_id, _status):
        transaction = Report.query.filter_by(id=_id).first()
        transaction.fraudStatus = _status
        db.session.commit()

    def __repr__(self):
        report = {
            'id': self.id,
            'funderAcct': self.funderAcct,
            'benefAcct': self.benefAcct,
            'paymentMode': self.paymentMode,
            'amount': self.amount,
            'prediction': self.prediction,
            'transactionDate': self.transactionDate,
            'fraudStatus': self.fraudStatus
        }
        return str(report)
