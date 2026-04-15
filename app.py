"""Main Flask application"""
import os
from flask import Flask, render_template, request, jsonify
from models import CalculationInput, CalculationOutput
from icm import calculate_icm
from bf import calculate_bubble_factor
from utils import parse_input

app = Flask(__name__)

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API endpoint for calculations"""
    try:
        data = request.json
        
        players = int(data.get('players', 2))
        stacks = [float(x) for x in data.get('stacks', [1, 1])]
        payouts = [float(x) for x in data.get('payouts', [1, 0])]
        
        # Validate input
        calc_input = CalculationInput(players=players, stacks=stacks, payouts=payouts)
        is_valid, error_msg = calc_input.validate()
        
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Calculate ICM and BF
        icm_values = calculate_icm(stacks, payouts)
        bf_values = calculate_bubble_factor(stacks, payouts)
        
        # Return results
        return jsonify({
            'success': True,
            'icm': icm_values,
            'bf': bf_values,
            'total_chips': sum(stacks),
            'total_payout': sum(payouts)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate():
    """Validate input parameters"""
    try:
        data = request.json
        
        players = int(data.get('players', 2))
        stacks_count = len(data.get('stacks', []))
        payouts_count = len(data.get('payouts', []))
        
        errors = []
        
        if players < 2 or players > 9:
            errors.append("Players must be between 2 and 9")
        
        if stacks_count != players:
            errors.append(f"Expected {players} stacks, got {stacks_count}")
        
        if payouts_count != players:
            errors.append(f"Expected {players} payouts, got {payouts_count}")
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors
        })
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [str(e)]
        })

@app.route('/api/examples', methods=['GET'])
def examples():
    """Get example scenarios"""
    examples = [
        {
            'name': '3-Player SNG',
            'players': 3,
            'stacks': [50, 30, 20],
            'payouts': [50, 30, 20]
        },
        {
            'name': '4-Player Tournament',
            'players': 4,
            'stacks': [100, 80, 50, 30],
            'payouts': [100, 70, 40, 10]
        },
        {
            'name': 'Equal Stacks',
            'players': 3,
            'stacks': [100, 100, 100],
            'payouts': [150, 100, 50]
        }
    ]
    
    return jsonify(examples)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
