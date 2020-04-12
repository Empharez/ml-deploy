from flask import Flask, request, render_template, jsonify, json, Response
import pickle
from flask_bootstrap import Bootstrap
import pandas as pd
from reportModel import *
from transactionModel import *
from config import * 
import numpy as np
from datetime import datetime
import json

pickle_in = open('new_fraud_model.pkl', 'rb')
model = pickle.load(pickle_in)

loadModel = open('fraudDetection.pkl', 'rb')
loadedModel = pickle.load(loadModel)

Bootstrap(app)


@app.route('/api/reports')
def get_all_results():
    flag = request.args.get('flag')
    paymentMethod = request.args.get('paymentMode')
    fromDate = request.args.get('fromDate')
    toDate = request.args.get('toDate')

    reports = Report.get_all_reports(flag, paymentMethod, fromDate, toDate)

    return jsonify({
        'status': 'success',
        'data': {
            'reports': reports
            }
        }), 200

@app.route('/api/transactions')
def get_transactions():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    paymentMethod = request.args.get('paymentMode')

    transactions = Transaction.get_transactions(status, paymentMethod, page)

    return jsonify({
        'status': 'success',
        'data': {
            'reports': transactions
            }
        }), 200


@app.route('/api/predict_transaction', methods=['POST'])
def predictTransaction():
    try:
        data = request.get_json(force=True)
        referenceNo = data['referenceNo']

        transaction = Transaction.get_by_reference(referenceNo)

        predictionData = {}

        predictionData['step'] = transaction['step']
        predictionData['paymentMode'] = transaction['paymentMode']
        predictionData['amount'] = transaction['amount']
        predictionData['funderAcct'] = transaction['funderAcct']
        predictionData['oldFunderBalance'] = transaction['oldFunderBalance']
        predictionData['newFunderBalance'] = transaction['newFunderBalance']
        predictionData['benefAcct'] = transaction['benefAcct']
        predictionData['oldBenefBalance'] = transaction['oldBenefBalance']
        predictionData['newBenefBalance'] = transaction['newBenefBalance']

        prediction_result = predict_transaction(predictionData)

        updateData(referenceNo, prediction_result)

        resultValue = checkValue(str(prediction_result))
        return jsonify({
            'status': 'success',
            'data': resultValue
            }), 200
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Value must be in integer'
            }), 400



@app.route('/api/transaction/<int:refNo>')
def get_transaction_by_rrr(refNo):
    transaction = Transaction.get_by_reference(refNo)
    return jsonify({
        'status': "success",
        'data': {
            'Transaction': transaction
        } 
    }), 200



@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        funderAcct = data['funderAcct']
        benefAcct = data['benefAcct']
        paymentMode = data['paymentMode']
        amount = data['amount']
        transactionDate = data['transactionDate']
        
        transHour = get_hour(transactionDate)
        newDate = toDateTime(transactionDate)
      
        prediction_data = data
        prediction_data.pop('transactionDate', None)
        prediction_data.update({ 'hour': transHour })
                
        prediction_result = predict_model(prediction_data)
        
        storeData(prediction_result, funderAcct, benefAcct, paymentMode, amount, newDate)
        
        resultValue = checkValue(str(prediction_result))

        return jsonify({
            'status': 'success',
            'data': resultValue
            }), 200
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Value must be in integer'
            }), 400


@app.route('/api/action/<int:id>/<string:transStatus>', methods=['PATCH'])
def take_action(id, transStatus):   
    try:
        Report.confirm_fraud(id, transStatus)
        
        return jsonify({
            'status': 'success',
            'message': 'Transaction status changed'
            }), 200
    except AttributeError: 
        return jsonify({
            'status': 'error',
            'message': 'This transaction id is not available'
            }), 404


@app.route('/api/action/<int:refNo>/<string:status>', methods=['PATCH'])
def change_transaction_status(refNo, status):   
    try:
        Transaction.change_status(refNo, status)
        
        return jsonify({
            'status': 'success',
            'message': 'Transaction status changed'
            }), 200
    except AttributeError: 
        return jsonify({
            'status': 'error',
            'message': 'This transaction id is not available'
            }), 404


def updateData(_rrr, _predictionResult):
    if (_predictionResult == 1):
        _status = 'suspected'
        Transaction.update_transaction(_rrr, _status, _predictionResult)
    else:
        _status = 'normal'
        Transaction.update_transaction(_rrr, _status, _predictionResult)


def storeData(_predictionResult, _funderAcct, _benefAcct, _paymentMode, _amount, _transactionDate):
    if (_predictionResult == 1):
        _status = 'suspected'
        Report.add_report(_funderAcct, _benefAcct, _paymentMode, _amount, _predictionResult, _transactionDate, _status)
    else:
        status = 'normal'
        Report.add_report(_funderAcct, _benefAcct, _paymentMode, _amount, _predictionResult, _transactionDate, status)

def get_hour(timeString):
  x = timeString.split()[1]
  y = x.split(':')[0]
  return y

# "2020-03-03 10:30"
def toDateTime(fullDateString):
    return datetime.strptime(fullDateString, '%Y-%m-%d %H:%M')


def checkValue(data):
    if (data != "0"):
        return True
    else:
        return False
        

def predict_model(input):
    input_data = list(input.values())
    input_variables = pd.DataFrame([input_data])
    prediction = model.predict(input_variables)[0]
    result = np.int16(prediction).item()
    return result

def predict_transaction(input):
    input_data = list(input.values())
    input_variables = pd.DataFrame([input_data])
    prediction = loadedModel.predict(input_variables)[0]
    result = np.int16(prediction).item()
    return result


if __name__ == "__main__":
    app.run(debug=True)