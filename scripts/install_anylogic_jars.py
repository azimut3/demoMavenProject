#!/usr/bin/env python3
"""
Script to install AnyLogic JAR files into local Maven repository
"""

import os
import subprocess
import sys

def install_jar_to_maven(jar_path, group_id, artifact_id, version):
    """Install a JAR file to local Maven repository"""
    try:
        cmd = [
            "mvn", "install:install-file",
            f"-Dfile={jar_path}",
            f"-DgroupId={group_id}",
            f"-DartifactId={artifact_id}",
            f"-Dversion={version}",
            "-Dpackaging=jar",
            "-DgeneratePom=true"
        ]
        
        print(f"Installing {os.path.basename(jar_path)}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Successfully installed {artifact_id}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {artifact_id}: {e}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function to install all AnyLogic JAR files"""
    print("Installing AnyLogic JAR files to local Maven repository...")
    print("=" * 60)
    
    # Define the JAR files and their Maven coordinates
    jar_files = [
        ("additional libs/al3d.jar", "com.anylogic.custom-model", "al3d", "1"),
        ("additional libs/engine.jar", "com.anylogic.custom-model", "engine", "1"),
        ("additional libs/engine.nl.jar", "com.anylogic.custom-model", "engine.nl", "1"),
        ("additional libs/engine.sa.jar", "com.anylogic.custom-model", "engine.sa", "1"),
        ("additional libs/process-modeling-library.jar", "com.anylogic.custom-model", "process-modeling-library", "1"),
        ("additional libs/rail-library.jar", "com.anylogic.custom-model", "rail-library", "1"),
        ("additional libs/grain-model.jar", "com.eiei.custom-model", "grain-model", "1.7")
    ]
    
    success_count = 0
    total_count = len(jar_files)
    
    for jar_path, group_id, artifact_id, version in jar_files:
        if os.path.exists(jar_path):
            if install_jar_to_maven(jar_path, group_id, artifact_id, version):
                success_count += 1
        else:
            print(f"⚠️  JAR file not found: {jar_path}")
    
    print("\n" + "=" * 60)
    print(f"Installation complete: {success_count}/{total_count} JAR files installed")
    
    if success_count == total_count:
        print("✅ All JAR files installed successfully!")
        print("\nYou can now run:")
        print("  mvn clean install")
        print("  mvn spring-boot:run")
    else:
        print("❌ Some JAR files failed to install")
        print("Please check the error messages above")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
