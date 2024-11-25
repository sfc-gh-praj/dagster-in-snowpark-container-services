# snowpark_demo init file

from json import load
from dagster import Definitions, load_assets_from_modules,EnvVar
import logging
# from .assets import snowparkrun 
from .assets.snowparkrun import example_snowpark_asset, run_docker_image_copy_data, run_docker_image_load_data

from .resouces import SnowparkSession
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    # Initialize resources with logging
    logger.debug("Initializing Snowpark resource...")
    snowpark_session = SnowparkSession()

    logger.debug("Snowpark resource initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Snowpark resource: {str(e)}")
    raise

# Creating the definition

defs = Definitions(
    assets=[example_snowpark_asset
            ,run_docker_image_copy_data
            ,run_docker_image_load_data
            ],
    resources={
        "session": snowpark_session,
    },
)
