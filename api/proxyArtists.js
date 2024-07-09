const axios = require('axios');

module.exports = async (req, res) => {
  console.log("Received request:", req.method, req.body);

  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
    return;
  }

  const { urls } = req.body;

  if (!urls) {
    res.status(400).json({ error: 'No URLs provided' });
    return;
  }

  try {
    const response = await axios.post('https://statify-flask.vercel.app/api/artists', { urls });
    res.status(200).json(response.data);
  } catch (error) {
    console.error("Error fetching artists:", error.message);
    res.status(500).json({ error: error.message });
  }
};

