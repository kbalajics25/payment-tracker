// Charts Configuration using Chart.js

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the reports page
    if (document.getElementById('creditVsDebitChart')) {
        initializeCharts();
    }
});

async function initializeCharts() {
    try {
        // Credit vs Debit Pie Chart
        await createCreditVsDebitChart();
        
        // Category Spending Bar Chart
        await createCategorySpendingChart();
        
        // Daily Spending Line Chart
        await createDailySpendingChart();
        
        // Weekly Spending Line Chart
        await createWeeklySpendingChart();
        
        // Monthly Spending Bar Chart
        await createMonthlySpendingChart();
        
        // Balance Trend Line Chart
        await createBalanceTrendChart();
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

async function createCreditVsDebitChart() {
    const ctx = document.getElementById('creditVsDebitChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/api/chart_data/credit_vs_debit');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: data.backgroundColor,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ₹${value.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating credit vs debit chart:', error);
    }
}

async function createCategorySpendingChart() {
    const ctx = document.getElementById('categorySpendingChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/api/chart_data/category_spending');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Spending by Category',
                    data: data.data,
                    backgroundColor: '#3b82f6',
                    borderColor: '#2563eb',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `₹${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating category spending chart:', error);
    }
}

async function createDailySpendingChart() {
    const ctx = document.getElementById('dailySpendingChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/api/chart_data/daily_spending');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Daily Expenses',
                    data: data.data,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `₹${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating daily spending chart:', error);
    }
}

async function createWeeklySpendingChart() {
    const ctx = document.getElementById('weeklySpendingChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/api/chart_data/weekly_spending');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Weekly Expenses',
                    data: data.data,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `₹${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating weekly spending chart:', error);
    }
}

async function createMonthlySpendingChart() {
    const ctx = document.getElementById('monthlySpendingChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/api/chart_data/monthly_spending');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Credit',
                        data: data.credit_data,
                        backgroundColor: '#10b981',
                        borderColor: '#059669',
                        borderWidth: 1
                    },
                    {
                        label: 'Debit',
                        data: data.debit_data,
                        backgroundColor: '#ef4444',
                        borderColor: '#dc2626',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ₹${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating monthly spending chart:', error);
    }
}

async function createBalanceTrendChart() {
    const ctx = document.getElementById('balanceTrendChart');
    if (!ctx) return;
    
    try {
        const response = await fetch('/api/chart_data/balance_trend');
        const data = await response.json();
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Balance',
                    data: data.data,
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Balance: ₹${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating balance trend chart:', error);
    }
}