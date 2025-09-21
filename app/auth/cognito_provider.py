# app/auth/cognito_provider.py
import boto3
import requests
from jose import jwk, jwt as jose_jwt
from app.config import settings
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class CognitoProvider:
    def __init__(self):
        self.region = settings.AWS_REGION
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID
        
        # JWK keys URL for token validation
        self.jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        self._jwks = None
    
    async def get_jwks(self):
        """Get JSON Web Key Set from Cognito"""
        if not self._jwks:
            try:
                response = requests.get(self.jwks_url, timeout=10)
                response.raise_for_status()
                self._jwks = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}")
                raise ValueError("Unable to fetch Cognito JWKS")
        return self._jwks
    
    async def validate_token(self, token: str) -> Dict:
        """Validate JWT token from Cognito"""
        try:
            # Get the token header
            headers = jose_jwt.get_unverified_headers(token)
            kid = headers.get('kid')
            
            if not kid:
                raise ValueError("No 'kid' found in token header")
            
            # Get the public key
            jwks = await self.get_jwks()
            key = None
            for jwk_key in jwks['keys']:
                if jwk_key['kid'] == kid:
                    key = jwk.construct(jwk_key)
                    break
            
            if not key:
                raise ValueError("Unable to find appropriate key")
            
            # Verify the token
            payload = jose_jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            return {
                "user_id": payload["sub"],
                "email": payload.get("email"),
                "email_verified": payload.get("email_verified", False),
                "full_name": payload.get("name", ""),
                "username": payload.get("cognito:username"),
                "roles": payload.get("cognito:groups", []),
                "custom_attributes": {k: v for k, v in payload.items() if k.startswith("custom:")}
            }
            
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            raise ValueError(f"Invalid token: {str(e)}")