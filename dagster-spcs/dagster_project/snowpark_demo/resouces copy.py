from pickle import FALSE
from dagster import ConfigurableResource
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from typing import Dict, Any
from pydantic import Field
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SnowparkSession(ConfigurableResource):
    """Resource class for managing Snowpark sessions"""
    
    account: str = Field(
        description="Snowflake account identifier"
    )

    user: str = Field(
        description="Snowflake username"
        
    )
    
    password: str = Field(
        description="Snowflake password"
    )
    
    warehouse: str = Field(
        description="Snowflake warehouse name"
    )
    
    database: str = Field(
        description="Snowflake database name"
    )
    
    schema: str = Field(
        description="Snowflake schema name"
    )
    
    role: str = Field(
        description="Snowflake role name"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._session = None

    def get_session(self) -> Session:
        """Get or create a Snowpark session"""
        logger.debug("found token file...")
        if os.path.isfile("/snowflake/session/token"):
            connection_parameters = {
                'host': os.getenv('SNOWFLAKE_HOST'),
                'port': os.getenv('SNOWFLAKE_PORT'),
                'protocol': "https",
                'account': os.getenv('SNOWFLAKE_ACCOUNT'),
                'authenticator': "oauth",
                'token': open('/snowflake/session/token', 'r').read(),
                'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
                'database': os.getenv('SNOWFLAKE_DATABASE'),
                'schema': os.getenv('SNOWFLAKE_SCHEMA'),
                'client_session_keep_alive': True
            }
        elif not self._session:
            logger.debug("Get env variables...")
            connection_parameters = {
                "account": self.account,
                "user": self.user,
                "password": self.password,
                "warehouse": self.warehouse,
                "database": self.database,
                "schema": self.schema,
            }
            
            # Add role if specified
            if self.role:
                connection_parameters["role"] = self.role
            
        self._session = Session.builder.configs(connection_parameters).create()
        
        return self._session

 