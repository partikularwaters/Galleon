# Work agreement: reorganize the API modules

Purpose: make the API modules easier to navigate without changing their behavior.

Inputs: the existing architecture guide and API tests.

Allowed changes:
- Move modules within `src/api/`.
- Update imports and the architecture guide.

Preserve:
- Public API behavior.
- Existing configuration and unrelated files.

Verification:
- Run the API tests and require them to pass.
- Check that imports resolve.

Approval boundary: ask before changing public API behavior or expanding the scope.

Next action: inspect the current modules and propose the exact moves before applying them.

This is an illustrative agreement, not permission to reorganize a real project.
