const SERVER_URL = window.location.protocol === 'file:' ? 'http://localhost:8000' : '';
const API_BASE_URL = SERVER_URL + '/api';
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) throw new Error(`API error: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API Fetch failed:', error);
        throw error;
    }
}
