#!/usr/bin/env python3
"""
Test a single customer to debug charging behavior
"""
import sys
import os
from client import ConsiditionClient

def main():
    base_url = "http://localhost:8080"
    map_name = "Turbohill"
    api_key = os.getenv("API_KEY")
    
    client = ConsiditionClient(base_url, api_key)
    
    # Get map
    map_obj = client.get_map(map_name)
    print("Map loaded successfully\n")
    
    # Find customer 0.11 (departs tick 15)
    customer_0_11 = None
    for node in map_obj['nodes']:
        for customer in node.get('customers', []):
            if customer['id'] == '0.11':
                customer_0_11 = customer
                break
    
    if not customer_0_11:
        print("Customer 0.11 not found!")
        return
    
    print(f"Customer 0.11:")
    print(f"  From: {customer_0_11['fromNode']} -> To: {customer_0_11['toNode']}")
    print(f"  Departure: tick {customer_0_11['departureTick']}")
    print(f"  Charge: {customer_0_11['chargeRemaining']:.2%} of {customer_0_11['maxCharge']} kWh")
    print(f"  Type: {customer_0_11['type']}, Persona: {customer_0_11['persona']}")
    print()
    
    # Send recommendation on tick 0 (BEFORE departure!)
    recommendation = {
        'customerId': '0.11',
        'chargingStation': '5.3',
        'chargeTo': 1.0
    }
    
    print(f"Sending recommendation at tick 0 (before departure): {recommendation}\n")
    
    # Play game
    input_payload = {
        "mapName": map_name,
        "ticks": [
            {"tick": 0, "customerRecommendations": [recommendation]}
        ]
    }
    
    response = client.post_game(input_payload)
    
    # Check response
    print(f"Response score: {response.get('score', 0)}")
    print(f"KWH Revenue: {response.get('kwhRevenue', 0)}")
    print(f"Customer Completion Score: {response.get('customerCompletionScore', 0)}\n")
    
    # Find customer 0.11 in logs
    customer_logs = response.get('customerLogs', [])
    for log in customer_logs:
        if log['customerId'] == '0.11':
            print(f"Customer 0.11 log entries: {len(log['logs'])}")
            print("\nAll log entries:")
            for i, entry in enumerate(log['logs']):
                state = entry.get('state')
                # Print all entries, highlight charging-related ones
                marker = "🔋" if state in ['Charging', 'WaitingForCharger', 'DoneCharging'] else "  "
                print(f"{marker} {i:2d}: Tick {entry.get('tick'):3d}, State: {state:20s}, "
                      f"Node: {str(entry.get('node')):6s}, Edge: {str(entry.get('edge')):15s}, "
                      f"Charge: {entry.get('chargeRemaining', 0):.3f}")
            break

if __name__ == "__main__":
    main()

