import sys
import time
import os
from client import ConsiditionClient
from algorithm import generate_customer_recommendations


def should_move_on_to_next_tick(response):
    return True


def generate_tick(map_obj, current_tick):
    recommendations = generate_customer_recommendations(
        map_obj, current_tick
    )
    if recommendations:
        print(f"Tick {current_tick}: Generated {len(recommendations)} "
              f"recommendations")
        # Validate recommendations before returning
        valid_recommendations = []
        seen_customer_ids = set()
        for rec in recommendations:
            customer_id = rec.get("customerId")
            charging_stops = rec.get("chargingRecommendations", [])
            
            # Skip if no customer ID
            if not customer_id:
                continue
            
            # Skip if duplicate customer ID
            if customer_id in seen_customer_ids:
                print(f"  Warning: Duplicate customer ID {customer_id} at tick {current_tick}")
                continue
            
            # Validate charging stops
            valid_stops = []
            for stop in charging_stops:
                node_id = stop.get("nodeId")
                charge_to = stop.get("chargeTo")
                
                # Validate stop
                if not node_id:
                    continue
                if charge_to is None:
                    continue
                try:
                    charge_to = float(charge_to)
                    if not (0.01 <= charge_to <= 0.95):
                        continue
                except (ValueError, TypeError):
                    continue
                
                valid_stops.append({
                    "nodeId": str(node_id),
                    "chargeTo": round(float(charge_to), 3)
                })
            
            # Only add if has valid stops
            if valid_stops:
                valid_recommendations.append({
                    "customerId": str(customer_id),
                    "chargingRecommendations": valid_stops
                })
                seen_customer_ids.add(customer_id)
            else:
                print(f"  Warning: Customer {customer_id} has no valid charging stops at tick {current_tick}")
        
        recommendations = valid_recommendations
    
    return {
        "tick": current_tick,
        "customerRecommendations": recommendations,
    }


def main():
    api_key = os.getenv("API_KEY")
    # Use localhost for local testing, or cloud API for submissions
    base_url = os.getenv("API_URL", "http://localhost:8080")
    
    # Check if we should use cloud API
    use_cloud = os.getenv("USE_CLOUD_API", "false").lower() == "true"
    if use_cloud:
        base_url = "https://api.considition.com"
        print(f"Using Cloud API: {base_url}")
    else:
        print(f"Using Local API: {base_url}")
    
    map_name = "Batterytown"

    client = ConsiditionClient(base_url, api_key)

    try:
        map_obj = client.get_map(map_name)
    except Exception as e:
        print(f"Failed to fetch map: {e}")
        sys.exit(1)

    if not map_obj:
        print("Failed to fetch map!")
        sys.exit(1)

    final_score = 0
    good_ticks = []

    current_tick = generate_tick(map_obj, 0)
    input_payload = {
        "mapName": map_name,
        "ticks": [current_tick],
    }

    total_ticks = int(map_obj.get("ticks", 0))

    for i in range(total_ticks):
        while True:
            print(f"Playing tick: {i}")
            start = time.perf_counter()
            try:
                game_response = client.post_game(input_payload)
            except Exception as e:
                print(f"Error posting game data: {e}")
                # Print payload for debugging
                import json
                print(f"\n=== DEBUG: Payload that caused error ===")
                print(json.dumps(input_payload, indent=2, default=str))
                
                # Check for common issues
                if "ticks" in input_payload:
                    for tick_data in input_payload["ticks"]:
                        recs = tick_data.get("customerRecommendations", [])
                        print(f"\nTick {tick_data.get('tick')}: {len(recs)} recommendations")
                        for rec in recs:
                            customer_id = rec.get("customerId")
                            stops = rec.get("chargingRecommendations", [])
                            print(f"  Customer {customer_id}: {len(stops)} stops")
                            for stop in stops:
                                node_id = stop.get("nodeId")
                                charge_to = stop.get("chargeTo")
                                print(f"    - Node: {node_id}, ChargeTo: {charge_to}")
                
                sys.exit(1)
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(f"Tick {i} took: {elapsed_ms:.2f}ms")

            if not game_response:
                print("Got no game response")
                sys.exit(1)

            # Sum the scores directly (assuming they are numbers)
            final_score = game_response.get("score", 0)

            if should_move_on_to_next_tick(game_response):
                good_ticks.append(current_tick)
                updated_map = game_response.get("map", map_obj) or map_obj
                current_tick = generate_tick(updated_map, i + 1)
                
                # Cloud API doesn't accept playToTick
                if use_cloud:
                    input_payload = {
                        "mapName": map_name,
                        "ticks": [*good_ticks, current_tick],
                    }
                else:
                    input_payload = {
                        "mapName": map_name,
                        "playToTick": i + 1,
                        "ticks": [*good_ticks, current_tick],
                    }
                break

            updated_map = game_response.get("map", map_obj) or map_obj
            current_tick = generate_tick(updated_map, i)
            
            # Cloud API doesn't accept playToTick
            if use_cloud:
                input_payload = {
                    "mapName": map_name,
                    "ticks": [*good_ticks, current_tick],
                }
            else:
                input_payload = {
                    "mapName": map_name,
                    "playToTick": i,
                    "ticks": [*good_ticks, current_tick],
                }

    print(f"Final score: {final_score}")


if __name__ == "__main__":
    main()
