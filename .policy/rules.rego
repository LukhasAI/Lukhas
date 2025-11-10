package rules

deny[msg] {
  file := input.files[_]
  is_python_file(file)
  line := file.added[_]
  is_broad_except(line)
  msg := sprintf("Broad exception handler detected in %s", [file_path(file)])
}

deny[msg] {
  file := input.files[_]
  is_test_deletion(file)
  msg := sprintf("Test file deleted: %s", [file.old_path])
}

deny[msg] {
  file := input.files[_]
  is_test_line_removal(file)
  line := removed_test_line(file)
  msg := sprintf("Test removed in %s: %s", [file_path(file), line])
}

deny[msg] {
  file := input.files[_]
  is_python_file(file)
  line := removed_invariant_line(file)
  msg := sprintf("Invariant removed in %s: %s", [file_path(file), line])
}

is_python_file(file) {
  path := file_path(file)
  endswith(path, ".py")
}

file_path(file) = path {
  path := file.new_path
  path != null
}
else = path {
  path := file.old_path
}

is_broad_except(line) {
  trimmed := trim_space(line)
  re_match("^except\\s*:(\\s*#.*)?$", trimmed)
}

is_test_deletion(file) {
  file.old_path != null
  file.new_path == null
  is_test_path(file.old_path)
}

is_test_path(path) {
  contains(path, "/tests/")
}

is_test_path(path) {
  re_match("(^|/)test_", path)
}

is_test_line_removal(file) {
  file.new_path != null
  some line
  line := file.removed[_]
  is_test_definition(line)
}

removed_test_line(file) = trimmed {
  line := file.removed[_]
  is_test_definition(line)
  trimmed := trim_space(line)
}

is_test_definition(line) {
  trimmed := trim_space(line)
  not startswith(trimmed, "#")
  re_match("^(def\\s+test_|class\\s+Test)", trimmed)
}

removed_invariant_line(file) = trimmed {
  line := file.removed[_]
  trimmed := trim_space(line)
  not startswith(trimmed, "#")
  re_match("(?i)(\\bassert\\b|\\binvariant\\b)", trimmed)
}
