from sqlalchemy import text

def _is_sqlite(db):
    return db.engine.dialect.name == 'sqlite'

def _table_exists(db, table_name):
    result = db.session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name},
    ).fetchone()
    return result is not None

def _get_columns(db, table_name):
    rows = db.session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    return {row[1] for row in rows}

def _add_column(db, table_name, column_def):
    db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_def}"))

def ensure_sqlite_schema(db):
    """
    启动时自动检查并修复SQLite缺失列/表。
    仅在SQLite下执行，避免影响其他数据库。
    """
    if not _is_sqlite(db):
        return

    # 先创建缺失表（不会影响已有表）
    db.create_all()

    # 修复折扣码缺失 created_at
    if _table_exists(db, 'discount_code'):
        columns = _get_columns(db, 'discount_code')
        if 'created_at' not in columns:
            _add_column(db, 'discount_code', 'created_at DATETIME')
            # 尽量用 valid_from 兜底
            db.session.execute(text(
                "UPDATE discount_code SET created_at = COALESCE(valid_from, CURRENT_TIMESTAMP)"
            ))

    # 修复订单表缺失 order_no
    if _table_exists(db, 'order_core'):
        columns = _get_columns(db, 'order_core')
        if 'order_no' not in columns:
            _add_column(db, 'order_core', 'order_no VARCHAR(6)')
            db.session.execute(text(
                "UPDATE order_core SET order_no = printf('%06d', id) WHERE order_no IS NULL OR order_no = ''"
            ))

    # 修复站点设置表缺失字段（早期版本可能无此表或列）
    if _table_exists(db, 'site_setting'):
        columns = _get_columns(db, 'site_setting')
        expected = {
            'site_name': "site_name VARCHAR(100)",
            'site_logo': "site_logo VARCHAR(200)",
            'footer_text': "footer_text VARCHAR(200)",
            'contact_email': "contact_email VARCHAR(120)",
            'wechat_qr': "wechat_qr VARCHAR(200)",
            'alipay_qr': "alipay_qr VARCHAR(200)",
            'bank_qr': "bank_qr VARCHAR(200)",
            'updated_at': "updated_at DATETIME",
            'gh_repo': "gh_repo VARCHAR(200)",
            'gh_branch': "gh_branch VARCHAR(100)",
            'gh_token_enc': "gh_token_enc TEXT",
            'about_us': "about_us TEXT",
            'quick_links': "quick_links TEXT",
            'bank_label': "bank_label VARCHAR(50)",
        }
        for col, col_def in expected.items():
            if col not in columns:
                _add_column(db, 'site_setting', col_def)

    db.session.commit()
