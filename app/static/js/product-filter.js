// 商品搜索、筛选、排序交互

class ProductFilter {
    constructor() {
        this.initEvents();
        this.initMobileFilter();
    }
    
    // 初始化事件
    initEvents() {
        // 搜索输入框实时搜索
        const searchInput = document.querySelector('.product-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.performSearch();
            }, 300));
        }
        
        const searchBtn = document.querySelector('.product-search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.performSearch();
            });
        }
        
        // 价格区间筛选
        const priceRangeInputs = document.querySelectorAll('.price-range-input');
        priceRangeInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.applyFilters();
            });
        });
        
        // 标签筛选
        const tagCheckboxes = document.querySelectorAll('.tag-checkbox');
        tagCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.applyFilters();
            });
        });
        
        // 排序下拉框
        const sortSelect = document.querySelector('.sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => {
                this.applySort();
            });
        }
        
        // 筛选重置按钮
        const resetFiltersBtn = document.querySelector('.reset-filters-btn');
        if (resetFiltersBtn) {
            resetFiltersBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.resetFilters();
            });
        }
    }
    
    // 初始化移动端筛选
    initMobileFilter() {
        const filterToggle = document.querySelector('.filter-toggle');
        const filterSidebar = document.querySelector('.filter-sidebar');
        const filterOverlay = document.querySelector('.filter-overlay');
        const filterClose = document.querySelector('.filter-close');
        
        if (filterToggle && filterSidebar && filterOverlay) {
            // 打开筛选侧边栏
            filterToggle.addEventListener('click', () => {
                filterSidebar.classList.add('active');
                filterOverlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            });
            
            // 关闭筛选侧边栏
            const closeFilter = () => {
                filterSidebar.classList.remove('active');
                filterOverlay.classList.remove('active');
                document.body.style.overflow = '';
            };
            
            filterClose.addEventListener('click', closeFilter);
            filterOverlay.addEventListener('click', closeFilter);
        }
    }
    
    // 执行搜索
    performSearch() {
        const searchInput = document.querySelector('.product-search-input');
        if (searchInput) {
            const searchQuery = searchInput.value.trim();
            this.updateURLParameter('q', searchQuery);
            this.loadProducts();
        }
    }
    
    // 应用筛选
    applyFilters() {
        // 获取价格区间筛选值
        const minPrice = document.querySelector('#min_price')?.value;
        const maxPrice = document.querySelector('#max_price')?.value;
        if (minPrice) {
            this.updateURLParameter('min_price', minPrice);
        } else {
            this.removeURLParameter('min_price');
        }
        if (maxPrice) {
            this.updateURLParameter('max_price', maxPrice);
        } else {
            this.removeURLParameter('max_price');
        }
        
        // 获取标签筛选值
        const selectedTags = [];
        document.querySelectorAll('.tag-checkbox:checked').forEach(checkbox => {
            selectedTags.push(checkbox.value);
        });
        this.updateURLParameter('tags', selectedTags.join(','));
        
        // 重置页码
        this.updateURLParameter('page', '1');
        
        // 加载商品
        this.loadProducts();
    }
    
    // 应用排序
    applySort() {
        const sortSelect = document.querySelector('.sort-select');
        if (sortSelect) {
            const sortValue = sortSelect.value;
            this.updateURLParameter('sort', sortValue);
            this.updateURLParameter('page', '1');
            this.loadProducts();
        }
    }
    
    // 重置筛选
    resetFilters() {
        // 重置价格输入框
        document.querySelectorAll('.price-range-input').forEach(input => {
            input.value = '';
        });
        
        // 重置标签复选框
        document.querySelectorAll('.tag-checkbox:checked').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // 重置搜索输入框
        const searchInput = document.querySelector('.product-search-input');
        if (searchInput) {
            searchInput.value = '';
        }
        
        // 重置排序
        const sortSelect = document.querySelector('.sort-select');
        if (sortSelect) {
            sortSelect.value = 'default';
        }
        
        // 重置URL参数
        this.resetURLParameters();
        
        // 加载商品
        this.loadProducts();
    }
    
    // 加载商品
    loadProducts() {
        // 显示加载动画
        this.showLoading();
        
        // 获取当前URL
        const url = new URL(window.location.href);
        
        // 发送AJAX请求
        fetch(url.toString(), {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            // 更新商品列表
            const productListContainer = document.querySelector('.product-list-container');
            if (productListContainer) {
                // 解析响应HTML，提取商品列表部分
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newProductList = doc.querySelector('.product-list-container');
                
                if (newProductList) {
                    productListContainer.innerHTML = newProductList.innerHTML;
                    if (window.cartManager) {
                        window.cartManager.bindAddToCartButtons();
                    }
                }
            }
            
            // 更新分页
            const paginationContainer = document.querySelector('.pagination-container');
            if (paginationContainer) {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newPagination = doc.querySelector('.pagination-container');
                
                if (newPagination) {
                    paginationContainer.innerHTML = newPagination.innerHTML;
                    // 重新绑定分页事件
                    this.initPagination();
                }
            }
            
            // 隐藏加载动画
            this.hideLoading();
        })
        .catch(error => {
            console.error('加载商品时出错:', error);
            this.hideLoading();
        });
    }
    
    // 初始化分页
    initPagination() {
        const paginationLinks = document.querySelectorAll('.pagination a');
        paginationLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('href').split('page=')[1];
                this.updateURLParameter('page', page);
                this.loadProducts();
            });
        });
    }
    
    // 更新URL参数
    updateURLParameter(key, value) {
        const url = new URL(window.location.href);
        if (value) {
            url.searchParams.set(key, value);
        } else {
            url.searchParams.delete(key);
        }
        window.history.pushState({path: url.href}, '', url.href);
    }
    
    // 移除URL参数
    removeURLParameter(key) {
        const url = new URL(window.location.href);
        url.searchParams.delete(key);
        window.history.pushState({path: url.href}, '', url.href);
    }
    
    // 重置URL参数
    resetURLParameters() {
        const url = new URL(window.location.href);
        const paramsToKeep = ['page'];
        
        // 保留指定参数
        const newUrl = new URL(url.origin + url.pathname);
        paramsToKeep.forEach(param => {
            if (url.searchParams.has(param)) {
                newUrl.searchParams.set(param, url.searchParams.get(param));
            }
        });
        
        window.history.pushState({path: newUrl.href}, '', newUrl.href);
    }
    
    // 显示加载动画
    showLoading() {
        const loadingElement = document.querySelector('.loading-indicator');
        if (loadingElement) {
            loadingElement.classList.remove('d-none');
        }
    }
    
    // 隐藏加载动画
    hideLoading() {
        const loadingElement = document.querySelector('.loading-indicator');
        if (loadingElement) {
            loadingElement.classList.add('d-none');
        }
    }
    
    // 防抖函数
    debounce(func, wait) {
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
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    new ProductFilter();
});
