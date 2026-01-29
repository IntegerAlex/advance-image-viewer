# Changelog

All notable changes to **Advance Image Viewer** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2026-01-29

### Added
- **Video Format Support**: Comprehensive video file support for 10+ formats
  - WebM (VP8/VP9), MP4 (H.264/H.265), AVI, MOV, MKV, FLV, WMV, M4V, 3GP, OGV
  - Automatic video detection and frame extraction
  - RFC 6386 compliant WebP image format support
- **Frame Navigation System**: Interactive video frame navigation
  - Frame slider with smooth throttled updates (10 updates/second max)
  - Direct frame number input with validation
  - Real-time frame counter display
- **Frame Export Functionality**: Export individual video frames as images
  - Export current frame with intelligent filename generation
  - Support for PNG, JPEG, and other image formats
  - File dialog with format selection
- **Video Metadata Display**: Comprehensive video information panel
  - Total frames, FPS, duration (HH:MM:SS format)
  - Video codec information
  - Resolution and file size details
- **Thumbnail Preview Grid**: Visual frame navigation
  - 20 evenly-distributed thumbnails in 2-column grid
  - Clickable thumbnails for instant frame navigation
  - Scrollable canvas with mouse wheel support
  - High-quality LANCZOS resampling for thumbnails
- **Performance Optimizations**: Enhanced video playback performance
  - Frame caching system (10 frame LRU cache)
  - Throttled slider updates to prevent excessive frame extractions
  - Immediate UI feedback during frame navigation
  - Efficient frame extraction with proper resource cleanup
- **Gemini AI Integration**: Video frame processing with AI
  - Automatic frame extraction for AI processing
  - Temporary file management for video frames
  - Seamless integration with existing AI workflow

### Changed
- **File Dialog**: Enhanced to support video formats and WebP images
  - Added video file type filters
  - Added WebP image format support
  - Improved file type categorization
- **Image Loading**: Unified image/video loading pipeline
  - Automatic format detection
  - Video controls appear dynamically when video is loaded
  - Graceful fallback for unsupported formats

### Fixed
- **LegacyReader Compatibility**: Fixed frame count detection for legacy imageio readers
  - Added fallback to metadata-based frame count calculation
  - Improved error handling for various video codecs
  - Better compatibility with different imageio backends

### Technical Improvements
- Added `src/video_utils.py` module for video processing utilities
- Implemented frame caching with FIFO eviction policy
- Enhanced error handling for video file operations
- Improved resource management with proper reader cleanup
- Added comprehensive video metadata extraction

## [0.2.1] - 2025-11-21

### Added
- Comprehensive documentation restructuring
  - Created dedicated `FEATURES.md` with detailed technical specifications
  - Created `CONTRIBUTING.md` with development guidelines and architecture
  - Reorganized `README.md` for user-focused experience
  - Added resource references to all documentation files

### Changed
- **Release Scripts**: Modified to upload assets to existing releases instead of deleting/recreating them
- **Cloudflare Worker**: Fixed asset naming mismatch for Windows installer
- **Documentation**: Transformed README to use more intellectual and technical language
- **Installer Scripts**: Corrected sed command escaping for proper tag extraction

### Fixed
- **Critical Bug**: AttributeError when launching with image path - 'SimpleImageViewer' object has no attribute 'metadata_text'
  - Fixed UI initialization order to prevent accessing uninitialized widgets
  - Reordered component creation to ensure metadata_text exists before image loading
- Windows installer asset naming inconsistency (`imageviewer.exe-windows-x86_64.exe`)
- Release script behavior to preserve existing releases
- Template literal variable interpolation issues in Cloudflare Worker

### Technical Improvements
- Enhanced cross-platform compatibility for release management
- Improved error handling in installation scripts
- Optimized documentation structure for better user/developer separation

## [0.2.0] - 2025-11-19

### Added
- **Menu Bar Interface**: Complete File menu with Open, Save As, and Exit options
- **Keyboard Shortcuts**: Full keyboard navigation support (Ctrl+O, Ctrl+S, Ctrl+Q)
- **Enhanced File Opening**: Menu-based file selection with improved user experience
- **Optional Command Line**: Image path argument now optional, application starts with empty interface

### Changed
- **Startup Behavior**: Removed automatic file dialog when no image path provided
- **UI Theme**: Reverted to classic dark theme (gray colors) for better compatibility
- **Save Functionality**: Moved save button to menu bar for cleaner interface
- **Documentation**: Updated README to reflect new CLI behavior and menu features

### Technical Improvements
- Added `handle_open_file()` method for menu-based file operations
- Enhanced `display_image()` to handle empty state gracefully
- Improved error handling for file operations
- Better separation of UI initialization and image loading logic

## [0.1.0] - 2025-11-17

### Added
- **Initial Release**: Complete image viewing application with AI capabilities
- **Core Features**:
  - Cursor-centric zoom mechanics with advanced transformation algorithms
  - High-performance rendering using PIL/Pillow
  - AI-powered image editing via Google Gemini API integration
  - Comprehensive debug interface with real-time telemetry
  - Cross-platform compatibility (Linux, macOS, Windows)

- **Technical Architecture**:
  - Modular event-driven design with Tkinter GUI framework
  - Asynchronous AI processing for responsive UI
  - Intelligent caching and memory management
  - Plugin architecture for extensibility

- **Distribution Infrastructure**:
  - PyInstaller-based standalone executable generation
  - Automated release scripts for multi-platform builds
  - Cloudflare CDN integration for global distribution
  - One-click installation scripts for all platforms

- **Development Tools**:
  - Build orchestration with `build.py`
  - Comprehensive release management with GitHub integration
  - Cross-platform testing and validation

### Technical Specifications
- **Python Version**: 3.8+ (optimized for 3.10+)
- **Dependencies**: PIL/Pillow, requests, Tkinter
- **Platform Support**: Linux (x86_64, aarch64), Windows (x86_64), macOS (planned)
- **AI Integration**: Google Gemini 1.5 Pro/Flash models
- **Build System**: PyInstaller for standalone executables

---

## Version History

### Version Numbering
This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Release Types
- **Stable Releases**: Tagged versions (e.g., `v1.0.0`) with full testing
- **Pre-releases**: Alpha/Beta/RC versions for testing (e.g., `v1.0.0-alpha.1`)
- **Nightly Builds**: Development snapshots (not tagged)

### Release Channels
- **GitHub Releases**: Official stable releases with binaries
- **Cloudflare CDN**: Global distribution for installation scripts
- **Source Distribution**: PyPI/source code releases

---

## Contributing to Changelog

When contributing changes:

1. **Categorize Changes**: Use appropriate sections (Added, Changed, Fixed, Removed, Deprecated)
2. **Reference Issues**: Link to GitHub issues/PRs when applicable
3. **Technical Details**: Include implementation details for significant changes
4. **Breaking Changes**: Clearly mark any backwards-incompatible changes

### Change Categories

- **Added**: New features or functionality
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security-related changes

### Example Entry

```
### Added
- New zoom interpolation algorithm improving rendering quality by 40%
  - Implements bicubic resampling with edge detection
  - Reduces memory usage for large images by 25%
  - Fixes [#123](https://github.com/user/repo/issues/123)

### Changed
- Updated Gemini API integration to use v1.5 models
  - Improved prompt processing with natural language understanding
  - Enhanced error handling for API rate limits
```

---

*"Change is the law of life. And those who look only to the past or present are certain to miss the future."* - John F. Kennedy
