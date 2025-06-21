The Plan: A Layered Approach to Configuration and Abstraction
Here's a high-level plan to address these challenges, focusing on clarity, flexibility, and adherence to good software engineering principles:

1. Centralize Environment Configuration in config/config.py
Introduce a new ENVIRONMENT variable: This will be the single source of truth for the current operational mode. It could be an enum or a string, e.g., ENVIRONMENT = "DEV", ENVIRONMENT = "TEST", ENVIRONMENT = "PROD".
Refine DEBUG_MODE: DEBUG_MODE can remain as a boolean flag for verbose logging and development-specific features, but ENVIRONMENT will define the broader context. A DEV environment might imply DEBUG_MODE = True, while PROD implies DEBUG_MODE = False.
Consider DEV vs. DEBUG: For now, DEV can encompass local development and debugging. If, in the future, you need a distinction between a local developer's machine and a shared development server, we can introduce LOCAL_DEV and SHARED_DEV or similar. For initial implementation, DEV, TEST, PROD is a solid start.
2. Abstract Repository Data Sourcing
Define an Interface: Create an interface (e.g., IRepositoryDataSource) that defines how repository data is retrieved. This interface would have methods like get_repository_snapshot(repo_identifier: str) -> RepositorySnapshotDTO.
Implement Concrete Data Sources:
FilesystemRepositoryDataSource: This implementation would read files directly from a specified local path (e.g., tests/sample_repos/dev_sample/).
DatabaseRepositoryDataSource: This implementation would query the PRP database to retrieve a previously stored RepositorySnapshotDTO.
Dependency Injection: The PRPWorkflowService (our orchestrator) will depend on the IRepositoryDataSource interface, not a concrete implementation.
3. Orchestrator's Role in Data Sourcing
Conditional Instantiation: In main.py (or wherever the PRPWorkflowService is instantiated and dependencies are configured), we will use the config.ENVIRONMENT variable to decide which concrete IRepositoryDataSource implementation to inject into the PRPWorkflowService.
If ENVIRONMENT == "DEV", inject FilesystemRepositoryDataSource.
If ENVIRONMENT == "TEST" or ENVIRONMENT == "PROD", inject DatabaseRepositoryDataSource.
Simplified PRPWorkflowService: The orchestrator itself won't need if/else statements for data sourcing; it will simply call self.repository_data_source.get_repository_snapshot(), trusting that the correct implementation has been provided.
4. Integrating with pytest and run_regression.sh
run_regression.sh: This script can set the ENVIRONMENT variable (e.g., via an environment variable like JENNAI_ENVIRONMENT=TEST) before running pytest or the main application. config.config can then read this environment variable to set its ENVIRONMENT value.
pytest:
Unit Tests: Most unit tests for individual components (like DataCollectService or AIResponseParser) should continue to use mocks, making them independent of the environment configuration.
Integration Tests: For integration tests (like test_full_workflow_with_sample_repo.py), we can use pytest fixtures to temporarily override the ENVIRONMENT setting or inject specific data sources, ensuring tests run against the desired data (e.g., always using dev_sample for a specific test, or a clean test database).
5. Data Flow for Repository Snapshots
DEV Environment: When running in DEV, the PRPWorkflowService will read from the filesystem (dev_sample). It will still persist the snapshot to the database, effectively "ingesting" the filesystem data into the database for later use in TEST or PROD.
TEST/PROD Environments: In these environments, the PRPWorkflowService will retrieve the snapshot from the database. The initial "ingestion" of repository data into the database would happen as a separate, pre-analysis step (e.g., a dedicated ingestion script or API endpoint).