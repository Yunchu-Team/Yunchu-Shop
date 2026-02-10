from datetime import datetime, timedelta
from app.models import EarningRecord, User
from app.extensions import db

class AffiliateCalculator:
    def __init__(self, commission_rate=0.1):
        self.commission_rate = commission_rate
    
    def calculate_commission(self, order_amount):
        """计算佣金"""
        return order_amount * self.commission_rate
    
    def create_earning_record(self, inviter_id, order_id, order_amount):
        """创建收益记录"""
        commission = self.calculate_commission(order_amount)
        
        earning_record = EarningRecord(
            user_id=inviter_id,
            source='affiliate',
            order_id=order_id,
            amount=commission,
            status='pending'
        )
        
        db.session.add(earning_record)
        
        # 更新用户的待结算余额
        user = User.query.get(inviter_id)
        if user:
            user.balance_pending += commission
        
        db.session.commit()
        
        return earning_record
    
    def settle_earnings(self, settlement_period=7):
        """结算收益"""
        # 查找达到结算周期的待结算收益
        cutoff_date = datetime.utcnow() - timedelta(days=settlement_period)
        pending_earnings = EarningRecord.query.filter(
            EarningRecord.status == 'pending',
            EarningRecord.created_at <= cutoff_date
        ).all()
        
        for earning in pending_earnings:
            # 更新收益状态
            earning.status = 'available'
            earning.settled_at = datetime.utcnow()
            
            # 更新用户余额
            user = User.query.get(earning.user_id)
            if user:
                user.balance_pending -= earning.amount
                user.balance_available += earning.amount
        
        db.session.commit()
        
        return len(pending_earnings)
    
    def process_withdrawal(self, withdrawal_request):
        """处理提现申请"""
        user = User.query.get(withdrawal_request.user_id)
        if not user:
            return False
        
        if user.balance_available < withdrawal_request.amount:
            return False
        
        # 更新用户余额
        user.balance_available -= withdrawal_request.amount
        user.total_earned += withdrawal_request.amount
        
        # 更新提现请求状态
        withdrawal_request.status = 'approved'
        
        db.session.commit()
        
        return True