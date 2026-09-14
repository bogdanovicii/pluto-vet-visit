#!/usr/bin/env bash
# The Vet Visit: log check. Usage: ./vet_check.sh [path/to/BepInEx/LogOutput.log]
# Prints PASS/FAIL/INFO lines and exits non-zero on any FAIL. Safe to run while the game is closed.
LOG="${1:-$HOME/.var/app/io.github.ebkr.r2modman/config/r2modmanPlus-local/ETG/profiles/Default/BepInEx/LogOutput.log}"
[ -f "$LOG" ] || { echo "FAIL log not found: $LOG"; exit 2; }
fail=0
chk() { # chk <expect:present|absent> <label> <pattern>
  local n; n=$(grep -c -- "$3" "$LOG")
  if [ "$1" = present ]; then [ "$n" -gt 0 ] && echo "PASS $2 ($n)" || { echo "FAIL $2 (0 matches)"; fail=1; }
  else [ "$n" -eq 0 ] && echo "PASS $2" || { echo "FAIL $2 ($n matches)"; fail=1; }; fi
}
info() { local n; n=$(grep -c -- "$2" "$LOG"); echo "INFO $1 ($n)"; }
echo "log: $LOG ($(wc -l < "$LOG") lines)"
chk present "plugin loaded"          "Loading \[Pluto The Cat - The Vet Visit"
chk present "Pluto found"            "\[VetVisit\] found Pluto"
chk present "ready"                  "\[VetVisit\] The Vet Visit is ready"
chk absent  "no step failure"        "\[VetVisit\] step \".*\" failed"
chk absent  "no Pluto missing"       "Pluto the Cat not found"
chk absent  "no missing room asset"  "Unable to find asset"
chk absent  "no room build failure"  "Failed to build room"
info "past level built"              "\[VetVisit\] built past dungeon"
info "clinic ready"                  "\[VetVisit\] clinic ready"
info "doors found"                   "\[VetVisit\] doors found"
info "intro cast"                    "\[VetVisit\] intro: owner"
info "wave 1 cleared"                "\[VetVisit\] wave 1 cleared"
info "wave 2 cleared"                "\[VetVisit\] wave 2 cleared"
info "Vet Tech built"                "\[VetVisit\] Vet Tech built"
info "Nurse built"                   "\[VetVisit\] The Nurse built"
info "reinforcements"                "\[VetVisit\] the Vet calls the Nurse"
info "fight started"                 "\[VetVisit\] fight started"
info "past killed"                   "\[VetVisit\] past killed"
echo "--- lines to send back ---"
grep -n "\[VetVisit\]\|PlutoVetVisit\|\[Alexandria\]" "$LOG" | head -80
[ $fail -eq 0 ] && echo "RESULT: PASS" || echo "RESULT: FAIL"
exit $fail
