// 前端表单验证

class FormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        if (this.form) {
            this.init();
        }
    }
    
    // 初始化
    init() {
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.form.classList.add('was-validated');
        });
        
        // 实时验证
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => {
                this.validateField(field);
            });
            
            field.addEventListener('input', () => {
                if (field.classList.contains('is-invalid')) {
                    this.validateField(field);
                }
            });
        });
    }
    
    // 验证整个表单
    validateForm() {
        let isValid = true;
        
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    // 验证单个字段
    validateField(field) {
        const validity = field.validity;
        const errorElement = this.form.querySelector(`#${field.id}-error`);
        
        if (validity.valid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (errorElement) {
                errorElement.textContent = '';
                errorElement.classList.add('d-none');
            }
            return true;
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            if (errorElement) {
                errorElement.textContent = this.getErrorMessage(field);
                errorElement.classList.remove('d-none');
            }
            return false;
        }
    }
    
    // 获取错误消息
    getErrorMessage(field) {
        const validity = field.validity;
        
        if (validity.valueMissing) {
            return field.dataset.requiredMessage || '此字段为必填项';
        }
        
        if (validity.typeMismatch) {
            switch (field.type) {
                case 'email':
                    return '请输入有效的电子邮件地址';
                case 'url':
                    return '请输入有效的URL';
                case 'number':
                    return '请输入有效的数字';
                default:
                    return '请输入有效的值';
            }
        }
        
        if (validity.patternMismatch) {
            return field.dataset.patternMessage || '输入格式不正确';
        }
        
        if (validity.tooShort) {
            return `最少需要${field.minLength}个字符`;
        }
        
        if (validity.tooLong) {
            return `最多允许${field.maxLength}个字符`;
        }
        
        if (validity.rangeUnderflow) {
            return `最小值为${field.min}`;
        }
        
        if (validity.rangeOverflow) {
            return `最大值为${field.max}`;
        }
        
        if (validity.stepMismatch) {
            return '输入值不符合要求的步长';
        }
        
        return '输入值无效';
    }
    
    // 自定义验证规则
    addCustomValidation(fieldId, validationFunction, errorMessage) {
        const field = this.form.querySelector(`#${fieldId}`);
        if (field) {
            field.addEventListener('blur', () => {
                if (!validationFunction(field.value)) {
                    field.setCustomValidity(errorMessage);
                    this.validateField(field);
                } else {
                    field.setCustomValidity('');
                    this.validateField(field);
                }
            });
            
            field.addEventListener('input', () => {
                if (!validationFunction(field.value)) {
                    field.setCustomValidity(errorMessage);
                    this.validateField(field);
                } else {
                    field.setCustomValidity('');
                    this.validateField(field);
                }
            });
        }
    }
    
    // 验证密码匹配
    validatePasswordMatch(passwordFieldId, confirmFieldId, errorMessage) {
        const passwordField = this.form.querySelector(`#${passwordFieldId}`);
        const confirmField = this.form.querySelector(`#${confirmFieldId}`);
        const errorElement = this.form.querySelector(`#${confirmFieldId}-error`);
        
        if (passwordField && confirmField) {
            const validateMatch = () => {
                if (passwordField.value !== confirmField.value) {
                    confirmField.setCustomValidity(errorMessage);
                    this.validateField(confirmField);
                    if (errorElement) {
                        errorElement.textContent = errorMessage;
                        errorElement.classList.remove('d-none');
                    }
                    return false;
                } else {
                    confirmField.setCustomValidity('');
                    this.validateField(confirmField);
                    if (errorElement) {
                        errorElement.textContent = '';
                        errorElement.classList.add('d-none');
                    }
                    return true;
                }
            };
            
            passwordField.addEventListener('input', validateMatch);
            confirmField.addEventListener('input', validateMatch);
            confirmField.addEventListener('blur', validateMatch);
        }
    }
    
    // 验证用户名可用性
    validateUsernameAvailability(usernameFieldId, errorMessage) {
        const usernameField = this.form.querySelector(`#${usernameFieldId}`);
        if (usernameField) {
            usernameField.addEventListener('blur', this.debounce(() => {
                const username = usernameField.value.trim();
                if (username) {
                    // 发送AJAX请求检查用户名是否可用
                    fetch(`/auth/check-username?username=${encodeURIComponent(username)}`)
                        .then(response => response.json())
                        .then(data => {
                            if (!data.available) {
                                usernameField.setCustomValidity(errorMessage);
                                this.validateField(usernameField);
                            } else {
                                usernameField.setCustomValidity('');
                                this.validateField(usernameField);
                            }
                        })
                        .catch(error => {
                            console.error('检查用户名可用性时出错:', error);
                        });
                }
            }, 500));
        }
    }
    
    // 验证电子邮件可用性
    validateEmailAvailability(emailFieldId, errorMessage) {
        const emailField = this.form.querySelector(`#${emailFieldId}`);
        if (emailField) {
            emailField.addEventListener('blur', this.debounce(() => {
                const email = emailField.value.trim();
                if (email) {
                    // 发送AJAX请求检查电子邮件是否可用
                    fetch(`/auth/check-email?email=${encodeURIComponent(email)}`)
                        .then(response => response.json())
                        .then(data => {
                            if (!data.available) {
                                emailField.setCustomValidity(errorMessage);
                                this.validateField(emailField);
                            } else {
                                emailField.setCustomValidity('');
                                this.validateField(emailField);
                            }
                        })
                        .catch(error => {
                            console.error('检查电子邮件可用性时出错:', error);
                        });
                }
            }, 500));
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

// 初始化所有表单验证
function initFormValidators() {
    document.querySelectorAll('form').forEach(form => {
        const formId = form.id;
        if (formId) {
            new FormValidator(`#${formId}`);
        }
    });
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    initFormValidators();
});