from dagster import asset
from ..resouces import SnowparkSession
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# snowparksession = SnowparkSession.get_session()

@asset
def example_snowpark_asset(session:SnowparkSession):
    """Example asset using the Snowpark resource"""
    logger.info("Running current_time() query")
    snowparksession = session.get_session()
    
    # Example: Execute a query
    results = snowparksession.sql("""
        SELECT current_timestamp()
    """)
    
    # Example: Read a table
    # df = snowparksession.read_table("all_claims_raw")

    results.write.mode("overwrite").save_as_table("Dagster_DemoTable")

    
    # return results

@asset(deps=[example_snowpark_asset])
def run_docker_image_copy_data(session:SnowparkSession) -> None:
    logger.info('Started executing the asset run_docker_image')
    '''
    FUNCTION_NAME: This will value will be dynamic for the functions in the code.
    '''
    snowparksession = session.get_session()
    service_name='function_copy'
    pool_name='PR_STD_POOL_XS'
    image_name='/pr_llmdemo/public/images/dagster:latest'
    snowparksession.sql(f'''DROP SERVICE if exists {service_name}''').collect()
    sql_qry=f'''
                        EXECUTE JOB SERVICE
                        IN COMPUTE POOL {pool_name}
                        NAME={service_name}
                        FROM SPECIFICATION  
                        '
                        spec:
                         container:
                         - name: main
                           image: {image_name}
                           env:
                             SNOWFLAKE_WAREHOUSE: xs_wh
                             FUNCTION_NAME: copy_stage
                           args:
                           - "--query=select current_time() as time,''hello''"
                           - "--result_table=junktable"
                        ';
                    '''

    _=snowparksession.sql(sql_qry).collect()

    job_status = snowparksession.sql(f''' SELECT    parse_json(SYSTEM$GET_SERVICE_STATUS('{service_name}'))[0]['status']::string as Status 
                                ''').collect()[0]['STATUS']
    logger.info(f'Status of the service job [{service_name}] is [{job_status}]')



@asset(deps=[example_snowpark_asset])
def run_docker_image_load_data(session:SnowparkSession) -> None:
    logger.info('Started executing the asset run_docker_image')
    '''
    FUNCTION_NAME: This will value will be dynamic for the functions in the code.
    '''
    snowparksession = session.get_session()
    service_name='function_load'
    pool_name='PR_STD_POOL_S'
    image_name='/pr_llmdemo/public/images/dagster:latest'
    snowparksession.sql(f'''DROP SERVICE if exists {service_name}''').collect()
    sql_qry=f'''
                        EXECUTE JOB SERVICE
                        IN COMPUTE POOL {pool_name}
                        NAME={service_name}
                        FROM SPECIFICATION  
                        '
                        spec:
                         container:
                         - name: main
                           image: {image_name}
                           env:
                             SNOWFLAKE_WAREHOUSE: xs_wh
                             FUNCTION_NAME: load_table
                           args:
                           - "--query=select current_time() as time,''hello''"
                           - "--result_table=junktable"
                        ';
                    '''

    _=snowparksession.sql(sql_qry).collect()

    job_status = snowparksession.sql(f''' SELECT    parse_json(SYSTEM$GET_SERVICE_STATUS('{service_name}'))[0]['status']::string as Status 
                                ''').collect()[0]['STATUS']
    logger.info(f'Status of the service job [{service_name}] is [{job_status}]')
    