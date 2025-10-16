from typing import Any, Dict, List
import logging
import os
import json
import time
from datetime import datetime

class GitHubStorageManager:
    """Manages the GitHub data storage of the research agent."""

    def __init__(self, agent):
        self.agent = agent

    def initialize_github_data_storage(self) -> Dict[str, Any]:
        """Initialize GitHub data storage system with private repositories."""
        print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-STORAGE: Starting GitHub data storage initialization")

        try:
            if not self.agent.github_controller:
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-STORAGE ERROR: GitHub controller not available")
                return {"success": False, "error": "GitHub controller not available"}

            # Create main data repository
            data_repo_name = f"arinn-data-storage-{int(time.time())}"
            data_repo_description = "ARINN Data Storage - Private repository for research data, databases, and configurations"

            print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-STORAGE: Creating private repository: {data_repo_name}")
            data_repo = self.agent.github_controller.create_repository(
                data_repo_name,
                data_repo_description,
                private=True
            )

            if not data_repo:
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-STORAGE ERROR: Failed to create data storage repository")
                return {"success": False, "error": "Failed to create data storage repository"}

            # Store repository info
            self.agent.data_storage_repo = {
                "name": data_repo_name,
                "full_name": data_repo["full_name"],
                "url": data_repo["html_url"],
                "created_at": datetime.now().isoformat()
            }

            print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-STORAGE: Repository created: {data_repo_name}")

            # Create initial data structure documentation
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-STORAGE: Creating data structure documentation")
            data_structure_doc = self._generate_data_structure_documentation()
            self.agent.github_controller.create_file(
                self.agent.github_controller.username,
                data_repo_name,
                "DATA_STRUCTURE.md",
                data_structure_doc,
                "Initialize data storage structure documentation"
            )

            # Upload initial data files
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-STORAGE: Uploading initial data files")
            self._upload_initial_data_files(data_repo_name)

            print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-STORAGE: GitHub data storage initialized successfully: {data_repo_name}")
            return {
                "success": True,
                "repository": self.agent.data_storage_repo,
                "message": "GitHub data storage system initialized successfully"
            }

        except Exception as e:
            error_msg = f"Failed to initialize GitHub data storage: {e}"
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-STORAGE CRITICAL ERROR: {error_msg}")
            return {"success": False, "error": error_msg}

    def _generate_data_structure_documentation(self) -> str:
        """Generate documentation for the data storage structure."""
        doc = "# ARINN Data Storage Structure\n\nThis repository contains ARINN's research data, databases, and configuration files.\n\n## Directory Structure\n\n```\n/databases/          # SQLite database files\n    ├── research.db          # Main research database\n    ├── image_ratings.db     # Image rating data\n    └── backup_*.db         # Database backups\n\n/configurations/     # Configuration files\n    ├── safety_config.json   # Safety settings\n    ├── research_state.json  # Current research state\n    └── agent_config.json    # Agent configuration\n\n/research_data/      # Research results and findings\n    ├── topics/              # Topic-specific data\n    ├── web_scraping/        # Scraped content\n    └── analysis/            # Analysis results\n\n/logs/               # Application logs and metrics\n    ├── performance.log      # Performance metrics\n    ├── research.log         # Research activity logs\n    └── error.log           # Error logs\n\n/backups/            # Automated backups\n    ├── daily/              # Daily backups\n    ├── weekly/             # Weekly backups\n    └── monthly/            # Monthly backups\n```\n\n## Data Management\n\n- **Automatic Sync**: Data is automatically synced between local storage and GitHub\n- **Version Control**: All data changes are tracked with Git versioning\n- **Backup**: Regular automated backups ensure data safety\n- **Privacy**: All repositories are private and secure\n\n## File Naming Convention\n\n- Database files: `{name}_{timestamp}.db`\n- Config files: `{component}_config.json`\n- Log files: `{component}_{date}.log`\n- Backup files: `backup_{timestamp}.{ext}`\n\n## Access Control\n\n- Repository is private and only accessible by ARINN\n- Data encryption may be applied for sensitive information\n- Access tokens are securely managed\n\n---\n*Generated by ARINN Data Storage System*\n"
        return doc

    def _upload_initial_data_files(self, repo_name: str):
        """Upload initial data files to the GitHub repository."""
        try:
            # Upload database files
            self._upload_database_files(repo_name)

            # Upload configuration files
            self._upload_config_files(repo_name)

            # Upload research data
            self._upload_research_data(repo_name)

            # Upload logs
            self._upload_log_files(repo_name)

        except Exception as e:
            logging.warning(f"Failed to upload initial data files: {e}")

    def _upload_database_files(self, repo_name: str):
        """Upload database files to GitHub."""
        try:
            # Find database files in data directory
            data_dir = getattr(self.agent, 'data_dir', './data')
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith('.db'):
                        file_path = os.path.join(data_dir, file)
                        rel_path = f"databases/{file}"

                        try:
                            with open(file_path, 'rb') as f:
                                content = f.read()

                            # GitHub API requires base64 encoding for binary files
                            import base64
                            encoded_content = base64.b64encode(content).decode('utf-8')

                            self.agent.github_controller.create_file(
                                self.agent.github_controller.username,
                                repo_name,
                                rel_path,
                                encoded_content,
                                f"Upload database file: {file}",
                                binary=True
                            )
                            logging.info(f"Uploaded database file: {file}")

                        except Exception as e:
                            logging.warning(f"Failed to upload database file {file}: {e}")

        except Exception as e:
            logging.warning(f"Database upload process failed: {e}")

    def _upload_config_files(self, repo_name: str):
        """Upload configuration files to GitHub."""
        try:
            config_files = [
                'safety_config.json',
                'research_state.json',
                'agent_config.json'
            ]

            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        rel_path = f"configurations/{config_file}"
                        self.agent.github_controller.create_file(
                            self.agent.github_controller.username,
                            repo_name,
                            rel_path,
                            content,
                            f"Upload configuration file: {config_file}"
                        )
                        logging.info(f"Uploaded config file: {config_file}")

                    except Exception as e:
                        logging.warning(f"Failed to upload config file {config_file}: {e}")

        except Exception as e:
            logging.warning(f"Config upload process failed: {e}")

    def _upload_research_data(self, repo_name: str):
        """Upload research data files to GitHub."""
        try:
            # Upload research results and findings
            research_files = [
                'self_improvement_test_results.json',
                'MAXIMUM_POWER_GUIDE.md',
                'README.md'
            ]

            for research_file in research_files:
                if os.path.exists(research_file):
                    try:
                        with open(research_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        rel_path = f"research_data/{research_file}"
                        self.agent.github_controller.create_file(
                            self.agent.github_controller.username,
                            repo_name,
                            rel_path,
                            content,
                            f"Upload research data: {research_file}"
                        )
                        logging.info(f"Uploaded research file: {research_file}")

                    except Exception as e:
                        logging.warning(f"Failed to upload research file {research_file}: {e}")

        except Exception as e:
            logging.warning(f"Research data upload failed: {e}")

    def _upload_log_files(self, repo_name: str):
        """Upload log files to GitHub."""
        try:
            log_files = [
                'security_audit.log'
            ]

            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        rel_path = f"logs/{log_file}"
                        self.agent.github_controller.create_file(
                            self.agent.github_controller.username,
                            repo_name,
                            rel_path,
                            content,
                            f"Upload log file: {log_file}"
                        )
                        logging.info(f"Uploaded log file: {log_file}")

                    except Exception as e:
                        logging.warning(f"Failed to upload log file {log_file}: {e}")

        except Exception as e:
            logging.warning(f"Log upload process failed: {e}")

    def sync_data_to_github(self, include_databases: bool = True, include_configs: bool = True) -> Dict[str, Any]:
        """Sync current data to GitHub repository."""
        print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC: Starting data sync to GitHub")
        print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC: Config - databases={include_databases}, configs={include_configs}")

        try:
            if not self.agent.github_controller or not hasattr(self.agent, 'data_storage_repo'):
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC ERROR: GitHub data storage not initialized")
                return {"success": False, "error": "GitHub data storage not initialized"}

            repo_name = self.agent.data_storage_repo["name"]
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC: Syncing to repository: {repo_name}")

            sync_results = {
                "databases_synced": 0,
                "configs_synced": 0,
                "timestamp": datetime.now().isoformat()
            }

            if include_databases:
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC: Syncing database files")
                db_count = self._sync_databases_to_github(repo_name)
                sync_results["databases_synced"] = db_count
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC: Synced {db_count} database files")

            if include_configs:
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC: Syncing configuration files")
                config_count = self._sync_configs_to_github(repo_name)
                sync_results["configs_synced"] = config_count
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC: Synced {config_count} config files")

            success_msg = f"Data sync completed: {sync_results['databases_synced']} databases, {sync_results['configs_synced']} configs"
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC: {success_msg}")

            return {
                "success": True,
                "sync_results": sync_results,
                "message": success_msg
            }

        except Exception as e:
            error_msg = f"Data sync to GitHub failed: {e}"
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - GITHUB-SYNC CRITICAL ERROR: {error_msg}")
            return {"success": False, "error": error_msg}

    def _sync_databases_to_github(self, repo_name: str) -> int:
        """Sync database files to GitHub."""
        synced_count = 0
        try:
            data_dir = getattr(self.agent, 'data_dir', './data')
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith('.db'):
                        file_path = os.path.join(data_dir, file)
                        rel_path = f"databases/{file}"

                        try:
                            with open(file_path, 'rb') as f:
                                content = f.read()

                            import base64
                            encoded_content = base64.b64encode(content).decode('utf-8')

                            # Try to update existing file, create if doesn't exist
                            try:
                                self.agent.github_controller.update_file(
                                    self.agent.github_controller.username,
                                    repo_name,
                                    rel_path,
                                    encoded_content,
                                    f"Sync database: {file}"
                                )
                            except:
                                self.agent.github_controller.create_file(
                                    self.agent.github_controller.username,
                                    repo_name,
                                    rel_path,
                                    encoded_content,
                                    f"Create database: {file}",
                                    binary=True
                                )

                            synced_count += 1
                            logging.info(f"Synced database: {file}")

                        except Exception as e:
                            logging.warning(f"Failed to sync database {file}: {e}")

        except Exception as e:
            logging.warning(f"Database sync process failed: {e}")

        return synced_count

    def _sync_configs_to_github(self, repo_name: str) -> int:
        """Sync configuration files to GitHub."""
        synced_count = 0
        try:
            config_files = [
                'safety_config.json',
                'research_state.json'
            ]

            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        rel_path = f"configurations/{config_file}"

                        # Try to update existing file, create if doesn't exist
                        try:
                            self.agent.github_controller.update_file(
                                self.agent.github_controller.username,
                                repo_name,
                                rel_path,
                                content,
                                f"Sync config: {config_file}"
                            )
                        except:
                            self.agent.github_controller.create_file(
                                self.agent.github_controller.username,
                                repo_name,
                                rel_path,
                                content,
                                f"Create config: {config_file}"
                            )

                        synced_count += 1
                        logging.info(f"Synced config: {config_file}")

                    except Exception as e:
                        logging.warning(f"Failed to sync config {config_file}: {e}")

        except Exception as e:
            logging.warning(f"Config sync process failed: {e}")

        return synced_count

    def download_data_from_github(self, include_databases: bool = True, include_configs: bool = True) -> Dict[str, Any]:
        """Download data from GitHub repository."""
        try:
            if not self.agent.github_controller or not hasattr(self.agent, 'data_storage_repo'):
                return {"success": False, "error": "GitHub data storage not initialized"}

            repo_name = self.agent.data_storage_repo["name"]
            download_results = {
                "databases_downloaded": 0,
                "configs_downloaded": 0,
                "timestamp": datetime.now().isoformat()
            }

            if include_databases:
                db_count = self._download_databases_from_github(repo_name)
                download_results["databases_downloaded"] = db_count

            if include_configs:
                config_count = self._download_configs_from_github(repo_name)
                download_results["configs_downloaded"] = config_count

            return {
                "success": True,
                "download_results": download_results,
                "message": f"Data download completed: {download_results['databases_downloaded']} databases, {download_results['configs_downloaded']} configs"
            }

        except Exception as e:
            error_msg = f"Data download from GitHub failed: {e}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}

    def _download_databases_from_github(self, repo_name: str) -> int:
        """Download database files from GitHub."""
        downloaded_count = 0
        try:
            # Get list of database files from GitHub
            contents = self.agent.github_controller.get_repository_contents(
                self.agent.github_controller.username,
                repo_name,
                "databases"
            )

            if contents:
                data_dir = getattr(self.agent, 'data_dir', './data')
                os.makedirs(data_dir, exist_ok=True)

                for item in contents:
                    if item["name"].endswith('.db'):
                        try:
                            # Download file content
                            file_content = self.agent.github_controller.get_file_content(
                                self.agent.github_controller.username,
                                repo_name,
                                item["path"]
                            )

                            if file_content and "content" in file_content:
                                import base64
                                # Decode base64 content
                                decoded_content = base64.b64decode(file_content["content"])

                                # Save to local file
                                local_path = os.path.join(data_dir, item["name"])
                                with open(local_path, 'wb') as f:
                                    f.write(decoded_content)

                                downloaded_count += 1
                                logging.info(f"Downloaded database: {item['name']}")

                        except Exception as e:
                            logging.warning(f"Failed to download database {item['name']}: {e}")

        except Exception as e:
            logging.warning(f"Database download process failed: {e}")

        return downloaded_count

    def _download_configs_from_github(self, repo_name: str) -> int:
        """Download configuration files from GitHub."""
        downloaded_count = 0
        try:
            # Get list of config files from GitHub
            contents = self.agent.github_controller.get_repository_contents(
                self.agent.github_controller.username,
                repo_name,
                "configurations"
            )

            if contents:
                for item in contents:
                    if item["name"].endswith('.json'):
                        try:
                            # Download file content
                            file_content = self.agent.github_controller.get_file_content(
                                self.agent.github_controller.username,
                                repo_name,
                                item["path"]
                            )

                            if file_content and "content" in file_content:
                                import base64
                                # Decode base64 content (GitHub returns base64 even for text)
                                decoded_content = base64.b64decode(file_content["content"]).decode('utf-8')

                                # Save to local file
                                with open(item["name"], 'w', encoding='utf-8') as f:
                                    f.write(decoded_content)

                                downloaded_count += 1
                                logging.info(f"Downloaded config: {item['name']}")

                        except Exception as e:
                            logging.warning(f"Failed to download config {item['name']}: {e}")

        except Exception as e:
            logging.warning(f"Config download process failed: {e}")

        return downloaded_count

    def create_data_backup(self, backup_type: str = "manual") -> Dict[str, Any]:
        """Create a comprehensive data backup on GitHub."""
        try:
            if not self.agent.github_controller or not hasattr(self.agent, 'data_storage_repo'):
                return {"success": False, "error": "GitHub data storage not initialized"}

            repo_name = self.agent.data_storage_repo["name"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create backup directory structure
            backup_path = f"backups/{backup_type}/{timestamp}"
            backup_info = {
                "backup_type": backup_type,
                "timestamp": timestamp,
                "created_at": datetime.now().isoformat(),
                "files_backed_up": []
            }

            # Backup databases
            db_backups = self._create_database_backup(repo_name, backup_path)
            backup_info["files_backed_up"].extend(db_backups)

            # Backup configurations
            config_backups = self._create_config_backup(repo_name, backup_path)
            backup_info["files_backed_up"].extend(config_backups)

            # Create backup manifest
            manifest_content = json.dumps(backup_info, indent=2)
            manifest_path = f"{backup_path}/backup_manifest.json"

            self.agent.github_controller.create_file(
                self.agent.github_controller.username,
                repo_name,
                manifest_path,
                manifest_content,
                f"Create {backup_type} backup manifest: {timestamp}"
            )

            logging.info(f"Data backup completed: {backup_type} backup with {len(backup_info['files_backed_up'])} files")

            return {
                "success": True,
                "backup_info": backup_info,
                "message": f"{backup_type.title()} backup completed successfully"
            }

        except Exception as e:
            error_msg = f"Data backup failed: {e}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}

    def _create_database_backup(self, repo_name: str, backup_path: str) -> List[str]:
        """Create database backup files."""
        backed_up_files = []
        try:
            data_dir = getattr(self.agent, 'data_dir', './data')
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith('.db'):
                        file_path = os.path.join(data_dir, file)
                        backup_file_path = f"{backup_path}/databases/{file}"

                        try:
                            with open(file_path, 'rb') as f:
                                content = f.read()

                            import base64
                            encoded_content = base64.b64encode(content).decode('utf-8')

                            self.agent.github_controller.create_file(
                                self.agent.github_controller.username,
                                repo_name,
                                backup_file_path,
                                encoded_content,
                                f"Database backup: {file}",
                                binary=True
                            )

                            backed_up_files.append(backup_file_path)
                            logging.info(f"Backed up database: {file}")

                        except Exception as e:
                            logging.warning(f"Failed to backup database {file}: {e}")

        except Exception as e:
            logging.warning(f"Database backup process failed: {e}")

        return backed_up_files

    def _create_config_backup(self, repo_name: str, backup_path: str) -> List[str]:
        """Create configuration backup files."""
        backed_up_files = []
        try:
            config_files = [
                'safety_config.json',
                'research_state.json'
            ]

            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        backup_file_path = f"{backup_path}/configurations/{config_file}"

                        self.agent.github_controller.create_file(
                            self.agent.github_controller.username,
                            repo_name,
                            backup_file_path,
                            content,
                            f"Config backup: {config_file}"
                        )

                        backed_up_files.append(backup_file_path)
                        logging.info(f"Backed up config: {config_file}")

                    except Exception as e:
                        logging.warning(f"Failed to backup config {config_file}: {e}")

        except Exception as e:
            logging.warning(f"Config backup process failed: {e}")

        return backed_up_files

    def get_data_storage_status(self) -> Dict[str, Any]:
        """Get status of GitHub data storage system."""
        try:
            if not hasattr(self.agent, 'data_storage_repo'):
                return {
                    "initialized": False,
                    "message": "GitHub data storage not initialized"
                }

            repo_info = self.agent.data_storage_repo

            # Get repository details from GitHub
            try:
                repo_details = self.agent.github_controller.get_repository(
                    self.agent.github_controller.username,
                    repo_info["name"]
                )

                return {
                    "initialized": True,
                    "repository": repo_info,
                    "github_info": {
                        "private": repo_details.get("private", True),
                        "size_kb": repo_details.get("size", 0),
                        "updated_at": repo_details.get("updated_at"),
                        "default_branch": repo_details.get("default_branch", "main")
                    },
                    "last_sync": getattr(self.agent, 'last_data_sync', None),
                    "status": "active"
                }

            except Exception as e:
                return {
                    "initialized": True,
                    "repository": repo_info,
                    "error": f"Could not fetch GitHub info: {e}",
                    "status": "connection_issue"
                }

        except Exception as e:
            return {
                "initialized": False,
                "error": str(e),
                "status": "error"
            }