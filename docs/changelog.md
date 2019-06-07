# Changelog

## [0.4.0] -- 2019-06-06
### Added
- `__aliases__` (mapping from name to list of names) as hook for package to declare what exports are equivalent, and therefore which to use just one of in the documentation.
- Anchor tags to class headers

### Changed
- Improved object signature renditions in API docs.
- Improved overall styling of API docs.

### Fixed
- Take measures to ensure objects are repeatedly documented if aliased for export, even 
if the documented package doesn't declare `__aliases__`

## [0.3.1] -- 2019-04-15
- Depend on patched `logmuse`

## [0.3.0] -- 2019-04-11
### Added
- By default, print version info for documentation target and for this package in footer of each docs page; this may be omitted with `--omit-meta`.
### Changed
- Using [`logmuse`](https://pypi.org/project/logmuse/) for logging
### Fixed
- Allow Python3 to discover each class's member functions, not just properties.
- Make `--whitelist` and `--blacklist` CLI options functional.
- Improve docs rendition of nested classes

## [0.2.0] -- 2019-03-20
### Added
- Support for specific inclusion/exclusion of objects for documentation.
- Support specification of grouping objects into separate documentation files.
### Changed
- Make signature for property match that of function with empty parameter list.

## [0.1.0] -- 2019-03-11
- First release version

