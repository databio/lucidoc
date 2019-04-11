# Changelog

## [0.3] - 2019-04-11
### Added
- By default, print version info for documentation target and for this package in footer of each docs page; this may be omitted with `--omit-meta`.
### Changed
- Using [`logmuse`](https://pypi.org/project/logmuse/) for logging
### Fixed
- Allow Python3 to discover each class's member functions, not just properties.
- Make `--whitelist` and `--blacklist` CLI options functional.

## [0.2] - 2019-03-20
### Added
- Support for specific inclusion/exclusion of objects for documentation.
- Support specification of grouping objects into separate documentation files.
### Changed
- Make signature for property match that of function with empty parameter list.

## [0.1] - 2019-03-11
- First release version
