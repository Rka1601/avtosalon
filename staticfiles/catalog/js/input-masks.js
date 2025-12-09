document.addEventListener('DOMContentLoaded', function() {
     function validateLicensePlate(plate) {
            plate = plate.replace(/\s/g, '').toUpperCase();
            
            if (plate.length === 0) return true;
            
            
            if (plate.length < 8 || plate.length > 9) {
                return false;
            }
            
            
            return /^[АВЕКМНОРСТУХABEKMHOPCTYX]{1}\d{3}[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$/.test(plate);
        }
    function applyPhoneMask(input) {
    input.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        
        let formatted = '';
        if (value.startsWith('7') || value.startsWith('8')) {
            value = value.substring(1);
        }
        
        if (value.length > 0) {
            formatted = '+7 (';
            if (value.length > 0) {
                formatted += value.substring(0, 3);
            }
            if (value.length > 3) {
                formatted += ') ' + value.substring(3, 6);
            }
            if (value.length > 6) {
                formatted += '-' + value.substring(6, 8);
            }
            if (value.length > 8) {
                formatted += '-' + value.substring(8, 10);
            }
        }
        
        e.target.value = formatted;
    });
}
    
    function applyInputMasks() {
        
        const phoneInputs = document.querySelectorAll('input[data-mask="+7 (000) 000-00-00"]');
        phoneInputs.forEach(input => {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.startsWith('7') || value.startsWith('8')) {
                    value = value.substring(1);
                }
                if (value.length > 0) {
                    value = '+7 (' + value;
                    if (value.length > 7) {
                        value = value.substring(0, 7) + ') ' + value.substring(7);
                    }
                    if (value.length > 12) {
                        value = value.substring(0, 12) + '-' + value.substring(12);
                    }
                    if (value.length > 15) {
                        value = value.substring(0, 15) + '-' + value.substring(15);
                    }
                }
                e.target.value = value;
            });
        });

        
        const passportSeriesInputs = document.querySelectorAll('input[data-mask="0000"]');
        passportSeriesInputs.forEach(input => {
            input.addEventListener('input', function(e) {
                e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
            });
        });

        
        const passportNumberInputs = document.querySelectorAll('input[data-mask="000000"]');
        passportNumberInputs.forEach(input => {
            input.addEventListener('input', function(e) {
                e.target.value = e.target.value.replace(/\D/g, '').substring(0, 6);
            });
        });

        
        const vinInputs = document.querySelectorAll('input[data-mask="_________________"]');
        vinInputs.forEach(input => {
            input.addEventListener('input', function(e) {
                e.target.value = e.target.value.toUpperCase().replace(/[^A-HJ-NPR-Z0-9]/g, '').substring(0, 17);
            });
        });

        
        
        
        const licensePlateInputs = document.querySelectorAll('input[data-mask="license-plate"]');
        licensePlateInputs.forEach(input => {
            let errorDisplay = null;
            
            
            function showError(message) {
                if (!errorDisplay) {
                    errorDisplay = document.createElement('div');
                    errorDisplay.className = 'text-danger small mt-1';
                    input.parentNode.appendChild(errorDisplay);
                }
                errorDisplay.textContent = message;
                input.classList.add('is-invalid');
            }
            
            function hideError() {
                if (errorDisplay) {
                    errorDisplay.remove();
                    errorDisplay = null;
                }
                input.classList.remove('is-invalid');
            }
            
            input.addEventListener('input', function(e) {
                let value = e.target.value.toUpperCase().replace(/[^АВЕКМНОРСТУХABEKMHOPCTYX0-9\s]/g, '');
                e.target.value = value;
                
                
                if (validateLicensePlate(value)) {
                    hideError();
                } else if (value.length > 0) {
                    showError('Госномер должен содержать 8-9 символов. Пример: А123BC777 или А123BC77');
                } else {
                    hideError();
                }
            });
            
            input.addEventListener('blur', function(e) {
                const value = e.target.value;
                if (!validateLicensePlate(value) && value.length > 0) {
                    showError('Госномер должен содержать 8-9 символов. Пример: А123BC777 или А123BC77');
                }
            });
            
            
            if (input.form) {
                input.form.addEventListener('submit', function(e) {
                    if (!validateLicensePlate(input.value)) {
                        showError('Исправьте госномер перед отправкой');
                        input.focus();
                        e.preventDefault();
                    }
                });
            }
        });

        
    }
    
function clearServerErrors(input) {
    
    input.classList.remove('is-invalid');
    
    
    const errorElements = input.parentNode.querySelectorAll('.errorlist, .text-danger');
    errorElements.forEach(element => {
        if (element.textContent.includes('госномер') || element.textContent.includes('Госномер')) {
            element.remove();
        }
    });
    
    
    input.style.borderColor = '';
}


const licensePlateInputs = document.querySelectorAll('input[data-mask="license-plate"]');
licensePlateInputs.forEach(input => {
    let errorDisplay = null;
    
    
    function showError(message) {
        clearServerErrors(input);
        
        if (!errorDisplay) {
            errorDisplay = document.createElement('div');
            errorDisplay.className = 'text-danger small mt-1';
            input.parentNode.appendChild(errorDisplay);
        }
        errorDisplay.textContent = message;
        input.classList.add('is-invalid');
    }
    
    function hideError() {
        clearServerErrors(input);
        
        if (errorDisplay) {
            errorDisplay.remove();
            errorDisplay = null;
        }
        input.classList.remove('is-invalid');
    }
    
    function clearAllFormErrors() {
        document.querySelectorAll('.is-invalid').forEach(input => {
            input.classList.remove('is-invalid');
        });
        
        document.querySelectorAll('.errorlist, .text-danger').forEach(element => {
            element.remove();
        });
}


document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[data-mask="+7 (000) 000-00-00"]');
    phoneInputs.forEach(applyPhoneMask);
    setTimeout(clearAllFormErrors, 50);
});
    input.addEventListener('input', function(e) {
        let value = e.target.value.toUpperCase().replace(/[^АВЕКМНОРСТУХABEKMHOPCTYX0-9\s]/g, '');
        e.target.value = value;
        
        
        clearServerErrors(input);
        
        
        if (validateLicensePlate(value)) {
            hideError();
        } else if (value.length > 0) {
            showError('Госномер должен содержать 8-9 символов. Пример: А123BC777 или А123BC77');
        } else {
            hideError();
        }
    });
    
    input.addEventListener('blur', function(e) {
        const value = e.target.value;
        if (!validateLicensePlate(value) && value.length > 0) {
            showError('Госномер должен содержать 8-9 символов. Пример: А123BC777 или А123BC77');
        }
    });
    
    
    setTimeout(() => {
        if (input.value && !validateLicensePlate(input.value)) {
            showError('Исправьте госномер');
        }
    }, 100);
});

    applyInputMasks();
});