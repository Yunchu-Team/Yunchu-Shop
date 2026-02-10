from flask import request, url_for

class Pagination:
    def __init__(self, page, per_page, total, items):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items
    
    @property
    def pages(self):
        """总页数"""
        return (self.total + self.per_page - 1) // self.per_page
    
    @property
    def has_prev(self):
        """是否有上一页"""
        return self.page > 1
    
    @property
    def has_next(self):
        """是否有下一页"""
        return self.page < self.pages
    
    def prev(self, error_out=False):
        """上一页的页码"""
        if not self.has_prev:
            return None
        return self.page - 1
    
    def next(self, error_out=False):
        """下一页的页码"""
        if not self.has_next:
            return None
        return self.page + 1
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """生成页码列表"""
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
    
    def get_url(self, page):
        """获取指定页码的URL"""
        args = request.args.copy()
        args['page'] = page
        return url_for(request.endpoint, **args)


def paginate(query, page=None, per_page=None, error_out=True):
    """分页查询"""
    if page is None:
        page = request.args.get('page', 1, type=int)
    
    if per_page is None:
        per_page = request.args.get('per_page', 20, type=int)
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    if error_out and page < 1:
        page = 1
    
    return Pagination(page, per_page, total, items)