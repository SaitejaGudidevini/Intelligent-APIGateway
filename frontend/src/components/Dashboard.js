import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Paper, Button } from '@mui/material';
import { getCurrentUser, checkHealth } from '../services/api';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [health, setHealth] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        const healthData = await checkHealth();
        setHealth(healthData);
      } catch (err) {
        navigate('/login');
      }
    };
    fetchData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        {user && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6">User Information</Typography>
            <Typography>Email: {user.email}</Typography>
            <Typography>Username: {user.username}</Typography>
          </Paper>
        )}
        {health && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6">System Health</Typography>
            <Typography>Status: {health.status}</Typography>
            <Typography>Timestamp: {new Date(health.timestamp * 1000).toLocaleString()}</Typography>
          </Paper>
        )}
        <Button variant="contained" color="secondary" onClick={handleLogout}>
          Logout
        </Button>
      </Box>
    </Container>
  );
};

export default Dashboard;
