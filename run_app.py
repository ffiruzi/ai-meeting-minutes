#!/usr/bin/env python3


import sys
import os
import subprocess
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
import importlib.util
from datetime import datetime


# ================================
# CONFIGURATION
# ================================

class AppConfig:
    """Enhanced application configuration."""

    APP_NAME = "Meeting Minutes Generator Pro"
    VERSION = "1.0.0-day6"
    STREAMLIT_APP = "streamlit_app.py"
    DEFAULT_PORT = 8501

    # Day 6 Dependencies - Fixed package names for import
    REQUIRED_PACKAGES = {
        'streamlit': '1.28.0',
        'openai': '1.0.0',
        'langgraph': '0.0.40',
        'dotenv': '1.0.0',  # python-dotenv imports as 'dotenv'
        'pydantic': '2.0.0',
        'reportlab': '3.6.0',  # Day 6: PDF generation
        'PIL': '8.0.0',  # Pillow imports as 'PIL'
    }

    OPTIONAL_PACKAGES = {
        'pytest': '7.0.0',
        'black': '23.0.0',
        'flake8': '6.0.0',
        'mypy': '1.0.0'
    }

    REQUIRED_DIRECTORIES = [
        'src',
        'src/agents',
        'src/utils',
        'src/sample_data',
        'tests'
    ]

    REQUIRED_FILES = [
        'streamlit_app.py',
        'src/workflow.py',
        'src/utils/openai_client.py',
        'src/agents/__init__.py',
        '.env.example'
    ]


# ================================
# LOGGING SETUP
# ================================

def setup_logging(debug_mode: bool = False) -> logging.Logger:
    """Setup enhanced logging configuration."""
    log_level = logging.DEBUG if debug_mode else logging.INFO

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Setup logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log")
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {log_level}")

    return logger


# ================================
# DEPENDENCY VALIDATION
# ================================

class DependencyValidator:
    """Enhanced dependency validation and management."""

    def __init__(self, logger: logging.Logger):
        """Initialize dependency validator."""
        self.logger = logger
        self.config = AppConfig()

    def check_python_version(self) -> Tuple[bool, str]:
        """Check Python version compatibility."""
        try:
            current_version = sys.version_info
            required_version = (3, 8)  # Minimum Python 3.8

            if current_version >= required_version:
                version_str = f"{current_version.major}.{current_version.minor}.{current_version.micro}"
                self.logger.info(f"✅ Python version: {version_str}")
                return True, f"Python {version_str}"
            else:
                current_str = f"{current_version.major}.{current_version.minor}"
                required_str = f"{required_version[0]}.{required_version[1]}"
                error_msg = f"Python {required_str}+ required, found {current_str}"
                self.logger.error(f"❌ {error_msg}")
                return False, error_msg

        except Exception as e:
            self.logger.error(f"❌ Failed to check Python version: {e}")
            return False, f"Version check failed: {e}"

    def check_package_installation(self, package_name: str, required_version: str = None) -> Tuple[bool, str]:
        """Check if a package is installed with optional version checking."""
        try:
            spec = importlib.util.find_spec(package_name)
            if spec is None:
                return False, f"Package '{package_name}' not found"

            # Try to get version if available
            try:
                module = importlib.import_module(package_name)
                version = getattr(module, '__version__', 'unknown')

                if required_version and version != 'unknown':
                    # Improved version comparison using semantic versioning
                    if self._compare_versions(version, required_version):
                        return True, f"{package_name} {version}"
                    else:
                        return False, f"{package_name} {version} < {required_version}"

                return True, f"{package_name} {version}"

            except Exception:
                return True, f"{package_name} (version unknown)"

        except Exception as e:
            return False, f"Error checking {package_name}: {e}"

    def _compare_versions(self, current: str, required: str) -> bool:
        """Compare semantic versions. Returns True if current >= required."""
        try:
            # Simple semantic version comparison
            def version_tuple(v):
                # Split version and convert to integers, handle pre-release suffixes
                parts = v.split('.')
                result = []
                for part in parts:
                    # Extract numeric part only (ignore alpha, beta, rc, etc.)
                    numeric_part = ''
                    for char in part:
                        if char.isdigit():
                            numeric_part += char
                        else:
                            break
                    result.append(int(numeric_part) if numeric_part else 0)
                # Ensure we have at least 3 parts (major.minor.patch)
                while len(result) < 3:
                    result.append(0)
                return tuple(result[:3])  # Only compare first 3 parts

            current_tuple = version_tuple(current)
            required_tuple = version_tuple(required)

            return current_tuple >= required_tuple

        except Exception:
            # If version comparison fails, assume it's okay
            return True

    def validate_all_dependencies(self) -> Dict[str, Any]:
        """Validate all required and optional dependencies."""
        self.logger.info("🔍 Validating dependencies...")

        results = {
            'python_ok': False,
            'python_info': '',
            'required_packages': {},
            'optional_packages': {},
            'missing_required': [],
            'missing_optional': [],
            'all_required_ok': False
        }

        # Check Python version
        python_ok, python_info = self.check_python_version()
        results['python_ok'] = python_ok
        results['python_info'] = python_info

        # Check required packages
        for package, version in self.config.REQUIRED_PACKAGES.items():
            package_ok, package_info = self.check_package_installation(package, version)
            results['required_packages'][package] = {
                'installed': package_ok,
                'info': package_info
            }

            if package_ok:
                self.logger.info(f"✅ {package_info}")
            else:
                self.logger.error(f"❌ {package_info}")
                results['missing_required'].append(package)

        # Check optional packages
        for package, version in self.config.OPTIONAL_PACKAGES.items():
            package_ok, package_info = self.check_package_installation(package)
            results['optional_packages'][package] = {
                'installed': package_ok,
                'info': package_info
            }

            if package_ok:
                self.logger.info(f"✅ {package_info} (optional)")
            else:
                self.logger.warning(f"⚠️  {package_info} (optional)")
                results['missing_optional'].append(package)

        # Overall status
        results['all_required_ok'] = python_ok and len(results['missing_required']) == 0

        return results

    def generate_install_commands(self, missing_packages: List[str]) -> List[str]:
        """Generate pip install commands for missing packages."""
        if not missing_packages:
            return []

        commands = []

        # Map import names back to pip package names
        package_name_map = {
            'dotenv': 'python-dotenv',
            'PIL': 'Pillow'
        }

        # Group packages for efficient installation
        package_list = []
        for package in missing_packages:
            # Map import name back to pip package name
            pip_package = package_name_map.get(package, package)

            if package in self.config.REQUIRED_PACKAGES:
                version = self.config.REQUIRED_PACKAGES[package]
                package_list.append(f"{pip_package}>={version}")
            else:
                package_list.append(pip_package)

        if package_list:
            commands.append(f"pip install {' '.join(package_list)}")

        return commands


# ================================
# SYSTEM VALIDATION
# ================================

class SystemValidator:
    """Enhanced system validation and setup."""

    def __init__(self, logger: logging.Logger):
        """Initialize system validator."""
        self.logger = logger
        self.config = AppConfig()

    def validate_directory_structure(self) -> Tuple[bool, List[str]]:
        """Validate required directory structure."""
        self.logger.info("📁 Validating directory structure...")

        missing_dirs = []

        for directory in self.config.REQUIRED_DIRECTORIES:
            dir_path = Path(directory)
            if not dir_path.exists():
                missing_dirs.append(directory)
                self.logger.error(f"❌ Missing directory: {directory}")
            else:
                self.logger.info(f"✅ Directory exists: {directory}")

        return len(missing_dirs) == 0, missing_dirs

    def validate_required_files(self) -> Tuple[bool, List[str]]:
        """Validate required files exist."""
        self.logger.info("📄 Validating required files...")

        missing_files = []

        for file_path in self.config.REQUIRED_FILES:
            if not Path(file_path).exists():
                missing_files.append(file_path)
                self.logger.error(f"❌ Missing file: {file_path}")
            else:
                self.logger.info(f"✅ File exists: {file_path}")

        return len(missing_files) == 0, missing_files

    def validate_environment_setup(self) -> Tuple[bool, str]:
        """Validate environment configuration."""
        self.logger.info("🔧 Validating environment setup...")

        try:
            from dotenv import load_dotenv
            load_dotenv()

            # Check for .env file
            env_file = Path('.env')
            env_example = Path('.env.example')

            if not env_file.exists():
                if env_example.exists():
                    self.logger.warning("⚠️  .env file missing, but .env.example exists")
                    return False, "Please copy .env.example to .env and configure your API keys"
                else:
                    self.logger.error("❌ No .env or .env.example file found")
                    return False, "Environment configuration files missing"

            # Check OpenAI API key
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                self.logger.warning("⚠️  OPENAI_API_KEY not set in environment")
                return False, "OPENAI_API_KEY not configured"

            if not openai_key.startswith('sk-'):
                self.logger.warning("⚠️  OPENAI_API_KEY format appears invalid")
                return False, "OPENAI_API_KEY format appears invalid"

            self.logger.info("✅ Environment configuration looks good")
            return True, "Environment properly configured"

        except ImportError:
            self.logger.error("❌ python-dotenv not installed")
            return False, "python-dotenv package required"
        except Exception as e:
            self.logger.error(f"❌ Environment validation failed: {e}")
            return False, f"Environment validation error: {e}"

    def create_missing_directories(self, missing_dirs: List[str]) -> bool:
        """Create missing directories."""
        try:
            for directory in missing_dirs:
                Path(directory).mkdir(parents=True, exist_ok=True)
                self.logger.info(f"✅ Created directory: {directory}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to create directories: {e}")
            return False


# ================================
# DAY 6 FEATURE VALIDATION
# ================================

class Day6FeatureValidator:
    """Validate Day 6 specific features."""

    def __init__(self, logger: logging.Logger):
        """Initialize Day 6 feature validator."""
        self.logger = logger

    def validate_pdf_generation(self) -> Tuple[bool, str]:
        """Validate PDF generation capabilities."""
        try:
            # Add src to path if not already there
            import sys
            if 'src' not in sys.path:
                sys.path.insert(0, 'src')

            from utils.pdf_generator import validate_pdf_requirements

            available, message = validate_pdf_requirements()

            if available:
                self.logger.info(f"✅ PDF generation: {message}")
                return True, message
            else:
                self.logger.warning(f"⚠️  PDF generation: {message}")
                return False, message

        except ImportError:
            message = "PDF generator module not found"
            self.logger.error(f"❌ {message}")
            return False, message
        except Exception as e:
            message = f"PDF validation failed: {e}"
            self.logger.error(f"❌ {message}")
            return False, message

    def validate_analytics(self) -> Tuple[bool, str]:
        """Validate analytics functionality."""
        try:
            # Add src to path if not already there
            import sys
            if 'src' not in sys.path:
                sys.path.insert(0, 'src')

            from utils.analytics import test_analytics

            if test_analytics():
                message = "Analytics functionality working"
                self.logger.info(f"✅ {message}")
                return True, message
            else:
                message = "Analytics test failed"
                self.logger.error(f"❌ {message}")
                return False, message

        except ImportError:
            message = "Analytics module not found"
            self.logger.error(f"❌ {message}")
            return False, message
        except Exception as e:
            message = f"Analytics validation failed: {e}"
            self.logger.error(f"❌ {message}")
            return False, message

    def validate_user_preferences(self) -> Tuple[bool, str]:
        """Validate user preferences functionality."""
        try:
            # Add src to path if not already there
            import sys
            if 'src' not in sys.path:
                sys.path.insert(0, 'src')

            from utils.user_preferences import test_preferences

            if test_preferences():
                message = "User preferences working"
                self.logger.info(f"✅ {message}")
                return True, message
            else:
                message = "User preferences test failed"
                self.logger.error(f"❌ {message}")
                return False, message

        except ImportError:
            message = "User preferences module not found"
            self.logger.error(f"❌ {message}")
            return False, message
        except Exception as e:
            message = f"User preferences validation failed: {e}"
            self.logger.error(f"❌ {message}")
            return False, message


# ================================
# APPLICATION RUNNER
# ================================

class EnhancedAppRunner:
    """Enhanced application runner with comprehensive validation."""

    def __init__(self, debug_mode: bool = False):
        """Initialize enhanced app runner."""
        self.debug_mode = debug_mode
        self.logger = setup_logging(debug_mode)
        self.config = AppConfig()

        # Add src to Python path for imports
        import sys
        src_path = str(Path('src').resolve())
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        self.dependency_validator = DependencyValidator(self.logger)
        self.system_validator = SystemValidator(self.logger)
        self.day6_validator = Day6FeatureValidator(self.logger)

    def print_banner(self):
        """Print application banner."""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🤖 {self.config.APP_NAME:<50} ║
║                                                              ║
║  Version: {self.config.VERSION:<48} ║
║  Day 6 Complete: Professional Edition                       ║
║                                                              ║
║  ✨ New Features:                                            ║
║  • Enhanced UI with animations                               ║
║  • Professional PDF export                                   ║
║  • Advanced analytics & insights                             ║
║  • User preferences & customization                          ║
║  • Mobile-optimized interface                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive system validation."""
        self.logger.info("🚀 Starting comprehensive validation...")

        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'dependencies': {},
            'system': {},
            'day6_features': {},
            'overall_status': 'unknown',
            'can_run': False,
            'warnings': [],
            'errors': []
        }

        # Validate dependencies
        dep_results = self.dependency_validator.validate_all_dependencies()
        validation_results['dependencies'] = dep_results

        if not dep_results['all_required_ok']:
            validation_results['errors'].append("Required dependencies missing")

        # Validate system structure
        dirs_ok, missing_dirs = self.system_validator.validate_directory_structure()
        files_ok, missing_files = self.system_validator.validate_required_files()
        env_ok, env_message = self.system_validator.validate_environment_setup()

        validation_results['system'] = {
            'directories_ok': dirs_ok,
            'missing_directories': missing_dirs,
            'files_ok': files_ok,
            'missing_files': missing_files,
            'environment_ok': env_ok,
            'environment_message': env_message
        }

        if not dirs_ok:
            validation_results['errors'].append(f"Missing directories: {missing_dirs}")
        if not files_ok:
            validation_results['errors'].append(f"Missing files: {missing_files}")
        if not env_ok:
            validation_results['warnings'].append(env_message)

        # Validate Day 6 features
        pdf_ok, pdf_msg = self.day6_validator.validate_pdf_generation()
        analytics_ok, analytics_msg = self.day6_validator.validate_analytics()
        prefs_ok, prefs_msg = self.day6_validator.validate_user_preferences()

        validation_results['day6_features'] = {
            'pdf_generation': {'available': pdf_ok, 'message': pdf_msg},
            'analytics': {'available': analytics_ok, 'message': analytics_msg},
            'user_preferences': {'available': prefs_ok, 'message': prefs_msg}
        }

        if not pdf_ok:
            validation_results['warnings'].append(f"PDF generation: {pdf_msg}")
        if not analytics_ok:
            validation_results['warnings'].append(f"Analytics: {analytics_msg}")
        if not prefs_ok:
            validation_results['warnings'].append(f"User preferences: {prefs_msg}")

        # Determine overall status
        critical_errors = len(validation_results['errors']) > 0
        has_warnings = len(validation_results['warnings']) > 0

        if critical_errors:
            validation_results['overall_status'] = 'failed'
            validation_results['can_run'] = False
        elif has_warnings:
            validation_results['overall_status'] = 'warning'
            validation_results['can_run'] = True
        else:
            validation_results['overall_status'] = 'success'
            validation_results['can_run'] = True

        return validation_results

    def print_validation_summary(self, results: Dict[str, Any]):
        """Print validation summary."""
        status = results['overall_status']

        print("\n" + "=" * 60)
        print("📋 VALIDATION SUMMARY")
        print("=" * 60)

        # Overall status
        status_emoji = {"success": "✅", "warning": "⚠️", "failed": "❌"}
        print(f"Status: {status_emoji.get(status, '❓')} {status.upper()}")
        print(f"Can Run: {'✅ YES' if results['can_run'] else '❌ NO'}")

        # Dependencies
        dep_info = results['dependencies']
        print(f"\n🔍 Dependencies:")
        print(f"  Python: {'✅' if dep_info['python_ok'] else '❌'} {dep_info['python_info']}")

        required_ok = len(dep_info['missing_required']) == 0
        print(f"  Required Packages: {'✅' if required_ok else '❌'} {len(dep_info['required_packages'])} packages")

        if dep_info['missing_required']:
            print(f"    Missing: {', '.join(dep_info['missing_required'])}")

        optional_missing = len(dep_info['missing_optional'])
        if optional_missing:
            print(f"  Optional Packages: ⚠️  {optional_missing} missing (non-critical)")

        # System structure
        sys_info = results['system']
        print(f"\n📁 System Structure:")
        print(f"  Directories: {'✅' if sys_info['directories_ok'] else '❌'}")
        print(f"  Files: {'✅' if sys_info['files_ok'] else '❌'}")
        print(f"  Environment: {'✅' if sys_info['environment_ok'] else '⚠️'} {sys_info['environment_message']}")

        # Day 6 features
        day6_info = results['day6_features']
        print(f"\n✨ Day 6 Features:")
        for feature, info in day6_info.items():
            emoji = "✅" if info['available'] else "⚠️"
            print(f"  {feature.replace('_', ' ').title()}: {emoji} {info['message']}")

        # Errors and warnings
        if results['errors']:
            print(f"\n❌ ERRORS:")
            for error in results['errors']:
                print(f"  • {error}")

        if results['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in results['warnings']:
                print(f"  • {warning}")

        # Installation help
        if dep_info['missing_required']:
            print(f"\n💡 TO FIX DEPENDENCIES:")
            install_commands = self.dependency_validator.generate_install_commands(dep_info['missing_required'])
            for cmd in install_commands:
                print(f"  {cmd}")

        print("=" * 60)

    def run_streamlit_app(self, port: int = None, host: str = "localhost"):
        """Run the Streamlit application."""
        port = port or self.config.DEFAULT_PORT

        try:
            self.logger.info(f"🚀 Starting Streamlit app on {host}:{port}")

            cmd = [
                sys.executable, "-m", "streamlit", "run",
                self.config.STREAMLIT_APP,
                "--server.port", str(port),
                "--server.address", host,
                "--server.headless", "true" if os.getenv("CI") else "false",
                "--browser.gatherUsageStats", "false"
            ]

            if self.debug_mode:
                cmd.extend(["--logger.level", "debug"])

            # Add environment variables
            env = os.environ.copy()
            env["STREAMLIT_THEME_PRIMARY_COLOR"] = "#1e40af"
            env["STREAMLIT_THEME_BACKGROUND_COLOR"] = "#ffffff"

            subprocess.run(cmd, env=env)

        except KeyboardInterrupt:
            self.logger.info("🛑 Application stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Failed to start Streamlit: {e}")
            sys.exit(1)

    def auto_fix_issues(self, results: Dict[str, Any]) -> bool:
        """Attempt to automatically fix common issues."""
        self.logger.info("🔧 Attempting to auto-fix issues...")

        fixed_issues = []

        # Create missing directories
        missing_dirs = results['system']['missing_directories']
        if missing_dirs:
            if self.system_validator.create_missing_directories(missing_dirs):
                fixed_issues.append(f"Created missing directories: {missing_dirs}")

        # Install missing packages (prompt user)
        missing_packages = results['dependencies']['missing_required']
        if missing_packages:
            print(f"\n⚠️  Missing required packages: {missing_packages}")
            response = input("Install missing packages automatically? (y/N): ")

            if response.lower() in ['y', 'yes']:
                try:
                    install_commands = self.dependency_validator.generate_install_commands(missing_packages)
                    for cmd in install_commands:
                        self.logger.info(f"Running: {cmd}")
                        subprocess.run(cmd.split(), check=True)

                    fixed_issues.append(f"Installed packages: {missing_packages}")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to install packages: {e}")

        if fixed_issues:
            self.logger.info(f"✅ Fixed issues: {fixed_issues}")
            return True

        return False


# ================================
# MAIN FUNCTION
# ================================

def main():
    """Enhanced main function with comprehensive setup and validation."""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=f"{AppConfig.APP_NAME} - Professional Meeting Minutes Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_app.py                    # Run with validation
  python run_app.py --setup            # Run setup validation only  
  python run_app.py --debug            # Run with debug logging
  python run_app.py --port 8502        # Run on custom port
  python run_app.py --fix              # Auto-fix common issues
  python run_app.py --no-validation    # Skip validation (not recommended)
        """
    )

    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--setup', action='store_true', help='Run setup validation only')
    parser.add_argument('--port', type=int, default=AppConfig.DEFAULT_PORT, help='Streamlit port')
    parser.add_argument('--host', default='localhost', help='Streamlit host')
    parser.add_argument('--fix', action='store_true', help='Attempt to auto-fix issues')
    parser.add_argument('--no-validation', action='store_true', help='Skip validation')
    parser.add_argument('--export-validation', help='Export validation results to JSON file')

    args = parser.parse_args()

    # Initialize enhanced app runner
    runner = EnhancedAppRunner(debug_mode=args.debug)

    # Print banner
    runner.print_banner()

    # Run validation unless explicitly skipped
    if not args.no_validation:
        validation_results = runner.run_comprehensive_validation()
        runner.print_validation_summary(validation_results)

        # Export validation results if requested
        if args.export_validation:
            try:
                with open(args.export_validation, 'w') as f:
                    json.dump(validation_results, f, indent=2)
                print(f"✅ Validation results exported to {args.export_validation}")
            except Exception as e:
                print(f"❌ Failed to export validation results: {e}")

        # Handle setup-only mode
        if args.setup:
            if validation_results['can_run']:
                print("\n✅ Setup validation completed successfully!")
                print("You can now run the application with: python run_app.py")
            else:
                print("\n❌ Setup validation failed. Please fix the issues above.")
                if args.fix:
                    if runner.auto_fix_issues(validation_results):
                        print("🔧 Auto-fix completed. Please run setup validation again.")
                    else:
                        print("🔧 Auto-fix could not resolve all issues.")
            return

        # Auto-fix if requested
        if args.fix and not validation_results['can_run']:
            if runner.auto_fix_issues(validation_results):
                print("🔧 Re-running validation after auto-fix...")
                validation_results = runner.run_comprehensive_validation()
                runner.print_validation_summary(validation_results)

        # Check if we can run
        if not validation_results['can_run']:
            print("\n❌ Cannot start application due to critical errors.")
            print("Please fix the issues above or run with --fix to attempt auto-repair.")
            sys.exit(1)

        if validation_results['warnings']:
            print("\n⚠️  Application can run but some features may be limited.")
            response = input("Continue anyway? (Y/n): ")
            if response.lower() in ['n', 'no']:
                print("Setup cancelled by user.")
                sys.exit(0)

    # Start the application
    print(f"\n🚀 Starting {AppConfig.APP_NAME}...")
    print(f"📱 Access the app at: http://{args.host}:{args.port}")
    print("🛑 Press Ctrl+C to stop the application")
    print("=" * 60)

    runner.run_streamlit_app(port=args.port, host=args.host)


if __name__ == "__main__":
    main()