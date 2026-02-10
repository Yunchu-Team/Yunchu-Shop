// 购物车逻辑（以服务端为准）

class CartManager {
    constructor() {
        this.initEvents();
        this.refreshCartCount();
    }

    refreshCartCount() {
        fetch('/order/cart/count', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateCartBadge(data.cart_count || 0);
            }
        })
        .catch(() => {});
    }

    updateCartBadge(count) {
        const cartBadge = document.querySelector('.cart-badge');
        if (!cartBadge) return;
        if (count > 0) {
            cartBadge.textContent = count;
            cartBadge.classList.remove('d-none');
        } else {
            cartBadge.classList.add('d-none');
        }
    }

    addToCart(productId, quantity = 1, redirectToCheckout = false) {
        this.syncWithBackend('add', productId, quantity)
            .then(data => {
                if (data.success) {
                    this.updateCartBadge(data.cart_count || 0);
                    this.showSuccessMessage(data.message || '商品已添加到购物车');
                    if (redirectToCheckout) {
                        window.location.href = '/order/checkout';
                    }
                } else {
                    if (typeof showNotice === 'function') {
                        showNotice(data.message || '添加失败', 'warning');
                    }
                }
            });
    }

    removeFromCart(productId) {
        this.syncWithBackend('remove', productId)
            .then(data => {
                if (data.success) {
                    this.updateCartBadge(data.cart_count || 0);
                    this.updateCartTotals(data.total);
                    if (window.location.pathname.includes('/cart')) {
                        location.reload();
                    }
                } else {
                    if (typeof showNotice === 'function') {
                        showNotice(data.message || '移除失败', 'warning');
                    }
                }
            });
    }

    updateQuantity(productId, quantity) {
        if (quantity <= 0) {
            this.removeFromCart(productId);
            return;
        }

        this.syncWithBackend('update', productId, quantity)
            .then(data => {
                if (data.success) {
                    this.updateCartBadge(data.cart_count || 0);
                    this.updateCartTotals(data.total);
                } else {
                    if (typeof showNotice === 'function') {
                        showNotice(data.message || '更新失败', 'warning');
                    }
                }
            });
    }

    clearCart() {
        this.syncWithBackend('clear')
            .then(data => {
                if (data.success) {
                    this.updateCartBadge(0);
                    if (window.location.pathname.includes('/cart')) {
                        location.reload();
                    }
                } else {
                    if (typeof showNotice === 'function') {
                        showNotice(data.message || '清空失败', 'warning');
                    }
                }
            });
    }

    updateCartTotals(total) {
        if (typeof total !== 'number') return;
        const totalEl = document.getElementById('cart-total');
        const finalEl = document.getElementById('cart-total-final');
        if (totalEl) totalEl.textContent = `¥${total.toFixed(2)}`;
        if (finalEl) finalEl.textContent = `¥${total.toFixed(2)}`;
    }

    syncWithBackend(action, productId = null, quantity = null) {
        const url = `/order/cart/${action}`;
        const token = typeof getCsrfToken === 'function' ? getCsrfToken() : '';

        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': token
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .catch(() => ({ success: false, message: '网络错误' }));
    }

    showSuccessMessage(message) {
        if (typeof showToast === 'function') {
            showToast(message, 'success');
        } else {
            if (typeof showNotice === 'function') {
                showNotice(message, 'success');
            }
        }
    }

    initEvents() {
        this.bindAddToCartButtons();

        if (window.location.pathname.includes('/cart')) {
            document.querySelectorAll('.update-quantity-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const productId = parseInt(btn.dataset.productId);
                    const quantityInput = document.querySelector(`.quantity-input[data-product-id="${productId}"]`);
                    const quantity = parseInt(quantityInput.value);
                    this.updateQuantity(productId, quantity);
                });
            });

            document.querySelectorAll('.remove-from-cart-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const productId = parseInt(btn.dataset.productId);
                    this.removeFromCart(productId);
                });
            });

            const clearCartBtn = document.querySelector('.clear-cart-btn');
            if (clearCartBtn) {
                clearCartBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (confirm('确定要清空购物车吗？')) {
                        this.clearCart();
                    }
                });
            }
        }
    }

    bindAddToCartButtons() {
        document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
            if (btn.dataset.bound === '1') return;
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const productId = parseInt(btn.dataset.productId);
                const quantity = parseInt(btn.dataset.quantity || 1);
                this.addToCart(productId, quantity);
            });
            btn.dataset.bound = '1';
        });
    }
}

window.addEventListener('DOMContentLoaded', function() {
    window.cartManager = new CartManager();
});
