document.addEventListener('DOMContentLoaded', function() {
    const videoElement = document.getElementById('qr-video');
    const scanButton = document.getElementById('start-scan');
    const stopButton = document.getElementById('stop-scan');
    const resultElement = document.getElementById('scan-result');
    const loadingIndicator = document.getElementById('loading-indicator');
    const manualInput = document.getElementById('manual-input');
    const manualSubmit = document.getElementById('manual-submit');
    const studentIdInput = document.getElementById('student_id');

    let scanner = null;

    // Function to start the QR scanner
    function startScanner() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // Create new QR scanner using the HTML5 QrCode library
            scanner = new Html5Qrcode("qr-reader");
            
            const qrConfig = { fps: 10, qrbox: 250 };
            
            scanner.start(
                { facingMode: "environment" },
                qrConfig,
                onScanSuccess,
                onScanFailure
            )
            .then(() => {
                videoElement.style.display = 'block';
                scanButton.style.display = 'none';
                stopButton.style.display = 'inline-block';
            })
            .catch(err => {
                console.error('Error starting scanner:', err);
                resultElement.innerHTML = `<div class="alert alert-danger">Error starting camera: ${err.message}</div>`;
            });
        } else {
            resultElement.innerHTML = '<div class="alert alert-danger">Sorry, your browser does not support accessing the camera.</div>';
        }
    }

    // Function to stop the QR scanner
    function stopScanner() {
        if (scanner) {
            scanner.stop()
            .then(() => {
                videoElement.style.display = 'none';
                scanButton.style.display = 'inline-block';
                stopButton.style.display = 'none';
            })
            .catch(err => {
                console.error('Error stopping scanner:', err);
            });
        }
    }

    // Function called when QR code is successfully scanned
    function onScanSuccess(decodedText, decodedResult) {
        // Stop scanning after successful scan
        stopScanner();
        
        // Check if decoded text is a valid student ID
        if (decodedText && decodedText.trim() !== '') {
            processStudentId(decodedText);
        } else {
            resultElement.innerHTML = '<div class="alert alert-warning">Invalid QR code. Please try again.</div>';
        }
    }

    // Function called on QR scan failure
    function onScanFailure(error) {
        // Just log failures, don't stop scanning
        console.warn(`QR scan error: ${error}`);
    }

    // Process the student ID (either from QR code or manual input)
    function processStudentId(studentId) {
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        resultElement.innerHTML = '';
        
        // Set the value in the hidden form field
        if (studentIdInput) {
            studentIdInput.value = studentId;
        }
        
        // Call the API to check student status
        fetch('/staff/scan-api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ student_id: studentId })
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.style.display = 'none';
            
            if (data.success) {
                const student = data.student;
                
                // Determine status color
                const cardStatusClass = getStatusClass(student.card_status);
                const feeStatusClass = getStatusClass(student.fee_status);
                
                // Format the result display
                resultElement.innerHTML = `
                    <div class="card mb-3">
                        <div class="card-header bg-primary text-white">
                            <h5>${student.name}</h5>
                            <h6>ID: ${student.student_id}</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <p><strong>Location:</strong> ${student.location}</p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>Card Status:</strong> 
                                        <span class="badge ${cardStatusClass}">${student.card_status}</span>
                                    </p>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <p><strong>Fee Status:</strong> 
                                        <span class="badge ${feeStatusClass}">${student.fee_status}</span>
                                    </p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>Dues:</strong> ₹${student.current_dues || 0}</p>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-12">
                                    <a href="/staff/check-student/${student.student_id}" class="btn btn-primary">View Details</a>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Auto-submit the form if configured to do so
                const form = document.getElementById('scan-form');
                if (form && form.dataset.autoSubmit === 'true') {
                    form.submit();
                }
            } else {
                resultElement.innerHTML = `<div class="alert alert-danger">${data.message || 'Error processing student ID'}</div>`;
            }
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            console.error('Error:', error);
            resultElement.innerHTML = `<div class="alert alert-danger">Error processing request: ${error.message}</div>`;
        });
    }

    // Helper function to get Bootstrap class based on status
    function getStatusClass(status) {
        switch(status) {
            case 'active':
            case 'paid':
                return 'bg-success';
            case 'pending':
                return 'bg-warning';
            case 'inactive':
            case 'cancelled':
            case 'expired':
            case 'overdue':
                return 'bg-danger';
            default:
                return 'bg-secondary';
        }
    }

    // Event listeners
    if (scanButton) {
        scanButton.addEventListener('click', startScanner);
    }
    
    if (stopButton) {
        stopButton.addEventListener('click', stopScanner);
    }
    
    if (manualSubmit) {
        manualSubmit.addEventListener('click', function() {
            const studentId = manualInput.value.trim();
            if (studentId) {
                processStudentId(studentId);
            } else {
                resultElement.innerHTML = '<div class="alert alert-warning">Please enter a student ID</div>';
            }
        });
    }
});
