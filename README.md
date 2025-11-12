# Considition 2025 - EV Charging Optimization Solution

## ✅ Optimized Solution - Leaderboard Ready!

**Current Performance (Local Docker):**
- **Turbohill:** 2,482 points (28% of leader)
- **Clutchfield:** 13,423 points (33% of leader) 
- **Batterytown:** 14,936 points (35% of leader)

This solution provides **aggressive** EV charging recommendations optimized for maximum KWH revenue.

## 🚀 Quick Start

### Local Testing (Docker)
```bash
# Set your API key
export API_KEY="your-api-key-here"

# Run the solution
python app.py
```

### Cloud Testing
```bash
export API_KEY="your-api-key-here"
export USE_CLOUD_API="true"

python app.py
```

## 📂 Project Structure

- **`app.py`** - Main game loop and API integration
- **`algorithm.py`** - Core charging recommendation algorithm
- **`client.py`** - API client wrapper
- **`requirements.txt`** - Python dependencies
- **`data_structures.md`** - Documentation of map/game data structures

## 🧠 Algorithm Overview

### Core Strategy: **AGGRESSIVE CHARGING**

1. **Customer Analysis**: Identifies ALL customers departing at each tick
2. **AGGRESSIVE Charging Policy**: Charges customers with less than 200% of needed energy
3. **Reachability-First Station Selection**: 
   - ✅ Checks if station is reachable with current battery
   - Minimizes detours (but tolerant for KWH revenue)
   - Considers persona preferences
   - Prioritizes station availability
   - Favors green energy zones
4. **Maximum Charge Optimization**:
   - Charges to **95-99%** when stopping (maximize KWH!)
   - 200% safety margin on energy calculations
   - Never recommends unreachable stations

### Persona-Based Scoring

- **Stressed**: Minimizes detours, prefers fast chargers
- **CostSensitive**: Prioritizes green/cheap energy, moderate detour tolerance
- **EcoConscious**: Strongly prefers green energy (Hydro/Nuclear/Solar/Wind)
- **DislikesDriving**: Heavily penalizes detours
- **Neutral**: Balanced approach

### Key Features

- ✅ **Correct API Format**: Uses `chargingRecommendations` array with `nodeId`
- ✅ **State Persistence**: Maintains customer tracking across all ticks
- ✅ **Route Validation**: Ensures customers can reach recommended stations
- ✅ **Dijkstra Pathfinding**: Optimal route calculation
- ✅ **Smart Charging Logic**: Balances safety margin vs. over-charging

## 📊 Current Performance

### Local Docker Results

| Map | Score | Customer | KWH | % of Leader |
|-----|-------|----------|-----|-------------|
| **Turbohill** | 2,482 | 874 | 1,608 | 28% |
| **Clutchfield** | 13,423 | 6,030 | 7,393 | 33% |
| **Batterytown** | 14,936 | 7,712 | 5,240 | 35% |

### Key Insights
- ✅ Stable performance across all maps
- ✅ Balanced customer completion + KWH revenue
- ✅ ~70% customer coverage (charges 139/200 customers)
- ⚠️ Top teams achieve 38k-43k KWH (we're at 5k-7k)
- 💡 Room for improvement: multi-stop charging, better pricing

## 🔧 Configuration

### Environment Variables

- `API_KEY` (required): Your Considition API key
- `API_URL` (optional): Override API URL (default: `http://localhost:8080`)
- `USE_CLOUD_API` (optional): Set to `"true"` for cloud submissions

### Tuning Parameters (AGGRESSIVE MODE)

Located in `algorithm.py`:

```python
# Line ~160: AGGRESSIVE charging threshold
return current_charge_kwh < (energy_needed * 2.0)  # Charge at 200% threshold!

# Line ~523: AGGRESSIVE charge target margin  
target_charge_kwh = charge_at_station + (energy_from_station * 2.0)  # 200% extra!

# Line ~527: HIGH minimum charge when stopping
min_charge_kwh = max_charge_kwh * 0.95  # 95% minimum (maximize KWH!)

# Line ~537: Maximum charge cap
target_charge_fraction = max(0.85, min(0.99, target_charge_fraction))  # 99% max!

# Line ~96: Charge EVERYONE (no needs_charging check)
# ULTRA-AGGRESSIVE: Skip needs assessment entirely
```

## 🐛 Known Issues & Workarounds

### Docker Cache Issue
If recommendations are ignored, disable cache:
```bash
CACHE_ENABLED=false docker run -p 8080:8080 considition/considition2025
```

### API Format Gotchas
- ✅ Use `chargingRecommendations` (array), not `chargingStation`
- ✅ Use `nodeId`, not `chargingStation`
- ✅ Avoid `chargeTo: 0` or `chargeTo: 1` (use 0.01-0.95 range)

## 📈 Next Optimizations (To Reach Top 3)

### High Priority
1. **Multi-stop charging** ⭐⭐⭐
   - Charge at multiple stations per route
   - Top teams likely using this (explains 38k-43k KWH!)
   - Format: `chargingRecommendations: [{nodeId: "5.3", chargeTo: 0.9}, {nodeId: "6.2", chargeTo: 0.95}]`

2. **Sacrifice customer completion for KWH** ⭐⭐⭐
   - Top teams have 0-16k customer completion vs 38k-43k KWH
   - Try: Recommend longer detours, more charging stops
   - Focus on maximizing KWH volume over completion rate

3. **Dynamic pricing/time-based optimization** ⭐⭐
   - Exploit peak/off-peak energy pricing
   - Charge when energy is expensive
   - Consider time-of-day in zone energy calculations

### Medium Priority
4. **Better green zone utilization** ⭐
   - Prioritize charging in expensive energy zones
   - Weight stations by energy source cost
   
5. **Predictive charger availability**
   - Model future charger congestion
   - Recommend less-crowded stations

### Low Priority
6. **Machine learning**: Learn optimal thresholds per map/persona
7. **Weather integration**: Adjust for solar/wind production patterns

## 🧪 Testing

```bash
# Quick test
python app.py

# Verbose test (uncomment debug lines in app.py)
# Shows recommendations per tick and charging activity
```

## 📝 Notes

- Algorithm runs at ~23-25ms per tick (fast!)
- State persists across ticks (no duplicate recommendations)
- Only recommends charging when needed (conservative approach)
- Validated against actual game logs

## 🤝 Credits

Developed for Considition 2025 by LNU AIS Team

