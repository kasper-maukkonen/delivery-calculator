from flask import Flask, request, jsonify
from datetime import datetime, time

app = Flask(__name__)

# Delivery fee calculation logic
def calculate_delivery_fee(cart_value, num_items, delivery_distance, order_time):
    SMALL_ORDER_SURCHARGE_THRESHOLD = 10
    SMALL_ORDER_SURCHARGE_RATE = 1.0  # (per Euro)
    BASE_DELIVERY_FEE = 2
    ADDITIONAL_DISTANCE_RATE = 1.0  # (per 500 meters)
    ITEM_SURCHARGE_THRESHOLD = 5
    ITEM_SURCHARGE_RATE = 0.5  # (per item)
    BULK_ITEM_THRESHOLD = 12
    BULK_ITEM_SURCHARGE = 1.2
    MAX_DELIVERY_FEE = 15
    FREE_DELIVERY_THRESHOLD = 200
    RUSH_HOUR_START = time(15, 0)  # 3 PM UTC
    RUSH_HOUR_END = time(19, 0)    # 7 PM UTC

   
    small_order_surcharge = max(0, SMALL_ORDER_SURCHARGE_THRESHOLD - cart_value) * SMALL_ORDER_SURCHARGE_RATE

   
    distance_fee = BASE_DELIVERY_FEE
    if delivery_distance > 1000:
        additional_distance = delivery_distance - 1000
        distance_fee += ((additional_distance // 500) + 1) * ADDITIONAL_DISTANCE_RATE

   
    item_surcharge = max(0, num_items - ITEM_SURCHARGE_THRESHOLD) * ITEM_SURCHARGE_RATE

    
    if num_items > BULK_ITEM_THRESHOLD:
        item_surcharge += (num_items - BULK_ITEM_THRESHOLD) * BULK_ITEM_SURCHARGE

    
    total_fee = distance_fee + small_order_surcharge + item_surcharge

    
    if (
        order_time.weekday() == 4  # Friday
        and RUSH_HOUR_START <= order_time.time() <= RUSH_HOUR_END
    ):
        total_fee *= 1.2

    
    total_fee = min(total_fee, MAX_DELIVERY_FEE)

   
    if cart_value >= FREE_DELIVERY_THRESHOLD:
        return 0

    return total_fee

@app.route('/calculate_delivery_fee', methods=['POST'])

def calculate_fee():
    try:
        data = request.get_json()
        cart_value = data['cart_value']
        num_items = data['num_items']
        delivery_distance = data['delivery_distance']
        order_time = datetime.fromisoformat(data['order_time'])

        # Call the calculate_delivery_fee
        delivery_fee = calculate_delivery_fee(cart_value, num_items, delivery_distance, order_time)
        return jsonify({'delivery_fee': delivery_fee})
    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Return an error response with a 400 Bad Request status

if __name__ == '__main__':
    app.run(debug=True)