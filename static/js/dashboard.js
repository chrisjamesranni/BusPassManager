document.addEventListener('DOMContentLoaded', function() {
    // Chart for student dashboard - payment history
    const paymentChartEl = document.getElementById('paymentChart');
    if (paymentChartEl) {
        const paymentData = JSON.parse(paymentChartEl.getAttribute('data-payments') || '[]');
        const labels = paymentData.map(p => {
            const date = new Date(p.payment_date);
            return `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
        });
        const amounts = paymentData.map(p => p.amount);

        new Chart(paymentChartEl, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Payment Amount',
                    data: amounts,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount (₹)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Payment Date'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Recent Payment History'
                    }
                }
            }
        });
    }

    // Chart for admin dashboard - monthly payments
    const adminChartEl = document.getElementById('adminPaymentChart');
    if (adminChartEl) {
        const monthlyData = JSON.parse(adminChartEl.getAttribute('data-payments') || '[]');
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

        new Chart(adminChartEl, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Monthly Payments',
                    data: monthlyData,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount (₹)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Month'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Payment Collections'
                    }
                }
            }
        });
    }

    // Chart for accountant dashboard - fee status distribution
    const feeStatusChartEl = document.getElementById('feeStatusChart');
    if (feeStatusChartEl) {
        const statusData = JSON.parse(feeStatusChartEl.getAttribute('data-status') || '[]');
        const statuses = statusData.map(s => s.status);
        const counts = statusData.map(s => s.count);
        const backgroundColors = [
            'rgba(75, 192, 192, 0.7)',  // paid - green
            'rgba(255, 206, 86, 0.7)',  // pending - yellow
            'rgba(255, 99, 132, 0.7)'   // overdue - red
        ];

        new Chart(feeStatusChartEl, {
            type: 'pie',
            data: {
                labels: statuses,
                datasets: [{
                    label: 'Fee Status Distribution',
                    data: counts,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: 'Fee Status Distribution'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Location-wise fee collection chart
    const locationChartEl = document.getElementById('locationChart');
    if (locationChartEl) {
        const locationData = JSON.parse(locationChartEl.getAttribute('data-locations') || '[]');
        const locations = locationData.map(l => l.name);
        const students = locationData.map(l => l.student_count);
        const fees = locationData.map(l => l.total_fee);

        new Chart(locationChartEl, {
            type: 'bar',
            data: {
                labels: locations,
                datasets: [
                    {
                        label: 'Students',
                        data: students,
                        backgroundColor: 'rgba(153, 102, 255, 0.7)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Total Fees (₹)',
                        data: fees,
                        backgroundColor: 'rgba(255, 159, 64, 0.7)',
                        borderColor: 'rgba(255, 159, 64, 1)',
                        borderWidth: 1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Number of Students'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false
                        },
                        title: {
                            display: true,
                            text: 'Total Fees (₹)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Location-wise Fee Collection'
                    }
                }
            }
        });
    }

    // Notification handling
    const notificationBtns = document.querySelectorAll('.mark-read-btn');
    notificationBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const notificationId = this.getAttribute('data-id');
            const notificationElement = document.getElementById(`notification-${notificationId}`);
            
            // Send request to mark as read
            fetch(`/student/notifications/read/${notificationId}`)
                .then(response => {
                    if (response.ok) {
                        // Update UI
                        if (notificationElement) {
                            notificationElement.classList.remove('unread');
                            notificationElement.classList.add('read');
                            btn.style.display = 'none';
                        }
                    }
                })
                .catch(error => console.error('Error marking notification as read:', error));
        });
    });

    // Card request handling
    const cardRequestForm = document.getElementById('card-request-form');
    if (cardRequestForm) {
        const requestTypeSelect = document.getElementById('request_type');
        const reasonTextarea = document.getElementById('reason');
        
        requestTypeSelect.addEventListener('change', function() {
            // Pre-fill reason based on request type
            switch(this.value) {
                case 'new':
                    reasonTextarea.placeholder = 'Please explain why you need a new bus card...';
                    break;
                case 'cancel':
                    reasonTextarea.placeholder = 'Please explain why you want to cancel your bus card...';
                    break;
                case 'replace':
                    reasonTextarea.placeholder = 'Please explain why you need a replacement card (lost/damaged/stolen)...';
                    break;
            }
        });
    }
});
