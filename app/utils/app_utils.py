import asyncio
import logging
import time
import pandas as pd
from neo4j import GraphDatabase, Result
from typing import Dict, Any, Union, Optional, List, Tuple
from fastapi import Query

from app.utils import enums
from app.config.settings import app_settings


# Configure the standard logger with our custom handler
logger = logging.getLogger("graph-api")
logger.setLevel(app_settings.log_level_int)

# Remove any existing handlers to avoid duplicates
for handler in logger.handlers:
    logger.removeHandler(handler)

# Configure handler with format from settings
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(app_settings.log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Make sure it propagates to the root logger
logger.propagate = True


# Initialize Neo4j connection parameters
try:
    neo = enums.neo4j
except Exception as e:
    logger.error(f"Failed to initialize Neo4j parameters: {e}")
    neo = None


# Database connection dependency
async def get_db_params(
    uri: Optional[str] = Query(None, description="Override Neo4j URI"),
    database: Optional[str] = Query(None, description="Override Neo4j database name"),
    username: Optional[str] = Query(None, description="Override Neo4j username"),
    password: Optional[str] = Query(None, description="Override Neo4j password"),
) -> Dict[str, Any]:
    """Get database connection parameters with optional overrides"""
    params = {}
    if uri:
        params["uri"] = uri
    if database:
        params["database"] = database
    if username:
        params["username"] = username
    if password:
        params["password"] = password
    return params


def read_cypher_to_dataframe(
    query: str,
    uri: str = neo.uri if neo else None,
    username: str = neo.username if neo else None,
    password: str = neo.password if neo else None,
    database: str = neo.database if neo else None,
    params: Dict[str, Any] = {},
) -> pd.DataFrame:
    """
    Executes a read Cypher query and returns the result as a pandas DataFrame.

    Args:
        query (str): A valid Cypher query string for reading data.
        uri (str): The URI of the Neo4j instance.
        username (str): The username for the Neo4j instance.
        password (str): The password for the Neo4j instance.
        database (str): The target database within the Neo4j instance.
        params (Dict[str, Any): Parameters to be passed to the query.
    Returns:
        pd.DataFrame: A DataFrame containing the query results.
    """
    start_time = time.time()

    if not all([uri, username, password, database]):
        raise ValueError("Neo4j connection parameters are missing")

    driver = None
    try:
        # Create a Neo4j driver instance
        driver = GraphDatabase.driver(uri=f"{uri}:7687", auth=(username, password))

        # Execute the query and transform the result into a DataFrame
        df = driver.execute_query(
            query_=query,
            database_=database,
            result_transformer_=Result.to_df,
            parameters_=params,
        )

        execution_time = time.time() - start_time
        logger.info(
            f"Read query completed in {execution_time:.2f}s. Retrieved {len(df)} rows."
        )

        return df

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"Error executing read query after {execution_time:.2f}s: {str(e)}"
        )
        raise RuntimeError(f"Neo4j query '{query}' failed: {e}")

    finally:
        if driver:
            driver.close()


def read_cypher_to_dataframe_batched(
    query: str,
    batch_size: int = 5000,
    max_batches: int = 1000,
    uri: str = neo.uri if neo else None,
    username: str = neo.username if neo else None,
    password: str = neo.password if neo else None,
    database: str = neo.database if neo else None,
) -> pd.DataFrame:
    """
    Execute a Cypher query and convert results to a pandas DataFrame,
    processed in batches to handle large result sets.

    Args:
        query (str): A valid Cypher query string
        batch_size (int): Number of records to retrieve per batch
        max_batches (int): Maximum number of batches to process
        uri (str): The URI of the Neo4j instance
        username (str): The username for the Neo4j instance
        password (str): The password for the Neo4j instance
        database (str): The target database within the Neo4j instance

    Returns:
        pd.DataFrame: A DataFrame containing all query results
    """
    all_results = []

    # Instead of modifying the query, we'll use explicit SKIP values
    for batch_num in range(max_batches):
        skip_value = batch_num * batch_size

        # Use parameters for SKIP and LIMIT values
        params = {"skip_value": skip_value, "limit_value": batch_size}

        # Add SKIP and LIMIT clauses to the query if not already present
        if "SKIP" not in query and "LIMIT" not in query:
            paged_query = f"{query} SKIP $skip_value LIMIT $limit_value"
        else:
            logger.warning("Query already contains SKIP/LIMIT - using as is")
            paged_query = query

        logger.info(f"Executing batch {batch_num+1}, skipping {skip_value} records")

        try:
            batch_results = read_cypher_to_dataframe(
                query=paged_query,
                uri=uri,
                username=username,
                password=password,
                database=database,
                params=params,
            )

            if batch_results.empty:
                logger.info(f"No more results after batch {batch_num}, stopping")
                break

            all_results.append(batch_results)
            logger.info(f"Batch {batch_num+1} returned {len(batch_results)} records")

            # If we got fewer records than the batch size, we've reached the end
            if len(batch_results) < batch_size:
                break

        except Exception as e:
            logger.error(f"Error processing batch {batch_num+1}: {str(e)}")
            # Continue with next batch or break depending on the error
            if "batch_num" in str(e):
                # If the error is related to the batch parameter, break the loop
                break
            else:
                # For other errors, try the next batch
                continue

    if all_results:
        result_df = pd.concat(all_results).reset_index(drop=True)
        logger.info(
            f"Combined results: {len(result_df)} total records from {len(all_results)} batches"
        )
        return result_df
    else:
        logger.warning("No results returned from any batch")
        return pd.DataFrame()


async def execute_query_async(
    query: str,
    uri: str = neo.uri if neo else None,
    username: str = neo.username if neo else None,
    password: str = neo.password if neo else None,
    database: str = neo.database if neo else None,
    params: Dict[str, Any] = {},
) -> pd.DataFrame:
    """
    Execute query in thread pool to avoid blocking
    @Args:
        query: The Cypher query to execute
        uri: The URI of the Neo4j database
        username: The username for the Neo4j database
        password: The password for the Neo4j database
        database: The database to use
        params: The parameters for the Cypher query
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: read_cypher_to_dataframe(
            query=query,
            uri=uri,
            username=username,
            password=password,
            database=database,
            params=params,
        ),
    )


async def execute_batch_async(
    queries_batch: List[str],
    uri: str = neo.uri if neo else None,
    username: str = neo.username if neo else None,
    password: str = neo.password if neo else None,
    database: str = neo.database if neo else None,
) -> List[pd.DataFrame]:
    """
    Execute batch of queries concurrently
    @Args:
        queries_batch: A list of Cypher queries to execute
    """
    semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent queries

    async def execute_with_semaphore(query: str):
        async with semaphore:
            return await execute_query_async(query)

    tasks = [execute_with_semaphore(query) for query in queries_batch]
    return await asyncio.gather(*tasks)


async def execute_cypher_query(
    query: str,
    parameters: Dict[str, Any] = None,
    uri: str = neo.uri if neo else None,
    username: str = neo.username if neo else None,
    password: str = neo.password if neo else None,
    database: str = neo.database if neo else None,
) -> List[Dict[str, Any]]:
    """
    Execute a Cypher query asynchronously and return results as a list of dictionaries.

    Args:
        query (str): The Cypher query to execute
        parameters (Dict[str, Any]): Parameters for the query
        uri (str): The URI of the Neo4j instance
        username (str): The username for the Neo4j instance
        password (str): The password for the Neo4j instance
        database (str): The target database within the Neo4j instance

    Returns:
        List[Dict[str, Any]]: Query results as list of dictionaries

    Raises:
        ValueError: If connection parameters are missing
        RuntimeError: If query execution fails
    """
    start_time = time.time()

    if not all([uri, username, password, database]):
        raise ValueError("Neo4j connection parameters are missing")

    if parameters is None:
        parameters = {}

    def _execute_query():
        driver = None
        try:
            # Create a Neo4j driver instance
            driver = GraphDatabase.driver(uri=f"{uri}:7687", auth=(username, password))

            # Execute the query and get records
            records, summary, keys = driver.execute_query(
                query_=query,
                database_=database,
                parameters_=parameters,
            )

            # Convert records to list of dictionaries
            result = [record.data() for record in records]

            execution_time = time.time() - start_time
            logger.info(
                f"Query completed in {execution_time:.2f}s. Retrieved {len(result)} records."
            )

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing query after {execution_time:.2f}s: {str(e)}")
            raise RuntimeError(f"Neo4j query failed: {e}")

        finally:
            if driver:
                driver.close()

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _execute_query)
