document.addEventListener('DOMContentLoaded', function() {
    const brandSelect = document.getElementById('brand-select');
    const modelSelect = document.getElementById('model-select');
    
    if (brandSelect && modelSelect) {
        
        brandSelect.addEventListener('change', function() {
            const brand = this.value;
            
            if (brand) {
                
                modelSelect.disabled = false;
                
                
                fetch(`/api/models/?brand=${encodeURIComponent(brand)}`)
                    .then(response => response.json())
                    .then(data => {
                        
                        modelSelect.innerHTML = '<option value="">Любая модель</option>';
                        
                        
                        data.models.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model;
                            option.textContent = model;
                            modelSelect.appendChild(option);
                        });
                        
                        
                        const savedModel = new URLSearchParams(window.location.search).get('model');
                        if (savedModel) {
                            modelSelect.value = savedModel;
                        }
                    })
                    .catch(error => {
                        console.error('Error loading models:', error);
                    });
            } else {
                
                modelSelect.disabled = true;
                modelSelect.innerHTML = '<option value="">Любая модель</option>';
            }
        });
        
        
        if (brandSelect.value) {
            brandSelect.dispatchEvent(new Event('change'));
        }
    }
    
    
    const minPriceInput = document.querySelector('input[name="min_price"]');
    const maxPriceInput = document.querySelector('input[name="max_price"]');
    
    if (minPriceInput && maxPriceInput) {
        minPriceInput.addEventListener('blur', validatePriceRange);
        maxPriceInput.addEventListener('blur', validatePriceRange);
    }
    
    function validatePriceRange() {
        const min = parseInt(minPriceInput.value) || 0;
        const max = parseInt(maxPriceInput.value) || 0;
        
        if (min > 0 && max > 0 && min > max) {
            alert('Минимальная цена не может быть больше максимальной!');
            minPriceInput.focus();
        }
    }
});