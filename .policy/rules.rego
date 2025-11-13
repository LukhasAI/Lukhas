package lukhas.guard

default allow = false

default deny = []

allow {
    count(deny) == 0
}

deny[msg] {
    input.risky_exception_added
    msg := "risky_exception_added"
}

deny[msg] {
    input.counted_files > input.max_files
    msg := sprintf("counted_files_exceed_limit:%d>%d", [input.counted_files, input.max_files])
}

deny[msg] {
    input.counted_lines > input.max_lines
    msg := sprintf("counted_lines_exceed_limit:%d>%d", [input.counted_lines, input.max_lines])
}

deny[msg] {
    some idx
    file := input.protected_hits[idx]
    msg := sprintf("protected_path_touched:%s", [file])
}
