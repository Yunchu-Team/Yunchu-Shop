from flask import render_template, url_for, flash, redirect, request, jsonify, current_app
from flask_login import login_required, current_user
from app.product import product_bp
from app.models import Product
from app.extensions import db
from app.utils.pagination import paginate

@product_bp.route('/list')
def product_list():
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    tags = request.args.get('tags')
    search_query = None
    sort_by = request.args.get('sort', 'default')
    page = request.args.get('page', 1, type=int)

    query = Product.query.filter_by(is_active=True)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if tags:
        tag_list = tags.split(',')
        for tag in tag_list:
            query = query.filter(Product.tags.like(f'%{tag}%'))

    # 搜索功能已移除

    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'sold_count':
        query = query.order_by(Product.sold_count.desc())
    elif sort_by == 'created_at':
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    pagination = paginate(query, page=page, per_page=12)

    all_tags = []
    for product in Product.query.filter_by(is_active=True).all():
        if product.tags:
            tags_list = product.tags.split(',')
            all_tags.extend(tags_list)
    tags_list = list(set(all_tags))

    return render_template('product/list.html',
                           pagination=pagination,
                           tags=tags_list,
                           min_price=min_price,
                           max_price=max_price,
                           search_query=search_query,
                           sort_by=sort_by)

@product_bp.route('/detail/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.is_active:
        flash('该商品已下架', 'warning')
        return redirect(url_for('product.product_list'))

    product.view_count += 1
    db.session.commit()

    related_products = Product.query.filter(
        Product.id != product_id,
        Product.is_active == True
    ).limit(4).all()

    return render_template('product/detail.html',
                           product=product,
                           related_products=related_products)

# 搜索功能已移除
