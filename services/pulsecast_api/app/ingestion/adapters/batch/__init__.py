"""
Batch adapters for files, object storage, JDBC sources, and enterprise stubs.
"""

# Import adapters for side-effect registration
from . import csv_file, s3_object, sftp_file, jdbc_table, enterprise_stubs

__all__ = [
    "csv_file",
    "s3_object",
    "sftp_file",
    "jdbc_table",
    "enterprise_stubs",
]
