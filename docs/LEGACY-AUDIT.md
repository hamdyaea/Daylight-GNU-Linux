# Historical audit and porting decisions

The starting master reference is 8596034092314e9a59ebf4720e470ac777a5ddd8; Version4 is e56dd21c6935770728e2611b78637864976f7b65. Historical branches and the original local working copy are preserved.

The old Conky updates every second, hard-codes enp0s3 and duplicates process-memory rows. The new Lua configuration provides balanced (2 seconds) and minimal (5 seconds) profiles, resolves a default interface and avoids repeated process rankings. Conky itself is retained: no unmeasured claim is made that a Rust graphical replacement would be faster.

The old Fluxbox startup includes /root paths, a fixed sleep and automatic terminal, welcome and log-launcher execution. The new separate session uses user-owned isolated settings and does not inherit the old rsyslog boot reporting.

The Python password generator used the random module, which is unsuitable for security-sensitive generation. Its replacement uses Linux getrandom and rejection sampling. PyConnect queried Google over HTTP and invoked ifconfig/ping through shell commands; the replacement is local-only by default, with an explicit remote check and no evaluation of user input as shell code.

Modernized application logic covers password generation, connection inspection, temperature conversion, date differences, dice, coin flipping, lottery simulation, rock/paper/scissors/lizard/Spock, battle cards, generic tournaments, fictional basketball scores, memory, slots, guessing, speech and a local alarm. Native GUI dialogs use YAD only while open. These are new implementations, not promises of identical legacy interface or rule parity. Old FIFA/NBA rosters are not advertised as current; the alarm no longer automatically opens YouTube.

Simulations are offline entertainment without money or betting. The historical background is preserved. New SVG graphics are working mountain/sun designs, not a finished photorealistic wallpaper collection.
