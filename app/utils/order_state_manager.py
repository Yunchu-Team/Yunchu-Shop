import os
import json
from datetime import datetime

class OrderStateManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_order_state_file(self, order_id):
        return os.path.join(self.data_dir, f"order_{order_id}.json")
    
    def create_initial_state(self, order_id, user_id, items, customer=None, order_no=None):
        state = {
            "order_id": order_id,
            "order_no": order_no,
            "user_id": user_id,
            "status": "pending_payment",
            "items": items,
            "customer": customer or {},
            "created_at": datetime.utcnow().isoformat(),
            "history": [{
                "status": "pending_payment",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "订单创建"
            }],
            "assigned_cdkey": None
        }
        
        with open(self.get_order_state_file(order_id), 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        return state
    
    def get_order_state(self, order_id):
        file_path = self.get_order_state_file(order_id)
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_state(self, order_id, new_status, message=None):
        state = self.get_order_state(order_id)
        if not state:
            return None
        
        state["status"] = new_status
        state["history"].append({
            "status": new_status,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message or f"状态更新为{new_status}"
        })
        
        with open(self.get_order_state_file(order_id), 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        return state
    
    def assign_cdkey(self, order_id, cdkeys):
        state = self.get_order_state(order_id)
        if not state:
            return None

        if isinstance(cdkeys, list):
            state["assigned_cdkey"] = cdkeys
        else:
            state["assigned_cdkey"] = cdkeys
        
        with open(self.get_order_state_file(order_id), 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        return state
