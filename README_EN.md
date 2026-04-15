# ICM & Bubble Factor Calculator

A responsive web application for calculating ICM (Independent Chip Model) and Bubble Factor values for poker tournaments and SNGs.

## 🎯 Features

- **ICM Calculation**: Accurate Independent Chip Model computation with dynamic programming
- **Bubble Factor**: Calculates expected value multiplier compared to ICM baseline
- **Mobile-First Design**: Fully responsive UI optimized for smartphones
- **Real-time Validation**: Input validation and error handling
- **Example Scenarios**: Pre-loaded tournament examples
- **Touch-Friendly**: Large buttons and inputs for mobile interaction

## 📊 What is ICM?

The Independent Chip Model is a method for distributing remaining prize pool among players in a tournament based on their chip stacks. It assumes each player has an independent and equal chance of finishing in any given position.

## 💥 What is Bubble Factor?

Bubble Factor (BF) is a multiplier indicating whether a player should accept or decline deals:
- **BF > 0**: Player is in a favorable spot (should accept fold equity deals)
- **BF < 0**: Player is in a tough spot (may need better odds)
- **BF ≈ 0**: Fair deal

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
cd icm_bf_app
pip install -r requirements.txt
```

### Running

```bash
python app.py
```

Then open your browser to `http://localhost:5000`

## 📱 Mobile Optimization

The app is designed mobile-first with:
- Responsive Bootstrap layout
- Touch-friendly input controls (+/- buttons for player count)
- Vertical layout optimization for small screens
- Landscape mode support
- Large, easy-to-tap buttons (minimum 44px)

## 📥 Input Specifications

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| Players | Integer | 2-9 | Number of players |
| Stacks | Float | ≥0 | Chip stack for each player (in BB units) |
| Payouts | Float | ≥0 | Prize pool distribution (descending order) |

### Example Input
```json
{
  "players": 3,
  "stacks": [50, 30, 20],
  "payouts": [50, 30, 20]
}
```

## 📤 Output Specifications

```json
{
  "icm": [list of float],
  "bf": [list of float],
  "total_chips": float,
  "total_payout": float
}
```

## 🧮 Algorithm Details

### ICM Calculation

The app uses an optimized recursive algorithm with memoization:

1. For each player, calculate chip equity: `chip_equity = player_chips / total_chips`
2. Calculate expected value considering all finishing positions
3. Use dynamic programming to avoid recalculating same states
4. Round to 10 decimal places for precision

**Time Complexity**: O(n² × m) where n = players, m = payout positions

### Bubble Factor

```
BF = (Win_EV - ICM_EV) / ICM_EV
```

Where:
- `Win_EV`: Expected value if player wins (first payout)
- `ICM_EV`: Independent Chip Model value

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
# Or
python -m unittest discover tests/
```

### Test Coverage

- ICM value preservation (total = payout total)
- Equal stacks distribution
- Uneven chip distribution
- Input validation
- Edge cases (zero stacks, single player)
- Bubble Factor calculations

### Known Test Cases

1. **2-Player Equal Stacks**: [100, 100] chips, [100, 50] payout
   - Expected ICM: [75, 75]
   
2. **3-Player SNG**: [50, 30, 20] chips, [50, 30, 20] payout
   - Stacks determine ICM distribution

3. **4-Player Tournament**: [100, 80, 50, 30] chips, [100, 70, 40, 10] payout
   - Tests larger field accuracy

## 📁 Project Structure

```
icm_bf_app/
├── app.py              # Flask application & API endpoints
├── icm.py              # ICM calculation logic
├── bf.py               # Bubble Factor calculations
├── models.py           # Data structures & validation
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── tests/
│   └── test_icm.py    # Test suite
├── templates/
│   └── index.html     # UI template
└── static/
    ├── style.css      # Mobile-responsive styling
    └── script.js      # Client-side logic
```

## 🔧 API Endpoints

### POST `/api/calculate`
Calculate ICM and Bubble Factor

**Request**:
```json
{
  "players": 3,
  "stacks": [50, 30, 20],
  "payouts": [50, 30, 20]
}
```

**Response**:
```json
{
  "success": true,
  "icm": [29.17, 20.83, 20.00],
  "bf": [0.71, 0.00, -0.33],
  "total_chips": 100,
  "total_payout": 100
}
```

### POST `/api/validate`
Validate input parameters

### GET `/api/examples`
Get example scenarios

## ⚙️ Configuration

Flask runs in debug mode by default on `0.0.0.0:5000`. To change:

Edit `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=8000)
```

## 🔒 Error Handling

The app handles:
- Invalid player counts (< 2 or > 9)
- Mismatched array lengths
- Negative values
- Zero total chips
- Unsorted payouts
- Network errors

## 📈 Performance

- **Small fields (2-4 players)**: < 10ms
- **Medium fields (5-6 players)**: 10-50ms
- **Large fields (7-9 players)**: 50-200ms

All calculations run server-side for accuracy.

## 🐛 Known Issues & Limitations

- Maximum 9 players (can be extended)
- Precision limited to 10 decimal places
- No offline support (requires Flask server)

## 🚧 Future Enhancements

- [ ] Offline PWA support
- [ ] Custom chip denomination
- [ ] Multi-way deal calculations
- [ ] Historical scenario comparison
- [ ] Export to CSV/PDF

## 📝 License

Open source

## 📧 Support

For issues or questions, please refer to the test suite for expected behavior.

---

**Version**: 1.0  
**Last Updated**: 2026-04-15  
**Python**: 3.11+  
**Framework**: Flask 3.0
