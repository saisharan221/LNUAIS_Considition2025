#!/usr/bin/env python3
"""
Analyze if customer actually needs charging
"""
import sys
import os
from client import ConsiditionClient
import heapq

def dijkstra(graph, start, end):
    """Calculate shortest path distance"""
    if start == end:
        return 0
    
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
        visited.add(current_node)
        
        if current_node == end:
            return current_dist
        
        for neighbor in graph.get(current_node, []):
            neighbor_node = neighbor["to"]
            edge_dist = neighbor["distance"]
            new_dist = current_dist + edge_dist
            
            if new_dist < distances[neighbor_node]:
                distances[neighbor_node] = new_dist
                heapq.heappush(pq, (new_dist, neighbor_node))
    
    return distances[end] if distances[end] != float('inf') else None

def main():
    client = ConsiditionClient("http://localhost:8080", os.getenv("API_KEY"))
    map_obj = client.get_map("Turbohill")
    
    # Build graph
    graph = {}
    for edge in map_obj['edges']:
        from_node = edge['fromNode']
        if from_node not in graph:
            graph[from_node] = []
        graph[from_node].append({
            "to": edge['toNode'],
            "distance": edge['length']
        })
    
    # Find customer 0.11
    customer = None
    for node in map_obj['nodes']:
        for c in node.get('customers', []):
            if c['id'] == '0.11':
                customer = c
                break
    
    # Calculate energy needs
    from_node = customer['fromNode']
    to_node = customer['toNode']
    current_charge_pct = customer['chargeRemaining']
    max_charge_kwh = customer['maxCharge']
    consumption = customer['energyConsumptionPerKm']
    
    current_charge_kwh = current_charge_pct * max_charge_kwh
    
    # Distance
    distance = dijkstra(graph, from_node, to_node)
    energy_needed = distance * consumption
    
    print(f"Customer 0.11 Analysis:")
    print(f"  Route: {from_node} -> {to_node}")
    print(f"  Distance: {distance:.2f} km")
    print(f"  Current charge: {current_charge_kwh:.2f} kWh ({current_charge_pct:.1%})")
    print(f"  Max charge: {max_charge_kwh} kWh")
    print(f"  Consumption: {consumption} kWh/km")
    print(f"  Energy needed: {energy_needed:.2f} kWh")
    print(f"  Energy surplus/deficit: {current_charge_kwh - energy_needed:.2f} kWh")
    print()
    
    if current_charge_kwh >= energy_needed:
        print("✅ Customer HAS ENOUGH battery to reach destination WITHOUT charging!")
        print("   Maybe game ignores recommendations for customers who don't need them?")
    else:
        print("❌ Customer NEEDS to charge to reach destination")

if __name__ == "__main__":
    main()

