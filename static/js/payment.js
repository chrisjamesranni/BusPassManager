document.addEventListener('DOMContentLoaded', function() {
    const paymentForm = document.getElementById('payment-form');
    const amountInput = document.getElementById('amount');
    const paymentMethodSelect = document.getElementById('payment_method');
    const cardDetailsDiv = document.getElementById('card-details');
    const netBankingDetailsDiv = document.getElementById('netbanking-details');
    const upiDetailsDiv = document.getElementById('upi-details');
    const paymentButton = document.getElementById('payment-button');
    const pendingAmountEl = document.getElementById('pending-amount');
    
    // Initialize payment method UI
    if (paymentMethodSelect) {
        paymentMethodSelect.addEventListener('change', function() {
            // Hide all payment detail divs
            if (cardDetailsDiv) cardDetailsDiv.style.display = 'none';
            if (netBankingDetailsDiv) netBankingDetailsDiv.style.display = 'none';
            if (upiDetailsDiv) upiDetailsDiv.style.display = 'none';
            
            // Show the selected payment detail div
            switch (this.value) {
                case 'credit_card':
                case 'debit_card':
                    if (cardDetailsDiv) cardDetailsDiv.style.display = 'block';
                    break;
                case 'net_banking':
                    if (netBankingDetailsDiv) netBankingDetailsDiv.style.display = 'block';
                    break;
                case 'upi':
                    if (upiDetailsDiv) upiDetailsDiv.style.display = 'block';
                    break;
            }
        });
    }
    
    // Set default amount to pending amount if available
    if (amountInput && pendingAmountEl) {
        const pendingAmount = parseFloat(pendingAmountEl.textContent);
        if (!isNaN(pendingAmount) && pendingAmount > 0) {
            amountInput.value = pendingAmount.toFixed(2);
        }
    }
    
    // Validate credit card number with Luhn algorithm (for demo purposes)
    function validateCardNumber(number) {
        // Remove spaces and non-digits
        number = number.replace(/\D/g, '');
        
        // Check if the card number is of valid length
        if (number.length < 13 || number.length > 19) {
            return false;
        }
        
        // Luhn algorithm
        let sum = 0;
        let double = false;
        
        // Walk through the number from right to left
        for (let i = number.length - 1; i >= 0; i--) {
            let digit = parseInt(number.charAt(i));
            
            if (double) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }
            
            sum += digit;
            double = !double;
        }
        
        return sum % 10 === 0;
    }
    
    // Format credit card number with spaces
    const cardNumberInput = document.getElementById('card-number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            // Remove existing spaces
            let value = this.value.replace(/\s/g, '');
            
            // Add a space after every 4 digits
            if (value.length > 0) {
                value = value.match(new RegExp('.{1,4}', 'g')).join(' ');
            }
            
            this.value = value;
        });
    }
    
    // Format expiry date (MM/YY)
    const expiryInput = document.getElementById('card-expiry');
    if (expiryInput) {
        expiryInput.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            
            if (value.length > 0) {
                // Format as MM/YY
                if (value.length <= 2) {
                    this.value = value;
                } else {
                    this.value = value.substring(0, 2) + '/' + value.substring(2, 4);
                }
            }
        });
    }
    
    // Payment form validation
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            // This is just for demo purposes - in a real app, you would process the payment through a payment gateway
            let hasErrors = false;
            
            // Validate amount
            if (amountInput && (!amountInput.value || parseFloat(amountInput.value) <= 0)) {
                alert('Please enter a valid amount');
                hasErrors = true;
            }
            
            // Validate payment method specific fields
            if (paymentMethodSelect) {
                const method = paymentMethodSelect.value;
                
                if (method === 'credit_card' || method === 'debit_card') {
                    // Validate card details
                    const cardNumber = document.getElementById('card-number');
                    const cardName = document.getElementById('card-name');
                    const cardExpiry = document.getElementById('card-expiry');
                    const cardCVV = document.getElementById('card-cvv');
                    
                    if (cardNumber && !validateCardNumber(cardNumber.value)) {
                        alert('Please enter a valid card number');
                        hasErrors = true;
                    }
                    
                    if (cardName && !cardName.value.trim()) {
                        alert('Please enter the name on the card');
                        hasErrors = true;
                    }
                    
                    if (cardExpiry) {
                        const expiryValue = cardExpiry.value;
                        if (!expiryValue.match(/^\d{2}\/\d{2}$/)) {
                            alert('Please enter a valid expiry date (MM/YY)');
                            hasErrors = true;
                        } else {
                            // Check if card is expired
                            const [month, year] = expiryValue.split('/');
                            const expiryDate = new Date(2000 + parseInt(year), parseInt(month) - 1);
                            const today = new Date();
                            
                            if (expiryDate < today) {
                                alert('Your card has expired');
                                hasErrors = true;
                            }
                        }
                    }
                    
                    if (cardCVV && (!cardCVV.value || cardCVV.value.length < 3)) {
                        alert('Please enter a valid CVV');
                        hasErrors = true;
                    }
                }
                else if (method === 'net_banking') {
                    const bankSelect = document.getElementById('bank-select');
                    if (bankSelect && bankSelect.value === '') {
                        alert('Please select a bank');
                        hasErrors = true;
                    }
                }
                else if (method === 'upi') {
                    const upiId = document.getElementById('upi-id');
                    if (upiId && !upiId.value.includes('@')) {
                        alert('Please enter a valid UPI ID (e.g., username@upi)');
                        hasErrors = true;
                    }
                }
            }
            
            if (hasErrors) {
                e.preventDefault();
                return false;
            }
            
            // Show processing state
            if (paymentButton) {
                paymentButton.disabled = true;
                paymentButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
            
            // In a real implementation, you would process payment via a secure payment gateway
            // This demo just submits the form to the backend
            return true;
        });
    }
    
    // Payment history display
    const paymentHistoryTable = document.getElementById('payment-history-table');
    if (paymentHistoryTable) {
        const rows = paymentHistoryTable.querySelectorAll('tr[data-payment-id]');
        
        rows.forEach(row => {
            const status = row.querySelector('.payment-status');
            if (status) {
                // Apply color based on status
                const statusText = status.textContent.trim().toLowerCase();
                if (statusText === 'paid') {
                    status.classList.add('text-success');
                } else if (statusText === 'pending') {
                    status.classList.add('text-warning');
                } else if (statusText === 'failed') {
                    status.classList.add('text-danger');
                } else if (statusText === 'refunded') {
                    status.classList.add('text-info');
                }
            }
        });
    }
});
