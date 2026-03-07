# app/ml/forecast_model.py
import pandas as pd
import numpy as np
from prophet import Prophet
import joblib
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class InvestmentForecaster:
    """
    Time series forecasting for investment returns
    Uses Facebook Prophet for accurate, probabilistic forecasts
    """
    
    def __init__(self):
        self.models = {}  # Cache trained models by asset class
    
    def prepare_data(self, historical_returns: Dict[str, List[float]]) -> pd.DataFrame:
        """
        Convert historical returns to Prophet format
        historical_returns: {'Equity': [0.12, 0.08, ...], 'Bonds': [0.05, 0.04, ...]}
        """
        all_data = []
        
        for asset_class, returns in historical_returns.items():
            if len(returns) < 12:  # Need at least 1 year of data
                continue
                
            # Create monthly dates (assuming monthly returns)
            dates = pd.date_range(
                start=pd.Timestamp.now() - pd.DateOffset(months=len(returns)-1),
                periods=len(returns),
                freq='M'
            )
            
            for date, return_value in zip(dates, returns):
                all_data.append({
                    'ds': date,  # Prophet requires 'ds' column for dates
                    'y': return_value,  # 'y' for values
                    'asset_class': asset_class
                })
        
        return pd.DataFrame(all_data)
    
    def train_model(self, asset_data: pd.DataFrame, asset_class: str) -> Prophet:
        """
        Train Prophet model for a specific asset class
        """
        # Filter data for this asset class
        df = asset_data[asset_data['asset_class'] == asset_class][['ds', 'y']].copy()
        
        # Configure Prophet with financial time series settings
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,  # Not relevant for investments
            daily_seasonality=False,
            changepoint_prior_scale=0.05,  # Conservative for finance
            seasonality_prior_scale=10.0
        )
        
        # Add custom seasonality for quarter-end effects
        model.add_seasonality(
            name='quarterly',
            period=91.25,  # Approximate quarter in days
            fourier_order=3
        )
        
        model.fit(df)
        self.models[asset_class] = model
        
        return model
    
    def forecast_returns(
        self, 
        asset_class: str, 
        years_ahead: int = 5,
        historical_returns: Dict[str, List[float]] = None
    ) -> Dict:
        """
        Forecast future returns with uncertainty intervals
        Returns: {
            'expected_annual_return': 0.08,
            'confidence_interval': [0.05, 0.12],
            'monthly_forecast': [...],
            'probability_positive': 0.85
        }
        """
        # Prepare data if historical returns provided
        if historical_returns and asset_class in historical_returns:
            data = self.prepare_data({asset_class: historical_returns[asset_class]})
            model = self.train_model(data, asset_class)
        elif asset_class in self.models:
            model = self.models[asset_class]
        else:
            # Fallback to default returns if no data
            defaults = {
                'Equity': {'expected': 0.10, 'low': 0.04, 'high': 0.16},
                'Bonds': {'expected': 0.05, 'low': 0.02, 'high': 0.08},
                'Money Market': {'expected': 0.03, 'low': 0.02, 'high': 0.04},
                'Real Estate': {'expected': 0.07, 'low': 0.03, 'high': 0.11}
            }
            return defaults.get(asset_class, {'expected': 0.06, 'low': 0.03, 'high': 0.09})
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=years_ahead * 12, freq='M')
        
        # Make forecast
        forecast = model.predict(future)
        
        # Calculate annual return from monthly forecast
        last_year = forecast.tail(12)['yhat'].values
        annual_return = (np.prod(1 + last_year) - 1)  # Compound monthly returns
        
        # Get confidence intervals
        lower_bound = forecast.tail(12)['yhat_lower'].mean()
        upper_bound = forecast.tail(12)['yhat_upper'].mean()
        
        # Calculate probability of positive returns
        positive_months = (forecast.tail(years_ahead * 12)['yhat'] > 0).mean()
        
        return {
            'expected_annual_return': round(float(annual_return), 4),
            'confidence_interval': [
                round(float(lower_bound), 4),
                round(float(upper_bound), 4)
            ],
            'probability_positive': round(float(positive_months), 4),
            'monthly_forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(24).to_dict('records')
        }
    
    def monte_carlo_simulation(
        self,
        initial_amount: float,
        monthly_contribution: float,
        years: int,
        expected_return: float,
        volatility: float,
        simulations: int = 1000
    ) -> Dict:
        """
        Run Monte Carlo simulation for investment outcomes
        Shows probability distribution of final amounts
        """
        np.random.seed(42)
        
        results = []
        
        for _ in range(simulations):
            amount = initial_amount
            
            for month in range(years * 12):
                # Generate random return with volatility
                monthly_return = np.random.normal(
                    expected_return/12,  # Convert annual to monthly
                    volatility/np.sqrt(12)  # Convert annual volatility
                )
                amount = amount * (1 + monthly_return) + monthly_contribution
            
            results.append(amount)
        
        results = np.array(results)
        
        return {
            'median_outcome': np.median(results),
            'percentile_10': np.percentile(results, 10),  # Worst 10%
            'percentile_25': np.percentile(results, 25),
            'percentile_75': np.percentile(results, 75),
            'percentile_90': np.percentile(results, 90),  # Best 10%
            'probability_positive': (results > initial_amount).mean(),
            'expected_value': results.mean(),
            'volatility': results.std()
        }

# Singleton instance
forecaster = InvestmentForecaster()