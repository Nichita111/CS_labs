#!/bin/bash
# Takes the screenshots for the report (macOS only).
#
# For every scenario in scripts/scenarios/ (or only the ones given as
# arguments, e.g. `01_task1_encrypt`) it opens a new Terminal.app window,
# starts `python3 main.py` there and types the scenario lines into it, one per
# prompt. Before the last line (the final "0 - Exit") a helper Terminal window
# captures the program window alone into images/<scenario>.png.
#
# Terminal.app needs the Screen Recording permission
# (System Settings > Privacy & Security > Screen & System Audio Recording).
# Windows are found through their tty, so other open Terminal windows are
# never touched.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COLUMNS_WIDE=125
cd "$LAB_DIR"
mkdir -p images

if [ $# -gt 0 ]; then
    scenarios=("$@")
else
    scenarios=()
    for file in scripts/scenarios/*.txt; do scenarios+=("$(basename "$file" .txt)"); done
fi

terminal() { osascript -e "tell application \"Terminal\" to $1"; }

# Opens a window with the given size; prints its id.
new_window() {
    osascript <<EOF
tell application "Terminal"
    set newTab to do script ""
    set newTty to tty of newTab
    set number of columns of newTab to $1
    set number of rows of newTab to $2
    repeat with w in windows
        if tty of selected tab of w is newTty then return id of w
    end repeat
    error "new window not found"
end tell
EOF
}

# Types a line into the window (like the keyboard does, followed by Return).
type_line() {
    local text=${2//\\/\\\\}
    text=${text//\"/\\\"}
    terminal "do script \"$text\" in selected tab of window id $1" >/dev/null
}

wait_until_idle() {
    sleep 1
    while [ "$(terminal "busy of selected tab of window id $1")" = "true" ]; do sleep 0.3; done
}

# Waits until the visible text ends with a prompt (": ").
wait_for_prompt() {
    for _ in $(seq 50); do
        if terminal "contents of selected tab of window id $1" | sed -e 's/[[:space:]]*$//' | grep -v '^$' | tail -1 | grep -q ':$'; then
            sleep 0.3
            return
        fi
        sleep 0.2
    done
    echo "timeout waiting for a prompt in window $1" >&2
    exit 1
}

helper_id=$(new_window 80 10)
sleep 1.5
trap 'terminal "close window id $helper_id" >/dev/null 2>&1 || true' EXIT

for name in "${scenarios[@]}"; do
    # Dry run with expect, to size the window to the session: every screen
    # row (long lines wrap) up to the final "Choose an option: " prompt.
    rows=$(LANG=en_US.UTF-8 expect scripts/play.exp "scripts/scenarios/$name.txt" | python3 -c '
import math, re, sys
cols = int(sys.argv[1])
lines = sys.stdin.read().replace("\r", "").split("\n")[:-2]  # drop "" and "Bye!"
lines = [re.sub(r"\x1b\[[0-9;]*m", "", line) for line in lines]
print(sum(max(1, math.ceil(len(line) / cols)) for line in lines))
' "$COLUMNS_WIDE")
    rm -f "images/$name.png"

    win_id=$(new_window "$COLUMNS_WIDE" "$rows")
    sleep 1.5  # let the shell start
    type_line "$win_id" "cd '$LAB_DIR' && clear && python3 main.py"

    inputs=()
    while IFS= read -r line; do inputs+=("$line"); done < "scripts/scenarios/$name.txt"
    last=$((${#inputs[@]} - 1))
    for i in "${!inputs[@]}"; do
        wait_for_prompt "$win_id"
        if [ "$i" -eq "$last" ]; then
            type_line "$helper_id" "screencapture -x -o -l $win_id '$LAB_DIR/images/$name.png'"
            wait_until_idle "$helper_id"
        fi
        type_line "$win_id" "${inputs[$i]}"
    done

    wait_until_idle "$win_id"
    terminal "close window id $win_id" >/dev/null
    if [ -s "images/$name.png" ]; then
        echo "images/$name.png (${rows} rows)"
    else
        echo "FAILED: images/$name.png was not created (Screen Recording permission for Terminal?)" >&2
        exit 1
    fi
done
