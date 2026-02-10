// 全局函数

// 日夜模式切换
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    
    // 检查本地存储中的主题偏好
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        html.setAttribute('data-theme', savedTheme);
    } else {
        // 默认根据系统偏好设置主题
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        html.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }
    
    // 主题切换按钮点击事件
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

// 购物车数量更新
function updateCartCount() {
    fetch('/order/cart/count', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const cartBadge = document.querySelector('.cart-badge');
        if (!cartBadge) return;
        const cartCount = data.cart_count || 0;
        if (cartCount > 0) {
            cartBadge.textContent = cartCount;
            cartBadge.classList.remove('d-none');
        } else {
            cartBadge.classList.add('d-none');
        }
    })
    .catch(() => {});
}

// 表单验证
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    });
}

// 获取CSRF令牌
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

// 自动为POST表单注入CSRF令牌
function attachCsrfToForms() {
    const token = getCsrfToken();
    if (!token) return;
    document.querySelectorAll('form').forEach(form => {
        const method = (form.getAttribute('method') || 'GET').toUpperCase();
        if (method !== 'POST') return;
        if (form.querySelector('input[name="csrf_token"]')) return;
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrf_token';
        input.value = token;
        form.appendChild(input);
    });
}

// 加载动画
function showLoading(target = 'body') {
    const loadingHtml = `
        <div class="loading-overlay">
            <div class="loading-spinner"></div>
        </div>
    `;
    
    const styleHtml = `
        <style>
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(255, 255, 255, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }
            
            [data-theme="dark"] .loading-overlay {
                background-color: rgba(33, 37, 41, 0.8);
            }
            
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid var(--accent-primary, #007bff);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    
    if (!document.querySelector('.loading-overlay')) {
        document.head.insertAdjacentHTML('beforeend', styleHtml);
        document.querySelector(target).insertAdjacentHTML('beforeend', loadingHtml);
    }
}

function hideLoading() {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// 通知消息
function showToast(message, type = 'info') {
    showNotice(message, type);
}

// 网页内输入框
function showInputDialog(title, placeholder = '', defaultValue = '') {
    return new Promise((resolve) => {
        let container = document.getElementById('dialog-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'dialog-container';
            document.body.appendChild(container);

            const style = document.createElement('style');
            style.textContent = `
                #dialog-container {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 99999;
                    background-color: rgba(0, 0, 0, 0.5);
                }
                .input-dialog {
                    background: #ffffff;
                    border-radius: 16px;
                    padding: 24px;
                    min-width: 400px;
                    max-width: 600px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
                    border: 1px solid #f0f0f0;
                }
                .input-dialog h5 {
                    margin-bottom: 16px;
                    color: #2c3e50;
                    font-weight: 600;
                }
                .input-dialog textarea {
                    width: 100%;
                    min-height: 100px;
                    border-radius: 10px;
                    border: 1.5px solid #cfd3d8;
                    padding: 12px;
                    font-size: 14px;
                    resize: vertical;
                }
                .input-dialog textarea:focus {
                    border-color: #9aa2ab;
                    outline: none;
                }
                .input-dialog .dialog-buttons {
                    display: flex;
                    justify-content: flex-end;
                    gap: 12px;
                    margin-top: 16px;
                }
                .input-dialog .btn {
                    border-radius: 10px;
                    padding: 8px 16px;
                }
            `;
            document.head.appendChild(style);
        }

        const dialog = document.createElement('div');
        dialog.className = 'input-dialog';
        dialog.innerHTML = `
            <h5>${title}</h5>
            <textarea placeholder="${placeholder}">${defaultValue}</textarea>
            <div class="dialog-buttons">
                <button class="btn btn-outline-secondary" id="dialog-cancel">取消</button>
                <button class="btn btn-primary" id="dialog-confirm">确定</button>
            </div>
        `;
        
        container.appendChild(dialog);
        
        const textarea = dialog.querySelector('textarea');
        textarea.focus();
        
        const cancelBtn = dialog.querySelector('#dialog-cancel');
        const confirmBtn = dialog.querySelector('#dialog-confirm');
        
        const cleanup = () => {
            dialog.remove();
            if (container.children.length === 0) {
                container.remove();
            }
        };
        
        cancelBtn.addEventListener('click', () => {
            cleanup();
            resolve(null);
        });
        
        confirmBtn.addEventListener('click', () => {
            const value = textarea.value.trim();
            cleanup();
            resolve(value);
        });
        
        // 点击背景关闭
        container.addEventListener('click', (e) => {
            if (e.target === container) {
                cleanup();
                resolve(null);
            }
        });
        
        // ESC键关闭
        const handleKeydown = (e) => {
            if (e.key === 'Escape') {
                cleanup();
                resolve(null);
                document.removeEventListener('keydown', handleKeydown);
            }
        };
        document.addEventListener('keydown', handleKeydown);
    });
}

// 页面内提示框（非弹窗）
function showNotice(message, type = 'info') {
    let container = document.getElementById('notice-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notice-container';
        document.body.appendChild(container);

        const style = document.createElement('style');
        style.textContent = `
            #notice-container {
                position: fixed;
                top: 16px;
                right: 16px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                z-index: 9999;
                pointer-events: none;
            }
            .notice-item {
                min-width: 260px;
                max-width: 360px;
                padding: 12px 16px;
                border-radius: 12px;
                background: #ffffff;
                border: 1px solid #e0e0e0;
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
                color: #2c3e50;
                animation: noticeSlideIn 0.25s ease, noticeFadeOut 0.25s ease 2.75s forwards;
                pointer-events: auto;
            }
            .notice-item.success { border-color: #b7eb8f; color: #389e0d; }
            .notice-item.warning { border-color: #ffe7ba; color: #ad6800; }
            .notice-item.danger { border-color: #ffa39e; color: #cf1322; }
            .notice-item.info { border-color: #91d5ff; color: #096dd9; }
            @keyframes noticeSlideIn {
                from { transform: translateX(20px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes noticeFadeOut {
                to { opacity: 0; transform: translateX(20px); }
            }
        `;
        document.head.appendChild(style);
    }

    const item = document.createElement('div');
    item.className = `notice-item ${type}`;
    item.textContent = message;
    container.appendChild(item);

    setTimeout(() => {
        item.remove();
    }, 3200);
}

// 数字格式化
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 价格格式化
function formatPrice(price) {
    return '¥' + formatNumber(parseFloat(price).toFixed(2));
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 平滑滚动
function smoothScrollTo(element, offset = 0) {
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
    const offsetPosition = elementPosition - offset;
    
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text).then(() => {
            showToast('复制成功', 'success');
            return true;
        }).catch(err => {
            showToast('复制失败', 'danger');
            return false;
        });
    } else {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showToast('复制成功', 'success');
            return true;
        } catch (err) {
            showToast('复制失败', 'danger');
            return false;
        } finally {
            document.body.removeChild(textArea);
        }
    }
}

// 检查元素是否在视口中
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// 图片懒加载
function initLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => {
        imageObserver.observe(img);
    });
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    initThemeToggle();
    updateCartCount();
    initFormValidation();
    initLazyLoading();
    attachCsrfToForms();
    
    // 其他初始化代码
    console.log('Page loaded and initialized');
});

// 窗口大小变化时的处理
window.addEventListener('resize', debounce(function() {
    // 处理窗口大小变化
    console.log('Window resized');
}, 250));

// 滚动时的处理
window.addEventListener('scroll', throttle(function() {
    // 处理滚动事件
    console.log('Scrolled');
}, 100));
