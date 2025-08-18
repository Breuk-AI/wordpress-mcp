# Changelog

All notable changes to WordPress MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multisite support (planned)
- Custom post type support (planned)
- Plugin/theme activation controls (planned)
- Media upload implementation (planned)
- Child theme creation (planned)
- Cache clearing implementation (planned)

## [1.0.0] - 2024-01-XX

### Added
- Initial public release
- Core WordPress management tools (posts, pages, media)
- WooCommerce integration with auto-detection
- Template editing with automatic backups
- System information tools
- Rate limiting for API protection
- Backup manager with automatic cleanup
- Configurable CORS policies
- Environment-based configuration
- Comprehensive documentation
- WordPress plugin with admin interface
- Application Password authentication support

### Changed
- Removed all hardcoded site-specific references
- Replaced config.json with environment variables
- Improved security with proper CORS handling
- Enhanced error handling throughout

### Security
- Fixed CORS vulnerability allowing all origins
- Added input sanitization and validation
- Implemented rate limiting
- Secured backup storage location

### Removed
- Site-specific configuration values
- Insecure CORS wildcard allowance

## [0.9.0] - 2024-01-XX (Pre-release)

### Added
- Initial private implementation for monopolygowin.com
- Basic WordPress REST API integration
- WooCommerce tools foundation
- Template editing capability
- MCP protocol implementation

---

## Version Guidelines

### Version Numbers
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality additions
- PATCH version for backwards-compatible bug fixes

### Release Types
- **Alpha**: Early testing, may have breaking changes
- **Beta**: Feature complete but may have bugs
- **RC (Release Candidate)**: Final testing before stable release
- **Stable**: Production-ready release

### Deprecation Policy
- Features will be deprecated with at least one minor version notice
- Deprecated features will be removed in the next major version
- Security fixes will be backported to the last two major versions
