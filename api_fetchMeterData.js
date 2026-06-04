export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { startDate, endDate, meterNo } = req.body;

  // Validate inputs
  if (!startDate || !endDate) {
    return res.status(400).json({ error: 'Start and end dates required' });
  }

  try {
    // Step 1: Login to get token
    const loginResponse = await fetch(
      'http://14.225.244.63:8899/api/Login?UserAccount=verdant&Password=verdantenergy@2026'
    );

    if (!loginResponse.ok) {
      return res.status(500).json({ error: 'Failed to login to meter API' });
    }

    const loginData = await loginResponse.json();
    
    if (loginData.CODE !== 1) {
      return res.status(401).json({ error: 'Authentication failed', details: loginData.MESSAGE });
    }

    const token = loginData.TOKEN;

    // Step 2: Fetch meter data
    const dataResponse = await fetch(
      `http://14.225.244.63:8899/api/GetMeterDataByDate?MeterNo=${meterNo}&StartDate=${startDate}&EndDate=${endDate}&Token=${token}`
    );

    if (!dataResponse.ok) {
      return res.status(500).json({ error: 'Failed to fetch meter data' });
    }

    const meterData = await dataResponse.json();

    // Step 3: Calculate daily consumption from first and last reading
    let result = {
      meter_no: meterNo,
      start_date: startDate,
      end_date: endDate,
      records_count: meterData.length,
      consumption: {
        ACTIVE_TOTAL: 0,
        ACTIVE_KW_INDICATE_RATE1: 0,
        ACTIVE_KW_INDICATE_RATE2: 0,
      },
      status: 'ok'
    };

    if (meterData.length >= 2) {
      const firstReading = meterData[0];
      const lastReading = meterData[meterData.length - 1];

      result.consumption.ACTIVE_TOTAL = 
        (lastReading.ACTIVE_TOTAL || 0) - (firstReading.ACTIVE_TOTAL || 0);
      result.consumption.ACTIVE_KW_INDICATE_RATE1 = 
        (lastReading.ACTIVE_KW_INDICATE_RATE1 || 0) - (firstReading.ACTIVE_KW_INDICATE_RATE1 || 0);
      result.consumption.ACTIVE_KW_INDICATE_RATE2 = 
        (lastReading.ACTIVE_KW_INDICATE_RATE2 || 0) - (firstReading.ACTIVE_KW_INDICATE_RATE2 || 0);
      
      result.first_time = firstReading.DATE_TIME;
      result.last_time = lastReading.DATE_TIME;
    } else if (meterData.length === 1) {
      result.status = 'partial';
      result.records_count = 1;
    } else {
      result.status = 'no_data';
    }

    return res.status(200).json(result);

  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({ 
      error: 'Server error', 
      details: error.message 
    });
  }
}
