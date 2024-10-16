import logging
from pipelinecloud.precheck import run_precheck
from pipelinecloud.dbconnection_basic import connect_to_database as connect_basic

# Set up logging to display debug information
logging.basicConfig(level=logging.INFO)


def full_check():
    """
    Run the precheck and both database connection methods.
    """
    logging.info("Running precheck...")
    run_precheck()

    logging.info("Running basic database connection...")
    connect_basic()

if __name__ == "__main__":
    full_check()
