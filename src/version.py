"""
===================================================================================================
Title : version.py

Description : version module, easy to update from code

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

import subprocess

def get_git_commit_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode('utf-8')
    except Exception:
        return "Unknown"

BUILD_VERSION = "0.1.1"
BUILD_DATE = "14-12-2024"
BUILD_NAME = "ant-agent"

COMMIT_HASH = get_git_commit_hash()