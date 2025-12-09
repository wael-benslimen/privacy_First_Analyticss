// Mock Backend Server for Testing Frontend
// This is a TEMPORARY solution until Python is installed
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// Mock login endpoint
app.post('/api/login/', (req, res) => {
    const { username, password } = req.body;

    if (username === 'admin' && password === 'admin123') {
        res.json({
            access: 'mock-token-12345',
            refresh: 'mock-refresh-token',
            user: {
                id: 1,
                username: 'admin',
                email: 'admin@example.com',
                role: 'admin'
            }
        });
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
});

// Mock count query endpoint
app.post('/api/query/count/', (req, res) => {
    const { epsilon } = req.body;

    res.json({
        query_type: 'count',
        result: {
            true_result: 1000,
            noisy_result: 1003,
            noise_added: 3
        },
        epsilon_used: epsilon || 1.0,
        filters_applied: {},
        execution_time: 0.0234,
        budget_remaining: 9.0
    });
});

const PORT = 8000;
app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('🚀 MOCK BACKEND SERVER RUNNING');
    console.log('='.repeat(60));
    console.log(`Server: http://127.0.0.1:${PORT}`);
    console.log('');
    console.log('⚠️  This is a TEMPORARY mock server for testing!');
    console.log('📌 Install Python to run the real Django backend');
    console.log('');
    console.log('Login credentials:');
    console.log('  Username: admin');
    console.log('  Password: admin123');
    console.log('='.repeat(60));
});
