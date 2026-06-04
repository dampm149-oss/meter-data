import fetch from 'node-fetch';

export default async function handler(req, res) {
  // Only allow POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { startDate, endDate, meterNo } = req.body;

    // Validate
    if (!startDate || !endDate || !meterNo) {
      return res.status(400).json({ error: 'Missing parameters' });
    }

    console.log(`Fetching meter ${meterNo} from ${startDate} to ${endDate}`);

    // Step 1: Login
    const loginUrl = 'http://14.225.244.63:8899/api/Login?UserAccount=verdant&Password=verdantenergy@2026';
    
    const loginRes = await fetch(loginUrl);
    const loginData = await loginRes.json();

    if (loginData.CODE !== 1) {
      return res.status(401).json({ 
        error: 'Login failed', 
        details: loginData.MESSAGE 
      });
    }

    const token = loginData.TOKEN;
    console.log('Login successful, token obtained');

    // Step 2: Fetch meter data
    const dataUrl = `http://14.225.244.63:8899/api/GetMeterDataByDate?MeterNo=${meterNo}&StartDate=${startDate}&EndDate=${endDate}&Token=${token}`;
    
    const dataRes = await fetch(dataUrl);
    const meterData = await dataRes.json();

    console.log(`Received ${meterData.length || 0} records for meter ${meterNo}`);

    // Step 3: Calculate consumption
    const result = {
      meter_no: meterNo,
      start_date: startDate,
      end_date: endDate,
      records_count: meterData ? meterData.length : 0,
      consumption: {
        ACTIVE_TOTAL: 0,
        ACTIVE_KW_INDICATE_RATE1: 0,
        ACTIVE_KW_INDICATE_RATE2: 0,
      },
      status: 'no_data',
      first_time: null,
      last_time: null
    };

    if (meterData && Array.isArray(meterData) && meterData.length >= 1) {
      const first = meterData[0];
      const last = meterData[meterData.length - 1];

      result.first_time = first.DATE_TIME || null;
      result.last_time = last.DATE_TIME || null;

      if (meterData.length >= 2) {
        result.consumption.ACTIVE_TOTAL = 
          (last.ACTIVE_TOTAL || 0) - (first.ACTIVE_TOTAL || 0);
        result.consumption.ACTIVE_KW_INDICATE_RATE1 = 
          (last.ACTIVE_KW_INDICATE_RATE1 || 0) - (first.ACTIVE_KW_INDICATE_RATE1 || 0);
        result.consumption.ACTIVE_KW_INDICATE_RATE2 = 
          (last.ACTIVE_KW_INDICATE_RATE2 || 0) - (first.ACTIVE_KW_INDICATE_RATE2 || 0);
        
        result.status = 'ok';
      } else {
        result.status = 'partial';
      }
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
