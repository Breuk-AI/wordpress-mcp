#!/usr/bin/env python3
"""
WordPress MCP - Public Release Cleanup Script
Prepares the repository for public release by removing development files
and keeping only user-facing utilities.
"""

import os
import shutil
import subprocess
from pathlib import Path
import json

class PublicReleaseCleanup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.files_removed = []
        self.files_kept = []
        self.directories_archived = []
        
    def run_git_command(self, command):
        """Run a git command and return success status."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Git command failed: {e}")
            return False
    
    def remove_development_files(self):
        """Remove all development and deployment batch files."""
        print("\n🗑️  Removing development files...")
        print("=" * 50)
        
        # List of files to remove (development/deployment tools)
        files_to_remove = [
            # Git/deployment automation
            "push-to-github.bat",
            "push-updates.bat", 
            "push-with-tests.bat",
            "final-push.bat",
            "final-push-now.bat",
            "finish-push.bat",
            "secure-github-push.bat",
            "quick-secure-push.bat",
            "ONE_CLICK_DEPLOY.bat",
            "setup-github.bat",  # Git initialization - not for end users
            
            # Fix/patch scripts
            "fix-github-remote.bat",
            "fix-ci-final.bat",
            "apply-security-patches.bat",
            "deploy-security-fixes.bat",
            
            # Check/verify scripts (development)
            "check-github.bat",
            "check-deployment-status.bat",
            "verify-github.bat",
            "test-diagnostic.bat",
            
            # Beautification/badges
            "add-badges.bat",
            "make-it-pretty.bat",
            "full-beautification.bat",
            
            # Release/setup scripts
            "create-release.bat",
            "setup-professional-repo.bat",
            
            # Helper files
            "deploy_helper.py",
            
            # Previous cleanup scripts (remove themselves)
            "cleanup-bat-files.bat",
            "cleanup_files.py",
            "cleanup.sh",
            "do_cleanup.bat",
            "PROFESSIONAL_CLEANUP.bat",
            
            # Documentation that's development-specific
            "CLEANUP_PLAN.md",
            "DEPLOYMENT_COMPLETE.md",
            "DEPLOYMENT_README.md",
            "SESSION_AUGUST_20_2025.md",
            "SESSION_SUMMARY.md",
            "SECURITY_FIXES.md",
            "CHAT_HISTORY_2025-01-19_FirstRelease.md",
            "RELEASE_NOTES_v1.0.1.md",
        ]
        
        for filename in files_to_remove:
            filepath = self.project_root / filename
            if filepath.exists():
                # Try git rm first, fall back to regular delete
                if self.run_git_command(f'git rm "{filename}" 2>nul'):
                    print(f"✓ Git removed: {filename}")
                else:
                    filepath.unlink()
                    print(f"✓ Deleted: {filename}")
                self.files_removed.append(filename)
            else:
                print(f"- Already gone: {filename}")
    
    def rename_user_scripts(self):
        """Rename user-facing scripts to be more descriptive."""
        print("\n✏️  Renaming user scripts...")
        print("=" * 50)
        
        # Rename run-tests.bat to verify-install.bat
        old_test = self.project_root / "run-tests.bat"
        new_test = self.project_root / "verify-install.bat"
        
        if old_test.exists():
            # Read and modify the content with UTF-8 encoding
            content = old_test.read_text(encoding='utf-8')
            content = content.replace(
                "Running WordPress MCP Tests",
                "Verifying WordPress MCP Installation"
            )
            content = content.replace(
                "Ready to push to GitHub!",
                "WordPress MCP is properly installed!"
            )
            # Remove the git command suggestion at the end
            lines = content.split('\n')
            filtered = [line for line in lines if not line.startswith('echo Run: git add')]
            content = '\n'.join(filtered)
            
            # Write to new file with UTF-8 encoding
            new_test.write_text(content, encoding='utf-8')
            
            # Remove old file via git
            self.run_git_command(f'git rm "{old_test.name}"')
            print(f"✓ Renamed: run-tests.bat → verify-install.bat")
            
            # Stage the new file
            self.run_git_command(f'git add "{new_test.name}"')
    
    def archive_old_backups(self):
        """Archive old backup directories."""
        print("\n📦 Archiving old backup directories...")
        print("=" * 50)
        
        backup_dirs = ["backups", "security-backups"]
        archive_dir = self.project_root / ".archive"
        
        for dirname in backup_dirs:
            dirpath = self.project_root / dirname
            if dirpath.exists() and dirpath.is_dir():
                # Create archive directory if it doesn't exist
                archive_dir.mkdir(exist_ok=True)
                
                # Move to archive
                archive_path = archive_dir / dirname
                if archive_path.exists():
                    shutil.rmtree(archive_path)
                shutil.move(str(dirpath), str(archive_path))
                
                # Remove from git
                self.run_git_command(f'git rm -rf "{dirname}" 2>nul')
                print(f"✓ Archived: {dirname} → .archive/{dirname}")
                self.directories_archived.append(dirname)
        
        # Add .archive to .gitignore
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text(encoding='utf-8')
            if ".archive/" not in content:
                with open(gitignore, 'a', encoding='utf-8') as f:
                    f.write("\n# Archived directories\n.archive/\n")
                print("✓ Added .archive/ to .gitignore")
    
    def list_kept_files(self):
        """List files that are being kept for users."""
        print("\n✅ Files kept for users:")
        print("=" * 50)
        
        user_files = [
            "setup-env.bat",
            "verify-install.bat",
            "setup-github.sh",  # For Linux/Mac users
            ".env.example",
            "requirements-dev.txt",
            "setup.py"
        ]
        
        for filename in user_files:
            filepath = self.project_root / filename
            if filepath.exists():
                print(f"✓ {filename}")
                self.files_kept.append(filename)
    
    def update_readme(self):
        """Update README to reflect the cleaned structure."""
        print("\n📝 Updating README...")
        print("=" * 50)
        
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            # Read with UTF-8 encoding to handle special characters
            content = readme_path.read_text(encoding='utf-8')
            
            # Update any references to run-tests.bat
            content = content.replace("run-tests.bat", "verify-install.bat")
            
            # Update setup instructions if needed
            if "setup-github.bat" in content:
                content = content.replace(
                    "setup-github.bat",
                    "git clone https://github.com/Breuk-AI/wordpress-mcp.git"
                )
            
            # Write with UTF-8 encoding
            readme_path.write_text(content, encoding='utf-8')
            print("✓ Updated README.md")
    
    def create_summary(self):
        """Create a summary of the cleanup."""
        print("\n" + "=" * 60)
        print("🎉 PUBLIC RELEASE CLEANUP COMPLETE!")
        print("=" * 60)
        
        print(f"\n📊 Summary:")
        print(f"  • Files removed: {len(self.files_removed)}")
        print(f"  • Files kept: {len(self.files_kept)}")
        print(f"  • Directories archived: {len(self.directories_archived)}")
        
        print("\n📁 Repository structure is now clean and user-friendly!")
        print("\nNext steps:")
        print("1. Review changes: git status")
        print("2. Commit: git commit -m '🎯 Clean repository for public release'")
        print("3. Push: git push origin main")
        
        # Save summary to memory
        summary = {
            "action": "Public Release Cleanup",
            "files_removed": len(self.files_removed),
            "files_kept": self.files_kept,
            "directories_archived": self.directories_archived
        }
        
        return summary
    
    def run(self):
        """Execute the complete cleanup process."""
        print("🚀 WordPress MCP - Public Release Cleanup")
        print("=" * 60)
        print("This will prepare the repository for public release by:")
        print("• Removing development/deployment scripts")
        print("• Keeping only user-facing utilities")
        print("• Archiving old backup directories")
        print("• Renaming scripts for clarity")
        
        input("\nPress Enter to continue (Ctrl+C to cancel)...")
        
        self.remove_development_files()
        self.rename_user_scripts()
        self.archive_old_backups()
        self.list_kept_files()
        self.update_readme()
        
        return self.create_summary()

if __name__ == "__main__":
    cleanup = PublicReleaseCleanup()
    summary = cleanup.run()
    
    # The script will remove itself in the next commit
    print("\n⚠️  Note: This cleanup script (public_release_cleanup.py)")
    print("   will be removed after you commit the changes.")
