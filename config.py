import os
import requests
import logging

logger = logging.getLogger(__name__)

def get_doppler_secret(key, default=None):
    """Get secret from Doppler API"""
    token = os.environ.get('DOPPLER_TOKEN', 'DOPPLER_TOKEN')
    if not token:
        return default
    
    try:
        response = requests.get(
            'https://api.doppler.com/v3/configs/config/secrets/download',
            headers={'Authorization': f'Bearer {token}'},
            params={'format': 'json'}
        )
        response.raise_for_status()
        secrets = response.json()
        return secrets.get(key, default)
    except Exception as e:
        logger.error(f"Error getting Doppler secret {key}: {e}")
        return default

class Config:
    #JWT secret key for signing tokens
    @property
    def SECRET_KEY(self):
        return get_doppler_secret('JWT_DOPPLER_SECRET', 'dev-secret-key')
    